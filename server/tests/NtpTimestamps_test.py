from server.app.models import NtpTimestamps
from server.app.models import PreciseTime


def test_calculate_float_time():
    t = PreciseTime(10000, 2**29)
    assert round(t.calculate_float_time,8) == 10000 + 2**(-3)
def test_same_time():
    t = PreciseTime(10000, 10000)
    times = NtpTimestamps(t,t,t,t)
    assert times.calculate_offset() == 0.0
    assert times.calculate_delay() == 0.0

def test_DifferentTimes():
    t1 = PreciseTime(10000, 0)
    t2 = PreciseTime(10002, 2**27)
    t3 = PreciseTime(10003, 10000)
    t4 = PreciseTime(10004, 10000)
    times = NtpTimestamps(t1,t2,t3,t4)
    #2^26/2^32=2^-6
    assert round(times.calculate_offset(),8) == 0.5+2**(-6)