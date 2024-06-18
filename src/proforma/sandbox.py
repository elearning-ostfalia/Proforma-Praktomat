# -*- coding: utf-8 -*-
import signal

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


from django.conf import settings
import docker
import tarfile
from abc import ABC, abstractmethod
import os
import tempfile
import random

# import requests => for Timeout Exception

import logging

logger = logging.getLogger(__name__)

# approach:
# 1. create container from image
# 1.a. python: upload and install requirements
# 1.b. python: commit new image (and reuse later for tests with same requirements.txt)
# 2 upload task files and student files
# 3 compile
# 4 commit container to temporary image
# 5 run tests with run command detached
# 6 wait for exit of container
# 7 get result file

# working without commit and using exec_run is faster but wait does not work with exec_run :-(

debug_sand_box = False

# module_init_called = False

class DockerSandbox(ABC):
    # remote_command = "python3 /sandbox/run_suite.py"
    # remote_result_subfolder = "__result__"
    # remote_result_folder = "/sandbox/" + remote_result_subfolder
    millisec = 1000000
    sec = millisec * 1000
    default_cmd = 'tail -f /dev/null'
    meg_byte = 1024 * 1024

    def __init__(self, client, studentenv,
                 compile_command, run_command, download_path):
        if debug_sand_box:
            logger.debug('__init__')

        self._client = client
        self._studentenv = studentenv
        self._compile_command = compile_command
        self._run_command = run_command
        self._download_path = download_path
        self._container = None
        self._image = None
        self._healthcheck = {
            "test": [], # ["CMD", "ls"],
            "interval": (DockerSandbox.sec * 1), # 500000000, # 500ms
            "timeout": (DockerSandbox.sec * 1), # 500000000, # 500ms
            "retries": 1,
            "start_period": (DockerSandbox.sec * 3), # 1000000000 # start after 1s
        }
        self._mem_limit = DockerSandbox.meg_byte * 1000

    def __del__(self):
        """ remove container
        """
        if debug_sand_box:
            logger.debug('__del__')
        if hasattr(self, '_container') and self._container is not None:
            try:
                # try and stop container
                self._container.stop()
            except Exception as e:
                # ignore error if failed
                logger.error(e)
            try:
                # try and remove container
                self._container.remove()
            except Exception as e:
                logger.error(e)
                # if container cannot be removed, try and force remove
                logger.info("try and force kill")
                self._container.remove(force=True)
                logger.info("force kill succeeded")
        if hasattr(self, '_image') and self._image is not None:
            try:
                self._image.remove()
            except Exception as e:
                logger.error(e)
        if debug_sand_box:
            logger.debug('__del__')


    def create(self, image_name):
        # with the init flag set to True signals are handled properly so that
        # stopping the container is much faster
        # self._container = self._client.containers.run(
        #     image_name, init=True,
        #     network_disabled=True,
        #     ulimits = ulimits, detach=True)

        if debug_sand_box:
            logger.debug('create container')
        self._container = self._client.containers.create(
            image_name, init=True,
            mem_limit=self._mem_limit,
#            cpu_period=100000, cpu_quota=90000,  # max. 70% of the CPU time => configure
            network_disabled=True,
            command=DockerSandbox.default_cmd, # keep container running
            detach=True,
            healthcheck=self._healthcheck
#            tty=True
        )

        if self._container is None:
            raise Exception("could not create container")
        if debug_sand_box:
            logger.debug('start container')
        self._container.start()

        # self.wait_test(image_name)

