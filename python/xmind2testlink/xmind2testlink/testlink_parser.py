"""
Module to parse test suite objects into testlink xml.
"""
import os
from codecs import open
from io import BytesIO
from os.path import exists
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from .datatype import *


class Tags():
    xml = 'xml'
    testsuite = "testsuite"
    details = 'details'
    testcase = 'testcase'
    summary = 'summary'
    precoditions = 'preconditions'
    steps = 'steps'
    step = 'step'
    step_number = 'step_number'
    actions = 'actions'
    expected = 'expectedresults'
    execution_type = 'execution_type'
    importance = 'importance'


class Attributes():
    name = 'name'


# Only text in CDATA can support newlines in testlink
CDATA_Tags = ['details', 'summary', 'preconditions', 'actions', 'expectedresults']


def to_testlink_xml_file(testsuite, path_to_xml):
    """Save test suite object to testlink xml file."""
    content = to_testlink_xml_content(testsuite)
    if exists(path_to_xml):
        os.remove(path_to_xml)

    with open(path_to_xml, 'w', encoding='utf-8') as f:
        f.write(prettify_xml(content))


def _convert_importance(importance_value):
    mapping = {'priority-1': '3', 'priority-2': '2', 'priority-3': '1'}
    if importance_value in mapping.keys():
        return mapping[importance_value]
    else:
        return '2'


def should_parse(item):
    return isinstance(item, str) and not item.startswith('!')


def to_testlink_xml_content(testsuite):
    assert isinstance(testsuite, TestSuite)
    root_suite = Element(Tags.testsuite)
    root_suite.set(Attributes.name, testsuite.name)

    if should_parse(testsuite.details):
        e = SubElement(root_suite, Tags.details)
        e.text = testsuite.details
    cache['testcase_count'] = 0

    def should_skip(item):
        return item is None or not isinstance(item, str) or item.strip() == '' or item.startswith('!')

    def append_testcase(suite_element, testcase):
        assert isinstance(testcase, TestCase)

        if should_skip(testcase.name):
            return

        cache['testcase_count'] += 1
        testcase_element = SubElement(suite_element, Tags.testcase)
        testcase_element.set(Attributes.name, testcase.name)

        if should_parse(testcase.summary):
            e = SubElement(testcase_element, Tags.summary)
            e.text = testcase.summary

        if should_parse(testcase.preconditions):
            e = SubElement(testcase_element, Tags.precoditions)
            e.text = testcase.preconditions

        if should_parse(testcase.execution_type):
            e = SubElement(testcase_element, Tags.execution_type)
            e.text = testcase.execution_type

        e = SubElement(testcase_element, Tags.importance)
        e.text = _convert_importance(testcase.importance)

        if testcase.steps:
            steps_element = SubElement(testcase_element, Tags.steps)

            for step in testcase.steps:
                assert isinstance(step, TestStep)

                if should_skip(step.action):
                    continue
                else:
                    step_element = SubElement(steps_element, Tags.step)

                if should_parse(step.action):
                    e = SubElement(step_element, Tags.actions)
                    e.text = step.action

                e = SubElement(step_element, Tags.expected)

                expectation_text = ''
                for ex in step.expected_list:
                    if should_parse(ex):
                        expectation_text += "{}{}".format(ex, os.linesep)
                e.text = expectation_text

                if should_parse(step.execution_type):
                    e = SubElement(step_element, Tags.execution_type)
                    e.text = step.execution_type

                e = SubElement(step_element, Tags.step_number)
                e.text = str(step.number)

    def append_subsuite(parent_suite, subsuite):
        assert isinstance(subsuite, TestSuite)

        if should_skip(subsuite.name):
            return

        suite_element = SubElement(parent_suite, Tags.testsuite)
        suite_element.set(Attributes.name, subsuite.name)

        if should_parse(subsuite.details):
            e = SubElement(suite_element, Tags.details)
            e.text = subsuite.details

        for testcase in subsuite.testcase_list:
            append_testcase(suite_element, testcase)

        for child in subsuite.sub_suites:
            append_subsuite(suite_element, child)

    for suite in testsuite.sub_suites:
        append_subsuite(root_suite, suite)
    for test in testsuite.testcase_list:
        append_testcase(root_suite, test)

    tree = ElementTree.ElementTree(root_suite)
    f = BytesIO()
    tree.write(f, encoding='utf-8', xml_declaration=True)
    return f.getvalue()


def prettify_xml(xml_string):
    """Return a pretty-printed XML string for the Element.
    """
    reparsed = minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="\t")


def format_lines_into_p_tag(text):
    """
    only text in p tag can be displayed as newline in testlink
    :param step_text:
    :return:
    """
    # CR+LF (\r\n) or LF(\n) is most commonly used newline charactor in most os (posix, windows nt)
    # this line is compatible with CR+LF and LF(\n)
    texts = text.replace('\r', '').split('\n')
    formated_text = ""

    for text in texts:
        formated_text = "{}<p>{}</p>".format(formated_text, text)

    return formated_text


ElementTree._original_serialize_xml = ElementTree._serialize_xml


def serialize_xml_with_CDATA(write, elem, qnames, namespaces, short_empty_elements, **kwargs):
    """Original xml serializer escaped all CDATA text, monkey patch it to generate CDATA text to be used in testlink"""
    if elem.tag in CDATA_Tags and elem.text:
        cdata_text = "<![CDATA[{}]]>".format(format_lines_into_p_tag(elem.text))
        write("<{}>{}</{}>".format(elem.tag, cdata_text, elem.tag))
        return
    return ElementTree._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)


ElementTree._serialize_xml = ElementTree._serialize['xml'] = serialize_xml_with_CDATA
