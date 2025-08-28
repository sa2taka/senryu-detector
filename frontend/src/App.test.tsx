import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders the main heading', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: '俳句・川柳検出ツール' })).toBeInTheDocument()
  })

  it('renders the description', () => {
    render(<App />)

    expect(screen.getByText('日本語テキストから5-7-5音律の俳句・川柳を検出します')).toBeInTheDocument()
  })

  it('renders the input area', () => {
    render(<App />)

    expect(screen.getByPlaceholderText('俳句・川柳を入力してください（Enterキーで検出）')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '俳句検出' })).toBeInTheDocument()
  })
})
