class ClassCategory:
    F2F = "F2F"
    FACE_2_FACE = "Face to Face"
    WORKSHOP = "Workshop"
    SKILL_WORKSHOP = "Skill Workshop"
    APPLY = "Apply"
    BUSINESS_ENGLISH = "Business English"
    LC = "LC"
    CAE = "CA"
    LIFE_CLUB = "Life Club"
    CA_EVENT = "CA Event"
    CA_SEMINAR = "CA Seminar"
    BEGINNER_BASICS = "Beginner Basics"
    BEGINNER_LC = "Beginner Life Club"
    CAS = "CA Seminar"
    ENGLISH_CORNER = "English_Corner"
    BUSINESS_ENGLISH_WORKSHOP = "Business English Workshop"
    CAREER_TRACK = "Career Track"
    SKILLS_CLINICS = "Skills Clinics"
    BBv2 = "BBv2"
    BEGINNER_BASICS_v2 = "Beginner Basics v2"


class Attribute:
    NAME = "name"
    CLASS = "class"
    VALUE = "value"
    STYLE = "style"
    CHECKED = "checked"


class PageResponseStatus:
    SUCCESS = 200
    NOT_FOUND = 404


class Partners:
    CEHK = "Cehk"
    COOL = "Cool"
    MINI = "Mini"
    RUPE = "Rupe"
    INDO = "Indo"
    ECSP = "Ecsp"
    EAPS = "Eaps"
    SOCN = 'Socn'


class CenterType:
    # used for LC and CAE center type chosen
    INCENTER = "InCenter"
    OUTCENTER = "OutCenter"


class ClassStatus:
    CHECK_IN = 'Checkin'
    NO_SHOW = 'NoShow'
    NO_SHOW_LATE = 'NoShowLate'
    CANCELLED = 'Cancelled'
    WAITING = 'Waiting'
    BOOKED = 'Booked'
    WAIT_FAILED = 'WaitFailed'
    STANDBY = 'Standby'
    TENTATIVELY_BOOKED = 'TentativelyBooked'


class ClassBookingStatusId:
    EMPTY = "0"
    BOOKED = "1"
    CHECK_IN = "2"
    NO_SHOW = "3"
    CANCELLED = "4"
    WAITING = "6"
    NO_SHOW_LATE = "8"
    TENTATIVELY_BOOKED = "11"
    STAND_BY = "12"


class Environments(object):
    UAT = "uat"
    UATCN = 'uatcn'
    QA = "qa"
    QACN = 'qacn'
    STAGING = "staging"
    STAGINGCN = 'stagingcn'
    LIVE = "live"
