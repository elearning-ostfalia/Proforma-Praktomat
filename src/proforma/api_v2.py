# -*- coding: utf-8 -*-
import tempfile
#from urllib.parse import urlparse # version 3
import urlparse
import traceback





from django.core.serializers import json
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import os
import re
import urllib
import requests
import shutil
import logging
import xmlschema
import pprint
from requests.exceptions import InvalidSchema
from export_universal_task.views import import_task_internal
from external_grade.views import grader_internal

#from proforma_taskget.views import login_phantomjs, get_task_from_externtal_server, answer_format_template

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PARENT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE_PATH = os.path.join(BASE_DIR, "/cache")
logger = logging.getLogger(__name__)


def grade_api_v2(request,):
    """
    grade_api_v2
    rtype: grade_api_v2
    """
    xml_version = None
    lms_is_lon_capa = False
    answer_format = "proformav2"
    xml_dict = dict()
    post_content = ""

#    logger.debug('HTTP_USER_AGENT: ' + request.META.get('HTTP_USER_AGENT') +
#                 '\nHTTP_HOST: ' + request.META.get('HTTP_HOST') +
#                 '\nrequest.path: ' + request.path +
#     '\nrequest.POST:' + str(list(request.POST.items())))


    # check POST returns submission_xml or raise exception with msg


    # create task and get Id
    try:
        # debugging uploaded files
        for field_name, file in request.FILES.items():
            filename = file.name
            logger.debug("grade_api_v2: request.Files: " + str(file) + "\tfilename: " + str(filename))

        # todo:
        # 1. check xml -> validate against xsd
        # 2. check uuid or download external xml
        # 3. files > file id all should be zipped
        # 4.
        # check if LON-CAPA
        #if check_lon_capa(request):
        #    lms_is_lon_capa = True
        #    answer_format = "loncapaV1"

        try:
            xml = check_post(request)
        except KeyError as e:
            raise Exception("No submisson attached")

        # get xml version
        xml_version = get_xml_version(submission_xml=xml)

        # do not validate for performance reasons
        # concat LON-CAPA
        # student_response -> in XML einfügen
        # validate xsd
        #if xml_version:
        #    # logger.debug("xml: " + xml)
        #    is_valid = validate_xml(xml=xml, xml_version=xml_version)
        #else:
        #    logger.debug("no version - " + str(xml))
        #    is_valid = validate_xml(xml=xml)

        #if is_valid is False:
        #    raise Exception("no valid answer submitted -> check xsd")

        submission_dict = xml2dict(xml)

        # check task-type
        # 1. external-task -> uri / http-field
        # 2. task-embedded
        # 3. inline-task-zip
        task_type_dict = check_task_type(submission_dict)

        external_task_http_field = False
        task_file = None
        task_filename = None
        if task_type_dict.get("external-task"):
            task_uri = task_type_dict["external-task"].get("task_path")  # todo check uri
            task_uuid = task_type_dict["external-task"].get("task_uuid")
            logger.debug("task_uri: " + str(task_uri))
            ##

            # test file-field
            m = re.match(r"(http\-file\:)(?P<file_name>.+)", task_uri)
            file_name = None
            if m:
                file_name = m.group('file_name')

            if file_name is not None:
                external_task_http_field = True
                logger.debug("file_name: " + str(file_name))
                for filename, file in request.FILES.items():
                    name = request.FILES[filename].name
                    if name == file_name:
                        task_filename = name
                        task_file = file
                if task_file is None:
                    raise Exception("task is not attached - Request-Files")
            else:
                logger.debug("file_name is None ")
                try:
                    # getTask todo: check cache for uuid
                    parse_uri = urlparse(task_uri)
                    # scheme://netloc/path;parameters?query#fragment

                    if parse_uri.netloc == 'vita.ostfalia.de':
                        cj = login_phantomjs(server="https://" + parse_uri.netloc)
                        task_file = get_task_from_externtal_server(server=parse_uri.scheme + "://" + parse_uri.netloc,
                                                                   task_path=parse_uri.path,
                                                                   cookie=cj,
                                                                   task_uuid=None)
                    else:
                        # todo clean this shit
                        parse_path = parse_uri.path + "?" + parse_uri.query
                        logger.debug("parse_path: " + parse_path)
                        task_file = get_task_from_externtal_server(server=parse_uri.scheme + "://" + parse_uri.netloc,
                                                                   task_path=parse_path)
                    if settings.CACHE and task_uuid:
                        write_cache_task(task_uuid, task_file)
                except InvalidSchema as e:
                    logger.exception(str(type(e)) + str(e.args))
                    raise Exception("external url is not valid: " + task_uri)

        submission_type = check_submission_type(submission_dict, request)
        # todo external submission
        if submission_type.get("embedded_files"):
            submission_zip_obj = file_dict2zip(submission_type.get("embedded_files"))
            submission_zip = {"submission" + ".zip": submission_zip_obj}  # todo name it to the user + course
        elif submission_type.get("external-submission"):
            logger.debug("submission_type: external-submission")
            submission_zip_obj = file_dict2zip(submission_type.get("external-submission"))
            submission_zip = {"submission" + ".zip": submission_zip_obj}  # todo name it to the user + course
            logger.debug("external-submission" + str(submission_zip))

        if external_task_http_field is False:
            task_filename = os.path.basename(parse_uri.path)
        logger.debug('import task')
        response_data = import_task_internal(task_filename, task_file)
        #print 'result for Task-ID: ' + str(response_data)
        task_id = str(response_data['taskid'])
        message = response_data['message']

        #task_id = create_external_task(content_file_obj=task_file, server=settings.GRADERV, taskFilename=task_filename,
        #                               formatVersion=answer_format)
        #print 'Task-ID: ' + str(task_id)
        if task_id == None:
            raise Exception("could not create task")

        # send submission to grader
        logger.debug('grade submission')
        #grade_result = send_submission2external_grader(request=request, server=settings.GRADERV, taskID=task_id,
        #                                               files=submission_zip, answer_format=answer_format)
        grade_result = grader_internal(task_id, submission_zip, answer_format)
        logger.debug("grading finished")
        response = HttpResponse()
        response.write(grade_result)
        response.status_code = 200
        return response

        # logger.debug("grade_result: " + grade_result)
        # if result.status_code == requests.codes.ok:
        #    return result.text

        #response = HttpResponse()
        #response.write(grade_result.text)
        #response.status_code = grade_result.status_code
        #return response

        #return grade_result
        #return HttpResponse(grade_result)

    except Exception as inst:
        logger.exception(inst)
        callstack = traceback.format_exc()
        print "Exception caught Stack Trace: " + str(callstack)  # __str__ allows args to be printed directly

        #x, y = inst.args
        #print 'x =', x
        #print 'y =', y
        #return response_error(msg="grade_api_v2\r\n" + str(inst) + '\r\n' + callstack, format=answer_format)
        response = HttpResponse()
        response.write(get_http_error_page('Error in grading process', str(inst), callstack))
        response.status_code = 500 # internal error
        return response


