import { render, screen } from '@testing-library/react'
import StatisticsDisplay from '../../components/StatisticsDisplay'
import { describe, it, expect } from 'vitest'
import { NTPData } from '../../utils/types'
import '@testing-library/jest-dom'

describe('StatisticsDisplay', () => {
  const mockData = new Map<string, NTPData[]>([
    [
      'time.apple.com',
      [
        { RTT: 10, offset: 2},
        { RTT: 20, offset: 4},
        { RTT: 30, offset: 6},
      ] as NTPData[],
    ],
    [
      'time.google.com',
      [
        { RTT: 5, offset: 3},
        { RTT: 17, offset: 3},
      ] as NTPData[],
    ],
  ])

  it('renders nothing if data is null', () => {
    const { container } = render(
      <StatisticsDisplay data={null} selectedMeasurement="RTT" />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders statistics for each server using selected measurement', () => {
    render(<StatisticsDisplay data={mockData} selectedMeasurement="RTT" />)

    expect(screen.getByText('time.google.com')).toBeInTheDocument()
    expect(screen.getByText('time.apple.com')).toBeInTheDocument()

    expect(screen.getByText('10.000 ms')).toBeInTheDocument() // min RTT for time.google.com
    expect(screen.getByText('30.000 ms')).toBeInTheDocument() // max RTT for time.google.com
    expect(screen.getByText('20.000 ms')).toBeInTheDocument() // mean RTT for time.google.com

    expect(screen.getByText('5.000 ms')).toBeInTheDocument() // min RTT for time.apple.com
    expect(screen.getByText('17.000 ms')).toBeInTheDocument() // max RTT for time.apple.com
    expect(screen.getByText('11.000 ms')).toBeInTheDocument() // mean RTT for time.apple.com
  })

  it('correctly switches measurement type', () => {
    render(<StatisticsDisplay data={mockData} selectedMeasurement="offset" />)


    expect(screen.getByText('2.000 ms')).toBeInTheDocument() // min offset for time.google.com
    expect(screen.getByText('6.000 ms')).toBeInTheDocument() // max offset for time.google.com
    expect(screen.getByText('4.000 ms')).toBeInTheDocument() // mean offset for time.google.com


    expect(screen.getAllByText('3.000 ms').length).toBe(3) // offsets for time.apple.com, all 3

  })
})