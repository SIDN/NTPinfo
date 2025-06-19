import { expect, test, describe } from 'vitest'
import { dateFormatConversion } from '../../utils/dateFormatConversion'
describe('dateFormatConversion', () => {
  test('Test with time as UTC date', () => {
    const unixTime = Date.UTC(2025, 5, 11, 14, 23, 45) 
    const result = dateFormatConversion(unixTime)
    expect(result).toBe('2025-06-11T14:23:45Z')
  })

  test('Test with time as number', () => {
    const timeWithMilliseconds = 1672531199123 // 2023-01-01T00:59:59.123Z
    const result = dateFormatConversion(timeWithMilliseconds)
    expect(result).toBe('2022-12-31T23:59:59Z')
  })

  test('Test UNIX epoch', () => {
    const result = dateFormatConversion(0)
    expect(result).toBe('1970-01-01T00:00:00Z')
  })


})