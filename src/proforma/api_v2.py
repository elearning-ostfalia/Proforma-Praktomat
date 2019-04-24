# -*- coding: utf-8 -*-
import tempfile
#from urllib.parse import urlparse # version 3
import urlparse
import traceback

from lxml import etree



#from django.core.serializers import json
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
#from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import os
import re
#import urllib
#import requests
import shutil
import logging
import xmlschema
#import pprint
from requests.exceptions import InvalidSchema
from export_universal_task.views import import_task_internal
from external_grade.views import grader_internal

#from proforma_taskget.views import login_phantomjs, get_task_from_externtal_server, answer_format_template

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PARENT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#CACHE_PATH = os.path.join(BASE_DIR, "/cache")
logger = logging.getLogger(__name__)

NAMESPACES = {'dns': 'urn:proforma:v2.0'}

def get_http_error_page(title, message, callstack):
    return """%s

    %s

Callstack:
    %s""" % (title, message, callstack)




def grade_api_v2(request,):
    """
    grade_api_v2
    rtype: grade_api_v2
    """

    logger.debug("new grading request")

    xml_version = None
    answer_format = "proformav2"

#    logger.debug('HTTP_USER_AGENT: ' + request.META.get('HTTP_USER_AGENT') +
#                 '\nHTTP_HOST: ' + request.META.get('HTTP_HOST') +
#                 '\nrequest.path: ' + request.path +
#     '\nrequest.POST:' + str(list(request.POST.items())))

    # create task and get Id
    try:
        # check request
        xml = check_post(request)
        #logger.debug("got xml")

        # debugging uploaded files
        #for field_name, file in request.FILES.items():
        #    filename = file.name
        #    logger.debug("grade_api_v2: request.Files: " + str(file) + "\tfilename: " + str(filename))

        # todo:
        # 1. check xml -> validate against xsd
        # 2. check uuid or download external xml
        # 3. files > file id all should be zipped


        # get xml version
        #xml_version = get_xml_version(submission_xml=xml)

        # do not validate for performance reasons
        # validate xsd
        #if xml_version:
        #    # logger.debug("xml: " + xml)
        #    is_valid = validate_xml(xml=xml, xml_version=xml_version)
        #else:
        #    logger.debug("no version - " + str(xml))
        #    is_valid = validate_xml(xml=xml)

        #logger.debug(xml)

        # note: we use lxml/etree here because it is very fast
        root = etree.fromstring(xml)

        task_file = None
        task_filename = None
        task_element = root.find(".//dns:external-task", NAMESPACES)
        if task_element is not None:
            task_path = task_element.text
            task_file, task_filename = get_external_task(request, task_path)
            #logger.debug('external-task in ' + task_path)
        else:
            task_element = root.find(".//dns:task", NAMESPACES)
            if task_element is not None:
                raise Exception ("embedded task in submission.xml is not supported")
            else:
                task_element = root.find(".//dns:inline-task-zip", NAMESPACES)
                if task_element is not None:
                    raise Exception ("inline-task-zip in submission.xml is not supported")
                else:
                    raise Exception("could not find task in submission.xml")
        #logger.debug("got task")


        # xml2dict is very slow
        #submission_dict = xml2dict(xml)
        #logger.debug("xml->dict")

        # # check task-type
        # if submission_dict.get("external-task"):
        #     # 1. external-task -> uri / http-field
        #     task_path = submission_dict["external-task"]["$"]
        #     #task_uuid = submission_dict["external-task"]["@uuid"]
        #     task_file, task_filename = get_external_task(request, task_path)
        # elif submission_dict.get("task"):
        #     # 2. task-embedded
        #     raise Exception ("embedded task in submission.xml is not supported")
        # elif submission_dict.get("inline-task-zip"):
        #     # 3. inline-task-zip
        #     raise Exception ("inline-task-zip in submission.xml is not supported")
        #     #return "inline-task-zip"
        # else:
        #     raise Exception ("could not find task in submission.xml")


        # task_type_dict = check_task_type(submission_dict)
        submission_files = get_submission_files(root, request) # returns a dictionary (filename -> contant)
        # compress to zip file
        #submission_zip_obj = file_dict2zip(submission_files)
        #submission_zip = {"submission" + ".zip": submission_zip_obj}  # todo name it to the user + course

        logger.debug('import task')
        response_data = import_task_internal(task_filename, task_file)
        #print 'result for Task-ID: ' + str(response_data)
        task_id = str(response_data['taskid'])
        message = response_data['message']
        if task_id == None:
            raise Exception("could not create task")

        # send submission to grader
        logger.debug('grade submission')
        grade_result = grader_internal(task_id, submission_files, answer_format)
        #grade_result = grader_internal(task_id, submission_zip, answer_format)
        logger.debug("grading finished")
        response = HttpResponse()
        response.write(grade_result)
        response.status_code = 200
        return response

    except Exception as inst:
        logger.exception(inst)
        callstack = traceback.format_exc()
        print "Exception caught Stack Trace: " + str(callstack)  # __str__ allows args to be printed directly
        response = HttpResponse()
        response.write(get_http_error_page('Error in grading process', str(inst), callstack))
        response.status_code = 500 # internal error
        return response