#        return response_error(msg="create_external_task", format=answer_format)



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
        if request.FILES:
                try:
                    # submission.xml in request.Files
                    logger.debug("FILES.keys(): " + str(request.FILES.keys()))
                    if request.FILES['submission.xml'].name is not None:
                        xml_dict = dict()
                        xml_dict[request.FILES['submission.xml'].name] = request.FILES['submission.xml']
                        logger.debug("xml_dict.keys(): " + str(xml_dict.keys()))
                        xml = xml_dict.popitem()[1].read()
                        xml_decoded = xml.decode(encoding)
                        return xml_decoded
                    elif request.FILES['submission.zip'].name:
                        # todo zip handling -> praktomat zip
                        raise Exception("zip handling is not implemented")
                    else:
                        raise KeyError("No submission attached")
                except MultiValueDictKeyError:
                    raise KeyError("No submission attached")
        else:
            raise KeyError("No submission attached")
    else:
        xml = request.POST.get("submission.xml")

        # logger.debug('submission' + xml)
        if xml is None:
            raise KeyError("No submission attached -> submission.xml")

        xml_encoded = xml.encode(encoding)
        return xml_encoded


def check_lon_capa(request):
    """
    check if LMS is LON-CAPA
    :param request:
    :return:
    """
    if request.POST.get("LONCAPA_student_response"):
        return True
    else:
        return False


