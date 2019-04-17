# -*- coding: utf-8 -*-
import json
import re
import tempfile
import zipfile
import traceback

from datetime import datetime
from os.path import dirname
from xml.dom import minidom
from xml.dom.minidom import Node

from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
from lxml import objectify
import logging

from accounts.models import User
from attestation.models import Rating
from checker import CreateFileChecker, CheckStyleChecker, JUnitChecker, AnonymityChecker, \
    JavaBuilder, DejaGnu, TextNotChecker, PythonChecker, RemoteSQLChecker, TextChecker, SetlXChecker
from checker.models import Checker
from solutions.models import Solution, SolutionFile
from tasks.models import Task, MediaFile
from export_universal_task.import_helper import check_post_request, import_task_v2, \
    extract_zip_with_xml_and_zip_dict, import_task as itask
#from VERSION import version


logger = logging.getLogger(__name__)


# def checker_struct(actual_task):
#     checker_classes = filter(lambda x: issubclass(x, Checker), models.get_models())
#     unsorted_checker = sum(map(lambda x: list(x.objects.filter(task=actual_task)), checker_classes), [])
#     checkers_sorted = sorted(unsorted_checker, key=lambda checker: checker.order)
#     rating_scale = actual_task.final_grade_rating_scale
#     media_objects = list(MediaFile.objects.all())
#     model_solution_objects = list(Solution.objects.all())
#     model_solution_file_objects = list(SolutionFile.objects.filter(solution__in=model_solution_objects))
#     return checker_classes, checkers_sorted, media_objects, rating_scale, model_solution_file_objects

def get_storage_path(instance, filename):
        """ Use this function as upload_to parameter for file fields. """
        return 'CheckerFiles/Task_%s/%s/%s' % (instance.task.pk, instance.__class__.__name__, filename)


# @csrf_exempt  # disable csrf-cookie
# def export(request, task_id=None, OutputZip=None):
#     """
#     url:
#     export_task/(?P<task_id>\d{1,6})
#     response: inline or zip
#     """
#
#     # defines which values the praktomat have not in a dict
#     defined = dict()
#     defined["langCode"] = "de"
#     defined["taskLangVersion"] = "1.6"
#     defined["taskLang"] = "java" #TODO: java only if java is the builder
#     defined["JavaVersion"] = "6"
#
#     # check if task exist
#     try:
#         actual_task = Task.objects.get(pk=task_id)
#     except ObjectDoesNotExist:
#         return HttpResponse("Your task: " + task_id + " does not Exist")
#
#     checker_classes, \
#     checkers_sorted, \
#     media_objects, \
#     rating_scale, \
#     model_solution_file_objects = checker_struct(actual_task)
#
#     # fetch files
#     files = []
#     solutionFilesList = []
#     namedFiles = dict()
#     actualSolution = actual_task.model_solution  # todo: only the model-solution not all solutions
#
#     for checker_object in checkers_sorted:
#         file_fields = filter(lambda x: isinstance(x, models.FileField), checker_object.__class__._meta.fields)
#         files += map(lambda file_field: checker_object.__getattribute__(file_field.attname), file_fields)
#
#     for media_object in media_objects:
#         files.append(media_object.media_file)
#
#     for file in files:
#         try:
#             if file.path is None:
#                 pass
#         except Exception as e:
#             return HttpResponse("One of your Checker-Files is empty. Please check the following checker: " + str(file.instance))
#         namedFiles[file] = file.instance.__class__.__name__
#
#     try:
#         solutionFiles = SolutionFile.objects.filter(solution=actualSolution)
#     except Exception as e:
#         return HttpResponse("Error in the solution: " + str(e))
#     for solutionFile in solutionFiles:
#         solutionFilesList.append(solutionFile)
#
#     try:
#         xml = render_to_string('export_external_task/xml_template.xml',
#                                {"defined": defined,
#                                 "task": actual_task,
#                                 "external": OutputZip,
#                                 "files": files,
#                                 "namedFiles": namedFiles,
#                                 "scale": rating_scale,
#                                 "checker": checkers_sorted,
#                                 "modelSolutions": solutionFilesList,
#                                 "checker_classes": checker_classes})
#     except TemplateSyntaxError as e:
#         return HttpResponse("Error in the template: " + str(e), content_type="application/xml")
#
#     xmlFilename = actual_task.title.encode('ascii', errors='replace').strip() + ".xml"
#     xml = xml.encode('utf-8')
#     xml = prettify(xml)
#     fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')  # todo: prettify lxml
#     prettyXml = re.sub(fix, '', xml)
#
#     if OutputZip:
#         zipName = "".join(actual_task.title.encode('ascii', errors='replace').split()) + ".zip"
#         temp = tempfile.TemporaryFile()
#         archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
#         archive.writestr(xmlFilename, prettyXml.encode('utf-8'))
#
#         for fileName in files:
#             archive.write(fileName.path, fileName.name)
#         archive.close()
#         wrapper = FileWrapper(temp)
#
#         response = HttpResponse(wrapper, content_type='application/zip', mimetype="application/x-zip-compressed")
#         response['Content-Disposition'] = 'attachment; filename=' + zipName
#         response['Content-Length'] = temp.tell()
#         temp.seek(0)
#         return response
#     else:
#         # return xml
#         return HttpResponse(prettyXml, content_type="application/xml")
#
#         # return zip
#         #return HttpResponse(response, mimetype="application/x-zip-compressed")
#         #response = HttpResponse(archive, mimetype="application/zip")
#         #response['Content-Disposition'] = 'attachment; filename=TaskExport.zip'


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def check_task_id(task_id):
    """
    check_task_id(task_id)
    return task object or None
    """
    try:
        task = Task.objects.get(pk=task_id)
        return task
    except ObjectDoesNotExist:
        return None


# @csrf_exempt  # disable csrf-cookie
# def listTasks(request, ):
#     """
#      url:
#      export_task/list
#      Displays the number of available tasks on the system
#     """
#     response = HttpResponse()
#     allTask = Task.objects.all()
#     response.write("Amount of available tasks: " + str(len(allTask)) + "\r\n")
#
#     for task in allTask:
#         response.write("Task " + str(task.pk) + " title: " + task.title + "\r\n")
#
#     return response


