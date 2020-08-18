import arrow

from ectools.internal.online_class_service_helper import OnlineClassApi, get_axis_root, get_axis_token
from ectools.service_helper import troop_service_get_teacher_info

# class type for class schedule
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


def get_arrow_time(time_value):
    """Convert time value to Arrow object."""
    return time_value if isinstance(time_value, arrow.Arrow) else arrow.get(time_value)


def calculate_time_range(begin_time, duration, class_index):
    """
        calculate start time and end time
    :param begin_time: begin time for the class schedule plan
    :param duration: duration of each class
    :param class_index: class index plan to schedule
    return (start_time, end_time):
    """
    begin_time = get_arrow_time(begin_time)
    start_time = begin_time.shift(seconds=int(duration) * (class_index - 1) * 60)
    start_time_string = start_time.format('YYYY-MM-DD HH:mm:ss')
    end_time = begin_time.shift(seconds=int(duration) * class_index * 60)
    end_time_string = end_time.format('YYYY-MM-DD HH:mm:ss')

    # format time string to 2020-03-04T11:00:00Z
    start_time_string = start_time_string[:10] + 'T' + start_time_string[11:] + 'Z'
    end_time_string = end_time_string[:10] + 'T' + end_time_string[11:] + 'Z'

    return (start_time_string, end_time_string)


def get_teacher_center(teacher_member_id_or_name):
    """Get a teacher's centercode base on teacher's member id."""
    teacher_info = troop_service_get_teacher_info(teacher_member_id_or_name)
    return teacher_info['centerCode']


class OnlineClassHelper():
    def __init__(self):
        self.__api = OnlineClassApi(get_axis_root(), get_axis_token())

    def get_class_type(self):
        class_type = self.__api.get_class_type()
        return class_type

    def allocate_class(self, service_type: str, service_subtype: str, level: str, partner: str, market: str,
                       language: str,
                       teaching_item: str, evc_server: str, duration: str, start_time: str, end_time: str,
                       center_code: str,
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
        class_info = self.__api.allocate_class({
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
                "operatedBy": "Automation",
                "operatorType": "Automation"
            }
        })
        return class_info

    def set_availability(self, teacher_member_id: int, start_time: str, end_time: str):
        """
            Set teacher availability.
        :param teacher_member_id: the member id of teacher
        :param start_time: start time of teacher's availability
        :param end_time: end time of teacher's availability
        """
        self.__api.set_availability(
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

    def assign_class(self, class_id: int, teacher_id: int):
        """
            Assign class to teacher.
        :param class_id: the class id
        :param teacher_id: the member id of teacher
        """
        self.__api.assign_class({
            "classId": class_id,
            "teacherMemberId": teacher_id
        })

    def schedule_class(self, teacher_member_id, class_type, start_time, class_count=1):
        """
            schedule class to teacher.
        :param teacher_member_id: member id of teacher you want to schedule class
        :param class_type: class type you want to schedule class, refer classTypeGroup dict
        :param start_time: start time to schedule class, format "YYYY-MM-DD HH-mm-ss" eg:"2020-03-10 01:00:00"
        :param class_count: how many class you want to schedule one time (limit to 12)
        :return class_id_list：class id of all the scheduled classes
        """
        if class_count > 12:  # limit maxinum class schedule one time <= 12
            raise ValueError("Only can schedule <=12 classes one time, current value is %d" % (class_count))
        class_type_list = self.get_class_type()
        class_type_dict = [x for x in class_type_list if x['classTypeId'] == class_type][0]

        # generate params from class_type_dict for api calls
        service_type = class_type_dict['serviceType']
        service_subtype = class_type_dict['serviceSubType']
        level = class_type_dict['level']
        partner = class_type_dict['partner']
        market = class_type_dict['market']
        language = class_type_dict['language']
        teaching_item = class_type_dict['teachingItem']
        evc_server = class_type_dict['evcServer']
        duration = class_type_dict['duration']
        center_code = get_teacher_center(teacher_member_id)

        # allocate class and get the allocated class id list
        class_id_list = []
        for i in range(1, class_count + 1):
            class_id = \
                self.allocate_class(service_type, service_subtype, level, partner, market, language, teaching_item,
                                    evc_server,
                                    duration,
                                    start_time=calculate_time_range(start_time, class_type_dict['duration'], i)[0],
                                    end_time=calculate_time_range(start_time, class_type_dict['duration'], i)[1],
                                    center_code=center_code, source_type_Code='Allocated')[0]['classId']
            class_id_list.append(class_id)

        # set availability for teacher
        self.set_availability(teacher_member_id, calculate_time_range(start_time, class_type_dict['duration'], 1)[0],
                              calculate_time_range(start_time, class_type_dict['duration'], class_count)[1])

        # assign class from the class id list to teacher
        for class_id in class_id_list:
            self.assign_class(class_id, teacher_member_id)
        return class_id_list
