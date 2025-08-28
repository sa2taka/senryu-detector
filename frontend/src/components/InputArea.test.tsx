import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { InputArea } from './InputArea'

describe('InputArea', () => {
  it('renders input area with placeholder', () => {
    const mockOnSubmit = vi.fn()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    expect(screen.getByPlaceholderText('俳句・川柳を入力してください（Enterキーで検出）')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '俳句検出' })).toBeInTheDocument()
  })

  it('calls onSubmit when form is submitted', async () => {
    const mockOnSubmit = vi.fn()
    const user = userEvent.setup()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: '俳句検出' })

    await user.type(textarea, '古池や蛙飛び込む水の音')
    await user.click(button)

    expect(mockOnSubmit).toHaveBeenCalledWith('古池や蛙飛び込む水の音')
  })

  it('calls onSubmit when Enter key is pressed', async () => {
    const mockOnSubmit = vi.fn()
    const user = userEvent.setup()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByRole('textbox')

    await user.type(textarea, '夏草や兵どもが夢の跡')
    await user.keyboard('{Enter}')

    expect(mockOnSubmit).toHaveBeenCalledWith('夏草や兵どもが夢の跡')
  })

  it('does not call onSubmit when Shift+Enter is pressed', async () => {
    const mockOnSubmit = vi.fn()
    const user = userEvent.setup()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByRole('textbox')

    await user.type(textarea, 'テスト')
    await user.keyboard('{Shift>}{Enter}{/Shift}')

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('disables input and button when loading', () => {
    const mockOnSubmit = vi.fn()
    render(<InputArea onSubmit={mockOnSubmit} loading={true} />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: '検出中...' })

    expect(textarea).toBeDisabled()
    expect(button).toBeDisabled()
  })

  it('does not submit when text is empty or only whitespace', async () => {
    const mockOnSubmit = vi.fn()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    const button = screen.getByRole('button', { name: '俳句検出' })

    // Empty text - button should be disabled
    expect(button).toBeDisabled()

    // Check button is enabled after typing and disabled again after clearing
    const textarea = screen.getByRole('textbox')
    fireEvent.change(textarea, { target: { value: 'テスト' } })
    expect(button).toBeEnabled()

    fireEvent.change(textarea, { target: { value: '   ' } })
    expect(button).toBeDisabled()
  })

  it('trims whitespace from input before submitting', async () => {
    const mockOnSubmit = vi.fn()
    const user = userEvent.setup()
    render(<InputArea onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByRole('textbox')
    const button = screen.getByRole('button', { name: '俳句検出' })

    await user.type(textarea, '  閑さや岩にしみ入る蝉の声  ')
    await user.click(button)

    expect(mockOnSubmit).toHaveBeenCalledWith('閑さや岩にしみ入る蝉の声')
  })
})