# @csrf_exempt  # disable csrf-cookie
# def activateTasks(request, task_id):
#     """
#      url:
#      export_task/activate
#      set Timer and Grading
#     """
#     response = HttpResponse()
#     try:
#         actual_task = Task.objects.get(pk=task_id)
#     except Exception:
#         response = response.write("Task: " + task_id + " does not exist\r\n Exception: " + str(Exception))
#         return response
#
#     #show task with rating scale and submission date
#     rscaleAll = Rating.objects
#     try:
#         rscale = Rating.objects.get(task=actual_task)
#     except:
#         response = response.write("Rating does not exist")
#         return response
#
#     if rscale:
#         response.write("Title: " + actual_task.title + "\r\n")
#         response.write("Rating Scale: " + str(rscale.aspect) + str(rscale.scale) + "\r\n")
#     else:
#         response.write("No RatingScale")
#     return response


# @csrf_exempt  # disable csrf-cookie
# def detail(request, task_id=None, ):
#     """
#      url:
#      export_task/detail/id
#      Displays some information about the wanted task
#     """
#     try:
#         actual_task = Task.objects.get(pk=task_id)
#     except ObjectDoesNotExist:
#         response = (error_page(1))
#         return response
#
#     response = HttpResponse()
#     response.write("Title: " + actual_task.title + "\n\r")
#     response.write("Details about task: " + str(task_id) + "\n\r")
#     response.write("Publication date: " + str(actual_task.publication_date) + "\n\r")
#     response.write("Submission date: " + str(actual_task.submission_date) + "\n\r")
#     return response


# def error_page(error_code):
#     """
#     error_page(error_code)
#     return (Http-response with Error)
#
#     error_code 1: task does not exist
#     error_code 2: no data is send to script
#     error_code 3: server couldn\'t fulfill the request. (get_data)
#     """
#     response = HttpResponse()
#     if error_code == 0:
#         response.write("Error your Task does not exist")
#     else:
#         response.write("A not defined error occured")
#     return response

#
# def prettify(elem):
#     """Return a pretty-printed XML string for the Element.
#     """
#     # rough_string = ET.tostring(elem, 'utf-8')
#     reparsed = minidom.parseString(elem)
#     remove_blanks(reparsed)
#     return reparsed.toprettyxml(indent='')


# def remove_blanks(node):
#     for x in node.childNodes:
#         if x.nodeType == Node.TEXT_NODE:
#             if x.nodeValue:
#                 x.nodeValue = x.nodeValue.strip()
#         elif x.nodeType == Node.ELEMENT_NODE:
#             remove_blanks(x)


# keep??
# def validation(xmlFile, schemaObject):
#     try:
#         xmlObject = objectify.parse(xmlFile, schemaObject)
#     except etree.XMLSyntaxError, e:
#         print("Your XML is not Valid against the schema.\r\n You got the following error: " + str(e) + "\r\n")
#         return False
#
#     except Exception as e:
#         print ("An unexpected Error occurred! \r\n" + str(e) + "\r\n")
#         return False
#
#     return xmlObject


def testVisibility(inst, xmlTest, namespace, public=None):
    # always is not necessary anymore we want the test everytime
    #if xmlTest.xpath('./test-configuration/test-meta-data/praktomat:always',
    #                 namespaces={'praktomat': 'urn:proforma:praktomat:v0.1'}):
    #    inst.always = str2bool(xmlTest.xpath('./test-configuration/test-meta-data/praktomat:always',
    #                                         namespaces={'praktomat': 'urn:proforma:praktomat:v0.1'})[0].text)
    inst.always = True

    if xmlTest is None:
        inst.public = False
        inst.required = True
    else:
        if xmlTest.xpath('./proforma:test-configuration/proforma:test-meta-data/praktomat:required',
                         namespaces=namespace):
            inst.required = str2bool(xmlTest.xpath('./proforma:test-configuration/'
                                                   'proforma:test-meta-data/'
                                                   'praktomat:required',
                                                   namespaces=namespace)[0].text)
        if xmlTest.xpath('./proforma:test-configuration/proforma:test-meta-data/praktomat:public',
                         namespaces=namespace):
            if public is False:
                inst.public = False
            elif public is True:
                inst.public = True
            else:
                inst.public = str2bool(xmlTest.xpath('./proforma:test-configuration/'
                                                     'proforma:test-meta-data/'
                                                     'praktomat:public',
                                                     namespaces=namespace)[0].text)

    return inst


@csrf_exempt
def import_task(request, task_xml, dict_zip_files_post=None):
    response = itask(request, task_xml, dict_zip_files_post=None)
    return response