#     def wait_test(self, image_name):
#         """ wait seems to work only with run, not with exec_run :-(
#         """
#         try:
#             print("wait_test") # sleep 2 seconds
#             # code, output = self._container.exec_run(cmd="sleep 2", user="999", detach=True)
#             tmp_container = self._client.containers.run(image_name, command="sleep 20", user="999", detach=True)
#
#             try:
#                 # wait_dict = self._container.wait(timeout=5, condition="next-exit") # timeout in seconds
#                 wait_dict = tmp_container.wait(timeout=5) # , condition="next-exit") # timeout in seconds
#                 print(wait_dict)
# #            except requests.exceptions.ReadTimeout as e:
#                 print("failed")
#             except Exception  as e:
#                 print("passed")
#                 logger.error(e)
#
#                 tmp_container = self._client.containers.run(image_name, command="sleep 2", user="999", detach=True)
#                 try:
#                     # wait_dict = self._container.wait(timeout=5, condition="next-exit") # timeout in seconds
#                     wait_dict = tmp_container.wait(timeout=5)  # , condition="next-exit") # timeout in seconds
#                     print(wait_dict)
#                     print("passed")
#                 except Exception as e:
#                     print("failed")
#                     logger.error(e)
#
#             print("end of wait_test")
#             logger.debug("end of sleep")
#
#         except Exception as ex:
#             logger.error("command execution failed")
#             logger.error(ex)


    def _get_run_timeout(self):
        """ in seconds
        """
        return settings.TEST_TIMEOUT

    def upload_environmment(self):
        if debug_sand_box:
            logger.debug('upload')

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
            if debug_sand_box:
                logger.debug("** upload to sandbox " + tmp_filename)
            # os.system("ls -al " + tmp_filename)
            with open(tmp_filename, 'rb') as fd:
                if not self._container.put_archive(path='/sandbox', data=fd):
                    raise Exception('cannot put requirements.tar/' + tmp_filename)
        finally:
            if tmp_filename:
                os.unlink(tmp_filename)

    def exec(self, command):
        if debug_sand_box:
            logger.debug("** compile tests in sandbox")
        logger.debug("exec: " + command)
        code, output = self._container.exec_run(command, user="praktomat")
        if debug_sand_box:
            logger.debug("exitcode is " + str(code))
        # capture output from generator
        text = output.decode('UTF-8').replace('\n', '\r\n')
        logger.debug(text)
        return (code == 0), text

    def compile_tests(self, command=None):
        if debug_sand_box:
            logger.debug("** compile tests in sandbox")
        # start_time = time.time()
        if not command is None:
            self._compile_command = command
        if self._compile_command is None:
            return True, ""
        return self.exec(self._compile_command)

    def runTests(self, command=None):
        """
        returns passed?, logs, timnout?
        """
        if debug_sand_box:
            logger.debug("** run tests in sandbox")
        if not command is None:
            self._run_command = command
        # start_time = time.time()

        # use stronger limits for test run
#        warning_dict = self._container.update(mem_limit="1g",
#                               cpu_period=100000, cpu_quota=20000) # max. 20% of the CPU time => configure
#       print(warning_dict)

        # commit intermediate container to image
        number = random.randrange(1000000000)
        self._image = self._container.commit("tmp", str(number))
        # stop old container and remove
        self._container.stop()
        self._container.remove()
        self._container = None
        print(self._image.tags)

        ulimits = [
            docker.types.Ulimit(name='CPU', soft=25, hard=30),
            docker.types.Ulimit(name='nproc', soft=250, hard=250),
            docker.types.Ulimit(name='nofile', soft=64, hard=64),
            docker.types.Ulimit(name='fsize', soft=1024 * 100, hard=1024 * 100), # 100MB
        ]
        if self._mem_limit < 1200 * DockerSandbox.meg_byte:
            ulimits.append(docker.types.Ulimit(name='AS', soft=self._mem_limit, hard=self._mem_limit))

        code = None
        # code, output = self._container.exec_run(cmd, user="999", detach=True)
        logger.debug("execute '" + self._run_command + "'")
        self._container = self._client.containers.run(self._image.tags[0],
                                                    command=self._run_command, user="praktomat", detach=True,
                                                    healthcheck=self._healthcheck, init=True,
                                                    mem_limit=self._mem_limit,
#                                                    cpu_period=100000, cpu_quota=90000,  # max. 40% of the CPU time => configure
                                                    network_disabled=True,
                                                    stdout=True,
                                                    stderr=True,
                                                    ulimits=ulimits,
                                                    working_dir="/sandbox",
                                                    name="tmp_" + str(number)
                                                    )

        logger.debug("wait timeout is " + str(self._get_run_timeout()))
        try:
            wait_dict = self._container.wait(timeout=self._get_run_timeout())
            # wait_dict = self._container.wait(timeout=self._get_run_timeout())
            # print(wait_dict)
            code = wait_dict['StatusCode']
        except Exception as e:
            # probably timeout
            code = 1
            logger.error(e)
            output = self._container.logs()
            if debug_sand_box:
                logger.debug("got logs")
            text = 'Execution timed out... (Check for infinite loop in your code)'
            text += output.decode('UTF-8').replace('\n', '\r\n')
