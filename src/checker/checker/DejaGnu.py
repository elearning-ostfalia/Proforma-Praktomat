# -*- coding: utf-8 -*-

"""
DejaGnu Tests.
"""

import os, sys
from os.path import dirname, join
import string
import re

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from checker.models import Checker, CheckerFileField, CheckerResult, execute_arglist, truncated_log
from checker.compiler.Builder import Builder
from utilities import encoding
from utilities.file_operations import *

# Stuff to highlight in output
RXFAIL = re.compile(r"^(.*)(FAIL|ERROR|Abort|Exception |your program crashed|cpu time limit exceeded|"
                        "ABBRUCH DURCH ZEITUEBERSCHREITUNG| # of unexpected failures.*[0-9]+)(.*)$",	re.MULTILINE)
RXPASS = re.compile(r"^(.*)(PASS)(.*)$", re.MULTILINE)
RXRUN_BY = re.compile(r"Run By .* on ")

# Stuff to remove from output
RXREMOVE = re.compile(r"(Schedule of variations:.*interface file.)|(Running \./[ -z]*/[a-z]*\.exp \.\.\.)", re.DOTALL)

class DejaGnu:
    """ Common superclass for all DejaGnu-related stuff. """

    # Directories
    def testsuite_dir(self, env):
        return os.path.join(env.tmpdir(), "testsuite")

    def config_dir(self, env):
        return os.path.join(self.testsuite_dir(env), "config")

    def lib_dir(self, env):
        return os.path.join(self.testsuite_dir(env), "lib")

    def tests_dir(self, env):
        return os.path.join(self.testsuite_dir(env), env.program() + ".tests")

    def setup_dirs(self, env):
        makedirs(self.testsuite_dir(env))
        makedirs(self.config_dir(env))
        makedirs(self.lib_dir(env))
        makedirs(self.tests_dir(env))



class DejaGnuTester(Checker, DejaGnu):
    """ Run a test case on the program.  Requires a previous `DejaGnuSetup'. """

    name = models.CharField(max_length=100, help_text=_("The name of the Test"))
    test_case = CheckerFileField(help_text=_(u"In den folgenden DejaGnu-Testfällen werden typischerweise Funktionen aufgerufen, die beim vorherigen Schritt <EM>Tests einrichten</EM> definiert wurden.	 Siehe	auch den Abschnitt <EM>How to write a test case</EM> im <A TARGET=\"_blank\" HREF=\"http://www.gnu.org/manual/dejagnu/\">DejaGnu-Handbuch</A>."))

    def __unicode__(self):
        return self.name

    def title(self):
        return self.name

    @staticmethod
    def description():
        return u"Diese Prüfung ist bestanden, wenn alle Testfälle zum erwarteten Ergebnis führten."

    def requires(self):
        return [ DejaGnuSetup ]

    # Return 1 if the output is ok
    def output_ok(self, output):
        return (RXFAIL.search(output) == None and
                string.find(output, "runtest completed") >= 0 and
                string.find(output, "non-expected failures") < 0 and
                string.find(output, "unexpected failures") < 0)

    def htmlize_output(self, log):
        # Always kill the author's name from the log
        log = re.sub(RXRUN_BY, "Run By " + settings.SITE_NAME + " on ", log)

        # Clean the output
        log = re.sub(RXREMOVE, "", log)

        log = re.sub(re.escape(settings.JVM_SECURE_DEJA),os.path.basename(settings.JVM_SECURE_DEJA),log)

        # HTMLize it all
        log = escape(log)

        # Every line that contains a passed message is to be enhanced.
        log = re.sub(RXPASS, r'\1 <B class="passed"> \2 </B> \3', log)
        # Every line that contains a failure message is to be enhanced.
        return "<TT><PRE>" + re.sub(RXFAIL, r'\1 <B class="error"> \2 </B> \3', log) + "</PRE></TT>"

    # Run tests.  Return a CheckerResult.
    def run(self, env):

        # Save public test cases in `tests.exp'
        tests_exp = os.path.join(self.tests_dir(env), "tests.exp")
        test_cases = string.replace(encoding.get_unicode(self.test_case.read()), u"PROGRAM", env.program())
        create_file(tests_exp,test_cases)

        testsuite = self.testsuite_dir(env)
        program_name = env.program()

        if " " in program_name:
            result = self.result()
            result.set_log("<pre><b class=\"fail\">Error</b>: Path to the main() - source file contains spaces.\n\nFor Java .zip submittions, the directory hierarchy of the .zip file must excactly match the package structure.\nThe default package must correspond to the .zip root directory.</pre>")
            result.set_passed(False)
            return result

        cmd = [settings.DEJAGNU_RUNTEST, "--tool", program_name, "tests.exp"]

        environ = {}
        environ['JAVA'] = settings.JVM
        environ['POLICY'] = join(join(dirname(dirname(__file__)),"scripts"),"praktomat.policy")
        environ['USER'] = env.user().get_full_name().encode(sys.getdefaultencoding(), 'ignore')
        environ['HOME'] = testsuite
        environ['UPLOAD_ROOT'] = settings.UPLOAD_ROOT
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')


        #[output, error, exitcode] = execute_arglist(cmd, testsuite, environment_variables=environ)
        #output = encoding.get_unicode(output)
        [output, error, exitcode, timed_out] = execute_arglist(cmd, testsuite,
                                                               environment_variables=environ,
                                                               use_default_user_configuration=True,
                                                               timeout=settings.TEST_TIMEOUT,
                                                               fileseeklimit=settings.TEST_MAXFILESIZE,
                                                               extradirs=[env.tmpdir(), script_dir])

        output = encoding.get_unicode(output)

        try:
            summary = encoding.get_unicode(open(os.path.join(testsuite, program_name + ".sum")).read())
            log		= encoding.get_unicode(open(os.path.join(testsuite, program_name + ".log")).read())
        except:
            summary = ""
            log		= ""

        complete_output = output + log

        result = self.create_result(env)
        result.set_log(complete_output, timed_out=timed_out)
        result.set_passed(not exitcode and not timed_out and self.output_ok(complete_output))

        return result