@csrf_exempt
def importTaskObject(request, task_xml, dict_zip_files_post=None):
    """
    importTaskObject(request)
    return response

    url: importTaskObject
    expect xml-file in post-request
    tries to objectify the xml and import it in Praktomat
    """
    log = ""  # for hints could not imported
    #RXCODING = re.compile(r"encoding[=](\"[-\w.]+[\"])")
    RXCODING = re.compile(r"encoding=\"(?P<enc>[\w.-]+)")
    DEFINED_USER = "sys_prod"
    message = ""
    response = HttpResponse()
    #the right ns is also for the right version necessary
    ns = {'proforma': 'urn:proforma:task:v0.9.4',
          'praktomat': 'urn:proforma:praktomat:v0.1',
          'unit': 'urn:proforma:junittest3',
          'unit2': 'urn:proforma:tests:unittest:v1',
          'ju3': 'urn:proforma:tests:junit3:v0.1',
          'ju4': 'urn:proforma:tests:junit4:v0.1'}

    xmlExercise = task_xml

    if dict_zip_files_post is None:
        dict_zip_files = None
    else:
        dict_zip_files = dict_zip_files_post


    try:
        #encoding = chardet.detect(xmlExercise)['encoding'] # does not work perfectly
        encoding = RXCODING.search(xmlExercise, re.IGNORECASE)
        if (encoding != 'UFT-8' or encoding != 'utf-8') and encoding is not None:
            xmlExercise = xmlExercise.decode(encoding.group('enc')).encode('utf-8')
        #encXML = utf8_file.decode('utf-8', "xmlcharrefreplace")
        #encXML = utf8_file.decode('utf-8', "ignore")
        xmlObject = objectify.fromstring(xmlExercise)

    except Exception as e:
        response.write("Error while parsing xml\r\n" + str(e))
        return response

    #xmlTask = xmlObject.getroot()
    xmlTask = xmlObject
    # TODO check against schema
    # schemaObject = schemaToObject(fSchema)
    # xmlObject = validation(fXml, schemaObject)

    #check Namespace
    if not 'urn:proforma:task:v0.9.4' in xmlObject.nsmap.values():
        response.write("The Exercise could not be imported!\r\nOnly support for Namspace: urn:proforma:task:v0.9.4")
        return response

    #TODO datetime max?
    newTask = Task.objects.create(title="test", description=xmlTask.description.text, submission_date=datetime.now(), publication_date=datetime.now())
    if (xmlTask.xpath("proforma:submission-restrictions", namespaces=ns) is None) \
       or xmlTask.xpath("proforma:submission-restrictions", namespaces=ns) is False:
        newTask.delete()
        response.write("The Exercise could not be imported!\r\nsubmission-restrictions-Part is missing")
        return response
    else:
        if xmlTask.xpath("proforma:submission-restrictions", namespaces=ns)[0].attrib.get("max-size") is not None:
            newTask.max_file_size = int(xmlTask.xpath("proforma:submission-restrictions", namespaces=ns)[0].attrib.get("max-size"))
        else:
            newTask.max_file_size = 1000

        if (xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                          namespaces=ns) and
            xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                          namespaces=ns)[0].text):
            newTask.supported_file_types = xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                                                         namespaces=ns)[0]
        else:
            newTask.supported_file_types = ".*"  # all

    # Files create dict with file objects
    embeddedFileDict = dict()
    for xmlFile in xmlTask.xpath("proforma:files/proforma:file", namespaces=ns):
        if xmlFile.attrib.get("class") == "internal" or xmlFile.attrib.get("class") == "instruction":
            t = tempfile.NamedTemporaryFile(delete=True)
            t.write(xmlFile.text.encode("utf-8"))
            t.flush()
            myT = File(t)
            myT.name = (xmlFile.attrib.get("filename"))
            embeddedFileDict[xmlFile.attrib.get("id")] = myT

    CreateFileDict = dict()
    for xmlFile in xmlTask.xpath("proforma:files/proforma:file", namespaces=ns):
        if xmlFile.attrib.get("class") == "library" or xmlFile.attrib.get("class") == "inputdata":
            t = tempfile.NamedTemporaryFile(delete=True)
            t.write(xmlFile.text.encode("utf-8"))
            t.flush()
            myT = File(t)
            myT.name = (xmlFile.attrib.get("filename"))
            CreateFileDict[xmlFile.attrib.get("id")] = myT
    # check if sysuser is created
    try:
        sysProd = User.objects.get(username=DEFINED_USER)
    except Exception as e:
        newTask.delete()
        response.write("System User (" + DEFINED_USER + ") does not exist: " + str(e))
        return response

    #new model-solution import
    if xmlTask.xpath("proforma:model-solutions/proforma:model-solution", namespaces=ns):
        modelSolutions = xmlTask.xpath("proforma:model-solutions", namespaces=ns)
        # check files>file.id with model-solutions>model-solution>filerefs>fileref>refid
        # jeweils eine model solution
        for modelSolution in xmlTask.xpath("proforma:model-solutions/proforma:model-solution", namespaces=ns):
            try:
                solution = Solution(task=newTask, author=sysProd)
            except Exception as e:
                newTask.delete()
                response.write("Error while importing Solution: " + str(e))
                return response
            if modelSolution.xpath("proforma:filerefs", namespaces=ns) is not None:
                for fileRef in modelSolution.filerefs.iterchildren():
                    if fileRef.attrib.get("refid") in embeddedFileDict:
                        solution.save()
                        solutionFile = SolutionFile(solution=solution)
                        solutionFile.file = embeddedFileDict.get(fileRef.attrib.get("refid"))  #TODO check more than one solution
                        solutionFile.save()
                        newTask.model_solution = solution
                    else:
                        newTask.delete()
                        response.write("You reference a model-solution to the files but there is no refid!")
                        return response

    else:
        newTask.delete()
        response.write("No Model Solution attached")
        return response

    if xmlTask.xpath("proforma:meta-data/proforma:title", namespaces=ns) is not None:
        newTask.title = xmlTask.xpath("proforma:meta-data/proforma:title", namespaces=ns)[0].text
    else:
        xmlTask.title = "unknown exercise"
    valOrder = 1
    for xmlTest in xmlTask.tests.iterchildren():
        if xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "anonymity":
            inst = AnonymityChecker.AnonymityChecker.objects.create(task=newTask, order=valOrder)
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-compilation":
            inst = JavaBuilder.JavaBuilder.objects.create(task=newTask,
                                                          order=valOrder,
                                                          _flags="",
                                                          _output_flags="",
                                                          _file_pattern=r"^.*\.[jJ][aA][vV][aA]$"
                                                          )
            # first check if path exist, second if the element is empty
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                              namespaces=ns)[0].text is not None):
                inst._flags = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                                            namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerOutputFlags",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerOutputFlags",
                              namespaces=ns)[0].text is not None):
                inst._output_flags = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                   "praktomat:config-CompilerOutputFlags",
                                                   namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                              namespaces=ns)[0].text):
                inst._libs = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                                           namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFilePattern",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFilePattern",
                              namespaces=ns)[0].text):
                inst._file_pattern = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                   "praktomat:config-CompilerFilePattern",
                                                   namespaces=ns)[0]
            try:
                inst = testVisibility(inst, xmlTest, ns)
            except Exception as e:
                newTask.delete()
                response.write("Error while parsing xml\r\n" + str(e))
                return response
            inst.save()

        #this one will not used anymore
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-CreateFileChecker":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):

                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                              order=valOrder,
                                                                              path=""
                                                                              )
                    inst.file = embeddedFileDict.get(fileref.fileref.attrib.get("refid")) #check if the refid is there
                    if dirname(embeddedFileDict.get(fileref.fileref.attrib.get("refid")).name) is not None:
                        inst.path = dirname(embeddedFileDict.get(fileref.fileref.attrib.get("refid")).name)
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save(force_update=True)

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "dejagnu-setup" or \
                        xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-DejaGnuSetup":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = DejaGnu.DejaGnuSetup.objects.create(task=newTask, order=valOrder)
                    inst.test_defs = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save()
                #todo else

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "dejagnu-tester" or \
                xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-DejaGnuTester":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = DejaGnu.DejaGnuTester.objects.create(task=newTask, order=valOrder)
                    inst.test_case = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                    if xmlTest.xpath("proforma:title", namespaces=ns)[0] is not None:
                        inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-TextNotChecker":
            fine = True
            inst = TextNotChecker.TextNotChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns)[0].text):
                inst.text = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                                          namespaces=ns)[0].text
            else:
                inst.delete()
                fine = False
                message = ("TextNotChecker removed: no config-text")

            if (fine and xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                       "praktomat:config-max_occurrence",
                                       namespaces=ns) and
                    xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                  "praktomat:config-max_occurrence",
                                  namespaces=ns)[0].text):
                inst.max_occ = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                             "praktomat:config-max_occurrence",
                                             namespaces=ns)[0].text
            else:
                inst.delete()
                fine = False
                message = ("TextNotChecker removed: no max_occurence")

            if fine:
                inst = testVisibility(inst, xmlTest, ns)
                inst.save()
            else:
                pass

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "textchecker":
            inst = TextChecker.TextChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/proforma:praktomat:config-text",
                              namespaces=ns)[0].text):
                inst.text = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                                          namespaces=ns)[0].text
            else:
                inst.delete()
                message = ("Textchecker removed: no config-text")

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()
        ##only for gate import
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-junittest3":
            #xmlTest.register_namespace('foo', 'urn:proforma:junittest3')
            inst = JUnitChecker.JUnitChecker.objects.create(task=newTask, order=valOrder,
                                                            test_description="I need a test description",
                                                            name="test name")

            if (xmlTest.xpath("proforma:test-configuration/unit:main-class",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/unit:main-class",
                              namespaces=ns)[0].text):
                inst.class_name = xmlTest.xpath("proforma:test-configuration/unit:main-class",
                                                namespaces=ns)[0].text

            if (xmlTest.xpath("proforma:test-configuration/proforma:filerefs/proforma:fileref", namespaces=ns) and
                    xmlTest.xpath("proforma:test-configuration/"
                                  "proforma:filerefs/"
                                  "proforma:fileref",
                                  namespaces=ns)[0].text):
                # print embeddedFileDict.get(int(xmlTest.attrib.get("id")))
                # print xmlTest.xpath("test-configuration/filerefs/fileref")[0].text
                #todo create File checker
                inst.order = (valOrder + 1)
                inst2 = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                           order=valOrder,
                                                                           path=""
                                                                           )
                inst2.file = embeddedFileDict.get(xmlTest.attrib.get("id"))
                #print dirname(xmlTask.xpath("/task/files/file")[0].attrib.get("filename"))
                if dirname(xmlTask.xpath("/task/files/file")[0].attrib.get("filename")) is not "":
                    inst2.path = dirname(xmlTask.xpath("/task/files/file")[0].attrib.get("filename")) #todo does not work in actual version
                inst2 = testVisibility(inst2, xmlTest)
                inst2.save()
                valOrder += 1
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-junit":
            inst = JUnitChecker.JUnitChecker.objects.create(task=newTask, order=valOrder)

            if (xmlTest.xpath("proforma:test-configuration/ju3:mainclass",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/ju3:mainclass",
                              namespaces=ns)[0].text):
                inst.class_name = xmlTest.xpath("proforma:test-configuration/ju3:mainclass",
                                                namespaces=ns)[0].text
                inst.junit_version = "junit3"

            if (xmlTest.xpath("proforma:test-configuration/ju4:mainclass",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/ju4:mainclass",
                              namespaces=ns)[0].text):
                inst.class_name = xmlTest.xpath("proforma:test-configuration/ju4:mainclass",
                                                namespaces=ns)[0].text
                inst.junit_version = "junit4"

            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns)[0].text):
                inst.test_description = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                      "praktomat:config-testDescription",
                                                      namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/"
                              "proforma:test-meta-data/praktomat:config-testname",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/"
                              "proforma:test-meta-data/praktomat:config-testname",
                              namespaces=ns)[0].text):
                inst.name = xmlTest.xpath("proforma:test-configuration/"
                                          "proforma:test-meta-data/praktomat:config-testname",
                                          namespaces=ns)[0].text
            if xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns) is not None:
                orderCounter = 1

            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs/proforma:fileref", namespaces=ns):
                if embeddedFileDict.get(fileref.attrib.get("refid")) is not None:
                    inst2 = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                               order=valOrder,
                                                                               path=""
                                                                               )
                    inst2.file = embeddedFileDict.get(fileref.attrib.get("refid")) #check if the refid is there
                    if dirname(embeddedFileDict.get(fileref.attrib.get("refid")).name) is not None:
                        inst2.path = dirname(embeddedFileDict.get(fileref.attrib.get("refid")).name)
                    else:
                        pass

                    inst2 = testVisibility(inst2, xmlTest, ns)
                    inst2.save()
                    orderCounter += 1
                    valOrder += 1  #to push the junit-checker behind create-file checkers
            inst.order = valOrder
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-checkstyle" or \
                        xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-CheckStyleChecker":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=newTask, order=valOrder)
                    inst.configuration = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
                if xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:max-checkstyle-warnings"
                                 , namespaces=ns):
                    inst.allowedWarnings = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:max-checkstyle-warnings"
                                 , namespaces=ns)[0]
                inst = testVisibility(inst, xmlTest, ns)
                inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "python":
            inst = PythonChecker.PythonChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns)[0].text):
                inst.name = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                                          namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-remove-regex",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-remove-regex",
                              namespaces=ns)[0].text):
                inst.remove = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                            "praktomat:config-remove-regex",
                                             namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-returnHtml",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-returnHtml",
                              namespaces=ns)[0].text):
                inst.public = str2bool(xmlTest.xpath("proforma:test-configuration/"
                                                     "proforma:test-meta-data/praktomat:config-returnHtml",
                                                     namespaces=ns)[0].text)
                if xmlTask.xpath("/proforma:task/proforma:files/proforma:file", namespaces=ns)[0].attrib.get("type") == "embedded":  # todo: test makes no sense
                    inst.doctest = embeddedFileDict.get(int(xmlTest.attrib.get("id")))

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "RemoteScriptChecker":
            inst = RemoteSQLChecker.RemoteScriptChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentFilename",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentFilename",
                              namespaces=ns)[0].text):
                inst.solution_file_name = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                        "praktomat:config-studentFilename",
                                                        namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentSolutionFilename",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentSolutionFilename",
                              namespaces=ns)[0].text):
                inst.student_solution_file_name = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                                "praktomat:config-studentSolutionFilename",
                                                                namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-returnHtml",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-returnHtml",
                              namespaces=ns)[0].text):
                inst.returns_html = str2bool(xmlTest.xpath("proforma:test-configuration/"
                                                           "proforma:test-meta-data/"
                                                           "praktomat:config-returnHtml",
                                                           namespaces=ns)[0].text)
                if xmlTask.xpath("/proforma:task/proforma:files/proforma:file",
                                 namespaces=ns)[0].attrib.get("type") == "embedded":  # todo: test makes no sense
                    inst.solution_file = embeddedFileDict.get(int(xmlTest.attrib.get("id")))

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        else:
            message = "Following Test could not imported\n" + objectify.dump(xmlTest) + "\r\n"

        valOrder += 1
    newTask.save()
    response_data = dict()
    response_data['taskid'] = newTask.id
    response_data['message'] = message
    return response_data #HttpResponse(json.dumps(response_data), content_type="application/json")