def get_external_task(request, task_uri):

    # logger.debug("task_uri: " + str(task_uri))
    ##
    # test file-field
    m = re.match(r"(http\-file\:)(?P<file_name>.+)", task_uri)
    file_name = None
    if m:
        file_name = m.group('file_name')
    else:
        raise Exception("uunsupported external task URI: " + task_uri)

    logger.debug("file_name: " + str(file_name))
    for filename, file in request.FILES.items():
        name = request.FILES[filename].name
        if name == file_name:
            task_filename = name
            task_file = file
            return task_file, task_filename

    raise Exception("could not find task with URI " + task_uri)




def check_post(request):
    """
    check the POST-Object
    1. could be just a submission.xml
    2. could be a submission.zip

    :rtype: submission.xml
    :param request: 
    """
    # todo check encoding of the xml -> first line
    encoding = 'utf-8'
    if not request.POST:

        #if not request.FILES:
        #    raise KeyError("No submission attached")

        try:
            # submission.xml in request.Files
            logger.debug("FILES.keys(): " + str(request.FILES.keys()))
            if request.FILES['submission.xml'].name is not None:
                #xml_dict = dict()
                #xml_dict[request.FILES['submission.xml'].name] = request.FILES['submission.xml']
                #logger.debug("xml_dict.keys(): " + str(xml_dict.keys()))
                #xml = xml_dict.popitem()[1].read()
                #xml_decoded = xml.decode(encoding)
                xml = str(request.FILES['submission.xml'].read()) # convert InMemoryUploadedFile to string
                #xml_encoded = xml.encode(encoding)
                return xml # xml_encoded
            elif request.FILES['submission.zip'].name:
                # todo zip handling -> praktomat zip
                raise Exception("zip handling is not implemented")
            else:
                raise KeyError("No submission attached")
        except MultiValueDictKeyError:
            raise KeyError("No submission attached")
    else:
        logger.debug("got submission.xml as form data")
        xml = request.POST.get("submission.xml")

        # logger.debug('submission' + xml)
        if xml is None:
            raise KeyError("No submission attached -> submission.xml")

        xml_encoded = xml.encode(encoding)
        return xml_encoded




# def response_error(msg, format):
#     """
#
#     :param msg:
#     :return: response
#     """
#     return HttpResponse(answer_format("error", msg, format))


# def get_xml_version(submission_xml):
#     pass  # todo check namespace for version
#     return "proforma_v2.0"


