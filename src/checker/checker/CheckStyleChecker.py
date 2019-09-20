# -*- coding: utf-8 -*-

import re
from pipes import quote

from django.db import models
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from checker.admin import CheckerInline

from checker.models import Checker, CheckerResult, CheckerFileField, execute_arglist, truncated_log
from utilities.file_operations import *


class CheckStyleChecker(Checker):

    name = models.CharField(max_length=100, default="CheckStyle", help_text=_("Name to be displayed "
                                                                              "on the solution detail page."))
    configuration = CheckerFileField(help_text=_("XML configuration of CheckStyle. "
                                                 "See http://checkstyle.sourceforge.net/"))
    allowedWarnings = models.IntegerField(default=0, help_text=_("How many warnings are allowed before the checker "
                                                                 "is not passed"))
    allowedErrors = models.IntegerField(default=0, help_text=_("How many errors are allowed before the checker "
                                                                 "is not passed"))
    regText = models.CharField(default=".*", max_length=5000,
                               help_text=_("Regular expression describing files to be analysed."))

    CHECKSTYLE_CHOICES = (
        (u'check-6.2', u'Checkstyle 6.2 all'),
        (u'check-7.6', u'Checkstyle 7.6 all'),
        (u'check-5.4', u'Checkstyle 5.4 all'),
        (u'check-8.23', u'Checkstyle 8.23 all'),
    )
    check_version = models.CharField(max_length=16, choices=CHECKSTYLE_CHOICES, default="check-8.23")

    def title(self):
        """ Returns the title for this checker category. """
        return self.name

    @staticmethod
    def description():
        """ Returns a description for this Checker. """
        return u"Runs checkstyle (http://checkstyle.sourceforge.net/)."

    def change_reg(self):
        try:
            re.compile(self.regText)
            is_valid = True
        except re.error:
            is_valid = False
        return is_valid

    def run(self, env):

        # Save save check configuration
        config_path = os.path.join(env.tmpdir(), "checks.xml")
        copy_file(self.configuration.path, config_path)
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')


        # check regText
        is_valid = self.change_reg()

        files2check = list()
        if is_valid:
            files = [name for (name, content) in env.sources()]
            for element in files:
                match = re.search(self.regText, element)
                if match:
                    files2check.append(match.group())

        # Run the tests
        # args = [settings.JVM, "-cp", settings.CHECKSTYLEALLJAR, "-Dbasedir=.", "com.puppycrawl.tools.checkstyle.Main",
        #        "-c", "checks.xml"] + [quote(name) for (name, content) in env.sources()]

        if not files2check:
            result = CheckerResult(checker=self)
            if not is_valid:
                result.set_log('No files where checked. The regular expression is not valid! Contact your Operator!')
            else:
                result.set_log('No files where checked.')
            result.set_passed(False)
            return result

        cmd = [settings.JVM, "-cp", settings.CHECKSTYLE_VER[self.check_version], "-Dbasedir=.",
               "com.puppycrawl.tools.checkstyle.Main",
               "-c", "checks.xml"] + [quote(element) for element in files2check]
        # (output, error, exitcode) = execute(args, env.tmpdir())
        [output, error, exitcode, timed_out] = execute_arglist(cmd, env.tmpdir(),
                                                               use_default_user_configuration=True,
                                                               timeout=settings.TEST_TIMEOUT,
                                                               fileseeklimit=settings.TEST_MAXFILESIZE,
                                                               extradirs=[script_dir])

        # Remove Praktomat-Path-Prefixes from result:
        output = re.sub(r"^"+re.escape(env.tmpdir())+"/+", "", output, flags=re.MULTILINE)

        result = CheckerResult(checker=self)
        (output, truncated) = truncated_log(output)

        # warningList = re.findall("warning", output, re.M)
        # warningCounter = len(warningList)
        lines = 0
        warning_in_line = 0 # is a line a warning? or must there a warn?

        warning = str.count(output, 'warning:')
        error = str.count(output, 'error:')

        result.set_passed(not exitcode and not timed_out and warning <= self.allowedWarnings
                          and error <= self.allowedErrors and not truncated)

        output = '<pre>' + '\n\n======== Test Results ======\n\n</pre><br/><pre>' + \
                 escape(output) + '</pre>'
        result.set_log(output, timed_out=timed_out, truncated=truncated)
        return result


class CheckStyleCheckerInline(CheckerInline):
    model = CheckStyleChecker
