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
import docker
import tarfile
import tempfile

from . import sandbox, task
from django.conf import settings
#from utilities.safeexec import execute_command, escape_xml_invalid_chars

import logging

logger = logging.getLogger(__name__)

compile_python = False


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
        """ remove container
        """
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

        tmp_filename = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as f:
                tmp_filename = f.name
                with tarfile.open(fileobj=f, mode='w:gz') as tar:
                    tar.add(self._studentenv, arcname=".", recursive=True)
            logger.debug("** upload to sandbox " + tmp_filename)
            # os.system("ls -al " + tmp_filename)
            with open(tmp_filename, 'rb') as fd:
                if not self._container.put_archive(path='/sandbox', data=fd):
                    raise Exception('cannot put requirements.tar/' + tmp_filename)
        finally:
            if tmp_filename:
                os.unlink(tmp_filename)

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

        with open(self._studentenv + '/result.tar', mode='bw') as f:
            for block in tar:
                f.write(block)
        with tarfile.open(self._studentenv + '/result.tar', 'r') as tar:
            tar.extractall(path=self._studentenv)
        os.unlink(self._studentenv + '/result.tar')

#        os.system("ls -al " + self._studentenv)
        resultpath = self._studentenv + '/' + DockerSandbox.remote_result_subfolder + '/unittest_results.xml'
        if not os.path.exists(resultpath):
            raise Exception("No test result file found")

        os.system("mv " + resultpath + " " + self._studentenv + '/unittest_results.xml')
        return "todo read result"

class PythonSandboxImage(sandbox.SandboxImage):
    """ python sandbox template for python tests """

    # name of python docker image
    image_name = "python-praktomat_sandbox"
    dockerfile_path = '/praktomat/docker-sandbox-image/python'
    base_image_tag = image_name + ':' + sandbox.SandboxImage.base_tag

    def __init__(self, praktomat_test):
        super().__init__(praktomat_test)

    def _get_image_name(self):
        """ name of base image """
        return PythonSandboxImage.image_name

    def _get_dockerfile_path(self):
        """ path to Dockerfile """
        return PythonSandboxImage.dockerfile_path

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


    def create(self):
        """ creates the docker image """
        logger.debug("create python image (if it does not exist)")

        self.check_preconditions()

        tag = self._get_image_tag()
        if self._image_exists(tag):
            logger.debug("python image for tag " + tag + " already exists")
            yield 'data: python image for tag ' + tag + ' already exists\n\n'
            # already exists => return
            return

        # check
        if not self._image_exists(PythonSandboxImage.base_image_tag):
            yield 'data: create new python base image\n\n'
            logger.debug("create python image for tag " + PythonSandboxImage.base_image_tag + " from " + self.dockerfile_path)
            image, logs_gen = self._client.images.build(path=self._get_dockerfile_path(),
                                                        tag=PythonSandboxImage.base_image_tag,
                                                        rm =True, forcerm=True)
            yield logs_gen

        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        if len(requirements_txt) == 0:
            # no requirements.txt is available =>
            # use default image => finished
            return

        requirements_txt = requirements_txt.first()
        requirements_path = os.path.join(settings.UPLOAD_ROOT,
                                         task.get_storage_path(requirements_txt, requirements_txt.filename))

#        logger.info('Create Python image for ' + templ_dir)

        # create container from base image, install requirements
        # and commit container to image
        # install modules from requirements.txt if available
        yield 'data: install requirements\n\n'
        logger.info('install requirements from ' + requirements_path)
        logger.debug('create container from ' + PythonSandboxImage.base_image_tag)
        container = self._client.containers.create(image=PythonSandboxImage.base_image_tag,
                                                   init=True)
        tmp_filename = None
        try:
            container.start()
            # start_time = time.time()

            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as f:
                tmp_filename = f.name
                with tarfile.open(fileobj=f, mode='w:gz') as tar:
                    tar.add(requirements_path, arcname="requirements.txt", recursive=False)

            logger.debug("** upload to sandbox " + tmp_filename)
            # os.system("ls -al " + tmp_filename)
            with open(tmp_filename, 'rb') as fd:
                if not container.put_archive(path='/sandbox', data=fd):
                    raise Exception('cannot put requirements.tar/' + tmp_filename)

            code, log = container.exec_run("pip install -r /sandbox/requirements.txt", user="root")
            yield log
            logger.debug(log.decode('UTF-8').replace('\n', '\r\n'))
            if code != 0:
                logger.error(log.decode('UTF-8').replace('\n', '\r\n'))
                raise Exception('Cannot install requirements.txt')

            yield 'data: commit image\n\n'
            logger.debug("** commit image to " + PythonSandboxImage.image_name + ':' + tag)
            container.commit(repository=PythonSandboxImage.image_name,
                             tag=tag)
#                             tag=PythonSandboxTemplate.image_name + ':' + tag)
        finally:
            if tmp_filename:
                os.unlink(tmp_filename)
            container.stop()
            container.remove()
            pass


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
            self._tag = PythonSandboxImage.get_hash(requirements_path)
        else:
            self._tag = super()._get_image_tag()

        return self._tag

    def get_container(self, studentenv):
        """ return an instance created from this template """
        self.create()
        tag = self._get_image_tag()

        # with the init flag set to True signals are handled properly so that
        # stopping the container is much faster
        container = self._client.containers.create(image=PythonSandboxImage.image_name + ':' + tag,
                                                   volumes=[],
                                                   init=True)

        return DockerSandbox(container, studentenv)



