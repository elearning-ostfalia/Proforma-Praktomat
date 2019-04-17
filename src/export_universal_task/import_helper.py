# -*- coding: utf-8 -*-

import re
import os
import tempfile
import zipfile
from datetime import datetime
import json
from pprint import pprint
from operator import getitem

import xmlschema
from django.views.decorators.csrf import csrf_exempt

from django.core.files import File
from django.http import HttpResponse
from lxml import objectify
from os.path import basename

from accounts.models import User
from checker import CheckStyleChecker, JUnitChecker, AnonymityChecker, \
    JavaBuilder, DejaGnu, TextNotChecker, PythonChecker, RemoteSQLChecker, TextChecker, SetlXChecker, \
    CreateFileChecker, CBuilder
from os.path import dirname
import export_universal_task.views
from solutions.models import Solution, SolutionFile
from tasks.models import Task
from django.conf import settings

import logging

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PARENT_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
XSD_V_2_PATH = "xsd/proforma_v2.0.xsd"
SYSUSER = "sys_prod"


def creating_file_checker(embedded_file_dict, new_task, ns, val_order, xml_test, required=None):
    order_counter = 1

    for fileref in xml_test.xpath("p:test-configuration/p:filerefs/p:fileref", namespaces=ns):
        if embedded_file_dict.get(fileref.attrib.get("refid")) is not None:
            inst2 = CreateFileChecker.CreateFileChecker.objects.create(task=new_task,
                                                                       order=val_order,
                                                                       path=""
                                                                       )
            inst2.file = embedded_file_dict.get(fileref.attrib.get("refid"))  # check if the refid is there
            if dirname(embedded_file_dict.get(fileref.attrib.get("refid")).name) is not None:
                inst2.path = dirname(embedded_file_dict.get(fileref.attrib.get("refid")).name)
            else:
                pass

            if required is False:
                inst2 = check_visibility(inst=inst2, xml_test=None, namespace=ns, public=False)
            elif required is True:
                inst2 = check_visibility(inst=inst2, xml_test=None, namespace=ns, public=True)
            else:
                inst2 = check_visibility(inst=inst2, xml_test=None, namespace=ns, public=False)
            inst2.save()
            order_counter += 1
            val_order += 1  # to push the junit-checker behind create-file checkers
    return val_order


def check_visibility(inst, namespace, xml_test=None, public=None):
    inst.always = True

    if xml_test is None:
        inst.public = False
        inst.required = False
    else:
        if xml_test.xpath('./p:test-configuration/p:test-meta-data/praktomat:required',
                          namespaces=namespace):
            inst.required = export_universal_task.views.str2bool(xml_test.xpath('./p:test-configuration/'
                                                                                'p:test-meta-data/'
                                                                                'praktomat:required',
                                                                                namespaces=namespace)[0].text)
        if xml_test.xpath('./p:test-configuration/p:test-meta-data/praktomat:public',
                          namespaces=namespace):
            if public is False:
                inst.public = False
            elif public is True:
                inst.public = True
            else:
                inst.public = export_universal_task.views.str2bool(xml_test.xpath('./p:test-configuration/'
                                                                                  'p:test-meta-data/'
                                                                                  'praktomat:public',
                                                                                  namespaces=namespace)[0].text)
    return inst


def respond_error_message(message):
    response = HttpResponse()
    response.write(message)
    return response


def check_post_request(request, ):

    postdata = None
    # check request object -> refactor method
    if request.method != 'POST':
        message = "No POST-Request"
        respond_error_message(message=message)
    else:
        try:
            postdata = request.POST.copy()
        except Exception as e:
            message = "Error no Files attached. " + str(e)
            respond_error_message(message=message)

    # it should be one File one xml or one zip
    if len(postdata) > 1:
        message = "Only one file is supported"
        respond_error_message(message=message)
    else:
        pass


def import_task_version_1_0_1(request, ):
    return True


def extract_zip_with_xml_and_zip_dict(uploaded_file):
    """
    return task task.xml with dict of zip_files
    :param uploaded_file:
    :return:
        task_xml -> the task.xml
        dict_zip_files: dict of the files in the zip
    """
    regex = r'(' + '|'.join([
        r'(^|/)\..*',  # files starting with a dot (unix hidden files)
        r'__MACOSX/.*',
        r'^/.*',  # path starting at the root dir
        r'\.\..*',  # parent folder with '..'
        r'/$',  # don't unpack folders - the zipfile package will create them on demand
        r'META-INF/.*'
    ]) + r')'

    # return task task.xml with dict of zip_files
    # is_zip = True
    # ZIP import
    task_xml = None
    ignored_file_names_re = re.compile(regex)
    zip_file = zipfile.ZipFile(uploaded_file, 'r')
    #zip_file = zipfile.ZipFile(uploaded_file[0], 'r')
    dict_zip_files = dict()
    for zipFileName in zip_file.namelist():
        if not ignored_file_names_re.search(zipFileName):  # unzip only allowed files + wanted file
            zip_file_name_base = basename(zipFileName)
            if zip_file_name_base == "task.xml":
                task_xml = zip_file.open(zipFileName).read()
            else:
                t = tempfile.NamedTemporaryFile(delete=True)
                t.write(zip_file.open(zipFileName).read())  # todo: encoding
                t.flush()
                my_temp = File(t)
                my_temp.name = zipFileName
                dict_zip_files[zipFileName] = my_temp

    if task_xml is None:
        raise Exception("Error: Your uploaded zip does not contain a task.xml.")
    return task_xml, dict_zip_files


def check_task_description(xml_dict, new_task):
    xml_description = xml_dict.get("description")
    if xml_description is None:
        new_task.description = "No description"
    else:
        new_task.description = xml_description
    new_task.save()
    return True


def check_task_title(xml_dict, new_task):
    xml_title = xml_dict.get("title")
    if xml_title is None:
        new_task.title = "No title"
    else:
        new_task.title = xml_title
    new_task.save()
    return True