def creatingFileChecker(embeddedFileDict, newTask, ns, valOrder, xmlTest):
    orderCounter = 1
    for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs/proforma:fileref", namespaces=ns):
        if embeddedFileDict.get(fileref.attrib.get("refid")) is not None:
            inst2 = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                       order=valOrder,
                                                                       path=""
            )
            inst2.file = embeddedFileDict.get(fileref.attrib.get("refid")) #check if the refid is there
            if dirname(embeddedFileDict.get(fileref.attrib.get("refid")).name) is not None:
                inst2.path = dirname(embeddedFileDict.get(fileref.attrib.get("refid")).name)
            else:
                pass

            inst2 = testVisibility(inst2, xmlTest, ns, False)
            inst2.save()
            orderCounter += 1
            valOrder += 1  #to push the junit-checker behind create-file checkers
    return valOrder


def creatingFileCheckerNoDep(FileDict, newTask, ns, valOrder, xmlTest):
    for fileRef in FileDict.itervalues():
        inst = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                  order=valOrder,
                                                                  path=""
                                                                  )
        inst.file = fileRef

        if dirname(fileRef.name) is not None:  # todo: exception if there is an error
            inst.path = dirname(fileRef.name)
        else:
            pass

        inst = testVisibility(inst, xmlTest, ns, False)
        inst.save()
        valOrder += 1
    return valOrder


