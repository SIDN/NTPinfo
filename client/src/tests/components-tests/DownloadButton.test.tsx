import { render, screen, fireEvent } from '@testing-library/react'
import DownloadButton from '../../components/DownloadButton'
import { describe, test, expect, vi } from 'vitest'
import '@testing-library/jest-dom'

describe('DownloadButton', () => {
  test('Render button with correct name', () => {
    render(<DownloadButton name="Download CSV" onclick={() => {}} />)
    expect(screen.getByText('Download CSV')).toBeInTheDocument()
  })

  test('Trigger onClick on button press', () => {
    const handleClick = vi.fn()
    render(<DownloadButton name="Download" onclick={handleClick} />)

    fireEvent.click(screen.getByText('Download'))
    expect(handleClick).toHaveBeenCalled()
  })
})