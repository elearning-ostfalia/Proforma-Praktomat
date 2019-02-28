# -*- coding: utf-8 -*-

import os
import re
from urllib2 import urlopen

from django.db import models
from django.utils.translation import ugettext_lazy as _
import time
from checker.models import Checker, CheckerFileField, CheckerResult, execute
from utilities.file_operations import *
from checker.admin import CheckerInline


class RemoteScriptChecker(Checker):
    name = models.CharField(max_length=100, default="External Remote Checker",
                            help_text=_("Name to be displayed on the solution detail page."))
    # script_filter = CheckerFileField(
    #     help_text=_("The shell script whose output for the given input file is compared to the given output file."))
    # remove = models.CharField(max_length=5000, blank=True,
    #                           help_text=_("Regular expression describing passages to be removed from the output."))
    solution_file = CheckerFileField(
        help_text=_("The solution file which contains the master solution."))
    solution_file_name = models.CharField(max_length=500, blank=True, help_text=_("What the file will be \
                                          named in the sandbox. If empty, we try to guess the right filename!"))
    student_solution_file_name = models.CharField(max_length=500, help_text=_("How is the submission_name\
                                                  by the student?"))
    returns_html = models.BooleanField(default=False, help_text=_(
        "If the script doesn't return HTML it will be enclosed in < pre > tags."))

    ENDOFCONTENT = -9
    STARTOFCONTENT = 16

    def title(self):
        """ Returns the title for this checker category. """
        return self.name

    @staticmethod
    def description():
        """ Returns a description for this Checker. """
        return u"Diese Prüfung wird bestanden, wenn das externe Programm keinen Fehlercode liefert."

    def submission_check(self, submit):
        sFilter = ScriptFilter()
        removedComments = sFilter.remove_comments(submit)
        removedHTML = sFilter.remove_HTML_code(removedComments)
        return removedHTML

    # Method for reading and preparing file submit.txt from LON-CAPA
    # @param submitFromLC:  submitted File
    # Submit.txt liegt im Verzeichnis des Scripts
    def get_submit(self, submit):
        try:
            submitFile = open(str(submit))
        except Exception:
            raise Exception('Zugriff auf submit.txt fehlgeschlagen')

        submitLines = str(submitFile.read())
        newSubmitLines = self.submission_check(submitLines)
        checkedSubmit = re.sub(r";[\s*;+]+", ";", newSubmitLines)
        splittedSubmit = self.split_submit(checkedSubmit)
        submitFile.close()
        return splittedSubmit

    # Method for reading an preparing solution file
    # @param: provided solution.txt
    def get_solution(self, solution):
        try:
            solutionFile = open(str(solution))
        except Exception:
            raise Exception('Zugriff auf Musterlösungs-Datei fehlgeschlagen')

        solution = str(solutionFile.read())
        splittedSolution = self.split_solution(solution)
        solutionFile.close()
        return splittedSolution

    # Method for splitting submit.txt
    # @param submit: submit.txt from LON-CAPA
    def split_submit(self, submit):
        newSubmit = []
        splittedSubmit = submit.split(";")
        for i in range(0, len(splittedSubmit) - 1):
            newSubmitLine = self.reduce_whitespaces(splittedSubmit[i])
            newSubmit.append(newSubmitLine + ";")
        return newSubmit

    # Method for splitting solution file
    # @param solution: given solution file
    def split_solution(self, solution):
        newSolution = []
        splittedSolution = solution.split(";")
        for i in range(0, len(splittedSolution) - 1):
            newSolutionline = self.reduce_whitespaces(splittedSolution[i])
            newSolution.append(str(newSolutionline) + str(";"))
        return newSolution

    # Method for reducing whitespaces in a String
    # @param statement: Statement to be reduced
    def reduce_whitespaces(self, statement):
        if statement[0].isspace():
            newStatement = statement[1:]
            newStatement = newStatement.lstrip()
        else:
            newStatement = statement
        newStatement2 = re.sub(r";\s*;+\s*", ";", newStatement)
        reducedStatement = re.sub("\s+", "+", newStatement2)
        return reducedStatement

    # Method for sending a single SQL-Statement to the interpreter
    # @param SQLStatement: SQL-statement to be sent to Interpreter
    def send_statement(self, SQLStatement):  # TODO url must be changeable
        url = str("http://db.vfh.fh-wolfenbuettel.de/sql/dbmwall.php?query2=" + SQLStatement)
        try:
            response = urlopen(url)
            response_content = response.readlines()
        except Exception, e:
            raise Exception('External Grader is not reachable %s' % url)

        return response_content

    # Method for retrieving HTML-code from the response Website to statement of submit.txt
    # @param statement: Statement from submit.txt to be sent to Interpreter
    def get_response_to_statement(self, statement):
        try:
            responseToStatement = self.send_statement(statement)
        except Exception, e:
            raise Exception, e
        return responseToStatement

    # Method for comparing responses to statements from submit.txt and solution
    # @param responseSubmit  : response to SL
    # @param responseSolution: response to ML
    def compare_response(self, submitString, solutionString, result_obj):
        evaluationString = []
        hint = "hint"
        errorCounter = 0
        missingStatement = "fehlendes Statement"
        additionalStatement = "unbenötigtes Statement"
        difference = len(solutionString) - len(submitString)
        if difference > 0:
            for j in range(0, difference):
                submitString.append(missingStatement)
        if difference < 0:
            for j in range(difference, 0):
                solutionString.append(missingStatement)
        for i in range(0, len(solutionString)):
            equationLeftSide = str(submitString[i].capitalize())
            incorrectSyntax1 = re.findall("fehler", submitString[i], re.I)
            incorrectSyntax2 = re.findall("nicht unterstützt!", submitString[i], re.I)
            equationRightSide = str(solutionString[i].capitalize())
            evaluation = bool(equationLeftSide == equationRightSide)
            syntaxCheck = (not incorrectSyntax1) and (not incorrectSyntax2)
            if not evaluation:
                result_obj.set_passed(False)  # Task has an error
                hint = "Sie haben ein semantisch falsches Statement eingereicht."
                if missingStatement in submitString[i]:
                    hint = missingStatement
                elif missingStatement in solutionString[i]:
                    hint = additionalStatement
                elif syntaxCheck:
                    hint = self.get_eval_hint(solutionString[i])
                elif not syntaxCheck:
                    hint = self.get_error_hint(solutionString[i])
                errorCounter += 1
            evaluationString.append(self.evaluate(bool(evaluation), hint, errorCounter))
        return evaluationString

    # Evaluation to LC
    # @param evaluation: Evaluated SQL-Interpreter response
    def evaluate(self, evaluation, hint, errorCounter):
        evaluate = bool(evaluation)
        if not evaluate:
            if errorCounter <= 1:
                evaluation = "Die Einreichung ist nicht richtig! " + str(hint)
            else:
                evaluation = "Die Einreichung ist nicht richtig!"
        else:
            evaluation = "Die Einreichung ist richtig!"
        return evaluation


    # Feedback to LON-CAPA for logged commands
    # @param statement: submitted SQL-Statement
    def add_to_log(self, statement, log):
        log.append(str(re.sub("\++", " ", statement + "\n")))
        return log

    def get_statement_type(self, statement):
        if re.findall("not properly ended", statement, re.I):
            return "semikolon"
        if re.findall("create", statement, re.I):
            return "create"
        if re.findall("insert", statement, re.I):
            return "insert"
        if re.findall("select", statement, re.I):
            return "select"
        else:
            return "unbekannt"

    def find_created_tables(self, solution):
        createdtables = []
        for statement in solution:
            if re.findall("create", statement, re.I):
                deletionStatement = re.sub("\+", " ", statement)
                newDeletionStatement = re.split("\s", deletionStatement)
                createdtables.append(newDeletionStatement[2])
        return createdtables

    def delete_created_tables(self, createdTables):
        for statement in createdTables:
            try:
                self.send_statement("DROP+TABLE+" + statement + ";")
            except Exception, e:
                raise Exception, e

    # get hint for syntactically correct but semanticly false statements
    # @param statement: false evaluated statement
    def get_eval_hint(self, statement):

        if self.get_statement_type(statement) == "insert":
            return "Fehler im \"INSERT\"-Statement! Stellen Sie sicher, \
                    dass die korrekten Datensätze eingefügt werden!"
        elif self.get_statement_type(statement) == "create":
            return "Fehler im \"CREATE\"-Statement! Achten Sie auf die Reihenfolge der Attribute \
                    und sehen Sie sich Ihre Constraints nochmals genauer an!"
        elif self.get_statement_type(statement) == "select":
            return "Fehler im \"SELECT\"-Statement! Führen Sie sich die Struktur \
                    der gesuchten Ergebnis-Tabelle nochmals genauer vor Augen"
        return "Fehler"

    # get hint for syntactically false statement
    # @param statement: false evaluated statement
    def get_error_hint(self, statement):
        if self.get_statement_type(statement) == "create":
            return "Syntax-Fehler im \"CREATE\"-Statement!"
        elif self.get_statement_type(statement) == "insert":
            return "Syntax-Fehler im \"INSERT\"-Statement!"
        elif self.get_statement_type(statement) == "select":
            return "Syntax-Fehler im \"SELECT\"-Statement!"
        elif self.get_statement_type(statement) == "unbekannt":
            return "unbekannt"
        elif re.findall("not properly ended", statement, re.I):
            return "Fehler: Anweisung nicht mit ; abgeschlossen!"
        return "Syntax Fehler"

    # create webLock-table or enqueue
    def enqueue(self):
        queue = "CREATE TABLE mk_webLock(id int);"
        for i in range(11):
            queueResponse = self.get_response_to_statement(queue)
            if not (re.findall("name is already used by an existing object", str(queueResponse), re.I)):
                return
            time.sleep(1)
            if i == 10:
                raise Exception("Timeout! Versuchen Sie es später erneut!")
        return

    # delete webLock-table
    def dequeue(self):
        dequeue = "DROP TABLE mk_webLock;"
        for i in range(6):
            dequeueResponse = self.get_response_to_statement(dequeue)
            if not (re.findall("Oracle Fehler: ORA-", str(dequeueResponse), re.I)):
                return
            time.sleep(1)
            if i == 5:
                raise Exception("Löschen von Web-Lock Tabelle konnte nicht durchgeführt werden!")

    def run(self, env):
        """ Runs tests in a special environment. Here's the actual work.
        This runs the check in the environment ENV, returning a CheckerResult. """

        # check: only one submission file allowed
        result = CheckerResult(checker=self)
        if len(env.sources()) > 1:
            result.set_log("Sie dürfen nur eine Datei angegeben!")
            result.set_passed(False)
            return result

        # copy solution file in directory
        filename = self.solution_file_name if self.solution_file_name else self.solution_file.path
        path = os.path.join(env.tmpdir(), os.path.basename(filename))
        copy_file(self.solution_file.path, path)

        try:
            self.enqueue()
        except Exception, e:
            result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
            result.set_passed(False)
            #self.dequeue() not necessary no db connection
            return result

        # defines
        solutionString = []
        submitString = []
        log = []
        # self.main("./submit4.txt", "./solution4.txt") #
        #main included
        # Zugriff auf solution
        for (name, content) in env.sources():  # TODO for for one file is too much
            try:
                submittedStatements = self.get_submit(os.path.join(env.tmpdir(), os.path.basename(name)))
            except Exception, e:
                result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
                result.set_passed(False)
                #  self.dequeue() not necessary no db connection
                return result

        try:
            solutionStatements = self.get_solution(path)
        except Exception:
            result.set_log("Zugriff auf Musterlösungs-Datei fehlgeschlagen")
            result.set_passed(False)
            try:
                self.dequeue()
            except Exception, e:
                result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
                result.set_passed(False)
                return result
            return result

        createdTables = self.find_created_tables(solutionStatements)
        try:
            self.delete_created_tables(createdTables[::-1])
        except Exception, e:
            result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
            result.set_passed(False)
            # self.dequeue() not necessary no db connection
            return result
        for statement in solutionStatements:
            try:
                responseToSolution = self.get_response_to_statement(statement)
            except Exception, e:
                result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
                result.set_passed(False)
                self.dequeue()
                return result
            solutionStringAppend = str(responseToSolution[self.STARTOFCONTENT:self.ENDOFCONTENT]).capitalize()
            solutionString.append(solutionStringAppend)
        self.delete_created_tables(createdTables[::-1])
        for statement in submittedStatements:
            try:
                responseToSubmit = self.get_response_to_statement(statement)
            except Exception, e:
                result.set_log("Es ist ein Fehler aufgetreten: %s" % e.message)
                result.set_passed(False)
                self.dequeue()
                return result

            log = self.add_to_log(statement, log)
            submitStringAppend = str(responseToSubmit[self.STARTOFCONTENT:self.ENDOFCONTENT]).capitalize()
            submitString.append(submitStringAppend)
        self.delete_created_tables(createdTables[::-1])
        evaluationString = self.compare_response(submitString, solutionString, result)
        result.set_log('<br />'.join(evaluationString))
        self.dequeue()

        return result


class ScriptFilter:
    def remove_HTML_code(self, fileContent):
        removedHTML = re.sub(r"<\S+?>", "", fileContent, re.I)
        return removedHTML

    def remove_comments(self, fileContent):
        removedComments = re.sub(r"--.*\n", "", fileContent, re.I)
        return removedComments

    def remove_unknown_symbols(self, fileContent):
        removedSymbols = fileContent
        return removedSymbols

    def main(self, file_name):
        myfile = open(str(file_name))
        fileContent = myfile.read()

        removedHTMLContent = self.remove_HTML_code(fileContent)
        for line in removedHTMLContent:
            print("nachher: " + line)
        removedComments = self.remove_comments(removedHTMLContent)
        for line in removedComments:
            print("nachher2: " + line)
        removedSymbols = self.remove_unknown_symbols(removedComments)


sFilter = ScriptFilter()


class RemoteScriptCheckerInline(CheckerInline):
    model = RemoteScriptChecker
