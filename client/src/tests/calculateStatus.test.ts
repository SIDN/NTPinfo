import { expect, test } from 'vitest'
import { calculateStatus } from '../utils/calculateStatus'
import { NTPData } from '../utils/types'
test('Passing Data', () => {
    const data: NTPData = {
        offset: 0.001,
        RTT: 0.001,
        stratum: 1,
        jitter: null,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('PASSING')
})

test('Passing Data with jitter', () => {
    const data: NTPData = {
        offset: 0.001,
        RTT: 0.001,
        stratum: 1,
        jitter: 0.0000000001,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('PASSING')
})

test('Unstable Data', () => {
    const data: NTPData = {
        offset: -0.3,
        RTT: 0.05,
        stratum: 3,
        jitter: null,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test('Unstable Data with jitter', () => {
    const data: NTPData = {
        offset: -0.3,
        RTT: 0.05,
        stratum: 3,
        jitter: 0.01,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('UNSTABLE')
})

test('Failing Data', () => {
    const data: NTPData = {
        offset: -0.51,
        RTT: 0.11,
        stratum: 4,
        jitter: null,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('FAILING')
})

test('Failing Data with jitter', () => {
    const data: NTPData = {
        offset: -0.51,
        RTT: 0.11,
        stratum: 4,
        jitter: 0.5,
        precision: 2,
        time: 233232322,
        ip: "123.12.29.90",
        server_name: "time.apple.com",
        ref_id: "GPSs",
        root_dispersion: 0,
        root_delay: 0,
        vantage_point_ip: ""
    }
    expect(calculateStatus(data)).toBe('FAILING')
})