"""
Module to parse xmind file into test suite and test case objects.
"""
import logging
import re
from xml.etree import ElementTree as  ET
from xml.etree.ElementTree import Element
from zipfile import ZipFile

from .datatype import *

content_xml = "content.xml"
comments_xml = "comments.xml"


def parse_xmind_file(file_path):
    """Extract xmind as zip file then read the content.xml"""
    with ZipFile(file_path) as xmind:
        for f in xmind.namelist():
            if f == content_xml:
                cache[content_xml] = xmind.open(f).read().decode('utf-8')

            if f == comments_xml:
                cache[comments_xml] = xmind.open(f).read().decode('utf-8')

    return parse_xmind_content()


def parse_xmind_content():
    """Main function to read the content xml and return test suite data."""
    xml_root = xmind_content_to_etree(cache[content_xml])
    assert isinstance(xml_root, Element)

    try:
        xml_root_suite = xml_root.find('sheet').find('topic')
        logging.info("Parse topic: {}".format(title_of(xml_root_suite)))
    except:
        logging.error('Cannot find any topic in your xmind!')
        raise

    return parse_suite(xml_root_suite)


def xmind_content_to_etree(content):
    # Remove the default namespace definition (xmlns="http://some/namespace")
    xml_content = re.sub(r'\sxmlns="[^"]+"', '', content, count=1)
    return ET.fromstring(xml_content.encode('utf-8'))


def xmind_xml_to_etree(xml_path):
    with open(xml_path) as f:
        content = f.read()
        return xmind_content_to_etree(content)


def comments_of(node):
    if cache.get(comments_xml, None):
        xml_root = xmind_content_to_etree(cache[comments_xml])
        node_id = node.attrib['id']
        comment = xml_root.find('./comment[@object-id="{}"]'.format(node_id))

        if comment is not None:
            return comment.find('content').text


def title_of(node):
    title = node.find('title')

    if title is not None:
        return title.text


def note_of(topic_node):
    note_node = topic_node.find('notes')

    if note_node is not None:
        note = note_node.find('plain').text
        return note.strip()


def maker_of(topic_node, maker_prefix):
    maker_node = topic_node.find('marker-refs')
    if maker_node is not None:
        for maker in maker_node:
            maker_id = maker.attrib['marker-id']
            if maker_id.startswith(maker_prefix):
                return maker_id


def children_topics_of(topic_node):
    children = topic_node.find('children')

    if children is not None:
        return children.find('./topics[@type="attached"]')
    else:
        return None


def parse_step(step_node):
    step = TestStep()
    step.action = title_of(step_node)
    step.expected_list = []
    expected_nodes = children_topics_of(step_node)

    for expection in expected_nodes:
        step.expected_list.append(title_of(expection))

    return step


def parse_steps(steps_node):
    steps = []

    for step_number, step_node in enumerate(steps_node, 1):
        step = parse_step(step_node)
        step.number = step_number
        steps.append(step)

    return steps


def parse_testcase(testcase_node):
    testcase = TestCase()
    testcase.name = title_of(testcase_node)
    testcase.summary = note_of(testcase_node)
    testcase.importance = maker_of(testcase_node, 'priority')
    testcase.preconditions = comments_of(testcase_node)
    steps_node = children_topics_of(testcase_node)

    if steps_node is not None:
        testcase.steps = parse_steps(steps_node)

    return testcase


def parse_suite(suite_node):
    suite = TestSuite()
    suite.name = title_of(suite_node)
    suite.details = note_of(suite_node)
    suite.testcase_list = []
    suite.sub_suites = []
    children_topics = children_topics_of(suite_node)
    if children_topics is not None:
        for node in children_topics:
            if is_testcase_node(node):
                testcase = parse_testcase(node)
                suite.testcase_list.append(testcase)
            else:
                sub_suite = parse_suite(node)
                suite.sub_suites.append(sub_suite)

    return suite


def is_testcase_node(node):
    """
    If current node is test case node, node structure should be like below.
    That is all its children nodes have and only have one level of children nodes
    node
    --test step1
    ----test step1 expectation (Only if this node doesn't have children node, is the given node test case node)
    :param node:
    :return: True if current node is test case node, False otherwise
    """
    steps = children_topics_of(node)
    if steps:
        is_step_has_expectation = []
        for step in steps:
            expectations = children_topics_of(step)
            if expectations:
                for exp in expectations:
                    is_step_has_expectation.append(not children_topics_of(exp))
            else:
                # any step doesn't have expectation, node is not testcase
                return False
        return is_step_has_expectation is not [] and all(is_step_has_expectation)

    return False
