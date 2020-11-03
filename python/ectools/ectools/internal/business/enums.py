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
    F2F_VIP = "F2F Vip"
    TEACHER_REVIEW = "1:1 Teacher Review"


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
    WAITING_FAILED = "10"
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
    QAHK = 'qahk'


class CouponType:
    # F2F, WS value shows "F2F" and "WS" in oboe -> adjust coupon page, hence add another F2F, WS to separate
    F2F = 'F2F'
    Face2Face = 'Face to Face'
    F2FPL20 = 'F2F/PL20'
    WORKSHOP = 'Workshop'
    WS = 'WS'
    APPLY = 'Apply'
    EF_EVENTS = 'EF Events'
    LC = 'LC'
    Life_Club = 'Life Club'
    LifeClub = 'LifeClub'
    BB = 'BB'
    PL20 = 'PL20'
    PL40 = 'PL40'
    GL = 'GL'
    OnlinePL = 'Online Private Class'
    OnlineGL = 'Online Group Class'
    BBv2 = 'BBv2'
    Beginner_Basics = 'Beginner Basics'
    Beginner_Basics_v2 = 'Beginner Basics'
    BBPL = 'BBPL'
    BBC = 'BBC'
    L0WS = 'L0WS'
    LCApply = 'LCApply'
    CareerWorkshop = 'CareerWorkshop'
    Career_Track = 'Career Track'
    Skills = 'Skills'
    Skills_Clinics = 'Skills Clinics'
    OSC = 'OSC'
    TeacherReview = '1:1 Teacher Review'
    EEA = 'EEA'


class StageName:
    BEGINNER = 'BEGINNER'
    BEGINNER_LOW = 'BEGINNER LOW'
    BEGINNER_STARTER = 'BEGINNER STARTER'
    BEGINNER_HIGH = 'BEGINNER HIGH'
    ELEMENTARY = 'ELEMENTARY'
    INTERMEDIATE = 'INTERMEDIATE'
    UPPER_INTERMEDIATE = 'UPPER INTERMEDIATE'
    ADVANCED = 'ADVANCED'
    UPPER_ADVANCED = 'UPPER ADVANCED'


class Timezone:
    UTC = "UTC"
    CHINA = "Asia/Shanghai"
    MOSCOW = "Europe/Moscow"
    JAKARTA = "Asia/Bangkok"
    BOSTON = "America/New_York"
    MADRID = "Europe/Madrid"