#def toJSON(task_object):
#        return json.dumps(task_object, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# def _try(o):
#     try:
#         return o.__dict__
#     except:
#         return str(o)


# def to_json(task_object):
#     return json.dumps(task_object, default=lambda o: _try(o), sort_keys=True, indent=0,
#                       separators=(',', ':')).replace('\n', '')


def create_user_check_user(user_name, new_task):
    try:
        sys_user = User.objects.get(username=user_name)
    except User.DoesNotExist:
        sys_user = User.objects.create_user(username=user_name, email="creator@localhost")
    except Exception as e:
        new_task.delete()
        e("system user does not exist and could not created " + str(e))
    return sys_user


def create_file_dict_func(xml_obj, namespace, external_file_dict=None, ):
    # Files create dict with internal file objects should also used for external files
    embedded_file_dict = dict()
    # external_file_dict = dict()
    create_file_dict = dict()
    test_file_dict = dict()
    modelsolution_file_dict = dict()

    try:
        list_of_files = xml_obj.xpath("/p:task/p:files/p:file", namespaces=namespace)

        for k in list_of_files:
            # todo add: embedded-bin-file
            # todo add: attached-txt-file
            used_by_grader = k.attrib.get('used-by-grader')
            if used_by_grader == "true":
                if k.xpath("p:embedded-txt-file", namespaces=namespace):
                    t = tempfile.NamedTemporaryFile(delete=True)
                    t.write(k['embedded-txt-file'].text.encode("utf-8"))
                    t.flush()
                    my_temp = File(t)
                    my_temp.name = k['embedded-txt-file'].attrib.get("filename")
                    embedded_file_dict[k.attrib.get("id")] = my_temp
                elif k.xpath("p:attached-bin-file", namespaces=namespace):
                    filename = k['attached-bin-file'].text
                    if external_file_dict is None:
                        raise Exception('no files in zip found')
                    embedded_file_dict[k.attrib.get("id")] = external_file_dict[filename]
                else:
                    raise Exception('unsupported file type in task.xml (embedded-bin-file or attached-txt-file)')

        create_file_dict = embedded_file_dict

        list_of_test_files = xml_obj.xpath("/p:task/p:tests/p:test/p:test-configuration/"
                                           "p:filerefs/p:fileref/@refid", namespaces=namespace)
        for test_ref_id in list_of_test_files:
            test_ref_id_of_dict = {test_ref_id: create_file_dict.pop(test_ref_id, "")}
            test_file_dict.update(test_ref_id_of_dict)

        list_of_modelsolution_refs_path = xml_obj.xpath("/p:task/"
                                                        "p:model-solutions/p:model-solution/p:filerefs/"
                                                        "p:fileref/@refid", namespaces=namespace)

        for model_solution_id in list_of_modelsolution_refs_path:
            model_ref_id_of_dict = {model_solution_id: create_file_dict.pop(model_solution_id, "")}
            modelsolution_file_dict.update(model_solution_id=model_ref_id_of_dict)
    except Exception as e:
        raise e
    except KeyError as e:
        print e
        raise e
    except Exception as e:
        print e
        raise e
    # for uploaded_file in xml_task.xpath("p:files/p:file", namespaces=ns):
    #     if uploaded_file.attrib.get("class") == "internal":
    #         if uploaded_file.attrib.get("type") == "embedded":
    #             t = tempfile.NamedTemporaryFile(delete=True)
    #             t.write(uploaded_file.text.encode("utf-8"))
    #             t.flush()
    #             my_temp = File(t)
    #             my_temp.name = (uploaded_file.attrib.get("filename"))
    #             embedded_file_dict[uploaded_file.attrib.get("id")] = my_temp
    #         else:
    #             embedded_file_dict[uploaded_file.attrib.get("id")] = \
    #                 dict_zip_files[uploaded_file.attrib.get("filename")]
    #
    #     # all files in this dict were created by CreateFileChecker
    #     if (uploaded_file.attrib.get("class") == "library") or \
    #        (uploaded_file.attrib.get("class") == "internal-library"):
    #         if uploaded_file.attrib.get("type") == "embedded":
    #             t = tempfile.NamedTemporaryFile(delete=True)
    #             t.write(uploaded_file.text.encode("utf-8"))
    #             t.flush()
    #             my_temp = File(t)
    #             my_temp.name = (uploaded_file.attrib.get("filename"))  # check! basename? i lost the path o not?
    #             create_file_dict[uploaded_file.attrib.get("id")] = my_temp
    #         else:
    #             create_file_dict[uploaded_file.attrib.get("id")] = dict_zip_files[uploaded_file.attrib.get("filename")]

    # dict of test + files
    # dict of model_solution

    # dict of test_file_ids
    return create_file_dict, test_file_dict, modelsolution_file_dict


def create_java_compiler_checker(xmlTest, val_order, new_task, ns):
    checker_ns = ns.copy()
    checker_ns['praktomat'] = 'urn:proforma:praktomat:v0.2'

    inst = JavaBuilder.JavaBuilder.objects.create(task=new_task,
                                                  order=val_order,
                                                  _flags="",
                                                  _output_flags="",
                                                  _file_pattern=r"^.*\.[jJ][aA][vV][aA]$"
                                                  )
    if xmlTest.attrib is not None:
        attributes = xmlTest.attrib
        if attributes.get("id"):
            inst.proforma_id = attributes.get("id")
    # first check if path exist, second if the element is empty, third import the value
    if xmlTest.xpath("p:title", namespaces=ns) is not None:
            inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]

    try:
        if xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                    namespaces=checker_ns)[0].text is not None: inst._flags = \
            xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                    namespaces=checker_ns)[0].text
    except Exception as e:
        pass
    try:
        if xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                         "praktomat:config-CompilerOutputFlags", namespaces=checker_ns)[0].text is not None:
            inst._output_flags = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                         "praktomat:config-CompilerOutputFlags", namespaces=checker_ns)[0].text
    except Exception as e:
        pass
    try:
        if xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                   namespaces=checker_ns)[0].text is not None : inst._libs = \
            xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                   namespaces=checker_ns)[0].text

    except Exception as e:
        pass
    try:
        if xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                         "praktomat:config-CompilerFilePattern",
                         namespaces=checker_ns)[0] is not None: inst._file_pattern = \
            xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                          "praktomat:config-CompilerFilePattern",
                          namespaces=checker_ns)[0]
    except Exception as e:  #XPathEvalError
        pass
    try:
        inst = check_visibility(inst=inst, namespace=checker_ns, xml_test=xmlTest)
    except Exception as e:
        new_task.delete()
        raise e("Error while parsing xml in test - compiler\r\n" + str(e))
    inst.save()
    pass


