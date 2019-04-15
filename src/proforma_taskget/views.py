# -*- coding: utf-8 -*-
#import http.cookiejar
#import tempfile
#import urllib.request, urllib.parse, urllib.error
#import urllib.parse
#import pickle
import logging
import os
#import time

#import requests
from django.conf import settings
from django.http import HttpResponse
#from django.views.decorators.csrf import csrf_exempt
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import expected_conditions as EC

#logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#CACHE_PATH = os.path.join(BASE_DIR, "/cache")
#REQUEST_WAIT = 8






# def write_cache_task(uuid, task_zip_content):
#     """
#     Writes the task_file in the cache directory structure: /cache/uuid/yymmdd_uuid.zip
#     :param uuid: string of the uuid
#     :param task_zip: zip-file
#     :return: task_file
#     """
#     # todo check uuid -> length
#     # todo check task_zip -> name / length
#     if (uuid is None) or (task_zip_content is None):
#         raise Exception("uuid or task is missing")
#     try:
#         with open(CACHE_PATH + uuid , 'wb') as task_file:
#             task_file.write(task_zip_content)
#             return task_file
#
#     except Exception:
#         logger.exception("Could not save task: " + Exception.message)
#         raise Exception("Could not save task: ")
#
#
# def read_cache_task(uuid):
#     """
#     Reads the cache directory structure: /cache/uuid/yymmdd_uuid.zip
#     :param uuid: string of the uuid
#     :return: the zip_file or None
#     """






def answer_format_template(award, message, format=None, awarded=None):
    if format is None or "loncapaV1":
        return """<loncapagrade>
        <awarddetail>%s</awarddetail>
        <message><![CDATA[proforma_taskget: %s]]></message>
        <awarded></awarded>
        </loncapagrade>""" % (award, message)
    else:
        return """<loncapagrade>
        <awarddetail>%s</awarddetail>
        <message><![CDATA[proforma_taskget; %s]]></message>
        <awarded>%s</awarded>
        </loncapagrade>""" % (award, message, awarded)

