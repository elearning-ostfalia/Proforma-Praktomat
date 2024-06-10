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

#import os
#import shutil
#from checker.basemodels import CheckerEnvironment
#from utilities.file_operations import copy_file
#from utilities.safeexec import execute_command

#from django.conf import settings
import docker
import tarfile
from abc import ABC, abstractmethod
import os
import tempfile
# import signal

import logging

logger = logging.getLogger(__name__)

# class TimeoutException(Exception):
#     pass
# def timeout_handler(signum, frame):
#     signame = signal.Signals(signum).name
#     print(f'Signal handler called with signal {signame} ({signum})')
#     print("timeout_handler called")
#     raise TimeoutException

# approach:
# - create container with no command
# => map solution via volumes (solution -> /solution)
# - run_exec detached, wait for stop
# => map result via volumes (or restart container and get_archive)

class DockerSandbox(ABC):
    remote_command = "python3 /sandbox/run_suite.py"
    remote_result_subfolder = "__result__"
    remote_result_folder = "/sandbox/" + remote_result_subfolder
    def __init__(self, client, studentenv):
        self._client = client
        self._studentenv = studentenv
        self._container = None

    def __del__(self):
        """ remove container
        """
        if self._container is not None:
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

    def create(self, image_name):
        # with the init flag set to True signals are handled properly so that
        # stopping the container is much faster
        # self._container = self._client.containers.run(
        #     image_name, init=True,
        #     network_disabled=True,
        #     ulimits = ulimits, detach=True)

        healthcheck = {
            "test": ["CMD-SHELL", "ls"],
            "interval": 500000000, # 500ms
            "timeout": 500000000, # 500ms
            "retries": 1,
            "start_period": 1000000000 # start after 1s
        }
        self._container = self._client.containers.create(
            image_name, init=True,
            mem_limit="1g",
            cpu_period=100000, cpu_quota=70000,  # max. 70% of the CPU time => configure
            network_disabled=True,
            command='tail -f /dev/null', detach=True,
            healthcheck=healthcheck
#            tty=True
        )

        if self._container is None:
            raise Exception("could not create container")
        self._container.start()



    @abstractmethod
    def _get_remote_command(self):
        return

    def _get_compile_command(self):
        return None

    def upload_environmment(self):
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

    def compile_tests(self):
        logger.debug("** compile tests in sandbox")
        # start_time = time.time()
        command = self._get_compile_command()
        if command is None:
            return True, ""

        code, output = self._container.exec_run(command, user="999")
        #        if code != 0:
        #            logger.debug(str.decode('UTF-8').replace('\n', '\r\n'))
        #            raise Exception("running test failed")

        # print("---run test  %s seconds ---" % (time.time() - start_time))
        logger.debug("exitcode is " + str(code))
        logger.debug("Test compilation log")
        # capture output from generator
        text = output.decode('UTF-8').replace('\n', '\r\n')
        logger.debug(text)
#        if code < 0:
            # append signal message
#            text = text + '\r\nSignal:\r\n' + signal.strsignal(- code)
        return (code == 0), text

    def runTests(self):
        logger.debug("** run tests in sandbox")
        # start_time = time.time()
        ulimits = [
            #            docker.types.Ulimit(name='nproc', soft=250),
            #            docker.types.Ulimit(name='nproc', hard=250),
            #            docker.types.Ulimit(name='CPU', soft=25),
            #            docker.types.Ulimit(name='CPU', hard=30),
            #            docker.types.Ulimit(name='AS', soft=1024 * 1024 * 1500), # 1.5GB
            #            docker.types.Ulimit(name='AS', hard=1024 * 1024 * 2000), # 2.0GB
            docker.types.Ulimit(name='nofile', soft=64),
            docker.types.Ulimit(name='nofile', hard=64),
        ]


        # use stronger limits for test run
        warning_dict = self._container.update(mem_limit="1g",
                               cpu_period=100000, cpu_quota=20000 # max. 20% of the CPU time => configure
                               )
        print(warning_dict)

        TIMEOUT = 20000
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIMEOUT)

        try:
            code, output = self._container.exec_run(self._get_remote_command(), user="999")
