# -*- coding: utf-8 -*-

"""
TextNotChecker.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from checker.models import Checker, CheckerResult


class TextNotChecker(Checker):
    """ Checks if the specified text is included in a submitted file """

    text = models.TextField(help_text=_("The text you search in the text"))
    max_occ = models.IntegerField(default=1, help_text=_("The allowed max. occurrence of text in the \
                                                          source. 0 means the word is not allowed"))

    def title(self):
        """Returns the title for this checker category."""
        return "Text Not Checker"

    @staticmethod
    def description():
        """ Returns a description for this Checker. """
        return u"Diese Prüfung ist bestanden, wenn der eingegebene Text nicht in einer Lösung gefunden wird."

    def run(self, env):
        """ Checks if the specified text is included in a submitted file """
        result = CheckerResult(checker=self)

        lines = []
        occurances = []
        passed = 1
        log = ""
        lineNum = 1
        inComment = False

        # search the sources
        for (name, content) in env.sources():
            lines = self._getLines(content)
            lineNum = 1
            for line in lines:
                if not inComment:
                    if line.find('/*') >= 0:
                        parts = line.split('/*')
                        if parts[0].find(self.text) >= 0:
                            occurances.append((name, lineNum))
                        inComment = True

                if not inComment:
                    parts = line.split('//')
                    if parts[0].find(self.text) >= 0:
                        occurances.append((name, lineNum))
                else:
                    if line.find('*/') > 0:
                        parts = line.split('*/')
                        if len(parts) > 1:
                            if parts[1].find(self.text) >= 0:
                                occurances.append((name, lineNum))

                        inComment = False

                lineNum += 1

        # Print Results:
        if len(occurances) > self.max_occ:
            passed = 0
            if len(occurances) == 0:
                log = self.text + u" kommt nicht in Ihrer Lösung vor!"
            else:
                log = self.text + ' darf maximal nur %d mal in Ihrer Einreichung vorkommen.<br />' % self.max_occ
                log += 'Es kommt jedoch %d mal, an folgenden Stellen vor:<br />' % len(occurances)
                for (name, num) in occurances:
                    log += name + " Zeile: " + str(num) + "<br />"
        else:
            if len(occurances) == 0:
                log = self.text + u" kommt nicht in Ihrer Lösung vor"
            else:

                log = self.text + " kommt an folgenden Stellen vor:<br>"
                for (name, num) in occurances:
                    log += name + " Zeile: " + str(num) + "<br>"

        result.set_log(log)
        result.set_passed(passed)

        return result

    def _getLines(self, text):
        """ Returns a list of lines (as strings) from text """
        lines = text.split("\n")
        return lines


from checker.admin import CheckerInline


class TextCheckerInline(CheckerInline):
    model = TextNotChecker