# def validate_xml(xml, xml_version=None):
#     logger.debug("xml_version: " + xml_version)
#     if xml_version is None:
#         logger.debug("PARENT_BASE_DIR: " + PARENT_BASE_DIR)
#         schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, 'xsd/proforma_v2.0.xsd'))
#         try:
#             schema.validate(xml)
#         except Exception as e:
#             logger.error("Schema is not valid: " + str(e))
#             raise Exception("Schema is not valid: " + str(e))
#     else:
#         if settings.PROFORMA_SCHEMA.get(xml_version):
#             logger.debug("try and validate xsd file: " + os.path.join(PARENT_BASE_DIR, settings.PROFORMA_SCHEMA.get(xml_version)))
#             schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, settings.PROFORMA_SCHEMA.get(xml_version)))
#             try:
#                 schema.validate(xml)
#             except Exception as e:
#                 logger.error("Schema is not valid: " + str(e))
#                 raise Exception("Schema is not valid: " + str(e))
#         else:
#             logger.exception("validate_xml: schema ist not supported")
#             raise Exception("schema ist not supported")
#
#     logger.debug("XML schema validation succeeded")
#
#     return True


# expensive (i.e. time consuming operation)
# def xml2dict(xml):
#     schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, 'xsd/proforma_v2.0.xsd'))  # todo fix this
#     xml_dict = xmlschema.to_dict(xml_document=xml, schema=schema)
#     return xml_dict


# def check_task_type(submission_dict):
#     if submission_dict.get("external-task"):
#         task_path = submission_dict["external-task"]["$"]
#         task_uuid = submission_dict["external-task"]["@uuid"]
#         return {"external-task": {"task_path": task_path, "task_uuid": task_uuid}}
#     elif submission_dict.get("task"):
#         return "task"
#     elif submission_dict.get("inline-task-zip"):
#         return "inline-task-zip"
#     else:
#         return None


#def get_submission_files(submission_dict, request):
def get_submission_files(root, request):
    submission_element = root.find(".//dns:external-submission", NAMESPACES)
    if submission_element is not None:
        field_name = submission_element.text
        if not field_name:
            raise Exception("invalid value for external-submission (none)")

        m = re.match(r"(http\-file\:)(?P<file_name>.+)", field_name)
        if not m:
            raise Exception("unsupported external-submission: " + field_name)

        file_name = m.group('file_name')
        if file_name is None:
            raise Exception("missing filename in external-submission")

        logger.debug("submission file_name: " + str(file_name))
        for filename, file in request.FILES.items():
            name = request.FILES[filename].name
            logger.debug("request.FILES[" + filename + "].name = " + name)

            if filename == file_name:
                submission_files_dict = dict()
                file_content = str(file.read().decode(encoding='utf-8', errors='replace'))
                # logger.debug("submission file content is: " + file_content)
                submission_files_dict.update({file_name: file_content})
                return submission_files_dict

        # special handling for filenames containing a relative path:
        # if file_name is not found:
        for filename, file in request.FILES.items():
            #name = request.FILES[filename].name
            #logger.debug("request.FILES[" + name + "]")
            pure_filename = os.path.basename(file_name) # remove path
            if filename == pure_filename:
                submission_files_dict = dict()
                file_content = str(file.read().decode(encoding='utf-8', errors='replace'))
                # logger.debug("submission file content is: " + file_content)
                submission_files_dict.update({file_name: file_content})
                return submission_files_dict


        raise Exception("could not find external submission " + file_name)

    submission_files_dict = dict()
    submission_elements = root.findall(".//dns:files/dns:file/dns:embedded-txt-file", NAMESPACES)
    for sub_file in submission_elements:
        #logger.debug(sub_file)
        filename = sub_file.attrib["filename"]
        file_content = sub_file.text.encode('utf-8')
        submission_files_dict.update({filename: file_content})

    submission_elements = root.findall(".//dns:files/dns:file/dns:embedded-bin-file", NAMESPACES)
    if len(submission_elements) > 0:
        raise Exception("embedded-bin-file in submission is not supported")
    submission_elements = root.findall(".//dns:files/dns:file/dns:attached-bin-file", NAMESPACES)
    if len(submission_elements) > 0:
        raise Exception("attached-bin-file in submission is not supported")
    submission_elements = root.findall(".//dns:files/dns:file/dns:attached-txt-file", NAMESPACES)
    if len(submission_elements) > 0:
        raise Exception("attached-txt-file in submission is not supported")

    if len(submission_files_dict) == 0:
        raise Exception("No submission attached")

    return submission_files_dict

