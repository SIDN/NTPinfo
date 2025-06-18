import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { TimeInput } from '../../components/TimeInput'
import '@testing-library/jest-dom'

describe('TimeInput', () => {
  const mockOnSelectionChange = vi.fn()
  const mockOnFromChange = vi.fn()
  const mockOnToChange = vi.fn()

  const defaultProps = {
    options: ['Last Day', 'Last Week', 'Last Hour', 'Custom'],
    selectedOption: 'Last Day',
    customFrom: '',
    customTo: '',
    onSelectionChange: mockOnSelectionChange,
    onFromChange: mockOnFromChange,
    onToChange: mockOnToChange,
  }

  test('Render Drodpwon with correct options', () => {
    render(<TimeInput {...defaultProps} />)
    const select = screen.getByRole('combobox')
    expect(select).toBeInTheDocument()

    const options = screen.getAllByRole('option')
    expect(options.length).toBe(4)
    expect(options.map(opt => opt.textContent)).toEqual(defaultProps.options)
  })

  test('Call onSelectionChange', () => {
    render(<TimeInput {...defaultProps} />)
    const select = screen.getByRole('combobox')

    fireEvent.change(select, { target: { value: 'Custom' } })
    expect(mockOnSelectionChange).toHaveBeenCalledWith('Custom')
  })

  test('Show From and To if Custom is selected', () => {
    render(<TimeInput {...defaultProps} selectedOption="Custom" />)
    expect(screen.getByLabelText(/From/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/To/i)).toBeInTheDocument()
  })

  test('Call onToChange and onFromChange', () => {
    render(<TimeInput {...defaultProps} selectedOption="Custom" />)

    const fromInput = screen.getByLabelText(/From/i) 
    const toInput = screen.getByLabelText(/To/i) 

    fireEvent.change(fromInput, { target: { value: '2025-06-01T10:00' } })
    fireEvent.change(toInput, { target: { value: '2025-06-02T18:30' } })

    expect(mockOnFromChange).toHaveBeenCalledWith('2025-06-01T10:00')
    expect(mockOnToChange).toHaveBeenCalledWith('2025-06-02T18:30')
  })
})