def create_java_unit_checker(xmlTest, val_order, new_task, ns, test_file_dict):
    checker_ns = ns.copy()
    checker_ns['praktomat'] = 'urn:proforma:praktomat:v0.2'
    checker_ns['unit_new'] = 'urn:proforma:tests:unittest:v1.1'
    checker_ns['unit'] = 'urn:proforma:tests:unittest:v1'

    inst = JUnitChecker.JUnitChecker.objects.create(task=new_task, order=val_order)

    if xmlTest.attrib is not None:
        attributes = xmlTest.attrib
        if attributes.get("id"):
            inst.proforma_id = attributes.get("id")

    if xmlTest.xpath("p:title", namespaces=ns) is not None:
            inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]


    if (xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                      namespaces=checker_ns) and
        xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                      namespaces=checker_ns)[0].text):
        inst.class_name = xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                                        namespaces=checker_ns)[0].text
    if (xmlTest.xpath("p:test-configuration/unit_new:unittest/unit_new:entry-point",
                      namespaces=checker_ns) and
        xmlTest.xpath("p:test-configuration/unit_new:unittest/unit_new:entry-point",
                      namespaces=checker_ns)[0].text):
        inst.class_name = xmlTest.xpath("p:test-configuration/unit_new:unittest/unit_new:entry-point",
                                        namespaces=checker_ns)[0].text
    #else:
    #    inst.delete()
    #    raise Exception("unittest main-class not found. Check your namespace")

    if xmlTest.xpath("p:test-configuration/unit:unittest[@framework='JUnit']", namespaces=checker_ns):
        if xmlTest.xpath("p:test-configuration/unit:unittest[@framework='JUnit']",
                         namespaces=checker_ns)[0].attrib.get("version"):
            version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                                   "unit:unittest[@framework='JUnit']",
                                                   namespaces=checker_ns)[0].attrib.get("version"))

            if int(version[0]) == 3:
                inst.junit_version = 'junit3'
            elif int(version[0]) == 4:
                if str(version[1]) == "12-gruendel":
                    inst.junit_version = 'junit4.12-gruendel'
                elif str(version[1]) == "12":
                    inst.junit_version = 'junit4.12'
                else:
                    inst.junit_version = 'junit4'
            else:
                inst.delete()
                raise Exception("JUnit-Version not known: " + str(version))
    elif xmlTest.xpath("p:test-configuration/unit_new:unittest[@framework='JUnit']", namespaces=checker_ns):
        if xmlTest.xpath("p:test-configuration/unit_new:unittest[@framework='JUnit']",
                         namespaces=checker_ns)[0].attrib.get("version"):
            version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                                   "unit_new:unittest[@framework='JUnit']",
                                                   namespaces=checker_ns)[0].attrib.get("version"))

            if int(version[0]) == 3:
                inst.junit_version = 'junit3'
            elif int(version[0]) == 4:
                if str(version[1]) == "12-gruendel":
                    inst.junit_version = 'junit4.12-gruendel'
                elif str(version[1]) == "12":
                    inst.junit_version = 'junit4.12'
                else:
                    inst.junit_version = 'junit4'
            else:
                inst.delete()
                raise Exception("JUnit-Version not known: " + str(version))

    if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                      namespaces=checker_ns) and
        xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                      namespaces=checker_ns)[0].text):
        inst.test_description = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                              "praktomat:config-testDescription",
                                              namespaces=checker_ns)[0].text
    if (xmlTest.xpath("p:test-configuration/"
                      "p:test-meta-data/praktomat:config-testname",
                      namespaces=checker_ns) and
        xmlTest.xpath("p:test-configuration/"
                      "p:test-meta-data/praktomat:config-testname",
                      namespaces=checker_ns)[0].text):
        inst.name = xmlTest.xpath("p:test-configuration/"
                                  "p:test-meta-data/praktomat:config-testname",
                                  namespaces=checker_ns)[0].text
    if xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=checker_ns):
        val_order = creating_file_checker(embedded_file_dict=test_file_dict, new_task=new_task, ns=checker_ns,
                                          val_order=val_order, xml_test=xmlTest)

    inst.order = val_order
    inst = check_visibility(inst=inst, namespace=checker_ns, xml_test=xmlTest)
    inst.save()


