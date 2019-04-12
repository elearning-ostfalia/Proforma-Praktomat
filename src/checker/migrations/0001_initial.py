# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CheckerResult'
        db.create_table('checker_checkerresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('solution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['solutions.Solution'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('passed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('internal_error', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('log', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('log_format', self.gf('django.db.models.fields.CharField')(default='0', max_length=2)),
        ))
        db.send_create_signal('checker', ['CheckerResult'])

        # Adding model 'AnonymityChecker'
        db.create_table('checker_anonymitychecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal('checker', ['AnonymityChecker'])

        # Adding model 'InterfaceChecker'
        db.create_table('checker_interfacechecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('interface1', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('interface2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('interface3', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('interface4', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('interface5', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('interface6', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('interface7', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('checker', ['InterfaceChecker'])

        # Adding model 'LineWidthChecker'
        db.create_table('checker_linewidthchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('max_line_length', self.gf('django.db.models.fields.IntegerField')(default=80)),
            ('tab_width', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('include', self.gf('django.db.models.fields.CharField')(default='.*', max_length=100, blank=True)),
            ('exclude', self.gf('django.db.models.fields.CharField')(default='.*\\.txt$', max_length=100, blank=True)),
        ))
        db.send_create_signal('checker', ['LineWidthChecker'])

        # Adding model 'TextChecker'
        db.create_table('checker_textchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('checker', ['TextChecker'])

        # Adding model 'TextNotChecker'
        db.create_table('checker_textnotchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('max_occ', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('checker', ['TextNotChecker'])

        # Adding model 'DiffChecker'
        db.create_table('checker_diffchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('shell_script', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('input_file', self.gf('checker.models.CheckerFileField')(max_length=500, blank=True)),
            ('output_file', self.gf('checker.models.CheckerFileField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('checker', ['DiffChecker'])

        # Adding model 'ScriptChecker'
        db.create_table('checker_scriptchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Externen Tutor ausf\xc3\xbchren', max_length=100)),
            ('shell_script', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('remove', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('returns_html', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['ScriptChecker'])

        # Adding model 'CreateFileChecker'
        db.create_table('checker_createfilechecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('file', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
        ))
        db.send_create_signal('checker', ['CreateFileChecker'])

        # Adding model 'LineCounter'
        db.create_table('checker_linecounter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal('checker', ['LineCounter'])

        # Adding model 'JavaBuilder'
        db.create_table('checker_javabuilder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('_flags', self.gf('django.db.models.fields.CharField')(default='-Wall', max_length=1000, blank=True)),
            ('_output_flags', self.gf('django.db.models.fields.CharField')(default='-o %s', max_length=1000, blank=True)),
            ('_libs', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
            ('_file_pattern', self.gf('django.db.models.fields.CharField')(default='^[a-zA-Z0-9_]*$', max_length=1000)),
            ('_main_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['JavaBuilder'])

        # Adding model 'JUnitChecker'
        db.create_table('checker_junitchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('test_description', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('junit_version', self.gf('django.db.models.fields.CharField')(default='junit4.12', max_length=100)),
        ))
        db.send_create_signal('checker', ['JUnitChecker'])

        # Adding model 'JUnit3Checker'
        db.create_table('checker_junit3checker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('test_case', self.gf('checker.models.CheckerFileField')(max_length=500)),
        ))
        db.send_create_signal('checker', ['JUnit3Checker'])

        # Adding model 'DejaGnuTester'
        db.create_table('checker_dejagnutester', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('test_case', self.gf('checker.models.CheckerFileField')(max_length=500)),
        ))
        db.send_create_signal('checker', ['DejaGnuTester'])

        # Adding model 'DejaGnuSetup'
        db.create_table('checker_dejagnusetup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('test_defs', self.gf('checker.models.CheckerFileField')(max_length=500)),
        ))
        db.send_create_signal('checker', ['DejaGnuSetup'])

        # Adding model 'CheckStyleChecker'
        db.create_table('checker_checkstylechecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(default='CheckStyle', max_length=100)),
            ('configuration', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('allowedWarnings', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('allowedErrors', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('regText', self.gf('django.db.models.fields.CharField')(default='.*', max_length=5000)),
            ('check_version', self.gf('django.db.models.fields.CharField')(default='check-6.2', max_length=16)),
        ))
        db.send_create_signal('checker', ['CheckStyleChecker'])

        # Adding model 'RemoteScriptChecker'
        db.create_table('checker_remotescriptchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(default='External Remote Checker', max_length=100)),
            ('solution_file', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('solution_file_name', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('student_solution_file_name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('returns_html', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['RemoteScriptChecker'])

        # Adding model 'PythonChecker'
        db.create_table('checker_pythonchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Externen Tutor ausf\xc3\xbchren', max_length=100)),
            ('doctest', self.gf('checker.models.CheckerFileField')(max_length=500)),
            ('remove', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('returns_html', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['PythonChecker'])

        # Adding model 'SetlXChecker'
        db.create_table('checker_setlxchecker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(default='SetlXChecker', max_length=100)),
            ('testFile', self.gf('checker.models.CheckerFileField')(max_length=500)),
        ))
        db.send_create_signal('checker', ['SetlXChecker'])

        # Adding model 'CBuilder'
        db.create_table('checker_cbuilder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('_flags', self.gf('django.db.models.fields.CharField')(default='-Wall', max_length=1000, blank=True)),
            ('_output_flags', self.gf('django.db.models.fields.CharField')(default='-o %s', max_length=1000, blank=True)),
            ('_libs', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
            ('_file_pattern', self.gf('django.db.models.fields.CharField')(default='^[a-zA-Z0-9_]*$', max_length=1000)),
            ('_main_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['CBuilder'])

        # Adding model 'CXXBuilder'
        db.create_table('checker_cxxbuilder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('_flags', self.gf('django.db.models.fields.CharField')(default='-Wall', max_length=1000, blank=True)),
            ('_output_flags', self.gf('django.db.models.fields.CharField')(default='-o %s', max_length=1000, blank=True)),
            ('_libs', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
            ('_file_pattern', self.gf('django.db.models.fields.CharField')(default='^[a-zA-Z0-9_]*$', max_length=1000)),
            ('_main_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['CXXBuilder'])

        # Adding model 'JavaGCCBuilder'
        db.create_table('checker_javagccbuilder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('_flags', self.gf('django.db.models.fields.CharField')(default='-Wall', max_length=1000, blank=True)),
            ('_output_flags', self.gf('django.db.models.fields.CharField')(default='-o %s', max_length=1000, blank=True)),
            ('_libs', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
            ('_file_pattern', self.gf('django.db.models.fields.CharField')(default='^[a-zA-Z0-9_]*$', max_length=1000)),
            ('_main_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['JavaGCCBuilder'])

        # Adding model 'FortranBuilder'
        db.create_table('checker_fortranbuilder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tasks.Task'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('always', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('proforma_id', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('_flags', self.gf('django.db.models.fields.CharField')(default='-Wall', max_length=1000, blank=True)),
            ('_output_flags', self.gf('django.db.models.fields.CharField')(default='-o %s', max_length=1000, blank=True)),
            ('_libs', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
            ('_file_pattern', self.gf('django.db.models.fields.CharField')(default='^[a-zA-Z0-9_]*$', max_length=1000)),
            ('_main_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('checker', ['FortranBuilder'])


    def backwards(self, orm):
        # Deleting model 'CheckerResult'
        db.delete_table('checker_checkerresult')

        # Deleting model 'AnonymityChecker'
        db.delete_table('checker_anonymitychecker')

        # Deleting model 'InterfaceChecker'
        db.delete_table('checker_interfacechecker')

        # Deleting model 'LineWidthChecker'
        db.delete_table('checker_linewidthchecker')

        # Deleting model 'TextChecker'
        db.delete_table('checker_textchecker')

        # Deleting model 'TextNotChecker'
        db.delete_table('checker_textnotchecker')

        # Deleting model 'DiffChecker'
        db.delete_table('checker_diffchecker')

        # Deleting model 'ScriptChecker'
        db.delete_table('checker_scriptchecker')

        # Deleting model 'CreateFileChecker'
        db.delete_table('checker_createfilechecker')

        # Deleting model 'LineCounter'
        db.delete_table('checker_linecounter')

        # Deleting model 'JavaBuilder'
        db.delete_table('checker_javabuilder')

        # Deleting model 'JUnitChecker'
        db.delete_table('checker_junitchecker')

        # Deleting model 'JUnit3Checker'
        db.delete_table('checker_junit3checker')

        # Deleting model 'DejaGnuTester'
        db.delete_table('checker_dejagnutester')

        # Deleting model 'DejaGnuSetup'
        db.delete_table('checker_dejagnusetup')

        # Deleting model 'CheckStyleChecker'
        db.delete_table('checker_checkstylechecker')

        # Deleting model 'RemoteScriptChecker'
        db.delete_table('checker_remotescriptchecker')

        # Deleting model 'PythonChecker'
        db.delete_table('checker_pythonchecker')

        # Deleting model 'SetlXChecker'
        db.delete_table('checker_setlxchecker')

        # Deleting model 'CBuilder'
        db.delete_table('checker_cbuilder')

        # Deleting model 'CXXBuilder'
        db.delete_table('checker_cxxbuilder')

        # Deleting model 'JavaGCCBuilder'
        db.delete_table('checker_javagccbuilder')

        # Deleting model 'FortranBuilder'
        db.delete_table('checker_fortranbuilder')


    models = {
        'accounts.tutorial': {
            'Meta': {'object_name': 'Tutorial'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tutors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tutored_tutorials'", 'symmetrical': 'False', 'to': "orm['accounts.User']"})
        },
        'accounts.user': {
            'Meta': {'ordering': "['first_name', 'last_name']", 'object_name': 'User', '_ormbases': ['auth.User']},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'final_grade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mat_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tutorial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.Tutorial']", 'null': 'True', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'attestation.ratingscale': {
            'Meta': {'object_name': 'RatingScale'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'checker.anonymitychecker': {
            'Meta': {'object_name': 'AnonymityChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.cbuilder': {
            'Meta': {'object_name': 'CBuilder'},
            '_file_pattern': ('django.db.models.fields.CharField', [], {'default': "'^[a-zA-Z0-9_]*$'", 'max_length': '1000'}),
            '_flags': ('django.db.models.fields.CharField', [], {'default': "'-Wall'", 'max_length': '1000', 'blank': 'True'}),
            '_libs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            '_main_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_output_flags': ('django.db.models.fields.CharField', [], {'default': "'-o %s'", 'max_length': '1000', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.checkerresult': {
            'Meta': {'object_name': 'CheckerResult'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'log': ('django.db.models.fields.TextField', [], {}),
            'log_format': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '2'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'passed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'solution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['solutions.Solution']"})
        },
        'checker.checkstylechecker': {
            'Meta': {'object_name': 'CheckStyleChecker'},
            'allowedErrors': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'allowedWarnings': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'check_version': ('django.db.models.fields.CharField', [], {'default': "'check-6.2'", 'max_length': '16'}),
            'configuration': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'CheckStyle'", 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'regText': ('django.db.models.fields.CharField', [], {'default': "'.*'", 'max_length': '5000'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.createfilechecker': {
            'Meta': {'object_name': 'CreateFileChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.cxxbuilder': {
            'Meta': {'object_name': 'CXXBuilder'},
            '_file_pattern': ('django.db.models.fields.CharField', [], {'default': "'^[a-zA-Z0-9_]*$'", 'max_length': '1000'}),
            '_flags': ('django.db.models.fields.CharField', [], {'default': "'-Wall'", 'max_length': '1000', 'blank': 'True'}),
            '_libs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            '_main_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_output_flags': ('django.db.models.fields.CharField', [], {'default': "'-o %s'", 'max_length': '1000', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.dejagnusetup': {
            'Meta': {'object_name': 'DejaGnuSetup'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'test_defs': ('checker.models.CheckerFileField', [], {'max_length': '500'})
        },
        'checker.dejagnutester': {
            'Meta': {'object_name': 'DejaGnuTester'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'test_case': ('checker.models.CheckerFileField', [], {'max_length': '500'})
        },
        'checker.diffchecker': {
            'Meta': {'object_name': 'DiffChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_file': ('checker.models.CheckerFileField', [], {'max_length': '500', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'output_file': ('checker.models.CheckerFileField', [], {'max_length': '500', 'blank': 'True'}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shell_script': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.fortranbuilder': {
            'Meta': {'object_name': 'FortranBuilder'},
            '_file_pattern': ('django.db.models.fields.CharField', [], {'default': "'^[a-zA-Z0-9_]*$'", 'max_length': '1000'}),
            '_flags': ('django.db.models.fields.CharField', [], {'default': "'-Wall'", 'max_length': '1000', 'blank': 'True'}),
            '_libs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            '_main_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_output_flags': ('django.db.models.fields.CharField', [], {'default': "'-o %s'", 'max_length': '1000', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.interfacechecker': {
            'Meta': {'object_name': 'InterfaceChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'interface2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'interface3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'interface4': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'interface5': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'interface6': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'interface7': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.javabuilder': {
            'Meta': {'object_name': 'JavaBuilder'},
            '_file_pattern': ('django.db.models.fields.CharField', [], {'default': "'^[a-zA-Z0-9_]*$'", 'max_length': '1000'}),
            '_flags': ('django.db.models.fields.CharField', [], {'default': "'-Wall'", 'max_length': '1000', 'blank': 'True'}),
            '_libs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            '_main_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_output_flags': ('django.db.models.fields.CharField', [], {'default': "'-o %s'", 'max_length': '1000', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.javagccbuilder': {
            'Meta': {'object_name': 'JavaGCCBuilder'},
            '_file_pattern': ('django.db.models.fields.CharField', [], {'default': "'^[a-zA-Z0-9_]*$'", 'max_length': '1000'}),
            '_flags': ('django.db.models.fields.CharField', [], {'default': "'-Wall'", 'max_length': '1000', 'blank': 'True'}),
            '_libs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'}),
            '_main_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            '_output_flags': ('django.db.models.fields.CharField', [], {'default': "'-o %s'", 'max_length': '1000', 'blank': 'True'}),
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.junit3checker': {
            'Meta': {'object_name': 'JUnit3Checker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'test_case': ('checker.models.CheckerFileField', [], {'max_length': '500'})
        },
        'checker.junitchecker': {
            'Meta': {'object_name': 'JUnitChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'junit_version': ('django.db.models.fields.CharField', [], {'default': "'junit4.12'", 'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'test_description': ('django.db.models.fields.TextField', [], {})
        },
        'checker.linecounter': {
            'Meta': {'object_name': 'LineCounter'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.linewidthchecker': {
            'Meta': {'object_name': 'LineWidthChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exclude': ('django.db.models.fields.CharField', [], {'default': "'.*\\\\.txt$'", 'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include': ('django.db.models.fields.CharField', [], {'default': "'.*'", 'max_length': '100', 'blank': 'True'}),
            'max_line_length': ('django.db.models.fields.IntegerField', [], {'default': '80'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tab_width': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.pythonchecker': {
            'Meta': {'object_name': 'PythonChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'doctest': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Externen Tutor ausf\\xc3\\xbchren'", 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'remove': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'returns_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.remotescriptchecker': {
            'Meta': {'object_name': 'RemoteScriptChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'External Remote Checker'", 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'returns_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'solution_file': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'solution_file_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'student_solution_file_name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.scriptchecker': {
            'Meta': {'object_name': 'ScriptChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Externen Tutor ausf\\xc3\\xbchren'", 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'remove': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'returns_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shell_script': ('checker.models.CheckerFileField', [], {'max_length': '500'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"})
        },
        'checker.setlxchecker': {
            'Meta': {'object_name': 'SetlXChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'SetlXChecker'", 'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'testFile': ('checker.models.CheckerFileField', [], {'max_length': '500'})
        },
        'checker.textchecker': {
            'Meta': {'object_name': 'TextChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'checker.textnotchecker': {
            'Meta': {'object_name': 'TextNotChecker'},
            'always': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occ': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'proforma_id': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'solutions.solution': {
            'Meta': {'object_name': 'Solution'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'plagiarism': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tasks.Task']"}),
            'warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'tasks.task': {
            'Meta': {'object_name': 'Task'},
            'all_checker_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'final_grade_rating_scale': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['attestation.RatingScale']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_file_size': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'model_solution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'model_solution_task'", 'null': 'True', 'to': "orm['solutions.Solution']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {}),
            'supported_file_types': ('django.db.models.fields.CharField', [], {'default': "'^(text/.*|image/.*)$'", 'max_length': '1000'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['checker']