def answer_format(award, message, format=None, awarded=None):
    if format is None or "loncapaV1":
        return """<loncapagrade>
        <awarddetail>%s</awarddetail>
        <message><![CDATA[proforma/api_v2: %s]]></message>
        <awarded></awarded>
        </loncapagrade>""" % (award, message)
    else:
        return """<loncapagrade>
        <awarddetail>%s</awarddetail>
        <message><![CDATA[proforma/api_v2: %s]]></message>
        <awarded>%s</awarded>
        </loncapagrade>""" % (award, message, awarded)


def response_error(msg, format):
    """

    :param msg:
    :return: response
    """
    return HttpResponse(answer_format("error", msg, format))


def get_xml_version(submission_xml):
    pass  # todo check namespace for version
    return "proforma_v2.0"


def validate_xml(xml, xml_version=None):
    logger.debug("xml_version: " + xml_version)
    if xml_version is None:
        logger.debug("PARENT_BASE_DIR: " + PARENT_BASE_DIR)
        schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, 'xsd/proforma_v2.0.xsd'))
        try:
            schema.validate(xml)
        except Exception as e:
            logger.error("Schema is not valid: " + str(e))
            raise Exception("Schema is not valid: " + str(e))
    else:
        if settings.PROFORMA_SCHEMA.get(xml_version):
            logger.debug("try and validate xsd file: " + os.path.join(PARENT_BASE_DIR, settings.PROFORMA_SCHEMA.get(xml_version)))
            schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, settings.PROFORMA_SCHEMA.get(xml_version)))
            try:
                schema.validate(xml)
            except Exception as e:
                logger.error("Schema is not valid: " + str(e))
                raise Exception("Schema is not valid: " + str(e))
        else:
            logger.exception("validate_xml: schema ist not supported")
            raise Exception("schema ist not supported")

    logger.debug("XML schema validation succeeded")

    return True


def xml2dict(xml):
    schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, 'xsd/proforma_v2.0.xsd'))  # todo fix this
    xml_dict = xmlschema.to_dict(xml_document=xml, schema=schema)
    return xml_dict


def check_task_type(submission_dict):
    if submission_dict.get("external-task"):
        task_path = submission_dict["external-task"]["$"]
        task_uuid = submission_dict["external-task"]["@uuid"]
        return {"external-task": {"task_path": task_path, "task_uuid": task_uuid}}
    elif submission_dict.get("task"):
        return "task"
    elif submission_dict.get("inline-task-zip"):
        return "inline-task-zip"
    else:
        return None


def check_submission_type(submission_dict, request):
    if submission_dict.get("external-submission"):
        submission_files_dict = None
        field_name = submission_dict["external-submission"]
        if field_name is not None:
            m = re.match(r"(http\-file\:)(?P<file_name>.+)", field_name)
            file_name = None
            if m:
                file_name = m.group('file_name')

        if file_name is not None:
            logger.debug("submission file_name: " + str(file_name))
            for filename, file in request.FILES.items():
                name = request.FILES[filename].name
                if name == file_name:
                    submission_files_dict = dict()
                    file_content = str(file.read().decode(encoding='utf-8', errors='replace'))
                    # logger.debug("submission file content is: " + file_content)
                    submission_files_dict.update({name: file_content})
                    break
            if submission_files_dict is None:
                raise Exception("submission is not attached - Request-Files")


        return{"external-submission": submission_files_dict}
    elif submission_dict.get("files"):
        # todo get a dict of files
        # embedded-files
        submission_files_dict = dict()
        if submission_dict["files"]["file"]:
            for sub_file in submission_dict["files"]["file"]:
                filename = sub_file["embedded-txt-file"]["@filename"]
                try:
                    file_content = sub_file["embedded-txt-file"]["$"].encode('utf-8')
                except KeyError:
                    raise Exception("No submission attached")
                submission_files_dict.update({filename: file_content})
            return {"embedded_files": submission_files_dict}
    else:
        raise Exception("No submission attached")


