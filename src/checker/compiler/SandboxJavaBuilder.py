# -*- coding: utf-8 -*-

# from . import JavaBuilder
import logging
import os
from proforma import sandbox
from checker.compiler.JavaBuilder import JavaBuilder
from django.utils.html import escape


logger = logging.getLogger(__name__)

class SandboxJavaBuilder(JavaBuilder):
    def run(self, env):
        """ Build it. """
        logger.debug("---- compile test start ----")
        test_dir = env.tmpdir()

        filenames = [name for name in self.get_file_names(env)]
        args = ['javac'] + self.output_flags(env) + self.flags(env) + filenames + self.libs()
        cmd = ' '.join(args)  # convert cmd to string
        # script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')

####

        #        [output, _, _, _, _]  = execute_arglist(args, env.tmpdir(), self.environment(), extradirs=[script_dir], unsafe=True)

        ####
        j_sandbox = sandbox.JavaImage(self).get_container(test_dir, None)
        j_sandbox.upload_environmment()
        # compile
        (passed, output) = j_sandbox.compile_tests(cmd)
        logger.debug("compilation passed is " + str(passed))
        logger.debug(output)
        if not passed:
            return self.handle_compile_error(env, output, "", False, False)
        exitcode = 0
#####
        result = self.create_result(env)

        output = escape(output)
        output = self.enhance_output(env, output)

        # We mustn't have any warnings.
        passed = passed and not self.has_warnings(output)
        log = self.build_log(output, args, set(filenames).intersection(
            [solutionfile.path() for solutionfile in env.solution().solutionfile_set.all()]))
        if not "format" in log:
            log["format"] = CheckerResult.NORMAL_LOG

        result.set_passed(passed)
        result.set_log(log["log"], log_format=log["format"])
        logger.debug(output)
        logger.debug("---- compile test end ----")

        return result
