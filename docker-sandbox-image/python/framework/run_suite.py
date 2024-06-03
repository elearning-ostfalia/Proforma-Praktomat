# coding=utf-8

import unittest
import xmlrunner
import subprocess
import os
from lxml import etree

result_folder = "__result__"

def convert_xml(filename):
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


def compile_test_code(start_folder):
    """ compile test code in order to remove it before testing """
    import compileall
    for dirpath, dirs, files in os.walk(start_folder):
        print(dirpath)
        print(dirs)
#        dirs = filter(lambda folder: folder not in [".venv", "lib", "lib64", "usr", "tmp"], dirs)
        # print(dirs)
        for folder in dirs:
            print("compile folder " + folder)
            # if not compileall.compile_dir(os.path.join(env.tmpdir(), folder), quiet=True):
            #    logger.error('could not compile ' + folder)
            command = "python3 -m compileall " + start_folder + "/" + folder
            exitcode = os.system(command)
            # exitcode = subprocess.run(['python3', '-m', 'compileall', folder], cwd=start_folder)
            if exitcode != 0:
                print(exitcode)
                # could not compile.
                # TODO: run without compilation in order to generate better output???
                regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)),(?<line>[0-9]+)'
                # regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)):(?<line>[0-9]+)(:(?<column>[0-9]+))?: (?<msgtype>[a-z]+): (?<text>.+)(?<code>\s+.+)?(?<position>\s+\^)?(\s+symbol:\s*(?<symbol>\s+.+))?'
                #return self.handle_compile_error(env, output, error, timed_out, oom_ed, regexp)
                raise Exception("compilation failed of folder " + folder + " failed")

        for file in files:
            print("compile file " + file)
            command = "python3 -m compileall " + start_folder + "/" + file
            exitcode = os.system(command)            
            # exitcode = subprocess.run(['python3', '-m', 'compileall', file], cwd=start_folder)
            if exitcode != 0:
                print(exitcode)                
                # could not compile.
                # TODO: run without compilation in order to generate better output???
                regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)),(?<line>[0-9]+)'
                # regexp = '(?<filename>\/?(\w+\/)*(\w+)\.([^:]+)):(?<line>[0-9]+)(:(?<column>[0-9]+))?: (?<msgtype>[a-z]+): (?<text>.+)(?<code>\s+.+)?(?<position>\s+\^)?(\s+symbol:\s*(?<symbol>\s+.+))?'
                #return self.handle_compile_error(env, output, error, timed_out, oom_ed, regexp)
                raise Exception("compilation failed of file "+ file + " failed")


        # only upper level => break
        break
        return None

def delete_py_files(start_folder):
    # delete python files in order to prevent leaking testcode to student (part 2)
    for dirpath, dirs, files in os.walk(start_folder):
        # dirs = filter(lambda folder: folder not in [".venv", "lib", "lib64", "usr", "tmp"], dirs)
        for folder in dirs:
            print(folder)
            for dirpath, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py'):
                        try:
                            print(os.path.join(dirpath, file))
                            os.unlink(os.path.join(dirpath, file))
                        except:
                            pass
        break
                            
    for dirpath, dirs, files in os.walk(start_folder):
        for file in files:
            print(file)
            if file.endswith('.py'):
                try:
                    print(os.path.join(dirpath, file))            
                    os.unlink(os.path.join(dirpath, file))
                except:
                    pass
        break      
                  



# os.system("ls -al")                        
# os.system("cd .. && ls -al")  

loader = unittest.TestLoader()
start_dir = '.'
suite = loader.discover(start_dir, "*test*.py")
print("Suite:")
print(suite)

os.system("ls -al " + start_dir)  
compile_test_code(start_dir)
delete_py_files(start_dir)



# os.system("ls -al")                        
# os.system("cd .. && ls -al")  

os.makedirs(result_folder, exist_ok=True)
with open(result_folder + '/unittest_results.xml', 'wb') as output:
    runner=xmlrunner.XMLTestRunner(output=output, outsuffix='')
    runner.run(suite)    

# XSLT
#if os.path.exists(result_folder + "/unittest_results.xml") and \
#        os.path.isfile(result_folder + "/unittest_results.xml"):
#    try:
#        # f = open(test_dir + "/unittest_results.xml", "r")
#        # logger.debug(f.read())

#        xmloutput = convert_xml(result_folder + "/unittest_results.xml")
#        result.set_log(xmloutput, timed_out=False, truncated=False, oom_ed=False,
#                        log_format=CheckerResult.PROFORMA_SUBTESTS)
#        result.set_extralog(output)
#        return result
#    except:
#        logger.error('Error in XML transformation')
#        traceback.print_exc()
#        # logger.error(inst)
#        # fallback: use default output
#        return result
#        # logger.error('could not convert to XML format')
#        # raise Exception('Inconclusive test result (1)')
#else:
#    if result.passed:
#        # Test is passed but there is no XML file.
#        # (exit in submission?)
#        result.set_passed(False)
#        result.set_log("Inconclusive test result", log_format=CheckerResult.TEXT_LOG)
#        return result
#        # raise Exception('Inconclusive test result (2)')
#    return result

os.system("ls -al ./__result__")




#os.system("mv __result__/*.xml  __result__/unittest_results.xml") 

# os.system("ls -al ./__result__")   
#os.system("ls -al unittest_results.xml") 

#os.system("mv unittest_results.xml ../result/unittest_results.xml")