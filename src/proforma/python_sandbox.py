# -*- coding: utf-8 -*-

# This file is part of Ostfalia-Praktomat.
#
# Copyright (C) 2023 Ostfalia University
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# functions for creating sandboxes

import os
import subprocess
import venv
import docker
import tarfile

from . import sandbox, task
from django.conf import settings
from utilities.safeexec import execute_command, escape_xml_invalid_chars

import logging

logger = logging.getLogger(__name__)

compile_python = False


#class PythonSandboxInstance(sandbox.SandboxInstance):
#    """ sandbox instance for python tests """
#    def __init__(self):
#        super().__init__()

class DockerSandbox():
    remote_command = "python3 /sandbox/run_suite.py"
    remote_result_subfolder = "__result__"
    remote_result_folder = "/sandbox/" + remote_result_subfolder
    def __init__(self, container, studentenv):
        self._container = container
        self._studentenv = studentenv
        if self._container is None:
            raise Exception('could not create container')
        self._container.restart()

    def __del__(self):
        self._container.stop()
        self._container.remove()

    def uploadEnvironmment(self):
        if not os.path.exists(self._studentenv):
            raise Exception("subfolder " + self._studentenv + " does not exist")

        if len(os.listdir(self._studentenv)) == 0:
            raise Exception("subfolder " + self._studentenv + " is empty")

        # we need to change permissions on student folder in order to
        # have the required permissions inside test docker container
        os.system("chown -R praktomat:praktomat " + self._studentenv)

        # start_time = time.time()
        with tarfile.open("environment.tar", 'w:gz') as tar:
            tar.add(self._studentenv, arcname=".", recursive=True)

        logger.debug("** upload to sandbox")
        with open('environment.tar', 'rb') as fd:
            if not self._container.put_archive(path='/sandbox', data=fd):
                raise Exception('cannot put environment.tar')

    def runTests(self):
        logger.debug("** run tests in sandbox")
        # start_time = time.time()
        code, str = self._container.exec_run(DockerSandbox.remote_command, user="999")
        if code != 0:
            logger.debug(str.decode('UTF-8').replace('\n', '\r\n'))
            raise Exception("running test failed")

        # print("---run test  %s seconds ---" % (time.time() - start_time))
        logger.debug(code)
        logger.debug("Test run log")
        logger.debug(str.decode('UTF-8').replace('\n', '\r\n'))
        return str.decode('UTF-8').replace('\n', '\r\n')

    def get_result_file(self):
        self._container.stop()
        logger.debug("get result")
        tar, dict = self._container.get_archive(DockerSandbox.remote_result_folder)
        logger.debug(dict)

        with open("result.tar", 'bw') as f:
            for block in tar:
                f.write(block)

        with tarfile.open("result.tar", 'r') as tar:
            tar.extractall(path=self._studentenv)

    #        os.system("ls -al")
    #        os.system("ls -al " + remote_result_subfolder)
        resultpath = self._studentenv + '/' + DockerSandbox.remote_result_subfolder + '/unittest_results.xml'
        if not os.path.exists(resultpath):
            raise Exception("No test result file found")

        os.system("mv " + resultpath + " " + self._studentenv + '/unittest_results.xml')
        return "todo read result"

