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


class PythonSandbox(sandbox.DockerSandbox):
    remote_result_subfolder = "__result__"
    remote_result_folder = "/sandbox/" + remote_result_subfolder
    def __init__(self, container, studentenv):
        super().__init__(container, studentenv,
                         "python3 -m compileall /sandbox -q",
                         "python3 /sandbox/run_suite.py",
                         PythonSandbox.remote_result_folder)

    def download_result_file(self):
        super().download_result_file()

        resultpath = self._studentenv + '/' + PythonSandbox.remote_result_subfolder + '/unittest_results.xml'
        if not os.path.exists(resultpath):
            raise Exception("No test result file found")
        os.system("mv " + resultpath + " " + self._studentenv + '/unittest_results.xml')

class PythonUnittestImage(sandbox.DockerSandboxImage):
    """ python sandbox template for python tests """

    # name of python docker image
    image_name = "python-praktomat_sandbox"
    base_image_tag = image_name + ':' + sandbox.DockerSandboxImage.base_tag

    def __init__(self, praktomat_test):
        super().__init__(praktomat_test,
                         dockerfile_path='/praktomat/docker-sandbox-image/python',
                         image_name=PythonUnittestImage.image_name,
                         dockerfilename='Dockerfile.alpine',
                         )

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

    def check_preconditions(self):
        requirements_txt = self._checker.files.filter(filename='requirements.txt', path='')
        if len(requirements_txt) > 1:
            raise Exception('more than one requirements.txt found')


    def create_image(self):
        """ creates the docker image """
        logger.debug("create python image (if it does not exist)")

        self.check_preconditions()

        tag = self._get_image_tag()
        if self._image_exists(tag):
            logger.debug("python image for tag " + tag + " already exists")
            yield 'data: python image for tag ' + tag + ' already exists\n\n'
            # already exists => return
            return

        # ensure base image exists
        self._create_image_for_tag(sandbox.DockerSandboxImage.base_tag)

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
        logger.debug('create container from ' + PythonUnittestImage.base_image_tag)
        container = self._client.containers.create(image=PythonUnittestImage.base_image_tag,
                                                   init=True,
                                                   command=sandbox.DockerSandbox.default_cmd,  # keep container running
                                                   )
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

            logger.debug(container.status);
            code, log = container.exec_run("pip3 install -r /sandbox/requirements.txt", user="root")
            yield from self.yield_log(log)
            logger.debug(log.decode('UTF-8').replace('\n', '\r\n'))
            if code != 0:
                raise Exception('Cannot install requirements.txt')

            yield 'data: commit image\n\n'
            logger.debug("** commit image to " + PythonUnittestImage.image_name + ':' + tag)
            container.commit(repository=PythonUnittestImage.image_name,
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
            self._tag = PythonUnittestImage._get_hash(requirements_path)
        else:
            self._tag = super()._get_image_tag()

        return self._tag

    def get_container(self, studentenv):
        """ return an instance created from this template """
        self.create_image()
        p_sandbox = PythonSandbox(self._client, studentenv)
        p_sandbox.create(self._image_name + ':' + self._get_image_tag())
        return p_sandbox


