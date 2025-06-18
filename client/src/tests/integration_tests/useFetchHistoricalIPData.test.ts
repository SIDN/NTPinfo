import { renderHook, act } from '@testing-library/react'
import { useFetchIPData } from '../../hooks/useFetchIPData'
import { waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { NTPData } from '../../utils/types'
import axios from 'axios'

vi.mock('./transformJSONDataToNTPData', () => ({
  transformJSONDataToNTPData: (data: any) => {
    console.log('Mock transformJSONDataToNTPData called with:', data);
    return { ...data, transformed: true }
  },
}))

describe('useFetchIPData', () => {
    it('fetches and sets measurement data correctly', async () => {
        const { result } = renderHook(() => useFetchIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/', { server: 'time.apple.com', ipv6_measurement:false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.httpStatus).toBe(200)
        expect(result.current.error).toBeNull()
        expect(result.current.data).toEqual(expected)
    })
})