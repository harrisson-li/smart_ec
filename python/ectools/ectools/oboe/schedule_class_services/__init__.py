from ectools.config import *
from ectools.internal.business.enums import Partners
from ectools.internal.data_helper import get_school_by_name
from ectools.internal.objects import Cache
from .schedule_class_topic_service import schedule_class_topic, schedule_class_topic_if_needed
from .schedule_offsite_class_service import schedule_offsite_class
from .schedule_regular_class_service import schedule_regular_class
from ..utils import ClassCategory


def schedule_class(**kwargs):
    """
    Main function to schedule class.

    For LC and CAE class, you could set keyword args with: schedule_date,
                                                           school_name,
                                                           class_category,
                                                           center_type (default = CenterType.OUTCENTER)

    For other class types, you could set keyword args with: schedule_date,
                                                            school_name,
                                                            class_category,
                                                            class_type (default = None),
                                                            class_topic (default = None),
                                                            is_preview (default = False),
                                                            is_online_attending=False,
                                                            is_vip_class=False

    :param kwargs: more detail please check function doc and unit tests.
    :return: will return the schedule id if success
    """
    if 'school_name' not in kwargs:
        student = Cache.get_current_student()
        kwargs['school_name'] = student.school.name

    class_category = kwargs.get('class_category')

    # If partner is socn, still need to use cool or mini to schedule class,
    # so for schedule class feature, we need to ignore socn
    school = get_school_by_name(kwargs['school_name'], ignore_socn=True)
    partner = school['partner']
    if config.partner == Partners.SOCN:
        set_partner(partner)

    if class_category in [ClassCategory.LC, ClassCategory.CAE]:
        return schedule_offsite_class(**kwargs)
    else:
        return schedule_regular_class(**kwargs)
