from ectools.internal.online_class_service_helper import online_class_helper_api

classTypeGroup = {
    "Common": {
        "GL-General-EvcUS1 for all levels": 1001,
        "GL-General-EvcCN1 for all levels": 1002,
        "PL-General-EvcUS1 for PL40, EFTV, Aviation": 2001,
        "PL-General-EvcCN1 for PL40, EFTV": 2002,
        "PL-General-EvcUS1 for PL20, OSA": 2003,
        "PL-General-EvcCN1 for PL20, OSA, KPL, KPLDemo": 2004,
        "PL-General-EvcCN2 for KPL, KPLDemo": 2005,
        "PL-General-Bilingual(cn)-EvcCN1 for PL40, OSC, BBC": 2006,
        "PL-General-Bilingual(cn)-EvcCN1 for PL20, OSA": 2007
    },
    "GL": {
        "GL-Bilingual(cn, NonPHX)-EvcCN1 for BEG": 1017,
        "GL-Bilingual(cn, Any)-EvcCN1 for BEG": 1013,
        "GL-Bilingual(br)-EvcUS1 for BEG": 1014,
        "GL-Bilingual(SPLang)-EvcUS1 for BEG": 1015,
        "GL-Bilingual(fr)-EvcUS1 for BEG": 1018,
        "GL-Bilingual(it)-EvcUS1 for BEG": 1019,
        "GL-Bilingual(de)-EvcUS1 for BEG": 1020,
        "GL-Anat-EvcUS1 for BEG": 1501,
        "GL-Anat-EvcUS1 for ELE": 1502,
        "GL-Anat-EvcUS1 for INT": 1503,
        "GL-Anat-EvcUS1 for UPINT": 1504,
        "GL-CROC-SOCN-EvcCN1": 1402,
        "GL-CROC-EC-EvcCN1": 1401
    },
    "PL": {
        "PL40-Bilingual(br)-EvcUS1 for BEG": 2106,
        "PL40-Bilingual(SPLang)-EvcUS1 for BEG": 2107,
        "PL40-Bilingual(Arabic)-EvcUS1 for BEG": 2108,
        "PL40-Bilingual(fr)-EvcUS1 for BEG": 2109,
        "PL40-Bilingual(it)-EvcUS1 for BEG": 2110,
        "PL40-Bilingual(de)-EvcUS1 for BEG": 2111,
        "PL40-Bilingual(cn)-EvcCN1 for all levels": 2105,
        "PL20-Bilingual(cn)-EvcCN1 for all levels": 2205,
        "PL20-Bilingual(es)-EvcUS1 for all levels": 2206,
        "OSA-Bilingual(cn)-EvcCN1 for BEG": 2406,
        "OSA-Bilingual(es)-EvcUS1 for BEG": 2404,
        "OSA-Bilingual(ru)-EvcUS1 for BEG": 2405,
        "BBC-Bilingual(cn)-EvcCN1 for all levels": 2322,
        "PL-OneClickBooking": 2401
    },
    "OSC": {
        "OSCVoca-EvcCN1 for all levels": 2306,
        "OSCPron-EvcCN1 for all levels": 2307,
        "OSCGram-EvcCN1 for all levels": 2308,
        "OSCVoca-Bilingual(cn)-EvcCN1 for all levels": 2309,
        "OSCPron-Bilingual(cn)-EvcCN1 for all levels": 2310,
        "OSCGram-Bilingual(cn)-EvcCN1 for all levels": 2311
    },
    "Kids": {
        "PL-KPL-EvcCN2": 2505,
        "PL-KPLDemo-EvcCN2": 2506,
        "PL-KTB-EvcCN2": 2507,
        "PL-KTBDemo-EvcCN2": 2508,
        "PL-KSS-EvcCN2": 2509,
        "PL-KSSDemo-EvcCN2": 2510,
    }
}


def get_class_type():
    class_type = online_class_helper_api.get_class_type()
    return class_type


def allocate_class(service_type: str, service_subtype: str, level: str, partner: str, market: str, language: str,
                   teaching_item: str, evc_server: str, duration: str, start_time: str, end_time: str, center_code: str,
                   source_type_Code: str):
    """
         Allocate class
    :param service_type: the class id
    :param service_subtype: the member id of teacher
    :param level:
    :param partner:
    :param market:
    :param language:
    :param teaching_item:
    :param evc_server:
    :param duration:
    :param start_time:
    :param end_time:
    :param center_code:
    :param source_type_Code:
    :return class_info:
    """
    class_info = online_class_helper_api.allocate_class({
        "classes": [
            {
                "allocationClassTypes": [
                    {
                        "serviceType": service_type,
                        "serviceSubType": service_subtype,
                        "level": level,
                        "partner": partner,
                        "market": market,
                        "language": language,
                        "teachingItem": teaching_item,
                        "evcServer": evc_server,
                        "duration": duration
                    }
                ],
                "startTime": start_time,
                "endTime": end_time,
                "centerCode": center_code,
                "sourceTypeCode": source_type_Code
            }
        ],
        "operator": {
            "operatedBy": "AxisTool",
            "operatorType": "AxisTool"
        }
    })
    return class_info


def set_availability(teacher_member_id: int, start_time: str, end_time: str):
    """
        Set teacher availability.
    :param teacher_member_id: the member id of teacher
    :param start_time: start time of teacher's availability
    :param end_time: end time of teacher's availability
    """
    online_class_helper_api.set_availability(
        {
            "timeRange": {
                "startTime": start_time,
                "endTime": end_time
            },
            "teacherCriteria": {
                "teacherMemberId": teacher_member_id
            },
            "availabilities": [
                {
                    "teacherMemberId": teacher_member_id,
                    "startTime": start_time,
                    "endTime": end_time
                }
            ]
        }
    )


def assign_class(class_id: int, teacher_id: int):
    """
        Assign class to teacher.
    :param class_id: the class id
    :param teacher_id: the member id of teacher
    """
    online_class_helper_api.assign_class({
        "classId": class_id,
        "teacherMemberId": teacher_id
    })
