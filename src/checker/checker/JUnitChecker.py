# -*- coding: utf-8 -*-

import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from checker.models import Checker, CheckerResult, execute_arglist, truncated_log
from checker.admin import CheckerInline
from utilities.file_operations import *
from solutions.models import Solution

from checker.compiler.JavaBuilder import JavaBuilder

RXFAIL = re.compile(r"^(.*)(FAILURES!!!|your program crashed|cpu time limit exceeded|"
                    r"ABBRUCH DURCH ZEITUEBERSCHREITUNG|Could not find class|Killed|"
                    r"failures|Class not found|Exception in thread)(.*)$", re.MULTILINE)


class JUnitChecker(Checker):
    """ New Checker for JUnit3 Unittests. """

    # Add fields to configure checker instances. You can use any of the Django fields. (See online documentation)
    # The fields created, task, public, required and always will be inherited from the abstract base class Checker
    class_name = models.CharField(max_length=100, help_text=_("The fully qualified name of the Testcase class"))
    test_description = models.TextField(help_text=_("Description of the Testcase. To be displayed on Checker Results"
                                                    " page when checker is  unfolded."))
    name = models.CharField(max_length=100, help_text=_("Name of the Testcase. To be displayed as title"
                                                        " on Checker Results page"))

    JUNIT_CHOICES = (
        (u'junit4', u'JUnit 4'),
        (u'junit4.12', u'JUnit 4.12'),
        (u'junit4.12-gruendel', u'JUnit 4.12 with Gruendel Addon'),
        (u'junit3', u'JUnit 3'),
    )
    junit_version = models.CharField(max_length=100, choices=JUNIT_CHOICES, default="junit4.12")

    def runner(self):
        return {'junit4' : 'org.junit.runner.JUnitCore',
                'junit4.12' : 'org.junit.runner.JUnitCore',
                'junit4.12-gruendel' : 'org.junit.runner.JUnitCore',
                'junit3' : 'junit.textui.TestRunner'}[self.junit_version]

    def title(self):
        return u"JUnit Test: " + self.name

    @staticmethod
    def description():
        return u"This Checker runs a JUnit Testcases existing in the sandbox. " \
               u"You may want to use CreateFile Checker to create JUnit .java files in the " \
               u"sandbox before running the JavaBuilder."

    def output_ok(self, output):
        return (RXFAIL.search(output) == None)

    def run(self, env):

        java_builder = JavaBuilder(_flags="", _libs=self.junit_version,
                                   _file_pattern=r"^.*\.[jJ][aA][vV][aA]$",
                                   _output_flags="")

        build_result = java_builder.run(env)

        if not build_result.passed:
            result = CheckerResult(checker=self)
            result.set_passed(False)
            result.set_log('<pre>' + escape(self.test_description) +
                           '\n\n======== Test Results ======\n\n</pre><br/>\n' +
                           unicode(build_result.log))
            return result

        environ = dict()

        environ['UPLOAD_ROOT'] = settings.UPLOAD_ROOT
        environ['JAVA'] = settings.JVM
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        environ['POLICY'] = os.path.join(script_dir, "junit.policy")

        cmd = [settings.JVM_SECURE, "-classpath", settings.JAVA_LIBS[self.junit_version] + ":.",
               self.runner(), self.class_name]
        [output, error, exitcode, timed_out] = execute_arglist(cmd, env.tmpdir(),
                                                               environment_variables=environ,
                                                               use_default_user_configuration=True,
                                                               timeout=settings.TEST_TIMEOUT,
                                                               fileseeklimit=settings.TEST_MAXFILESIZE,
                                                               extradirs=[script_dir])

        result = CheckerResult(checker=self)
        (output, truncated) = truncated_log(output)
        output = '<pre>' + escape(self.test_description) + '\n\n======== Test Results ======\n\n</pre><br/><pre>' + \
                 escape(output) + '</pre>'
        result.set_log(output, timed_out=timed_out, truncated=truncated)
        result.set_passed(not exitcode and not timed_out and self.output_ok(output) and not truncated)

        return result

#class JUnitCheckerForm(AlwaysChangedModelForm):
#	def __init__(self, **args):
#		""" override default values for the model fields """
#		super(JUnitCheckerForm, self).__init__(**args)
#		self.fields["_flags"].initial = ""
#		self.fields["_output_flags"].initial = ""
#		self.fields["_libs"].initial = "junit3"
#		self.fields["_file_pattern"].initial = r"^.*\.[jJ][aA][vV][aA]$"

class JavaBuilderInline(CheckerInline):
    """ This Class defines how the the the checker is represented as inline in the task admin page. """
    model = JUnitChecker
#	form = JUnitCheckerForm

# A more advanced example: By overwriting the form of the checkerinline the initial values of the inherited atributes can be overritten.
# An other example would be to validate the inputfields in the form. (See Django documentation)
#class ExampleForm(AlwaysChangedModelForm):
    #def __init__(self, **args):
        #""" override public and required """
        #super(ExampleForm, self).__init__(**args)
        #self.fields["public"].initial = False
        #self.fields["required"].initial = False

#class ExampleCheckerInline(CheckerInline):
    #model = ExampleChecker
    #form = ExampleForm