def reg_check(regText):
    try:
        re.compile(regText)
        is_valid = True
    except re.error:
        is_valid = False
    return is_valid


@csrf_exempt
def importTaskObjectV2(task_xml, dict_zip_files): #request, ):
    """
    importTaskObject(request)
    return response

    url: importTaskObject
    expect xml-file in post-request
    tries to objectify the xml and import it in Praktomat
    """
    log = ""  # for hints could not imported
    RXCODING = re.compile(r"encoding=(\"|\')(?P<enc>[\w.-]+)")
    RXVERSION = re.compile(r"^(?P<major>(\d+))(\.){1}?(?P<minor>(\d+))(\.){1}?(\.|\d+)+$")
    DEFINED_USER = "sys_prod"
    message = ""
    response = HttpResponse()
    #the right ns is also for the right version necessary
    ns = {"proforma": "urn:proforma:task:v0.9.4",
          "praktomat": "urn:proforma:praktomat:v0.1",
          "unit": "urn:proforma:unittest",
          "jartest": 'urn:proforma:tests:jartest:v1',
          }
    #check_post_request(request)
    #filename, uploaded_file = request.FILES.popitem()  # returns list?

    # check ZIP
    #if filename[-3:].upper() == 'ZIP':
    #    task_xml, dict_zip_files = extract_zip_with_xml_and_zip_dict(uploaded_file=uploaded_file)
    #else:
    #    task_xml = uploaded_file[0].read()  # todo check name

    try:
        #encoding = chardet.detect(xmlExercise)['encoding'] # does not work perfectly
        encodingSearch = RXCODING.search(task_xml, re.IGNORECASE)
        if encodingSearch:
            encoding = encodingSearch.group("enc")

            if str(encoding).upper() != 'UTF-8':
                xmlExercise = task_xml.decode(encodingSearch.group('enc')).encode('utf-8')  # todo: remove decode
            else:
                pass
            #xmlExercise = xmlExercise.decode('utf-8', 'replace')
            #encXML = utf8_file.decode('utf-8', "xmlcharrefreplace")
            #encXML = utf8_file.decode('utf-8', "ignore")
        else:
            pass

        xmlObject = objectify.fromstring(task_xml)

    except Exception as e:
        response.write("Error while parsing xml\r\n" + str(e))
        return response

    #xmlTask = xmlObject.getroot()
    xmlTask = xmlObject
    # TODO check against schema
    # schemaObject = schemaToObject(fSchema)
    # xmlObject = validation(fXml, schemaObject)

    #check Namespace
    if not 'urn:proforma:task:v0.9.4' in xmlObject.nsmap.values():
        response.write("The Exercise could not be imported!\r\nOnly support for Namspace: urn:proforma:task:v0.9.4")
        return response

    #TODO datetime max?
    newTask = Task.objects.create(title="test", description=xmlTask.description.text, submission_date=datetime.now(), publication_date=datetime.now())
    if (xmlTask.xpath("proforma:submission-restrictions", namespaces=ns) is None) \
       or xmlTask.xpath("proforma:submission-restrictions", namespaces=ns) is False:
        newTask.delete()
        response.write("The Exercise could not be imported!\r\nsubmission-restrictions-Part is missing")
        return response
    else:
        if xmlTask.xpath("proforma:submission-restrictions", namespaces=ns)[0].attrib.get("max-size") is not None:
            newTask.max_file_size = int(xmlTask.xpath("proforma:submission-restrictions", namespaces=ns)[0].attrib.get("max-size"))
        else:
            newTask.max_file_size = 1000

        if (xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                          namespaces=ns) and
            xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                          namespaces=ns)[0].text):
            newTask.supported_file_types = xmlTask.xpath("proforma:meta-data/praktomat:allowed-upload-filename-mimetypes",
                                                         namespaces=ns)[0]
        else:
            newTask.supported_file_types = ".*"  # all

    # Files create dict with file objects
    embeddedFileDict = dict()
    for xmlFile in xmlTask.xpath("proforma:files/proforma:file", namespaces=ns):
        if xmlFile.attrib.get("class") == "internal" or xmlFile.attrib.get("class") == "instruction":
            t = tempfile.NamedTemporaryFile(delete=True)
            t.write(xmlFile.text.encode("utf-8"))
            t.flush()
            myT = File(t)
            myT.name = (xmlFile.attrib.get("filename"))  # check! basename? i lost the path..
            embeddedFileDict[xmlFile.attrib.get("id")] = myT  #warum id = int? soll doch string sein

    # Files create dict with file objects for library
    createFileDict = dict()
    for xmlFile in xmlTask.xpath("proforma:files/proforma:file", namespaces=ns):
        if (xmlFile.attrib.get("class") == "library") or (xmlFile.attrib.get("class") == "internal-library"):
            t = tempfile.NamedTemporaryFile(delete=True)
            t.write(xmlFile.text.encode("utf-8"))
            t.flush()
            myT = File(t)
            myT.name = (xmlFile.attrib.get("filename"))  # check! basename? i lost the path..
            createFileDict[xmlFile.attrib.get("id")] = myT  #warum id = int? soll doch string sein


    # check if sysuser is created
    try:
        sysProd = User.objects.get(username=DEFINED_USER)
    except Exception as e:
        newTask.delete()
        response.write("System User (" + DEFINED_USER + ") does not exist: " + str(e))
        return response

    #new model-solution import
    if xmlTask.xpath("proforma:model-solutions/proforma:model-solution", namespaces=ns):
        modelSolutions = xmlTask.xpath("proforma:model-solutions", namespaces=ns)
        # check files>file.id with model-solutions>model-solution>filerefs>fileref>refid
        # jeweils eine model solution
        for modelSolution in xmlTask.xpath("proforma:model-solutions/proforma:model-solution", namespaces=ns):
            try:
                solution = Solution(task=newTask, author=sysProd)
            except Exception as e:
                newTask.delete()
                response.write("Error while importing Solution: " + str(e))
                return response
            if modelSolution.xpath("proforma:filerefs", namespaces=ns):
                for fileRef in modelSolution.filerefs.iterchildren():
                    if fileRef.attrib.get("refid") in embeddedFileDict:
                        solution.save()
                        solutionFile = SolutionFile(solution=solution)
                        solutionFile.file = embeddedFileDict.get(fileRef.attrib.get("refid"))  #TODO check more than one solution
                        solutionFile.save()
                        newTask.model_solution = solution
                    else:
                        newTask.delete()
                        response.write("You reference a model-solution to the files but there is no refid!")
                        return response

    else:
        newTask.delete()
        response.write("No Model Solution attached")
        return response

    if xmlTask.xpath("proforma:meta-data/proforma:title", namespaces=ns):
        newTask.title = xmlTask.xpath("proforma:meta-data/proforma:title", namespaces=ns)[0].text
    else:
        xmlTask.title = "unknown exercise"

    valOrder = 1

    # create library and internal-library with create FileChecker
    valOrder = creatingFileCheckerNoDep(createFileDict, newTask, ns, valOrder, xmlTest=None)



    for xmlTest in xmlTask.tests.iterchildren():
        if xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "anonymity":
            inst = AnonymityChecker.AnonymityChecker.objects.create(task=newTask, order=valOrder)
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-compilation":
            inst = JavaBuilder.JavaBuilder.objects.create(task=newTask,
                                                          order=valOrder,
                                                          _flags="",
                                                          _output_flags="",
                                                          _file_pattern=r"^.*\.[jJ][aA][vV][aA]$"
                                                          )
            # first check if path exist, second if the element is empty
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                              namespaces=ns)[0].text is not None):
                inst._flags = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFlags",
                                            namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerOutputFlags",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerOutputFlags",
                              namespaces=ns)[0].text is not None):
                inst._output_flags = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                   "praktomat:config-CompilerOutputFlags",
                                                   namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                              namespaces=ns)[0].text):
                inst._libs = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerLibs",
                                           namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFilePattern",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-CompilerFilePattern",
                              namespaces=ns)[0].text):
                inst._file_pattern = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                   "praktomat:config-CompilerFilePattern",
                                                   namespaces=ns)[0]
            try:
                inst = testVisibility(inst, xmlTest, ns)
            except Exception as e:
                newTask.delete()
                response.write("Error while parsing xml\r\n" + str(e))
                return response
            inst.save()

        #this one will not used anymore
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-CreateFileChecker":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):

                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = CreateFileChecker.CreateFileChecker.objects.create(task=newTask,
                                                                              order=valOrder,
                                                                              path=""
                                                                              )
                    inst.file = embeddedFileDict.get(fileref.fileref.attrib.get("refid")) #check if the refid is there
                    if dirname(embeddedFileDict.get(fileref.fileref.attrib.get("refid")).name) is not None:
                        inst.path = dirname(embeddedFileDict.get(fileref.fileref.attrib.get("refid")).name)
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save(force_update=True)

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "dejagnu-setup":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = DejaGnu.DejaGnuSetup.objects.create(task=newTask, order=valOrder)
                    inst.test_defs = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save()
                #todo else

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "dejagnu-tester":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = DejaGnu.DejaGnuTester.objects.create(task=newTask, order=valOrder)
                    inst.test_case = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                    if xmlTest.xpath("proforma:title", namespaces=ns)[0] is not None:
                        inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
                    inst = testVisibility(inst, xmlTest, ns)
                    inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "no-type-TextNotChecker":
            fine = True
            inst = TextNotChecker.TextNotChecker.objects.create(task=newTask, order=valOrder)
            if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns)[0].text):
                inst.text = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                                          namespaces=ns)[0].text
            else:
                inst.delete()
                fine = False
                message = "TextNotChecker removed: no config-text"

            if (fine and xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                       "praktomat:config-max_occurrence",
                                       namespaces=ns) and
                    xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                  "praktomat:config-max_occurrence",
                                  namespaces=ns)[0].text):
                inst.max_occ = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                             "praktomat:config-max_occurrence",
                                             namespaces=ns)[0].text
            else:
                inst.delete()
                fine = False
                message = "TextNotChecker removed: no max_occurence"

            if fine:
                inst = testVisibility(inst, xmlTest, ns)
                inst.save()
            else:
                pass

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "textchecker":
            inst = TextChecker.TextChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/proforma:praktomat:config-text",
                              namespaces=ns)[0].text):
                inst.text = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-text",
                                          namespaces=ns)[0].text
                if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
            else:
                inst.delete()
                message = "Textchecker removed: no config-text"

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()
        #setlx with jartest
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "jartest" and \
                xmlTest.xpath("proforma:test-configuration/jartest:jartest[@framework='setlX']", namespaces=ns):

            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = SetlXChecker.SetlXChecker.objects.create(task=newTask, order=valOrder)
                    inst.testFile = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))

            if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]

            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns)[0].text):
                inst.test_description = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                      "praktomat:config-testDescription",
                                                      namespaces=ns)[0].text

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        #checkstyle with jartest todo:version-check check for valid regex
        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "jartest" and \
                xmlTest.xpath("proforma:test-configuration/jartest:jartest[@framework='checkstyle']", namespaces=ns):

            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=newTask, order=valOrder)
                    inst.configuration = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
                if xmlTest.xpath("proforma:test-configuration/jartest:jartest/jartest:parameter",
                                 namespaces=ns) is not None:
                    paraList = list()
                    for parameter in xmlTest.xpath("proforma:test-configuration/jartest:jartest/jartest:parameter", namespaces=ns):
                        paraList.append(str(parameter))
                    regText = '|'.join(paraList)
                    is_valid = reg_check(regText)
                    if is_valid:
                        inst.regText = regText
                    else:
                        message = "no vaild regex for checkstyle: " + str(regText)
                if xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:max-checkstyle-warnings"
                                 , namespaces=ns) is not None:
                    inst.allowedWarnings = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:max-checkstyle-warnings"
                                 , namespaces=ns)[0]


                inst = testVisibility(inst, xmlTest, ns)
                inst.save()

            if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]

            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns)[0].text):
                inst.test_description = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                      "praktomat:config-testDescription",
                                                      namespaces=ns)[0].text

            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "unittest" and \
                xmlTest.xpath("proforma:test-configuration/unit:unittest[@framework='JUnit']", namespaces=ns):
            inst = JUnitChecker.JUnitChecker.objects.create(task=newTask, order=valOrder)

            if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]

            if (xmlTest.xpath("proforma:test-configuration/unit:unittest/unit:main-class",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/unit:unittest/unit:main-class",
                              namespaces=ns)[0].text):
                inst.class_name = xmlTest.xpath("proforma:test-configuration/unit:unittest/unit:main-class",
                                                namespaces=ns)[0].text
            else:
                inst.delete()
                message = "unittest main-class not found. Check your namespace"
                break

            if xmlTest.xpath("proforma:test-configuration/unit:unittest[@framework='JUnit']", namespaces=ns):
                if xmlTest.xpath("proforma:test-configuration/unit:unittest[@framework='JUnit']",
                                 namespaces=ns)[0].attrib.get("version"):
                    version = re.split('\.', xmlTest.xpath("proforma:test-configuration/"
                                                           "unit:unittest[@framework='JUnit']",
                                                           namespaces=ns)[0].attrib.get("version"))

                    if int(version[0]) == 3:
                        inst.junit_version = 'junit3'
                    elif int(version[0]) == 4:
                        inst.junit_version = 'junit4'
                    else:
                        inst.delete()
                        message = "JUnit-Version not known: " + str(version)
                        break

            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-testDescription",
                              namespaces=ns)[0].text):
                inst.test_description = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                      "praktomat:config-testDescription",
                                                      namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/"
                              "proforma:test-meta-data/praktomat:config-testname",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/"
                              "proforma:test-meta-data/praktomat:config-testname",
                              namespaces=ns)[0].text):
                inst.name = xmlTest.xpath("proforma:test-configuration/"
                                          "proforma:test-meta-data/praktomat:config-testname",
                                          namespaces=ns)[0].text
            if xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                valOrder = creatingFileChecker(embeddedFileDict, newTask, ns, valOrder, xmlTest)

            inst.order = valOrder
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "java-checkstyle":
            for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                    inst = CheckStyleChecker.CheckStyleChecker.objects.create(task=newTask, order=valOrder)
                    inst.configuration = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                if xmlTest.xpath("proforma:title", namespaces=ns) is not None:
                    inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0]
                if xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:max-checkstyle-warnings"
                                 , namespaces=ns):
                    inst.allowedWarnings = xmlTest.xpath("proforma:test-configuration/"
                                                         "proforma:test-meta-data/"
                                                         "praktomat:max-checkstyle-warnings", namespaces=ns)[0]
                inst = testVisibility(inst, xmlTest, ns)
                inst.save()

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "python":
            inst = PythonChecker.PythonChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:title", namespaces=ns) and
               xmlTest.xpath("proforma:title", namespaces=ns)[0].text):
                inst.name = xmlTest.xpath("proforma:title", namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-remove-regex", namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-remove-regex",
                              namespaces=ns)[0].text):
                inst.remove = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                            "praktomat:config-remove-regex",
                                             namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-returnHtml",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/praktomat:config-returnHtml",
                              namespaces=ns)[0].text):
                inst.public = str2bool(xmlTest.xpath("proforma:test-configuration/"
                                                     "proforma:test-meta-data/praktomat:config-returnHtml",
                                                     namespaces=ns)[0].text)
            if xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                for fileref in xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                    if embeddedFileDict.get(fileref.fileref.attrib.get("refid")) is not None:
                        inst.doctest = embeddedFileDict.get(fileref.fileref.attrib.get("refid"))
                        inst = testVisibility(inst, xmlTest, ns)
                        inst.save()
                    else:
                        inst.delete()
                        message = "No File for python-checker found"

        elif xmlTest.xpath("proforma:test-type", namespaces=ns)[0] == "RemoteScriptChecker":
            inst = RemoteSQLChecker.RemoteScriptChecker.objects.create(task=newTask, order=valOrder)
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentFilename",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentFilename",
                              namespaces=ns)[0].text):
                inst.solution_file_name = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                        "praktomat:config-studentFilename",
                                                        namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentSolutionFilename",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-studentSolutionFilename",
                              namespaces=ns)[0].text):
                inst.student_solution_file_name = xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                                                                "praktomat:config-studentSolutionFilename",
                                                                namespaces=ns)[0].text
            if (xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-returnHtml",
                              namespaces=ns) and
                xmlTest.xpath("proforma:test-configuration/proforma:test-meta-data/"
                              "praktomat:config-returnHtml",
                              namespaces=ns)[0].text):
                inst.returns_html = str2bool(xmlTest.xpath("proforma:test-configuration/"
                                                           "proforma:test-meta-data/"
                                                           "praktomat:config-returnHtml",
                                                           namespaces=ns)[0].text)
            if xmlTest.xpath("proforma:test-configuration/proforma:filerefs", namespaces=ns):
                valOrder = creatingFileChecker(embeddedFileDict, newTask, ns, valOrder, xmlTest)

            inst.order = valOrder
            inst = testVisibility(inst, xmlTest, ns)
            inst.save()

        else:
            message = "Following Test could not imported\n" + objectify.dump(xmlTest) + "\r\n"

        valOrder += 1
    newTask.save()
    response_data = dict()
    response_data['taskid'] = newTask.id
    response_data['message'] = message
    return response_data # HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt  # disable csrf-cookie
