from ipaddress import IPv6Address, IPv4Address, ip_address

from server.app.models.NtpExtraDetails import NtpExtraDetails
from server.app.models.NtpMainDetails import NtpMainDetails
from server.app.models.NtpMeasurement import NtpMeasurement
from server.app.models.NtpServerInfo import NtpServerInfo
from server.app.models.NtpTimestamps import NtpTimestamps
from server.app.models.PreciseTime import PreciseTime

def test_calculate_float_time():
    t = PreciseTime(10000, 2**29)
    assert round(t.calculate_float_time(),8) == 10000 + 2**(-3)
def test_same_time():
    t = PreciseTime(10000, 10000)
    times = NtpTimestamps(t,t,t,t)
    assert times.calculate_offset() == 0.0
    assert times.calculate_delay() == 0.0

def test_DifferentTimesOffset():
    t1 = PreciseTime(10000, 0)
    t2 = PreciseTime(10002, 2**27)
    t3 = PreciseTime(10003, 10000)
    t4 = PreciseTime(10004, 10000)
    times = NtpTimestamps(t1,t2,t3,t4)
    #2^26/2^32=2^-6
    assert round(times.calculate_offset(),14) == 0.5+2**(-6)

def test_DifferentTimesDelay():
    t1 = PreciseTime(10000, 0)
    t2 = PreciseTime(10002, 0)
    t3 = PreciseTime(10003, 0)
    t4 = PreciseTime(10004, 2**27)
    times = NtpTimestamps(t1,t2,t3,t4)
    #2^27/2^32=2^-5
    assert round(times.calculate_delay(),14) == 3-2**(-5)


def test_create_object():
    t1 = PreciseTime(10000, 0)
    t2 = PreciseTime(10002, 2**27)
    t3 = PreciseTime(10003, 10000)
    t4 = PreciseTime(10004, 10000)
    server_details=NtpServerInfo(3,IPv4Address('192.0.2.1'),"local",IPv6Address('2001:db8::1'),"reference")
    times = NtpTimestamps(t1,t2,t3,t4)
    maindetails = NtpMainDetails(0.009,0,1,0,"stable")
    extra=NtpExtraDetails(PreciseTime(100000,0),PreciseTime(100000,0),0)
    extraInvalid=NtpExtraDetails(PreciseTime(100000,0),PreciseTime(100000,0),3)

    m=NtpMeasurement(server_details,times,maindetails,extra)

    assert m.extra_details.is_valid() == True
    assert extraInvalid.is_valid() == False

