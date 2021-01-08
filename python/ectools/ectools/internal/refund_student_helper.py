from ectools.config import config
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.logger import get_logger
from requests import Session

S18_REFUND_URL = '{}/services/oboe2/SalesForce/Test/S18Refund'
DEACTIVATE_PACKAGE_URL = '{}/services/oboe2/SalesForce/Test/DeactivatePack'


class RefundType:
    REFUND = 'Refund'
    CANCEL = 'Cancel'


class DeactivatePackType:
    FULL = 'Full'
    BY_ORDER = 'ByOrder'
    BY_ORDER_PRODUCT = 'ByOrderProduct'


def refund_smart_plus_student(student_id, refund_type):
    """
    refund S18/Smart Plus student
    coupon will be extended after refund student,
    coupon will NOT be extended after cancel student.
    """
    assert student_id is not None
    url = S18_REFUND_URL.format(config.etown_root)
    data = {"MemberId": student_id, "RefundType": refund_type}
    result = Session().post(url, json=data)
    assert result.status_code == HTTP_STATUS_OK, result.text

    if 'Success' in result.text:
        get_logger().info('{0} student:{1} success!'.format(refund_type, student_id))
    else:
        get_logger().info('{0} student:{1} failed!'.format(refund_type, student_id))


def deactivate_phoenix_student(student_id, order_id=None, order_product_id=None, deactivate_pack_type=None):
    """
    deactivate phoenix student
    deactivate_pack_type: has three types, Full means refund this student; ByOrder means refund some order;
    ByOrderProduct means refund pack product.
    All coupon will NOT be extended after refund phoenix pack.
    """
    assert student_id is not None
    url = DEACTIVATE_PACKAGE_URL.format(config.etown_root)
    data = {"MemberId": student_id, "OrderId": order_id, "OrderProductIds": order_product_id,
            "DeactivatePackageType": deactivate_pack_type}
    result = Session().post(url, json=data)
    assert result.status_code == HTTP_STATUS_OK, result.text

    if 'Success' in result.text:
        get_logger().info('Deactivate {0} student:{1} success!'.format(deactivate_pack_type, student_id))
    else:
        get_logger().info('Deactivate {0} student:{1} failed!'.format(deactivate_pack_type, student_id))

