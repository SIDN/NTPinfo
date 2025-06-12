import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { downloadJSON, downloadCSV } from '../utils/downloadFormats'
import type { NTPData, RIPEData } from '../utils/types'

describe('Test Download Formats', () => {
  const mockCreateObjectURL = vi.fn(() => 'blob:http://localhost/blobid')
  const mockRevokeObjectURL = vi.fn()
  const mockClick = vi.fn()

  beforeEach(() => {
    // Stub URL methods
    vi.stubGlobal('URL', {
      createObjectURL: mockCreateObjectURL,
      revokeObjectURL: mockRevokeObjectURL,
    })

    // Stub document.createElement and mock <a> click
    vi.stubGlobal('document', {
      ...document,
      createElement: vi.fn(() => ({
        href: '',
        download: '',
        click: mockClick,
      })),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  const ntpData: NTPData = {
    offset: 1,
    RTT: 2,
    stratum: 1,
    jitter: null,
    precision: 10,
    time: 1700000000000,
    ip: '192.168.0.1',
    server_name: 'random',
    ref_id: '1234',
    root_dispersion: 1,
    root_delay: 1,
    vantage_point_ip: '1.1.1.1',
    coordinates: [50.262, 4.333],
    country_code: "DE"
  }

  const ripeData: RIPEData = {
    measurementData: ntpData,
    probe_id: 42,
    probe_country: 'NL',
    probe_location: [52.37, 4.89],
    got_results: true,
    measurement_id: 123456,
  }

  test('Test Download JSON file', () => {
    downloadJSON([ntpData, ripeData])
    expect(mockCreateObjectURL).toHaveBeenCalled()
    expect(mockClick).toHaveBeenCalled()
    expect(mockRevokeObjectURL).toHaveBeenCalled()
  })

  test('Test Download CSV file', () => {
    downloadCSV([ntpData, ripeData])
    expect(mockCreateObjectURL).toHaveBeenCalled()
    expect(mockClick).toHaveBeenCalled()
    expect(mockRevokeObjectURL).toHaveBeenCalled()
  })
})