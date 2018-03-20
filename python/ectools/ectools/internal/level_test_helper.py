"""
For level test 2.0, we have to submit score via service, no tools provided by school team.

The flow explained as bellow:

1. Get login session via /login/secure.ashx
2. Troop query to get current level id
3. Start level test via /services/api/school/command/leveltest/StartTest
4. Troop query to get all sections for current level test
5. Submit score for each section
"""
from ectools.config import config, get_logger
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.internal.troop_service_helper import login, get_request_session
from ectools.service_helper import account_service_load_student
from ectools.service_helper import query_troop_service
from ectools.utility import get_score

START_TEST_API = '{}/services/api/school/command/leveltest/StartTest'
SUBMIT_SECTION_SCORE = '{}/services/api/school/command/scoring/SubmitLevelTestSectionScore'


def pass_level_test_v2(student_id, score=get_score()):
    get_logger().info('Pass level test 2.0 for student: {}, score={}'.format(student_id, score))

    student = account_service_load_student(student_id)
    student_name, password = student['user_name'], student['password']
    login(student_name, password)
    client = get_request_session(student_name)

    # get level test id
    result = query_troop_service(student_name, query_string='q=student_course_enrollment!current')

    # e.g. = student_level!dc268633-efd9-4577-ba0d-b3ffa5484d9a
    level_info = result['studentLevel']['id']

    # e.g. = dc268633-efd9-4577-ba0d-b3ffa5484d9a
    level_id = level_info[14:]

    # start level test
    url = START_TEST_API.format(config.etown_root)
    data = {"levelId": level_id, "isReset": False}
    result = client.post(url, json=data)
    assert result.status_code == HTTP_STATUS_OK, result.text

    # get level test sections, q=student_level!dc268633-efd9-4577-ba0d-b3ffa5484d9a.children,.levelTest
    query_string = 'q=%s.children,.levelTest' % level_info
    result = query_troop_service(student_name, query_string=query_string, return_first_item=False)
    level_test_info = [i for i in result if 'pcLevelTest' in i][0]

    # e.g. = 'student_leveltest!4de86ffb-99cc-4865-ac71-bcb91334fae3'
    pc_level_test_id = level_test_info['pcLevelTest']['id']

    query_string = 'q=%s' % pc_level_test_id
    result = query_troop_service(student_name, query_string=query_string)
    section_id_list = [i['id'] for i in result['children']]

    # submit level test section one by one
    url = SUBMIT_SECTION_SCORE.format(config.etown_root)
    data = {"score": score, "minutesSpent": 3, "studyMode": 0}

    for section in section_id_list:
        data['studentLevelTestSectionId'] = section[26:]
        result = client.post(url, json=data)
        assert result.status_code == HTTP_STATUS_OK, result.text