def create_java_checkstyle_checker(xmlTest, val_order, new_task, ns, test_file_dict):
    checker_ns = ns.copy()
    checker_ns['praktomat'] = 'urn:proforma:praktomat:v0.2'
    checker_ns['check'] = 'urn:proforma:tests:java-checkstyle:v1.1'
    
    for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=checker_ns):
        if test_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
            inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=new_task, order=val_order)
            inst.configuration = test_file_dict.get(fileref.fileref.attrib.get("refid"))
        if xmlTest.xpath("p:title", namespaces=checker_ns) is not None:
            inst.name = xmlTest.xpath("p:title", namespaces=checker_ns)[0]
        if xmlTest.attrib is not None:
            attributes = xmlTest.attrib
            if attributes.get("id"):
                inst.proforma_id = attributes.get("id")
        if xmlTest.xpath("p:test-configuration/praktomat:version", namespaces=checker_ns):
            checkstyle_version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                          "praktomat:version", namespaces=checker_ns)[0].text)
            if int(checkstyle_version[0]) == 7 and int(checkstyle_version[1]) == 6:
                inst.check_version = 'check-7.6'
            elif int(checkstyle_version[0]) == 6 and int(checkstyle_version[1]) == 2:
                inst.check_version = 'check-6.2'
            elif int(checkstyle_version[0]) == 5 and int(checkstyle_version[1]) == 4:
                inst.check_version = 'check-5.4'
            else:
                inst.delete()
                raise Exception("Checkstyle-Version is not supported: " + str(checkstyle_version))
        elif xmlTest.xpath("p:test-configuration/check:java-checkstyle",
                           namespaces=checker_ns)[0].attrib.get("version"):
            checkstyle_version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                          "check:java-checkstyle", namespaces=checker_ns)[0].attrib.get("version"))
            if int(checkstyle_version[0]) == 7 and int(checkstyle_version[1]) == 6:
                inst.check_version = 'check-7.6'
            elif int(checkstyle_version[0]) == 6 and int(checkstyle_version[1]) == 2:
                inst.check_version = 'check-6.2'
            elif int(checkstyle_version[0]) == 5 and int(checkstyle_version[1]) == 4:
                inst.check_version = 'check-5.4'
            else:
                inst.delete()
                raise Exception("Checkstyle-Version is not supported: " + str(checkstyle_version))

        if xmlTest.xpath("p:test-configuration/check:java-checkstyle/"
                         "check:max-checkstyle-warnings", namespaces=checker_ns):
            inst.allowedWarnings = xmlTest.xpath("p:test-configuration/"
                                                 "check:java-checkstyle/"
                                                 "check:max-checkstyle-warnings", namespaces=checker_ns)[0]
        inst = check_visibility(inst=inst, namespace=checker_ns, xml_test=xmlTest)
        inst.save()


def create_setlx_checker(xmlTest, val_order, new_task, ns, test_file_dict):
    for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
        if test_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
            inst = SetlXChecker.SetlXChecker.objects.create(task=new_task, order=val_order)
            inst.testFile = test_file_dict.get(fileref.fileref.attrib.get("refid"))

    if xmlTest.xpath("p:title", namespaces=ns) is not None:
        if inst is None:
            raise Exception("Error in JARTest")
        else:
            inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]

    if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                      namespaces=ns) and
        xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                      namespaces=ns)[0].text):
        inst.test_description = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                              "praktomat:config-testDescription",
                                              namespaces=ns)[0].text

    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
    inst.save()


def create_python_checker(xmlTest, val_order, new_task, ns, test_file_dict):
        inst = PythonChecker.PythonChecker.objects.create(task=new_task, order=val_order)
        if (xmlTest.xpath("p:title", namespaces=ns) and
           xmlTest.xpath("p:title", namespaces=ns)[0].text):
            inst.name = xmlTest.xpath("p:title", namespaces=ns)[0].text
        if (xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                          "praktomat:config-remove-regex", namespaces=ns) and
            xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-remove-regex",
                          namespaces=ns)[0].text):
            inst.remove = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                        "praktomat:config-remove-regex", namespaces=ns)[0].text
        if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-returnHtml",
                          namespaces=ns) and
            xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-returnHtml",
                          namespaces=ns)[0].text):
            inst.public = export_universal_task.\
                          views.str2bool(xmlTest.xpath("p:test-configuration/"
                                                       "p:test-meta-data/"
                                                       "praktomat:config-returnHtml", namespaces=ns)[0].text)
        if xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
            for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                if test_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst.doctest = test_file_dict.get(fileref.fileref.attrib.get("refid"))
                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                    inst.save()
                else:
                    inst.delete()
                    message = "No File for python-checker found"


def import_task_v2(task_xml, dict_zip_files=None):
    format_namespace = "urn:proforma:v2.0"
    ns = {"p": format_namespace}
    message = ""

    # no need to actually validate xml against xsd
    # (it is only time consuming)
    schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, XSD_V_2_PATH))
    xml_dict = schema.to_dict(task_xml)

    # try:
    #     xml_dict = validate_xml(xml=task_xml)
    # except Exception as e:
    #     logger.debug(str(type(e))+str(e.args))
    #     return json_error_message(json_message="validate_xml error (task.xml): " + str(e.args), http_code=400)

    xml_obj = objectify.fromstring(task_xml)

    new_task = Task.objects.create(title="test",
                                   description="",
                                   submission_date=datetime.now(),
                                   publication_date=datetime.now())


    check_task_title(xml_dict=xml_dict, new_task=new_task)
    check_task_description(xml_dict=xml_dict, new_task=new_task)
    check_submission_restriction(xml_dict=xml_dict, new_task=new_task)
    try:
        create_user_check_user(user_name=SYSUSER, new_task=new_task)
    except Exception as e:
        return json_error_message(json_message="create_user_check_user error: " + str(e.args), http_code=400)

    if dict_zip_files is None:
        create_file_dict, test_file_dict, list_of_modelsolution_refs_path = create_file_dict_func(xml_obj=xml_obj, namespace=ns)
    else:
        create_file_dict, test_file_dict, list_of_modelsolution_refs_path = create_file_dict_func(xml_obj=xml_obj, namespace=ns, external_file_dict=dict_zip_files)

    val_order = 1
    inst = None
    # create library and internal-library with create FileChecker
    val_order = export_universal_task.views.creatingFileCheckerNoDep(create_file_dict, new_task, ns,
                                                                     val_order, xmlTest=None)
    for xmlTest in xml_obj.tests.iterchildren():
        #try:
        if xmlTest.xpath("p:test-type", namespaces=ns)[0].text == "java-compilation":  # todo check compilation_xsd
            create_java_compiler_checker(xmlTest, val_order, new_task, ns)
        elif xmlTest.xpath("p:test-type", namespaces=ns)[0].text == "unittest":
            create_java_unit_checker(xmlTest, val_order, new_task, ns, test_file_dict)
        elif xmlTest.xpath("p:test-type", namespaces=ns)[0].text == "java-checkstyle":
            create_java_checkstyle_checker(xmlTest, val_order, new_task, ns, test_file_dict)
        #elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "jartest" and \
        #     xmlTest.xpath("p:test-configuration/jartest:jartest[@framework='setlX']", namespaces=ns):
        #        create_setlx_checker(xmlTest, val_order, new_task, ns, test_file_dict)
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "python-doctest":
                create_python_checker(xmlTest, val_order, new_task, ns, test_file_dict)
        #except Exception as e:
        #    return json_error_message(json_message="create_test error: " + str(e.args), http_code=400) # Karins Versuch
        #    return HttpResponse(content=to_json(e), content_type="application/json")
        val_order += 1
    new_task.save()
    # proglang -> e.g Java 1.6 / Python 2.7
    # files : used-by-grader="true"

    # model-solutions
    # tests
    #   compiler
    #   JUNIT
    #   Checkstyle
    response_data = dict()
    response_data['taskid'] = new_task.id
    response_data['message'] = message
    return response_data # HttpResponse(json.dumps(response_data), content_type="application/json")