# compress file dictionary as zip file
# def file_dict2zip(file_dict):
#     tmp_dir = tempfile.mkdtemp()
#
#     try:
#
#         os.chdir(os.path.dirname(tmp_dir))
#         for key in file_dict:
#             logger.debug("file_dict2zip Key: " + key)
#             if os.path.dirname(key) == '':
#                 with open(os.path.join(tmp_dir, key), 'w') as f:
#                     f.write(file_dict[key])
#             else:
#                 if not os.path.exists(os.path.join(tmp_dir, os.path.dirname(key))):
#                     os.makedirs(os.path.join(tmp_dir, os.path.dirname(key)))
#                 with open(os.path.join(tmp_dir, key), 'w') as f:
#                     f.write(file_dict[key])
#
#         submission_zip = shutil.make_archive(base_name="submission", format="zip", root_dir=tmp_dir)
#         submission_zip_fileobj = open(submission_zip, 'rb')
#         return submission_zip_fileobj
#     except IOError as e:
#         raise IOError("IOError:", "An error occurred while open zip-file", e)
#     #except Exception as e:
#     #    raise Exception("zip-creation error:", "An error occurred while creating zip: E125001: "
#     #                    "Couldn't determine absolute path of '.'", e)
#     finally:
#         shutil.rmtree(tmp_dir)


# def create_external_task(content_file_obj, server, taskFilename, formatVersion):
#
#
#
#     #if settings.server.get(server):
#     #    LOGINBYSERVER
#     FILENAME = taskFilename
#     #f = codecs.open(content_file_obj.name, 'r+', 'utf-8')
#     #files = {FILENAME: codecs.open(content_file_obj.name, 'r+', 'utf-8')}
#
#     try:
#         files = {FILENAME: open(content_file_obj.name, 'rb')}
#     except IOError:  #
#         files = {FILENAME: content_file_obj}
#     url = urlparse.urljoin(server, 'importTask')
# #    url = urllib.parse.urljoin(server, 'importTask')
#     result = requests.post(url, files=files)
#
#     message = ''
#     if result.headers['Content-Type'] == 'application/json':
#         logger.debug(result.text)
#         #try:
#         taskid = result.json().get('taskid')
#         message = result.json().get('message')
#
#         #except ValueError:
#         #    message = "Error while creating task on grader: " + str(ValueError)
#         #    raise ValueError(message)
#         #except Exception:
#         #    message = "Error while creating task on grader: " + str(Exception)
#         #    raise Exception(message)
#     else:
#         message = "Could not create task on grader: " + result.text
#         raise IOError(message)
#
#     if taskid == None:
#         logger.debug('could not create task: ' + str(message))
#         raise Exception('could not create task: ' + str(message))
#
#     return taskid


# def send_submission2external_grader(request, server, taskID, files, answer_format):
#     logger.debug("send_submission2external_grader called")
#     serverpath = urlparse.urlparse(server)#
# ##    serverpath = urllib.parse.urlparse(server)
#     domainOutput = "external_grade/" + str(answer_format) + "/v1/task/"
#     path = "/".join([str(x).rstrip('/') for x in [serverpath.path, domainOutput, str(taskID)]])
#     gradingURL = urlparse.urljoin(server, path)
# ##    gradingURL = urllib.parse.urljoin(server, path)
#     logger.debug("gradingURL: " + gradingURL)
#     result = requests.post(url=gradingURL, files=files)
#     return result
#     #if result.status_code == requests.codes.ok:
#     #    return result.text
#     #else:
#     #    logger.exception("send_submission2external_grader: " + str(result.status_code) + "result_text: " + result.text)
#     #    raise Exception(result.text)