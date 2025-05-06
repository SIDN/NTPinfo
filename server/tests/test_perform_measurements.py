from ipaddress import IPv6Address, IPv4Address, ip_address

from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime
from server.app.services.NtpCalculator import NtpCalculator
from server.app.services.NtpValidation import NtpValidation
from server.app.utils.perform_measurements import ntp_precise_time_to_human_date, ref_id_to_ip_or_name


def test_ntp_precise_time_to_human_date():
    t=PreciseTime(None,12345)
    assert ntp_precise_time_to_human_date(t)==""
    t2=PreciseTime(3955513183,623996928)
    assert ntp_precise_time_to_human_date(t2)=="2025-05-06 09:39:43.145286 UTC"

def test_ref_id_to_ip_or_name():
    ip,name=ref_id_to_ip_or_name(1590075150,2)
    assert ip=="5.200.6.34"
    assert name==None