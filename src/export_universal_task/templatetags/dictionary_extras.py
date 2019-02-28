# -*- coding: utf-8 -*-
from django import template
from os import path
from utilities import encoding


register = template.Library()


@register.filter(name='access')
def access(value, arg):
    return value[arg]


@register.filter(name='instance_name')
def to_class_name(value):
    return value.__class__.__name__


@register.filter(name='testType')
def testType(value):
    dict_TestTypes = dict([('JavaBuilder', 'java-compilation'), ('JUnitChecker', 'java-junit'),
                           ('CheckstyleChecker', 'java-checkstyle'), ('DejaGnu', 'dejagnu'),
                           ('RemoteScriptChecker', 'RemoteScriptChecker'), ('TextChecker', 'textchecker'), ('PythonChecker', 'PythonChecker'),
                           ('AnonymityChecker', 'anonymity')])  # todo: dict must be more global or no one will find
    ttype = value.__class__.__name__
    if ttype in dict_TestTypes:
        return dict_TestTypes[ttype]
    else:
        return "no-type-" + str(ttype)


@register.filter(name='basename')
def filename_only(value):
    try:
        name = path.basename(value.file.name)
    except NameError:
        raise template.TemplateSyntaxError("ERROR: File not found: %s") % value
    return name

@register.filter(name='extBasename')
def filenamewPath(instance, value):
    try:
        name = path.basename(value.file.name)
    except NameError:
        raise template.TemplateSyntaxError("ERROR: File not found: %s") % value
    if hasattr(instance, "filename"):
        name = instance.filename
    if hasattr(instance, "path"):
        name = path.join(instance.path, name)

    return name

@register.filter(name='get_file_content')
def get_file_content(fn):
    try:
        # return encoding.get_utf8(fn.read())
        #return fn.read()  # problem with strange codepage
        return encoding.get_unicode(fn.read()) #  problem with writing in zip # todo
    except UnicodeError:
        raise template.TemplateSyntaxError("UnicodeERROR: File could not read: %s") % fn
    except NameError:
        raise template.TemplateSyntaxError("ERROR: File could not read: %s") % fn


@register.filter(name='get_instance_id')
def get_instance_id(filename):
    try:
        instance = filename.instance
    except NameError:
        raise template.TemplateSyntaxError("ERROR: Instance of File not found: %s") % instance
    return instance


@register.filter(name='get_BuilderAtt')
def getBuilderAtt(instance, value):
    if value == 'flags':
        try:
            attr = instance._flags
        except NameError:
            raise template.TemplateSyntaxError("ERROR: Attribute not found: %s") % value
        return attr
    elif value == 'output_flags':
        try:
            attr = instance._output_flags
        except NameError:
            raise template.TemplateSyntaxError("ERROR: Attribute not found: %s") % value
        return attr
    elif value == 'libs':
        try:
            attr = instance._libs
        except NameError:
            raise template.TemplateSyntaxError("ERROR: Attribute not found: %s") % value
        return attr
    elif value == 'file_pattern':
        try:
            attr = instance._file_pattern
        except NameError:
            raise template.TemplateSyntaxError("ERROR: Attribute not found: %s") % value
        return attr
    else:
        return "Attribute does not exist in template_extras"