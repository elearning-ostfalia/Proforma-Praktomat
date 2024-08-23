# -*- coding: utf-8 -*-

# This file is part of Ostfalia-Praktomat.
#
# Copyright (C) 2024 Ostfalia University
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
# functions for creating specialized sandboxes

from . import sandbox
# import sandbox
import sys
import glob
import logging
from django.conf import settings
import os
import random
import tempfile
import tarfile

logger = logging.getLogger(__name__)


## CPP/C tests
class CppSandbox(sandbox.DockerSandbox):
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv,
                         "python3 /sandbox/compile_suite.py",  # compile command
                         "python3 /sandbox/run_suite.py " + command,  # run command
                         "/sandbox/test_detail.xml")  # download path


#    def __del__(self):
#        super().__del__()

class CppImage(sandbox.DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         '/praktomat/docker-sandbox-image/cpp',
                         "cpp-praktomat_sandbox",
                         None)

    #    def __del__(self):
    #        super().__del__()

    def get_container(self, studentenv, command):
        self.create_image()
        cpp_sandbox = CppSandbox(self._client, studentenv, command)
        cpp_sandbox.create(self._get_image_fullname(self._get_image_tag()))
        return cpp_sandbox


## Java tests
class JavaSandbox(sandbox.DockerSandbox):
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv,
                         "javac -classpath . @sources.txt",  # compile command: java
                         #                         "javac -classpath . -nowarn -d . @sources.txt",  # compile command: java
                         command,  # run command
                         None)  # download path
        self._mem_limit = sandbox.DockerSandbox.meg_byte * settings.TEST_MAXMEM_DOCKER_JAVA  # increase memory limit





class JavaImage(sandbox.DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         '/praktomat/docker-sandbox-image/java',
                         "java-praktomat_sandbox",
                         None)

    def get_container(self, studentenv = None, command = None):
        self.create_image()
        if studentenv is not None:
            j_sandbox = JavaSandbox(self._client, studentenv, command)
            j_sandbox.create(self._get_image_fullname(self._get_image_tag()))
            return j_sandbox
        else:
            return None


class PythonSandbox(sandbox.DockerSandbox):
    remote_result_subfolder = "__result__"
    remote_result_folder = "/sandbox/" + remote_result_subfolder

    def __init__(self, container, studentenv):
        super().__init__(container, studentenv,
                         "python3 -m compileall /sandbox -q",
                         "python3 /sandbox/run_suite.py",
                         PythonSandbox.remote_result_folder)
        from django.conf import settings
        self._mem_limit = sandbox.DockerSandbox.meg_byte * settings.TEST_MAXMEM_DOCKER_PYTHON  # increase memory limit

    def download_result_file(self):
        super().download_result_file()

        resultpath = self._studentenv + '/' + PythonSandbox.remote_result_subfolder + '/unittest_results.xml'
        if not os.path.exists(resultpath):
            raise Exception("No test result file found")
        os.system("mv " + resultpath + " " + self._studentenv + '/unittest_results.xml')


