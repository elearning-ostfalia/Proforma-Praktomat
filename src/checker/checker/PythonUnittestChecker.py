
# -*- coding: utf-8 -*-
import os.path
import re
import traceback

from lxml import etree

from checker.basemodels import CheckerResult, truncated_log, CheckerEnvironment
from utilities.safeexec import execute_arglist
from utilities.file_operations import *
from checker.checker.ProFormAChecker import ProFormAChecker
from django.conf import settings
from proforma import python_sandbox
from utilities.safeexec import execute_command

import logging

logger = logging.getLogger(__name__)

class PythonUnittestChecker(ProFormAChecker):
    """ New Checker for Python Unittests. """
#    exec_command = models.CharField(max_length=200, help_text=_("executable name"))

    def convert_xml(self, filename):
        stylesheet = '''<?xml version="1.0"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

        <xsl:output method="xml" version="1.0" indent="yes" omit-xml-declaration="yes" encoding="UTF-8"/>

	<xsl:template match="/testsuites">
		<subtests-response>
			<xsl:apply-templates select="testsuite/testcase"/>
		</subtests-response>
	</xsl:template>

	<xsl:template match="testcase">
		<subtest-response>
			<xsl:attribute name="id"><xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/></xsl:attribute>

			<test-result>
				<result>
					<xsl:choose>
						<xsl:when test="failure">
							<score>0.0</score>
						</xsl:when>
						<xsl:when test="error">
							<score>0.0</score>
						</xsl:when>
						<xsl:otherwise>
							<score>1.0</score>
						</xsl:otherwise>						
					</xsl:choose>
				</result>
				<feedback-list>
					<student-feedback level="info">
						<xsl:attribute name="level">
							<xsl:choose>
								<xsl:when test="error">error</xsl:when>
								<xsl:when test="failure">error</xsl:when>
								<xsl:otherwise>info</xsl:otherwise>
							</xsl:choose>
						</xsl:attribute>
						<title><xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/></title>
                        <xsl:choose>
                            <xsl:when test="failure">
                                <content format="plaintext">
                                    <xsl:value-of select="failure"/>
                                </content>
                            </xsl:when>
                            <xsl:when test="error">
                                <content format="plaintext">
                                    <xsl:value-of select="error"/>
                                </content>
                            </xsl:when>
                        </xsl:choose>													
					</student-feedback>
				</feedback-list>
			</test-result>
		</subtest-response>
	</xsl:template>

</xsl:stylesheet>
        '''
        xslt_root = etree.XML(stylesheet)
        transform = etree.XSLT(xslt_root)
        doc = etree.parse(filename)
        result_tree = transform(doc)
        return str(result_tree)

    def compile_test_code(self, env):
        """ compile test code in order to remove it before testing """
        import compileall
        for dirpath, dirs, files in os.walk(env.tmpdir()):
            # print(dirpath)
            # print(dirs)
            dirs = filter(lambda folder: folder not in [".venv", "lib", "lib64", "usr", "tmp"], dirs)
            # print(dirs)
            for folder in dirs:
                logger.debug("compile " + folder)
                # if not compileall.compile_dir(os.path.join(env.tmpdir(), folder), quiet=True):
                #    logger.error('could not compile ' + folder)
                [output, error, exitcode, timed_out, oom_ed] = \
                    execute_arglist(['python3', '-m', 'compileall', folder], env.tmpdir(), unsafe=True)
                if exitcode != 0:
                    # could not compile.
                    # TODO: run without compilation in order to generate better output???
                    regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)),(?<line>[0-9]+)'
                    # regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)):(?<line>[0-9]+)(:(?<column>[0-9]+))?: (?<msgtype>[a-z]+): (?<text>.+)(?<code>\s+.+)?(?<position>\s+\^)?(\s+symbol:\s*(?<symbol>\s+.+))?'
                    return self.handle_compile_error(env, output, error, timed_out, oom_ed, regexp)

            for file in files:
                logger.debug("compile " + file)
                [output, error, exitcode, timed_out, oom_ed] = \
                    execute_arglist(['python3', '-m', 'compileall', file], env.tmpdir(), unsafe=True)
                if exitcode != 0:
                    # could not compile.
                    # TODO: run without compilation in order to generate better output???
                    regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)),(?<line>[0-9]+)'
                    # regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)):(?<line>[0-9]+)(:(?<column>[0-9]+))?: (?<msgtype>[a-z]+): (?<text>.+)(?<code>\s+.+)?(?<position>\s+\^)?(\s+symbol:\s*(?<symbol>\s+.+))?'
                    return self.handle_compile_error(env, output, error, timed_out, oom_ed, regexp)

