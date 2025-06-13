import { expect, test } from 'vitest'
import { calculateStatus } from '../utils/calculateStatus'
import { NTPData } from '../utils/types'
test('Passing Data', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 0.0001,
        RTT: 0.0004,
        stratum: 1,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: null,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('PASSING')
})

test('Passing Data with jitter', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 0.0001,
        RTT: 0.0004,
        stratum: 1,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: 0.00002,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('PASSING')
})

test('Unstable Data 1', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 1000,
        RTT: 40,
        stratum: 2,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: null,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test ('Unstable Data 2', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 200,
        RTT: 120,
        stratum: 2,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: null,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test ('Unstable Data 3', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 600,
        RTT: 120,
        stratum: 2,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: null,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test ('Unstable Data 4', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 600,
        RTT: 120,
        stratum: 2,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: 5,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test('Failing Data', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 600,
        RTT: 120,
        stratum: 4,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: null,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('FAILING')
})

test('Failing Data with jitter', () => {
    const data: NTPData = {
        ntp_version: 4,
        vantage_point_ip: "192.0.2.1",
        ip: "203.0.113.10",
        server_name: "time.example.net",
        is_anycast: false,
        country_code: "US",
        coordinates: [37.7749, -122.4194],
        ntp_server_ref_parent_ip: "198.51.100.1",
        ref_id: "GPS",
        client_sent_time: [1718277600, 123456789],
        server_recv_time: [1718277600, 123556789],
        server_sent_time: [1718277600, 123656789],
        client_recv_time: [1718277600, 123756789],
        offset: 600,
        RTT: 120,
        stratum: 4,
        precision: -20,
        root_delay: 0.00003,
        poll: 6,
        root_dispersion: 0.00008,
        ntp_last_sync_time: [1718277500, 0],
        leap: 0,
        jitter: 12,
        nr_measurements_jitter: 12,
        time: 1718277600.1238
    }
    expect(calculateStatus(data)).toBe('FAILING')
})