def import_1_01(request):
    response = import_task(request)
    return response

# internal proforma entry point
@csrf_exempt  # disable csrf-cookie
def import_task(request, ):
    """
    :param request: request object for getting POST and GET
    :return: response

    expect xml-file in post-request
    tries to objectify the xml and import it in Praktomat
    """

    logger.debug('import_task called')

    try:
        check_post_request(request)
        filename, uploaded_file = request.FILES.popitem()  # returns list?
        response_data = import_task_internal(filename, uploaded_file[0])
        return HttpResponse(json.dumps(response_data), content_type="application/json")


    except Exception as inst:
        logger.exception(inst)
        print "Exception caught: " + str(type(inst))  # the exception instance
        print "Exception caught: " + str(inst.args)  # arguments stored in .args
        print "Exception caught: " + str(inst)  # __str__ allows args to be printed directly
        callstack = traceback.format_exc()
        print "Exception caught Stack Trace: " + str(callstack)  # __str__ allows args to be printed directly

        #x, y = inst.args
        #print 'x =', x
        #print 'y =', y
        response = HttpResponse()
        response.write("Error while importing task\r\n" + str(inst) + '\r\n' + callstack)


def import_task_internal(filename, task_file):

    logger.debug('import_task_internal called')

    # here is the actual namespace for the version
    format_namespace_v0_9_4 = "urn:proforma:task:v0.9.4"
    format_namespace_v1_0_1 = "urn:proforma:task:v1.0.1"
    format_namespace_v2_0 = "urn:proforma:v2.0"

    rxcoding = re.compile(r"encoding=\"(?P<enc>[\w.-]+)")

    dict_zip_files = None
    if filename[-3:].upper() == 'ZIP':
        task_xml, dict_zip_files = extract_zip_with_xml_and_zip_dict(uploaded_file=task_file)
    else:
        task_xml = task_file[0].read()  # todo check name

    encoding = rxcoding.search(task_xml, re.IGNORECASE)
    if (encoding != 'UFT-8' or encoding != 'utf-8') and encoding is not None:
        task_xml = task_xml.decode(encoding.group('enc')).encode('utf-8')
    xml_object = objectify.fromstring(task_xml)

    #xml_task = xml_object
    # TODO check against schema

    # check Namespace
    if format_namespace_v0_9_4 in xml_object.nsmap.values():
        logger.debug('handle 0.9.4 task')
        response_data = importTaskObjectV2(task_xml, dict_zip_files)  # request,)
    elif format_namespace_v1_0_1 in xml_object.nsmap.values():
        logger.debug('handle 1.0.1 task')
        response_data = itask(task_xml, dict_zip_files)
    elif format_namespace_v2_0 in xml_object.nsmap.values():
        logger.debug('handle 2.0 task')
        response_data = import_task_v2(task_xml, dict_zip_files)
    else:
        raise Exception("The Exercise could not be imported!\r\nOnly support for the following namespaces: " +
                       format_namespace_v0_9_4 + "\r\n" +
                       format_namespace_v1_0_1 + "\r\n" +
                       format_namespace_v2_0)

    return response_data


@csrf_exempt  # NOTE: für Marcel danach remove;)
def test_post(request, ):
    response = HttpResponse()

    if not (request.method == "POST"):
        response.write("No Post-Request")
    else:
        postMessages = request.POST
        for key, value in postMessages.iteritems():
            response.write("Key: " + str(key) + " ,Value: " + str(value) + "\r\n")
        try:
            if not (request.FILES is None):
                response.write("List of Files: \r\n")
                for key, value in request.FILES.iteritems():
                    response.write("Key: " + str(key) + " ,Value: " + str(value) + "\r\n")
                    response.write("Content of: " + str(key) + "\r\n")
                    response.write(request.FILES[key].read() + "\r\n")
            else:
                response.write("\r\n\r\n No Files Attached")
        except Exception:
            response.write("\r\n\r\n Exception!: " + str(Exception))
    return response