#                if not compileall.compile_file(os.path.join(env.tmpdir(), file), quiet=True):
#                        logger.error('could not compile ' + file)

            # only upper level => break
            break
            return None




    def run(self, studentenv):
        """ run testcase """
        # Precondition:
        # env already contains student's submission
        logger.debug('main environment is in ' + studentenv.tmpdir())

        # code layer will contain testcode
        # codelayer = CheckerEnvironment(env._solution)
        # copy task files and unzip zip file if submission consists of just a zip file.
        self.prepare_run(studentenv)
        logger.debug('task code is in ' + studentenv.tmpdir())
        # execute_command('ls -al ' +  studentenv.tmpdir())


        template = python_sandbox.PythonSandboxTemplate(self)
        sandbox = template.get_instance(studentenv)
        runenv = sandbox.create()
        # execute_command('ls -al ' +  runenv.tmpdir())
        # execute_command('ls -al ' +  runenv.tmpdir() + '/..')

        test_dir = runenv.tmpdir()

        # compile python code in order to prevent leaking testcode to student (part 1)
        logger.debug('compile python')
        result  = self.compile_test_code(runenv)
        if result is not None:
            return result
#        [output, error, exitcode, timed_out, oom_ed] = execute_arglist(['python3', '-m', 'compileall'], test_dir, unsafe=True)
#        if exitcode != 0:
#            # could not compile.
#            # TODO: run without compilation in order to generate better output???
#            regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)),(?<line>[0-9]+)'
#            # regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)):(?<line>[0-9]+)(:(?<column>[0-9]+))?: (?<msgtype>[a-z]+): (?<text>.+)(?<code>\s+.+)?(?<position>\s+\^)?(\s+symbol:\s*(?<symbol>\s+.+))?'
#            return self.handle_compile_error(env, output, error, timed_out, oom_ed, regexp)

        # create run script:
        with open(test_dir + '/run_suite.py', 'w') as file:
            file.write("""# coding=utf-8
import unittest
import xmlrunner
import os

loader = unittest.TestLoader()
start_dir = '.'
suite = loader.discover(start_dir, "*test*.py")
# delete python files in order to prevent leaking testcode to student (part 2)
for dirpath, dirs, files in os.walk('.'):
    dirs = filter(lambda folder: folder not in [".venv", "lib", "lib64", "usr", "tmp"], dirs)
    for folder in dirs:
        # print(folder)
        for dirpath, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.py'):
                    try:
                        # print(os.path.join(dirpath, file))
                        os.unlink(os.path.join(dirpath, file))
                    except:
                        pass
    break
                        
for dirpath, dirs, files in os.walk('.'):
    for file in files:
        # print(file)
        if file.endswith('.py'):
            try:
                # print(os.path.join(dirpath, file))            
                os.unlink(os.path.join(dirpath, file))
            except:
                pass
    break                        
                        
with open('unittest_results.xml', 'wb') as output:
    runner=xmlrunner.XMLTestRunner(output=output, outsuffix='')
    runner.run(suite)
""")
        os.chmod(test_dir + '/run_suite.py', 0o770)

        # TODO
        # RXSECURE = re.compile(r"(exit|test_detail\.xml)", re.MULTILINE)
        # if not self.submission_ok(env, RXSECURE):
        #    result = self.create_result(env)
        #    result.set_passed(False)
        #    result.set_log("Invalid keyword found in submission (e.g. exit)", log_format=CheckerResult.TEXT_LOG)
        #    return result

        # execute_command(['sudo', 'mount', '--bind', '/proc', test_dir + '/proc'])

        # run test
        # cmd = ['.venv/bin/python3', 'run_suite.py']
        cmd = ['/usr/local/bin/python3', 'run_suite.py']
        # set environment variables
        runenv.set_variable('VIRTUAL_ENV', '/.venv')
#        runenv.set_variable('PATH', '/.venv:./usr')
        runenv.set_variable('PATH', './usr/local/bin:/.venv')
        logger.debug('run ' + str(cmd))
        os.makedirs(test_dir + '/.matplotlib')
        runenv.set_variable('MPLCONFIGDIR', '/.matplotlib')
        (result, output) = self.run_command(cmd, runenv)
        logger.debug('result: ' + str(result))
        logger.debug('output: ' + str(output))
        # execute_command(['sudo', 'umount', test_dir + '/proc'])

        # XSLT
        if os.path.exists(test_dir + "/unittest_results.xml") and \
                os.path.isfile(test_dir + "/unittest_results.xml"):
            try:
                # f = open(test_dir + "/unittest_results.xml", "r")
                # logger.debug(f.read())

                xmloutput = self.convert_xml(test_dir + "/unittest_results.xml")
                result.set_log(xmloutput, timed_out=False, truncated=False, oom_ed=False,
                               log_format=CheckerResult.PROFORMA_SUBTESTS)
                result.set_extralog(output)
                return result
            except:
                logger.error('Error in XML transformation')
                traceback.print_exc()
                # logger.error(inst)
                # fallback: use default output
                return result
                # logger.error('could not convert to XML format')
                # raise Exception('Inconclusive test result (1)')
        else:
            if result.passed:
                # Test is passed but there is no XML file.
                # (exit in submission?)
                result.set_passed(False)
                result.set_log("Inconclusive test result", log_format=CheckerResult.TEXT_LOG)
                return result
                # raise Exception('Inconclusive test result (2)')
            return result