#            text += '\r\n+++ Test Timeout +++'
            return False, text, True
        if debug_sand_box:
            logger.debug("run finished")
        output = self._container.logs()
        # capture output from generator
        text = output.decode('UTF-8').replace('\n', '\r\n')
        return (code == 0), text, False


    def download_result_file(self):
        if debug_sand_box:
            logger.debug("get result")
        try:
            tar, dict = self._container.get_archive(self._download_path)
            logger.debug(dict)

            with open(self._studentenv + '/result.tar', mode='bw') as f:
                for block in tar:
                    f.write(block)
            with tarfile.open(self._studentenv + '/result.tar', 'r') as tar:
                tar.extractall(path=self._studentenv)
            os.unlink(self._studentenv + '/result.tar')
        except:
            pass



class DockerSandboxImage(ABC):
    base_tag = '0' # default tag name

    def __init__(self, checker, dockerfile_path, image_name, dockerfilename = 'Dockerfile'):
        self._checker = None
        # global module_init_called
        # if not module_init_called:
        #    logger.debug("constructor for sandbox of checker.proforma_id: " + self._checker.proforma_id)
        self._client = docker.from_env()
        self._tag = None
        self._dockerfile_path = dockerfile_path
        self._image_name = image_name
        self._dockerfilename = dockerfilename
        self._checker = checker

    def __del__(self):
        if hasattr(self, '_client') and self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                pass

    @abstractmethod
    def get_container(self, proformAChecker, studentenv):
        """ return an instance created from this template """
        return

    def _get_image_tag(self):
        return DockerSandboxImage.base_tag

    def _image_exists(self, tag):
        full_imagename = self._image_name + ":" + tag
        logger.debug("check if image exists: " + full_imagename)
        images = self._client.images.list(filters = {"reference": full_imagename})
        print(images)
        return len(images) > 0

    def _create_image(self):
        """ creates the default docker image """
        self._create_image_for_tag(self._get_image_tag())

    def _create_image_for_tag(self, tag):
        """ creates the docker image """
        if self._image_exists(tag):
            logger.debug("image for tag " + tag + " already exists")
            return

        # check
        logger.debug("create image for tag " + tag + " from " + self._dockerfile_path)
        image, logs_gen = self._client.images.build(path=self._dockerfile_path,
                                                    dockerfile=self._dockerfilename,
                                                    tag=self._image_name + ':' + tag,
                                                    rm =True, forcerm=True)
        return self._image_name + ':' + tag


## CPP/C tests
class CppSandbox(DockerSandbox):
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv,
                         "python3 /sandbox/compile_suite.py", # compile command
                         "python3 /sandbox/run_suite.py " + command, # run command
                         "/sandbox/test_detail.xml") # download path


class CppImage(DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         '/praktomat/docker-sandbox-image/cpp',
                         "cpp-praktomat_sandbox")

    def get_container(self, studentenv, command):
        self._create_image()
        sandbox = CppSandbox(self._client, studentenv, command)
        sandbox.create(self._image_name + ':' + self._get_image_tag())
        return sandbox


## Java tests
class JavaSandbox(DockerSandbox):
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv,
                        "javac -classpath . @sources.txt", # compile command: java
#                         "javac -classpath . -nowarn -d . @sources.txt",  # compile command: java
                         command, # run command
                         None) # download path
        self._mem_limit = DockerSandbox.meg_byte * 2000 # increase memory limit


class JavaImage(DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         '/praktomat/docker-sandbox-image/java',
                         "java-praktomat_sandbox")

    def get_container(self, studentenv, command):
        self._create_image()
        sandbox = JavaSandbox(self._client, studentenv, command)
        sandbox.create(self._image_name + ':' + self._get_image_tag())
        return sandbox



# def create_images():
#     global main_called
#     main_called = True
#     # create images
#     print("create docker image for c/C++ tests")
#     CppImage(None).get_container('/', 'ls')
#     print("create docker image for java tests")
#     JavaImage(None).get_container('/', 'ls')
#
# if __name__ == '__main__':
#     create_images()
#
#
#