class PythonImage(sandbox.DockerSandboxImage):
    """ python sandbox template for python tests """

    # name of python docker image
    image_name = "python-praktomat_sandbox"
    base_image_tag = image_name + ':' + sandbox.DockerSandboxImage.base_tag

    def look_for_requirements_txt(path):
        filelist = glob.glob(path + '/*requirements.txt')
        if len(filelist) > 0:
            logger.debug(filelist)
            return filelist[0]
        else:
            return None

    def __init__(self, praktomat_test, requirements_path=None):
        super().__init__(praktomat_test,
                         dockerfile_path='/praktomat/docker-sandbox-image/python',
                         image_name=PythonImage.image_name,
                         #                         dockerfilename='Dockerfile.alpine',
                         dockerfilename=None)

        self._requirements_path = requirements_path

    #    def __del__(self):
    #        super().__del__()

    def yield_log(self, log):
        if log is None:
            return
        log = log.decode('UTF-8').replace('\n', '\r\n')

        lines = filter(str.strip, log.splitlines())
        for line in lines:
            yield "data: " + line + "\n\n"

    def _get_hash(requirements_txt):
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

    #    def check_preconditions(self):
    #        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
    #        if len(requirements_txt) > 1:
    #            raise Exception('more than one requirements.txt found')

    def create_image_yield(self):
        #        """ creates the docker image """
        logger.debug("create python image (if it does not exist)")

        #        self.check_preconditions()

        tag = self._get_image_tag()
        # print("tag " + str(tag))
        if self._image_exists(tag):
            logger.debug("python image for tag " + tag + " already exists")
            yield 'data: python image for tag ' + tag + ' already exists\n\n'
            # already exists => return
            return

        # ensure base image exists
        self._create_image_for_tag(sandbox.DockerSandboxImage.base_tag)

        if self._requirements_path is None:
            return

        # create container from base image, install requirements
        # and commit container to image
        # install modules from requirements.txt if available
        yield 'data: install requirements\n\n'
        logger.info('install requirements from ' + self._requirements_path)
        logger.debug('create container from ' + PythonImage.base_image_tag)
        number = random.randrange(1000000000)
        name = "tmp_python_image_" + str(number)
        try:
            container = self._client.containers.create(image=PythonImage.base_image_tag,
                                                       init=True,
                                                       command=sandbox.DockerSandbox.default_cmd,  # keep container running
                                                       name=name
                                                       )

        except Exception as e:
            # in case of an exception there might be a dangling container left
            # that is not removed by the docker code.
            # So we look for a container named xxx and try and remove it
            logger.error("FATAL ERROR: cannot create new python image - " + name)
            sandbox.delete_dangling_container(self._client, name)
            raise e

        tmp_filename = None
        try:
            container.start()
            # start_time = time.time()

            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as f:
                tmp_filename = f.name
                with tarfile.open(fileobj=f, mode='w:gz') as tar:
                    tar.add(self._requirements_path, arcname="requirements.txt", recursive=False)

            logger.debug("** upload to sandbox " + tmp_filename)
            # os.system("ls -al " + tmp_filename)
            with open(tmp_filename, 'rb') as fd:
                if not container.put_archive(path='/sandbox', data=fd):
                    raise Exception('cannot put requirements.tar/' + tmp_filename)

            logger.debug(container.status)
            code, log = container.exec_run("pip3 install -r /sandbox/requirements.txt", user="root")
            yield from self.yield_log(log)
            logger.debug(log.decode('UTF-8').replace('\n', '\r\n'))
            if code != 0:
                raise Exception('Cannot install requirements.txt')

            yield 'data: commit image\n\n'
            logger.debug("** commit image to " + PythonImage.image_name + ':' + tag)
            container.commit(repository=PythonImage.image_name,
                             tag=tag)
        #                             tag=PythonSandboxTemplate.image_name + ':' + tag)
        finally:
            if tmp_filename:
                os.unlink(tmp_filename)
            container.stop()
            container.remove(force=True)
            pass

    def create_image(self):
        for a in self.create_image_yield():  # function is generator, so this must be handled in order to be executed
            pass

    def _get_image_tag(self):
        if not self._tag is None:
            return self._tag

        if self._requirements_path is None:
            self._tag = super()._get_image_tag()
        else:
            self._tag = PythonImage._get_hash(self._requirements_path)

            #        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        #        if len(requirements_txt) > 1:
        #            raise Exception('more than one requirements.txt found')
        #        if len(requirements_txt) == 0:
        #            self._tag = super()._get_image_tag()
        #        else:
        #            requirements_txt = requirements_txt.first()
        #            requirements_path = os.path.join(settings.UPLOAD_ROOT, task.get_storage_path(requirements_txt, requirements_txt.filename))
        #            self._tag = PythonImage._get_hash(requirements_path)

        return self._tag

    def get_container(self, studentenv):
        """ return an instance created from this template """
        self.create_image()  # function is generator, so this must be handled in order to be executed
        p_sandbox = PythonSandbox(self._client, studentenv)
        p_sandbox.create(self._get_image_fullname(self._get_image_tag()))
        return p_sandbox



class CheckstyleSandbox(sandbox.DockerSandbox):
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv,
                         None, # no compile command
                         command,  # run command
                         None)  # download path
#        self._mem_limit = DockerSandbox.meg_byte * settings.TEST_MAXMEM_DOCKER_JAVA  # increase memory limit



class CheckstyleImage(sandbox.DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         '/praktomat/docker-sandbox-image/checkstyle',
                         "checkstyle-praktomat_sandbox",
                         None)

    def get_container(self, studentenv = None, command = None):
        self.create_image()
        if studentenv is not None:
            j_sandbox = CheckstyleSandbox(self._client, studentenv, command)
            j_sandbox.create(self._get_image_fullname(self._get_image_tag()))
            return j_sandbox
        else:
            return None


def create_images():
    # create images
    print("creating docker image for Java tests ...")
    sys.stdout.flush()
    sys.stderr.flush()
    JavaImage(None).create_image()
    print("done")

    print("creating docker image for Checkstyle tests ...")
    sys.stdout.flush()
    sys.stderr.flush()
    CheckstyleImage(None).create_image()
    print("done")

    print("creating docker image for Python tests ...")
    sys.stdout.flush()
    sys.stderr.flush()
    for a in PythonImage(None).create_image_yield():
        pass
    print("done")
    print("creating docker image for c/C++ tests ...")
    sys.stdout.flush()
    sys.stderr.flush()
    CppImage(None).create_image()
    print("done")


if __name__ == '__main__':
    # flush echo messages from shell script on praktomat docker startup
    sys.stdout.flush()
    sys.stderr.flush()

    sandbox.cleanup()
    create_images()