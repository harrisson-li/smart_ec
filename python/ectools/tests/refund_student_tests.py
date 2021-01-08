from ectools.config import set_environment
from ectools.internal.refund_student_helper import *


def test_refund_smart_plus():
    set_environment('qacn')
    refund_smart_plus_student(200000987, RefundType.CANCEL)
    refund_smart_plus_student(200000977, RefundType.REFUND)


def test_refund_phoenix():
    set_environment('qacn')
    deactivate_phoenix_student(200000984, deactivate_pack_type=DeactivatePackType.FULL)

