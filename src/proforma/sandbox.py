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

#import os
#import shutil
#from checker.basemodels import CheckerEnvironment
#from utilities.file_operations import copy_file
#from utilities.safeexec import execute_command

#from django.conf import settings
import docker
import abc

import logging

logger = logging.getLogger(__name__)


class SandboxImage:
    base_tag = '0' # default tag name

    def __init__(self, checker):
        self._checker = checker
        logger.debug(self._checker.proforma_id)
        self._client = docker.from_env()
        self._tag = None

    def __del__(self):
        self._client.close()
    @abc.abstractmethod
    def get_container(self, proformAChecker, studentenv):
        """ return an instance created from this template """
        return

    @abc.abstractmethod
    def _get_image_name(self):
        """ name of image """
        return

    @abc.abstractmethod
    def _get_dockerfile_path(self):
        """ path to Dockerfile """
        return

    def _get_image_tag(self):
        return SandboxImage.base_tag

    def _image_exists(self, tag):
        images = self._client.images.list(
            filters = {"reference": self._get_image_name() + ":" + tag})
        print(images)
        return len(images) > 0

