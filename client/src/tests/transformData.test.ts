import { expect, test, describe } from 'vitest'
import { transformJSONDataToNTPData } from '../utils/transformJSONDataToNTPData'
import { transformJSONDataToRIPEData } from '../utils/transformJSONDataToRIPEData'

describe("transform JSON Data to NTP Data", () => {
    test("tranform to NTP Data", () => {
    const fetchedData = {
            offset: 0.001,
            rtt: 0.001,
            stratum: 1,
            jitter: null,
            precision: 2,
            client_sent_time:{seconds: 233232322},
            ntp_server_ip: "123.12.29.90",
            ntp_server_name: "time.apple.com",
            ref_name: "GPSs",
            root_dispersion: 0,
            root_delay: 0,
            vantage_point_ip: "1.1.1.1"
        }

        const res = transformJSONDataToNTPData(fetchedData)

        expect(res?.offset).toBe(fetchedData.offset)
        expect(res?.RTT).toBe(fetchedData.rtt)
        expect(res?.stratum).toBe(fetchedData.stratum)
        expect(res?.jitter).toBeNull()
        expect(res?.precision).toBe(fetchedData.precision)
        expect(res?.time).toBe((fetchedData.client_sent_time.seconds - 2208988800) * 1000)
        expect(res?.ip).toBe(fetchedData.ntp_server_ip)
        expect(res?.server_name).toBe(fetchedData.ntp_server_name)
        expect(res?.ref_id).toBe(fetchedData.ref_name)
        expect(res?.root_delay).toBe(fetchedData.root_delay)
        expect(res?.root_dispersion).toBe(fetchedData.root_dispersion)
        expect(res?.vantage_point_ip).toBe(fetchedData.vantage_point_ip)
    })

    test("Return null on null input", () => {
        expect(transformJSONDataToNTPData(null)).toBeNull()
    })
})

describe('transform JSOn Data to RIPE Data', () => {
    test("tranform to RIPE Data Success", () => {
    const input = {
      result: [
        {
          offset: 0.00123,
          rtt: 0.00456,
          client_sent_time: { seconds: 3792998400 }
        }
      ],
      stratum: 2,
      jitter: 0.0002,
      precision: -20,
      ntp_server_ip: "192.0.2.1",
      ntp_server_name: "ntp.example.com",
      ref_id: "GPS",
      root_dispersion: 0.1,
      root_delay: 0.05,
      probe_addr: { ipv4: "203.0.113.5" },
      probe_id: 12345,
      probe_location: {
        country_code: "NL",
        coordinates: [4.895168, 52.370216]
      },
      ripe_measurement_id: 67890
    }

    const result = transformJSONDataToRIPEData(input)

    expect(result).not.toBeNull()
    expect(result!.measurementData.offset).toBeCloseTo(1.23)
    expect(result!.measurementData.RTT).toBeCloseTo(4.56)
    expect(result!.measurementData.time).toBe((3792998400 - 2208988800) * 1000)
    expect(result!.got_results).toBe(true)
    expect(result!.probe_id).toBe(12345)
    expect(result!.probe_country).toBe("NL")
    expect(result!.probe_location).toEqual([52.370216, 4.895168])
  })

  test('Return null on null input', () => {
    expect(transformJSONDataToRIPEData(null)).toBeNull()
  })

  test('Return null on empty input or result', () => {
    expect(transformJSONDataToRIPEData({})).toBeNull()
    expect(transformJSONDataToRIPEData({ result: [] })).toBeNull()
  })
})