#                                                , detach=True)
            logger.debug("exitcode is "+ str(code))
            logger.debug("Test run log")
            text = output.decode('UTF-8').replace('\n', '\r\n')
            logger.debug(output)

            # signal.alarm(0) # stop timer
        # except TimeoutException as ex:
        #     logger.error("command execution timed out")
        except Exception as ex:
            logger.error("command execution failed")
            logger.error(ex)


        # wait for exit of command
        # wait_dict = self._container.wait(timeout=30, condition="next-exit")
        # print(wait_dict)

        # logger.debug("container status is " + self._container.status) # created


        # print("---run test  %s seconds ---" % (time.time() - start_time))
#        output = self._container.logs()
#        logger.debug("exitcode is "+ str(code))
#        logger.debug("Test run log")
        # capture output from generator
#        text = output.decode('UTF-8').replace('\n', '\r\n')
#        logger.debug(text)
#        if code < 0:
            # append signal message
#            text = text + '\r\nSignal:\r\n' + signal.strsignal(- code)
        return (code == 0), text



class DockerSandboxImage(ABC):
    base_tag = '0' # default tag name

    def __init__(self, checker):
        self._checker = checker
        logger.debug("constructor for sandbox of checker.proforma_id: " + self._checker.proforma_id)
        self._client = docker.from_env()
        self._tag = None

    def __del__(self):
        self._client.close()

    @abstractmethod
    def get_container(self, proformAChecker, studentenv):
        """ return an instance created from this template """
        return

    @abstractmethod
    def _get_image_name(self):
        """ name of image """
        return

    @abstractmethod
    def _get_dockerfile_path(self):
        """ path to Dockerfile """
        return

    def _get_image_tag(self):
        return DockerSandboxImage.base_tag

    def _image_exists(self, tag):
        imagename = self._get_image_name() + ":" + tag
        logger.debug("check if image exists: " + imagename)
        images = self._client.images.list(filters = {"reference": imagename})
        print(images)
        return len(images) > 0


class GoogletestSandbox(DockerSandbox):
    remote_result = "/sandbox/test_detail.xml"
    def __init__(self, client, studentenv, command):
        super().__init__(client, studentenv)
        self._command = command

    def _get_compile_command(self):
        return "python3 /sandbox/compile_suite.py "

    def _get_remote_command(self):
        return "python3 /sandbox/run_suite.py " + self._command

    def get_result_file(self):
        self._container.stop()
        logger.debug("get result")
        tar = None
        try:
            tar, dict = self._container.get_archive(GoogletestSandbox.remote_result)
            logger.debug(dict)
            with open(self._studentenv + '/result.tar', mode='bw') as f:
                for block in tar:
                    f.write(block)
            with tarfile.open(self._studentenv + '/result.tar', 'r') as tar:
                tar.extractall(path=self._studentenv)
            os.unlink(self._studentenv + '/result.tar')
        except:
            pass

        # os.system("ls -al " + self._studentenv)

class GoogletestImage(DockerSandboxImage):
    def __init__(self, praktomat_test):
        super().__init__(praktomat_test)

    def _get_image_name(self):
        """ name of base image """
        return "cpp-praktomat_sandbox"

    def _get_dockerfile_path(self):
        """ path to Dockerfile """
        return '/praktomat/docker-sandbox-image/cpp'

    def _create_image(self):
        """ creates the docker image """
        logger.debug("create GoogletestImage image (if it does not exist)")

        tag = self._get_image_tag()
        logger.debug("tag is " + tag)
        if self._image_exists(tag):
            logger.debug("image for tag " + tag + " already exists")
            # yield 'data: image for tag ' + tag + ' already exists\n\n'
            # already exists => return
            return

        # check
        # yield 'data: create new image\n\n'
        logger.debug("create image for tag " + tag + " from " + self._get_dockerfile_path())
        image, logs_gen = self._client.images.build(path=self._get_dockerfile_path(),
                                                    tag=self._get_image_name() + ':' + tag,
                                                    rm =True, forcerm=True)
        # yield logs_gen

    def get_container(self, studentenv, command):
        """ return an instance created from this template """
        logger.debug("request for Googletest container")

        self._create_image()
        tag = self._get_image_tag()
        logger.debug("tag needed is " + tag)

        sandbox = GoogletestSandbox(self._client, studentenv, command)
        sandbox.create(self._get_image_name() + ':' + tag)
        return sandbox



