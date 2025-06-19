import { render, screen, fireEvent } from '@testing-library/react'
import ConsentPopup from '../../components/ConsentPopup'
import { describe, test, expect, beforeEach } from 'vitest'
import '@testing-library/jest-dom'

describe('ConsentPopup', () => {
  beforeEach(() => {
    sessionStorage.clear() // start cleanly
  })

  test('Show popup if consent not given', () => {
    render(<ConsentPopup />)
    expect(screen.getByText(/privacy notice/i)).toBeInTheDocument()
    expect(screen.getByText(/I consent/i)).toBeInTheDocument()
  })

  test('Do not show popup is consent given', () => {
    sessionStorage.setItem('consentGiven', 'true')
    render(<ConsentPopup />)
    expect(screen.queryByText(/privacy notice/i)).not.toBeInTheDocument()
  })

  test('Hide popup on button click', () => {
    render(<ConsentPopup />)
    const consentButton = screen.getByText(/I consent/i)
    fireEvent.click(consentButton)

    expect(sessionStorage.getItem('consentGiven')).toBe('true')
    expect(screen.queryByText(/privacy notice/i)).not.toBeInTheDocument()
  })
})