class PythonSandboxTemplate(sandbox.SandboxTemplate):
    """ python sandbox template for python tests """

    # name of python docker image
    python_image_name = "python-praktomat_sandbox"
    python_dockerfile_path = '/praktomat/docker-sandbox-image/python'

    def __init__(self, praktomat_test):
        super().__init__(praktomat_test)
        self._client = docker.from_env()
        self._tag = None

    def get_hash(requirements_txt):
        """ create simple hash for requirements.txt content """
        import hashlib
        with open(requirements_txt, 'r') as f:
            # read strip lines
            modules = [line.strip() for line in f.readlines()]
            # skip empty lines
            modules = list(filter(lambda line: len(line) > 0, modules))
            # I do not know if the order matters so I do not sort the modules!
            # Otherwise a wrong order can never be corrected.
            # modules.sort()
            # print('Modules: ' + '\n'.join(modules))
            md5 = hashlib.md5('\n'.join(modules).encode('utf-8')).hexdigest()
            return md5

    def check_preconditions(self):
        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        if len(requirements_txt) > 1:
            raise Exception('more than one requirements.txt found')

    def execute_arglist_yield(args, working_directory, environment_variables={}):
        """ yield output text during execution. """
        assert isinstance(args, list)

        command = args[:]
        # do not modify environment for current process => use copy!!
        environment = os.environ.copy()
        environment.update(environment_variables)

        logger.debug('execute command in ' + working_directory + ':')
        logger.debug('command :' + str(command))

        try:
            with subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=working_directory,
                env=environment,
                start_new_session=True, # call of os.setsid()
            ) as process:
                while True:
                    data = process.stdout.readline()  # Alternatively proc.stdout.read(1024)
                    if len(data) == 0:
                        break
                    yield 'data: ' + str(data) + '\n\n'
                # if it is too fast then get remainder
                remainder = process.communicate()[0]
                if remainder is not None and len(remainder) > 0:
                    yield 'data: ' + str(remainder) + '\n\n'

                # Get exit code
                result = process.wait(0)
                if result != 0:
                    # stop further execution
                    raise Exception('command exited with code != 0')

        except Exception as e:
            if type(e) == subprocess.TimeoutExpired:
                logger.debug("TIMEOUT")
                yield 'data: timeout\n\n'
            else:
                logger.error("exception occured: " + str(type(e)))
            raise


    def _image_exists(self, tag):
        images = self._client.images.list(
            filters = {"reference": PythonSandboxTemplate.python_image_name + ":" + tag})
        print(images)
        return len(images) > 0

    def create(self):
        """ creates a docker image """
        logger.debug("create python image (if it does not exist)")

        self.check_preconditions()

        tag = self._get_image_tag()
        if self._image_exists(tag):
            logger.debug("python image for tag " + tag + " already exists")
            yield 'data: python image for tag ' + tag + ' already exists\n\n'
            # already exists => return
            return

        yield 'data: create new python base image\n\n'
        logger.debug("create python image for tag " + tag + " from " + self.python_dockerfile_path)
        image, logs_gen = self._client.images.build(path=self.python_dockerfile_path,
                                                    tag=PythonSandboxTemplate.python_image_name+':'+tag,
                                                    rm =True)
        print(logs_gen)

        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        if len(requirements_txt) == 0:
            requirements_txt = None
            requirements_path = None
        else:
            requirements_txt = requirements_txt.first()
            requirements_path = os.path.join(settings.UPLOAD_ROOT,
                                             task.get_storage_path(requirements_txt, requirements_txt.filename))

        # logger.info('Create Python image for ' + templ_dir)
    #
    #     try:
    #         # install modules from requirements.txt if available
    #         if requirements_txt is not None:
    #             hash = PythonSandboxTemplate.get_hash(requirements_path)
    #             print(hash)
    #             yield 'data: install requirements\n\n'
    #             logger.info('install requirements')
    #             # rc = subprocess.run(["ls", "-al", "bin/pip"], cwd=os.path.join(templ_dir, '.venv'))
    #             env = {}
    #             env['PATH'] = env['VIRTUAL_ENV'] = os.path.join(templ_dir, '.venv')
    # #            execute_command("bin/python bin/pip install -r " + requirements_path,
    # #                            cwd=os.path.join(templ_dir, '.venv'), env=env)
    #
    #             cmd = ["bin/python", "bin/pip", "install", "-r", requirements_path]
    #             try:
    #                 yield from PythonSandboxTemplate.execute_arglist_yield(cmd, os.path.join(templ_dir, '.venv'), env)
    #             except:
    #                 # convert exception in order to have more info for the user
    #                 raise Exception('Cannot install requirements.txt')
    #
    #         yield 'data: add missing libraries\n\n'
    #         logger.info('copy python libraries from OS')
    #         pythonbin = os.readlink('/usr/bin/python3')
    #         logger.debug('python is ' + pythonbin)  # expect python3.x
    #         # copy python libs
    #         createlib = "(cd / && tar -chf - usr/lib/" + pythonbin + ") | (cd " + templ_dir + " && tar -xf -)"
    #         execute_command(createlib, shell=True)
    #
    #         logger.debug('copy shared libraries from os')
    #         self._include_shared_object('libffi.so', templ_dir)
    #         self._include_shared_object('libffi.so.8', templ_dir)
    #         self._include_shared_object('libbz2.so.1.0', templ_dir)
    #         self._include_shared_object('libsqlite3.so.0', templ_dir)
    #
    #         logger.debug('copy all shared libraries needed for python to work')
    #         self._checker.copy_shared_objects(templ_dir)
    #
    #         # compile python code (smaller???)
    #         if compile_python:
    #             import compileall
    #             import glob
    #             logger.debug('**** compile')
    #             success = compileall.compile_dir(templ_dir, quiet=True)
    #
    #         # delete all python source code
    # #        logger.debug('delete py')
    # #        for filePath in glob.glob(templ_dir + '/**/*.py', recursive=True):
    # #            if 'encodings' not in filePath and 'codecs' not in filePath:
    # #                print(filePath)
    # #                try:
    # #                    os.remove(filePath)
    # #                except:
    # #                    logger.error("Error while deleting file : ", filePath)
    # #            else:
    # #                print('**' + filePath)
    #
    #         yield 'data: freeze template\n\n'
    #         self._commit(templ_dir)
    #     except:
    #         # try and delete complete templ_dir
    #         shutil.rmtree(templ_dir, ignore_errors=True)
    #         raise
    #

    def _get_image_tag(self):
        if not self._tag is None:
            return self._tag

        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        if len(requirements_txt) > 1:
            raise Exception('more than one requirements.txt found')
        if len(requirements_txt) == 0:
            requirements_txt = None
            requirements_path = None
        else:
            requirements_txt = requirements_txt.first()
            requirements_path = os.path.join(settings.UPLOAD_ROOT, task.get_storage_path(requirements_txt, requirements_txt.filename))

        if requirements_path is not None:
            self._tag = PythonSandboxTemplate.get_hash(requirements_path)
        else:
            self._tag = "0" # "latest" # default tag

        return self._tag

    def get_python_template_path(self):
        """ returns the template pathname for the given requirements.txt """
        hash = self._get_image_tag()
        if hash is not None:
            return os.path.join(settings.UPLOAD_ROOT, PythonSandboxTemplate.get_python_path(), hash)
        else:
            return PythonSandboxTemplate.get_python_path()



    def get_instance(self, studentenv):
        """ return an instance created from this template """
        self.create()
        tag = self._get_image_tag()

        # logger.info('Use Python template ' + templ_dir)
        # instance = sandbox.SandboxInstance(templ_dir, studentenv)
        # return instance

        # with the init flag set to True signals are handled properly so that
        # stopping the container is much faster
        container = self._client.containers.create(image=PythonSandboxTemplate.python_image_name+':'+tag,
                                             volumes=[],
                                             init=True)

        return DockerSandbox(container, studentenv)



