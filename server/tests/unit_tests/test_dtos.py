import pytest
from psycopg.types.net import IPv4Address

from server.app.dtos.ProbeData import ServerLocation
from server.app.dtos.NtpServerInfo import NtpServerInfo
from server.app.dtos.NtpMainDetails import NtpMainDetails
from server.app.dtos.PreciseTime import PreciseTime
from server.app.dtos.NtpExtraDetails import NtpExtraDetails
from server.app.dtos.MeasurementRequest import MeasurementRequest


def test_measurement_request():
    with pytest.raises(TypeError):
        MeasurementRequest(3,True)
    with pytest.raises(TypeError):
        MeasurementRequest("server", 2)

def test_ntp_extra_details():
    # root_delay
    with pytest.raises(TypeError):
        NtpExtraDetails(3, 2, PreciseTime(3, 5), PreciseTime(3, 5), 0)
    # poll
    with pytest.raises(TypeError):
        NtpExtraDetails(PreciseTime(3, 5), "True", PreciseTime(3, 5), PreciseTime(3, 5), 0)
    # root_dispersion
    with pytest.raises(TypeError):
        NtpExtraDetails(3, 2, "PreciseTime(3)", PreciseTime(3, 5), 0)
    # ntp_last_sync_time
    with pytest.raises(TypeError):
        NtpExtraDetails(PreciseTime(3, 5), 3, "PreciseTime(3)", "False", 0)
    # leap
    with pytest.raises(TypeError):
        NtpExtraDetails(PreciseTime(3, 5), 3, PreciseTime(3, 5), PreciseTime(3, 5), "False")
    NtpExtraDetails(PreciseTime(3, 5), 3, PreciseTime(3, 5), PreciseTime(3, 5), 0)

def test_ntp_main_details():
    # offset
    with pytest.raises(TypeError):
        NtpMainDetails("d", 2, 3, 5, "0")
    # rtt
    with pytest.raises(TypeError):
        NtpMainDetails(3, "d", 3, 5, "0")
    # stratum
    with pytest.raises(TypeError):
        NtpMainDetails(3, 2, "-s", 5, "0")
    # precision
    with pytest.raises(TypeError):
        NtpMainDetails(3, 2, 2, "kk", "0")
    # reachability
    with pytest.raises(TypeError):
        NtpMainDetails(3, 2, 2, 2, None)
    NtpMainDetails(3, 2, 2, 2, "")

def test_ntp_server_info():
    # ntp_version
    with pytest.raises(TypeError):
        NtpServerInfo("d", IPv4Address("123.23.34.5"), ServerLocation("DE", (2, 3)), "yes", IPv4Address("123.33.34.5"), "GPS")
    # ntp_server_ip
    with pytest.raises(TypeError):
        NtpServerInfo(3, 3, ServerLocation("DE", (2, 3)), "yes", IPv4Address("123.33.34.5"), "GPS")
    # ntp_server_location
    with pytest.raises(TypeError):
        NtpServerInfo(3, IPv4Address("123.23.34.5"), "no", "yes", IPv4Address("123.33.34.5"), "GPS")
    # ntp_server_name
    with pytest.raises(TypeError):
        NtpServerInfo(3, IPv4Address("123.23.34.5"), ServerLocation("DE", (2, 3)), 9, IPv4Address("123.33.34.5"), "GPS")
    # ntp_server_ref_parent_ip
    with pytest.raises(TypeError):
        NtpServerInfo(3, IPv4Address("123.23.34.5"), ServerLocation("DE", (2, 3)), "yes", "ip", "GPS")
    # ref_name
    with pytest.raises(TypeError):
        NtpServerInfo(3, IPv4Address("123.23.34.5"), ServerLocation("DE", (2, 3)), "yes", IPv4Address("123.33.34.5"), 3)

    NtpServerInfo(3, None, ServerLocation("DE", (2, 3)), "yes", None, "GPS")