# A template for test cases.
DEFAULT_TEST_CASES = """# `tests.exp' template
# Insert test cases in the format
# PROGRAM_test "[input]" "[expected_output]"
"""

class DejaGnuSetup(Checker, DejaGnu):

    test_defs = CheckerFileField(help_text=_(u"Das Setup benutzt den <A HREF=\"http://www.gnu.org/software/dejagnu/dejagnu.html\">DejaGnu-Testrahmen</A>, um die Programme zu testen. Die in dieser Datei enthaltenen Definitionen gelten für alle Testfälle dieser Aufgabe. Sie werden beim Testen in die DejaGnu-Datei <TT>default.exp</TT> geschrieben. (Vergl. hierzuden Abschnitt <EM>Target dependent procedures</EM> im	<A HREF=\"http://www.gnu.org/manual/dejagnu/\" TARGET=\"_blank\">DejaGnu-Handbuch</A>.) Die Variablen PROGRAM und JAVA werden mit dem Programmnamen bzw. dem Pfad zur Java-Runtime ersetzt."))

    def title(self):
        return "Tests einrichten"

    @staticmethod
    def description():
        return u"Dies ist keine wirkliche Prüfung.  Sie dient nur dazu, den nachfolgenden Tests Definitionen zur Verfügung zu stellen. Diese 'Prüfung' wird immer bestanden."

    def requires(self):
        return [ Builder ]

    # Set up tests.
    def run(self, env):
        self.setup_dirs(env)
        create_file(os.path.join(self.lib_dir(env), env.program() + ".exp"), u"")
        defs = string.replace(encoding.get_unicode(self.test_defs.read()), "PROGRAM", env.program())
#		defs = string.replace(defs, "JAVA", join(join(dirname(dirname(__file__)),"scripts"),"java"))
        defs = string.replace(defs, "JAVA", settings.JVM_SECURE_DEJA)
        create_file(os.path.join(self.config_dir(env), "default.exp"), defs)

        return self.result()

from checker.admin import	CheckerInline, AlwaysChangedModelForm


class SetupForm(AlwaysChangedModelForm):
    def __init__(self, **args):
        """ override public and required """
        super(SetupForm, self).__init__(**args)
        self.fields["public"].initial = False
        self.fields["required"].initial = False


class DejaGnuSetupInline(CheckerInline):
    form = SetupForm
    model = DejaGnuSetup
    #exclude = ["public", "required"]


class DejaGnuTesterInline(CheckerInline):
    model = DejaGnuTester