def file_dict2zip(file_dict):
    tmp_dir = tempfile.mkdtemp()

    try:

        os.chdir(os.path.dirname(tmp_dir))
        for key in file_dict:
            logger.debug("file_dict2zip Key: " + key)
            if os.path.dirname(key) == '':
                with open(os.path.join(tmp_dir, key), 'w') as f:
                    f.write(file_dict[key])
            else:
                if not os.path.exists(os.path.join(tmp_dir, os.path.dirname(key))):
                    os.makedirs(os.path.join(tmp_dir, os.path.dirname(key)))
                with open(os.path.join(tmp_dir, key), 'w') as f:
                    f.write(file_dict[key])

        submission_zip = shutil.make_archive(base_name="submission", format="zip", root_dir=tmp_dir)
        submission_zip_fileobj = open(submission_zip, 'rb')
        return submission_zip_fileobj
    except IOError as e:
        raise IOError("IOError:", "An error occurred while open zip-file", e)
    #except Exception as e:
    #    raise Exception("zip-creation error:", "An error occurred while creating zip: E125001: "
    #                    "Couldn't determine absolute path of '.'", e)
    finally:
        shutil.rmtree(tmp_dir)


def create_external_task(content_file_obj, server, taskFilename, formatVersion):



    #if settings.server.get(server):
    #    LOGINBYSERVER
    FILENAME = taskFilename
    #f = codecs.open(content_file_obj.name, 'r+', 'utf-8')
    #files = {FILENAME: codecs.open(content_file_obj.name, 'r+', 'utf-8')}

    try:
        files = {FILENAME: open(content_file_obj.name, 'rb')}
    except IOError:  #
        files = {FILENAME: content_file_obj}
    url = urlparse.urljoin(server, 'importTask')
#    url = urllib.parse.urljoin(server, 'importTask')
    result = requests.post(url, files=files)

    message = ''
    if result.headers['Content-Type'] == 'application/json':
        logger.debug(result.text)
        #try:
        taskid = result.json().get('taskid')
        message = result.json().get('message')

        #except ValueError:
        #    message = "Error while creating task on grader: " + str(ValueError)
        #    raise ValueError(message)
        #except Exception:
        #    message = "Error while creating task on grader: " + str(Exception)
        #    raise Exception(message)
    else:
        message = "Could not create task on grader: " + result.text
        raise IOError(message)

    if taskid == None:
        logger.debug('could not create task: ' + str(message))
        raise Exception('could not create task: ' + str(message))

    return taskid


def send_submission2external_grader(request, server, taskID, files, answer_format):
    logger.debug("send_submission2external_grader called")
    serverpath = urlparse.urlparse(server)#
##    serverpath = urllib.parse.urlparse(server)
    domainOutput = "external_grade/" + str(answer_format) + "/v1/task/"
    path = "/".join([str(x).rstrip('/') for x in [serverpath.path, domainOutput, str(taskID)]])
    gradingURL = urlparse.urljoin(server, path)
##    gradingURL = urllib.parse.urljoin(server, path)
    logger.debug("gradingURL: " + gradingURL)
    result = requests.post(url=gradingURL, files=files)
    return result
    #if result.status_code == requests.codes.ok:
    #    return result.text
    #else:
    #    logger.exception("send_submission2external_grader: " + str(result.status_code) + "result_text: " + result.text)
    #    raise Exception(result.text)