def getitem_from_dict(dataDict, mapList):
    """Iterate nested dictionary"""
    return reduce(getitem, mapList, dataDict)


def import_task(task_xml, dict_zip_files_post=None ):
    """
    :param request: request object for getting POST and GET
    :return: response

    expect xml-file in post-request
    tries to objectify the xml and import it in Praktomat
    """
    # is_zip = False
    rxcoding = re.compile(r"encoding=\"(?P<enc>[\w.-]+)")
    # rxversion = re.compile(r"^(?P<major>(\d+))(\.){1}?(?P<minor>(\d+))(\.){1}?(\.|\d+)+$")
    defined_user = "sys_prod"
    message = ""

    xmlexercise = task_xml

    if dict_zip_files_post is None:
        dict_zip_files = None
    else:
        dict_zip_files = dict_zip_files_post

    response = HttpResponse()

    # here is the actual namespace for the version
    format_namespace = "urn:proforma:task:v1.0.1"

    # the right ns is also for the right version necessary
    ns = {"p": format_namespace,
          "praktomat": "urn:proforma:praktomat:v0.2",
          "unit": "urn:proforma:tests:unittest:v1",
          "jartest": 'urn:proforma:tests:jartest:v1',
          }

    try:
        encoding = rxcoding.search(xmlexercise, re.IGNORECASE)
        if (encoding != 'UFT-8' or encoding != 'utf-8') and encoding is not None:
            xmlexercise = xmlexercise.decode(encoding.group('enc')).encode('utf-8')
        xml_object = objectify.fromstring(xmlexercise)

    except Exception as e:
        response.write("Error while parsing xml\r\n" + str(e))
        return response

    xml_task = xml_object
    # TODO check against schema

    # check Namespace
    if format_namespace not in xml_object.nsmap.values():
        response.write("The Exercise could not be imported!\r\nOnly support for Namspace: " + format_namespace)
        return response

    # TODO datetime max?

    new_task = Task.objects.create(title="test",
                                   description=xml_task.description.text,
                                   submission_date=datetime.now(),
                                   publication_date=datetime.now())

    # check for submission-restriction
    if xml_task.find("p:submission-restrictions", namespaces=ns) is None:
        new_task.delete()
        response.write("The Exercise could not be imported!\r\nsubmission-restrictions-Part is missing")
        return response
    else:
        if xml_task.xpath("p:submission-restrictions/*[@max-size]", namespaces=ns):
            new_task.max_file_size = int(xml_task.xpath("p:submission-restrictions/*[@max-size]",
                                                        namespaces=ns)[0].attrib.get("max-size"))
        else:
            new_task.max_file_size = 1000

        if xml_task.xpath("p:meta-data/*[@mime-type-regexp]", namespaces=ns):
            new_task.supported_file_types = xml_task.xpath("p:meta-data/*[@mime-type-regexp]", namespaces=ns)[0]
        else:
            new_task.supported_file_types = ".*"  # all

    # check for embedded or external files

    # Files create dict with internal file objects should also used for external files
    embedded_file_dict = dict()
    # external_file_dict = dict()
    create_file_dict = dict()

    for uploaded_file in xml_task.xpath("p:files/p:file", namespaces=ns):
        if uploaded_file.attrib.get("class") == "internal":
            if uploaded_file.attrib.get("type") == "embedded":
                t = tempfile.NamedTemporaryFile(delete=True)
                t.write(uploaded_file.text.encode("utf-8"))
                t.flush()
                my_temp = File(t)
                my_temp.name = (uploaded_file.attrib.get("filename"))
                embedded_file_dict[uploaded_file.attrib.get("id")] = my_temp
            else:
                embedded_file_dict[uploaded_file.attrib.get("id")] = \
                    dict_zip_files[uploaded_file.attrib.get("filename")]

        # all files in this dict were created by CreateFileChecker
        if (uploaded_file.attrib.get("class") == "library") or \
           (uploaded_file.attrib.get("class") == "internal-library"):
            if uploaded_file.attrib.get("type") == "embedded":
                t = tempfile.NamedTemporaryFile(delete=True)
                t.write(uploaded_file.text.encode("utf-8"))
                t.flush()
                my_temp = File(t)
                my_temp.name = (uploaded_file.attrib.get("filename"))  # check! basename? i lost the path o not?
                create_file_dict[uploaded_file.attrib.get("id")] = my_temp
            else:
                create_file_dict[uploaded_file.attrib.get("id")] = dict_zip_files[uploaded_file.attrib.get("filename")]
        # if uploaded_file.attrib.get("type") == "file" and is_zip:
        #     # 1. check filename with zip_dict -> ID zuweisen
        #     # elif uploaded_file.attrib.get("class") == "internal":
        #     # embedded_file_dict[uploaded_file.attrib.get("id")] = zip_file_object.
        #     for zip_filename in zip_dict:
        #         if uploaded_file.attrib.get("filename") == zip_filename:
        #             if (uploaded_file.attrib.get("class") == "library") or \
        #                     (uploaded_file.attrib.get("class") == "internal-library"):
        #                 create_file_dict[uploaded_file.attrib.get("id")] = zipFileName.key  # get value of key!
        #             elif uploaded_file.attrib.get("class") == "internal":
        #                 #  embedded_file_dict[uploaded_file.attrib.get("id")] = zip_file_object  #todo this will fail
        #                 pass
        #             else:
        #                 new_task.delete()
        #                 response.write("file class in task.xml is not known")
        #                 return response
        #         else:
        #             new_task.delete()
        #             response.write("content of zip is not referenced by task.xml")
        #             return response

    # check if sysuser is created
    try:
        sys_user = User.objects.get(username=defined_user)
    except Exception as e:
        new_task.delete()
        response.write("System User (" + defined_user + ") does not exist: " + str(e))
        return response

    # check UUID
    if xml_task.xpath("/p:task/@uuid", namespaces=ns):
        pass
    else:
        new_task.delete()
        response.write("No uuid")
        return response
    # new model-solution import
    if xml_task.xpath("p:model-solutions/p:model-solution", namespaces=ns):

        # check files > file.id with model-solutions > model-solution > filerefs > fileref > refid
        for modelSolution in xml_task.xpath("p:model-solutions/p:model-solution", namespaces=ns):
            try:
                solution = Solution(task=new_task, author=sys_user)
            except Exception as e:
                new_task.delete()
                response.write("Error while importing Solution: " + str(e))
                return response

            # TODO check more than one solution
            if modelSolution.xpath("p:filerefs", namespaces=ns):
                for fileRef in modelSolution.filerefs.iterchildren():
                    if fileRef.attrib.get("refid") in embedded_file_dict:
                        solution.save()
                        solution_file = SolutionFile(solution=solution)
                        solution_file.file = embedded_file_dict.get(fileRef.attrib.get("refid"))
                        solution_file.save()
                        new_task.model_solution = solution
                    else:
                        new_task.delete()
                        response.write("You reference a model-solution to the files but there is no refid!")
                        return response
    else:
        new_task.delete()
        response.write("No Model Solution attached")
        return response

    # task name
    if xml_task.xpath("p:meta-data/p:title", namespaces=ns):
        new_task.title = xml_task.xpath("p:meta-data/p:title", namespaces=ns)[0].text
    else:
        xml_task.title = "unknown exercise"

    val_order = 1
    inst = None
    # create library and internal-library with create FileChecker
    val_order = export_universal_task.views.creatingFileCheckerNoDep(create_file_dict, new_task, ns,
                                                                     val_order, xmlTest=None)

    for xmlTest in xml_task.tests.iterchildren():
        try:
            if xmlTest.xpath("p:test-type", namespaces=ns)[0] == "anonymity":
                inst = AnonymityChecker.AnonymityChecker.objects.create(task=new_task, order=val_order)
                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "c-compilation":
                inst = CBuilder.CBuilder.objects.create(task=new_task,
                                                        order=val_order,
                                                        _flags="-Wall",
                                                        _output_flags="-o %s",
                                                        _file_pattern=r"^[a-zA-Z0-9_]*\.[cC]$"
                                                        )
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                  namespaces=ns)[0].text is not None):
                    inst._flags = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                                namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerOutputFlags",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerOutputFlags",
                                  namespaces=ns)[0].text is not None):
                    inst._output_flags = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                       "praktomat:config-CompilerOutputFlags",
                                                       namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                  namespaces=ns)[0].text):
                    inst._libs = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                               namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFilePattern",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFilePattern",
                                  namespaces=ns)[0].text):
                    inst._file_pattern = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                       "praktomat:config-CompilerFilePattern",
                                                       namespaces=ns)[0]
                try:
                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                except Exception as e:
                    new_task.delete()
                    response.write("Error while parsing xml\r\n" + str(e))
                    return response
                inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "java-compilation":
                inst = JavaBuilder.JavaBuilder.objects.create(task=new_task,
                                                              order=val_order,
                                                              _flags="",
                                                              _output_flags="",
                                                              _file_pattern=r"^.*\.[jJ][aA][vV][aA]$"
                                                              )
                if xmlTest.attrib is not None:
                    attributes = xmlTest.attrib
                    if attributes.get("id"):
                        inst.proforma_id = attributes.get("id")
                # first check if path exist, second if the element is empty, third import the value
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                  namespaces=ns)[0].text is not None):
                    inst._flags = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFlags",
                                                namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerOutputFlags",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerOutputFlags",
                                  namespaces=ns)[0].text is not None):
                    inst._output_flags = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                       "praktomat:config-CompilerOutputFlags",
                                                       namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                  namespaces=ns)[0].text):
                    inst._libs = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerLibs",
                                               namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFilePattern",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-CompilerFilePattern",
                                  namespaces=ns)[0].text):
                    inst._file_pattern = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                       "praktomat:config-CompilerFilePattern",
                                                       namespaces=ns)[0]
                try:
                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                except Exception as e:
                    new_task.delete()
                    response.write("Error while parsing xml\r\n" + str(e))
                    return response
                inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "dejagnu-setup":
                for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst = DejaGnu.DejaGnuSetup.objects.create(task=new_task, order=val_order)
                        inst.test_defs = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))
                        inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                        inst.save()
                    # todo else

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "dejagnu-tester":
                for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst = DejaGnu.DejaGnuTester.objects.create(task=new_task, order=val_order)
                        inst.test_case = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))
                        if xmlTest.xpath("p:title", namespaces=ns)[0] is not None:
                            inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]
                        inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                        inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "no-type-TextNotChecker":
                fine = True
                inst = TextNotChecker.TextNotChecker.objects.create(task=new_task, order=val_order)
                if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-text",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-text",
                                  namespaces=ns)[0].text):
                    inst.text = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-text",
                                              namespaces=ns)[0].text
                else:
                    inst.delete()
                    fine = False
                    message = "TextNotChecker removed: no config-text"

                if (fine and xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                           "praktomat:config-max_occurrence",
                                           namespaces=ns) and
                        xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                      "praktomat:config-max_occurrence",
                                      namespaces=ns)[0].text):
                    inst.max_occ = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                 "praktomat:config-max_occurrence",
                                                 namespaces=ns)[0].text
                else:
                    inst.delete()
                    fine = False
                    message = "TextNotChecker removed: no max_occurence"

                if fine:
                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                    inst.save()
                else:
                    pass

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "textchecker":
                inst = TextChecker.TextChecker.objects.create(task=new_task, order=val_order)
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-text",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/p:praktomat:config-text",
                                  namespaces=ns)[0].text):
                    inst.text = xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-text",
                                              namespaces=ns)[0].text
                    if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]
                else:
                    inst.delete()
                    message = "Textchecker removed: no config-text"

                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            # setlx with jartest
            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "jartest" and \
                    xmlTest.xpath("p:test-configuration/jartest:jartest[@framework='setlX']", namespaces=ns):

                for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst = SetlXChecker.SetlXChecker.objects.create(task=new_task, order=val_order)
                        inst.testFile = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))

                if xmlTest.xpath("p:title", namespaces=ns) is not None:
                    if inst is None:
                        message = "Error in JARTest"
                        break
                    else:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]

                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns)[0].text):
                    inst.test_description = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                          "praktomat:config-testDescription",
                                                          namespaces=ns)[0].text

                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            # checkstyle with jartest todo:version-check check for valid regex

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "jartest" and \
                    xmlTest.xpath("p:test-configuration/jartest:jartest[@framework='checkstyle']", namespaces=ns):

                for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=new_task, order=val_order)
                        inst.configuration = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))
                    if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]
                    if xmlTest.xpath("p:test-configuration/jartest:jartest/jartest:parameter",
                                     namespaces=ns) is not None:
                        para_list = list()
                        for parameter in xmlTest.xpath("p:test-configuration/jartest:jartest/"
                                                       "jartest:parameter", namespaces=ns):
                            para_list.append(str(parameter))
                        reg_text = '|'.join(para_list)
                        is_valid = export_universal_task.views.reg_check(reg_text)
                        if is_valid:
                            inst.regText = reg_text
                        else:
                            message = "no vaild regex for checkstyle: " + str(reg_text)
                    if xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                     "praktomat:max-checkstyle-warnings", namespaces=ns) is not None:
                        inst.allowedWarnings = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                             "praktomat:max-checkstyle-warnings", namespaces=ns)[0]

                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                    inst.save()

                if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]

                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns)[0].text):
                    inst.test_description = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                          "praktomat:config-testDescription",
                                                          namespaces=ns)[0].text

                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "unittest" and \
                    xmlTest.xpath("p:test-configuration/unit:unittest[@framework='JUnit']", namespaces=ns):
                inst = JUnitChecker.JUnitChecker.objects.create(task=new_task, order=val_order)

                if xmlTest.attrib is not None:
                    attributes = xmlTest.attrib
                    if attributes.get("id"):
                        inst.proforma_id = attributes.get("id")

                if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]

                if (xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                                  namespaces=ns)[0].text):
                    inst.class_name = xmlTest.xpath("p:test-configuration/unit:unittest/unit:main-class",
                                                    namespaces=ns)[0].text
                else:
                    inst.delete()
                    message = "unittest main-class not found. Check your namespace"
                    break

                if xmlTest.xpath("p:test-configuration/unit:unittest[@framework='JUnit']", namespaces=ns):
                    if xmlTest.xpath("p:test-configuration/unit:unittest[@framework='JUnit']",
                                     namespaces=ns)[0].attrib.get("version"):
                        version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                                               "unit:unittest[@framework='JUnit']",
                                                               namespaces=ns)[0].attrib.get("version"))

                        if int(version[0]) == 3:
                            inst.junit_version = 'junit3'
                        elif int(version[0]) == 4:
                            if str(version[1]) == "12-gruendel":
                                inst.junit_version = 'junit4.12-gruendel'
                            elif str(version[1]) == "12":
                                inst.junit_version = 'junit4.12'
                            else:
                                inst.junit_version = 'junit4'
                        else:
                            inst.delete()
                            message = "JUnit-Version not known: " + str(version)
                            break

                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-testDescription",
                                  namespaces=ns)[0].text):
                    inst.test_description = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                          "praktomat:config-testDescription",
                                                          namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/"
                                  "p:test-meta-data/praktomat:config-testname",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/"
                                  "p:test-meta-data/praktomat:config-testname",
                                  namespaces=ns)[0].text):
                    inst.name = xmlTest.xpath("p:test-configuration/"
                                              "p:test-meta-data/praktomat:config-testname",
                                              namespaces=ns)[0].text
                if xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    val_order = creating_file_checker(embedded_file_dict=embedded_file_dict, new_task=new_task, ns=ns,
                                                      val_order=val_order, xml_test=xmlTest)

                inst.order = val_order
                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "java-checkstyle":
                for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=new_task, order=val_order)
                        inst.configuration = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))
                    if xmlTest.xpath("p:title", namespaces=ns) is not None:
                        inst.name = xmlTest.xpath("p:title", namespaces=ns)[0]
                    if xmlTest.attrib is not None:
                        attributes = xmlTest.attrib
                        if attributes.get("id"):
                            inst.proforma_id = attributes.get("id")
                    if xmlTest.xpath("p:test-configuration/praktomat:version", namespaces=ns):
                        checkstyle_version = re.split('\.', xmlTest.xpath("p:test-configuration/"
                                                      "praktomat:version", namespaces=ns)[0].text)
                        if int(checkstyle_version[0]) == 7 and int(checkstyle_version[1]) == 6:
                            inst.check_version = 'check-7.6'
                        elif int(checkstyle_version[0]) == 6 and int(checkstyle_version[1]) == 2:
                            inst.check_version = 'check-6.2'
                        elif int(checkstyle_version[0]) == 5 and int(checkstyle_version[1]) == 4:
                            inst.check_version = 'check-5.4'
                        else:
                            inst.delete()
                            message = "Checkstyle-Version is not supported: " + str(checkstyle_version)
                            break

                    if xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                     "praktomat:max-checkstyle-warnings", namespaces=ns):
                        inst.allowedWarnings = xmlTest.xpath("p:test-configuration/"
                                                             "p:test-meta-data/"
                                                             "praktomat:max-checkstyle-warnings", namespaces=ns)[0]
                    if xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                     "praktomat:max-checkstyle-errors", namespaces=ns):
                        inst.allowedErrors = xmlTest.xpath("p:test-configuration/"
                                                           "p:test-meta-data/"
                                                           "praktomat:max-checkstyle-errors", namespaces=ns)[0]
                    inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                    inst.save()

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "python":
                inst = PythonChecker.PythonChecker.objects.create(task=new_task, order=val_order)
                if (xmlTest.xpath("p:title", namespaces=ns) and
                   xmlTest.xpath("p:title", namespaces=ns)[0].text):
                    inst.name = xmlTest.xpath("p:title", namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-remove-regex", namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-remove-regex",
                                  namespaces=ns)[0].text):
                    inst.remove = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                "praktomat:config-remove-regex", namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-returnHtml",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/praktomat:config-returnHtml",
                                  namespaces=ns)[0].text):
                    inst.public = export_universal_task.\
                                  views.str2bool(xmlTest.xpath("p:test-configuration/"
                                                               "p:test-meta-data/"
                                                               "praktomat:config-returnHtml", namespaces=ns)[0].text)
                if xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    for fileref in xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                        if embedded_file_dict.get(fileref.fileref.attrib.get("refid")) is not None:
                            inst.doctest = embedded_file_dict.get(fileref.fileref.attrib.get("refid"))
                            inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                            inst.save()
                        else:
                            inst.delete()
                            message = "No File for python-checker found"

            elif xmlTest.xpath("p:test-type", namespaces=ns)[0] == "RemoteScriptChecker":
                inst = RemoteSQLChecker.RemoteScriptChecker.objects.create(task=new_task, order=val_order)
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-studentFilename",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-studentFilename",
                                  namespaces=ns)[0].text):
                    inst.solution_file_name = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                            "praktomat:config-studentFilename",
                                                            namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-studentSolutionFilename",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-studentSolutionFilename",
                                  namespaces=ns)[0].text):
                    inst.student_solution_file_name = xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                                                    "praktomat:config-studentSolutionFilename",
                                                                    namespaces=ns)[0].text
                if (xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-returnHtml",
                                  namespaces=ns) and
                    xmlTest.xpath("p:test-configuration/p:test-meta-data/"
                                  "praktomat:config-returnHtml",
                                  namespaces=ns)[0].text):
                    inst.returns_html = export_universal_task.\
                                        views.str2bool(xmlTest.xpath("p:test-configuration/"
                                                                     "p:test-meta-data/"
                                                                     "praktomat:config-returnHtml",
                                                                     namespaces=ns)[0].text)
                if xmlTest.xpath("p:test-configuration/p:filerefs", namespaces=ns):
                    val_order = creating_file_checker(embedded_file_dict, new_task, ns, val_order, xmlTest)

                inst.order = val_order
                inst = check_visibility(inst=inst, namespace=ns, xml_test=xmlTest)
                inst.save()

            else:
                message = "Following Test could not imported\n" + objectify.dump(xmlTest) + "\r\n"
        except Exception as e:
            new_task.delete()
            response.write("Error while importing tests:" + str(inst) + "\r\n" + str(e))
            return response
        val_order += 1
    new_task.save()
    response_data = dict()
    response_data['taskid'] = new_task.id
    response_data['message'] = message
    return response_data # HttpResponse(json.dumps(response_data), content_type="application/json")


def check_submission_restriction(xml_dict, new_task):
    path = ['submission-restrictions']
    max_size = None
    restriction = getitem_from_dict(xml_dict, path)

    try:
        max_size = restriction.get("@max-size")
    except AttributeError:
        # no max size given => use default (1MB)
        max_size = 1000000

    # convert to KB
    new_task.max_file_size = int(max_size) / 1024

    new_task.save()
    # todo add file restrictions
    return True


@csrf_exempt  # disable csrf-cookie
def json_error_message(json_message, http_code=None):
    if http_code is None:
        return HttpResponse(content=json.dumps(json_message), status=400, content_type="application/json")
    else:
        return HttpResponse(content=json.dumps(json_message), status=http_code, content_type="application/json")


# def validate_xml(xml, xml_version=None):
#     if xml_version is None:
#         schema = xmlschema.XMLSchema(os.path.join(PARENT_BASE_DIR, XSD_V_2_PATH))
#         #try:
#         #    schema.validate(xml)
#         #except Exception as e:
#         #    logger.error("Schema is not valid: " + str(e))
#         #    raise Exception("Schema is not valid: " + str(e))
#     return schema.to_dict(xml)
