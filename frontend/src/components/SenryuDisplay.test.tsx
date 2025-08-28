import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SenryuDisplay } from './SenryuDisplay'
import type { DetectionResult } from '../types/api'

const mockValidResult: DetectionResult = {
  text: '古池や蛙飛び込む水の音',
  pattern: '5-7-5',
  mora_counts: [5, 7, 5],
  is_valid: true,
  confidence: 0.95,
  segments: [
    { text: '古池や', mora_count: 5 },
    { text: '蛙飛び込む', mora_count: 7 },
    { text: '水の音', mora_count: 5 }
  ]
}

const mockInvalidResult: DetectionResult = {
  text: '春風にぽっぽーという汽笛が聞こえる',
  pattern: '5-8-5',
  mora_counts: [5, 8, 5],
  is_valid: false,
  confidence: 0.75,
  segments: [
    { text: '春風に', mora_count: 5 },
    { text: 'ぽっぽーという', mora_count: 8 },
    { text: '汽笛が聞こえる', mora_count: 5 }
  ]
}

describe('SenryuDisplay', () => {
  it('shows no results message when results are empty', () => {
    render(<SenryuDisplay results={[]} originalText="テスト文章" />)

    expect(screen.getByText('検出結果')).toBeInTheDocument()
    expect(screen.getByText('「テスト文章」からは俳句・川柳が検出されませんでした。')).toBeInTheDocument()
  })

  it('displays valid senryu result correctly', () => {
    render(<SenryuDisplay results={[mockValidResult]} originalText="古池や蛙飛び込む水の音" />)

    expect(screen.getByText('検出結果 (1件)')).toBeInTheDocument()
    expect(screen.getByText('5-7-5')).toBeInTheDocument()
    expect(screen.getByText('信頼度: 95.0%')).toBeInTheDocument()
    expect(screen.getByText('✓ 有効')).toBeInTheDocument()

    // Check segments
    expect(screen.getByText('古池や')).toBeInTheDocument()
    expect(screen.getAllByText('5音')).toHaveLength(2) // First and third segments both have 5音
    expect(screen.getByText('蛙飛び込む')).toBeInTheDocument()
    expect(screen.getByText('7音')).toBeInTheDocument()
    expect(screen.getByText('水の音')).toBeInTheDocument()

    // Check full text display
    expect(screen.getByText('"古池や蛙飛び込む水の音"')).toBeInTheDocument()
    expect(screen.getByText('5-7-5音律')).toBeInTheDocument()
  })

  it('displays invalid senryu result correctly', () => {
    render(<SenryuDisplay results={[mockInvalidResult]} originalText="春風にぽっぽーという汽笛が聞こえる" />)

    expect(screen.getByText('検出結果 (1件)')).toBeInTheDocument()
    expect(screen.getByText('5-8-5')).toBeInTheDocument()
    expect(screen.getByText('信頼度: 75.0%')).toBeInTheDocument()
    expect(screen.getByText('⚠ 字余り')).toBeInTheDocument()

    // Check segments
    expect(screen.getByText('春風に')).toBeInTheDocument()
    expect(screen.getAllByText('5音')).toHaveLength(2) // First and third segments both have 5音
    expect(screen.getByText('ぽっぽーという')).toBeInTheDocument()
    expect(screen.getByText('8音')).toBeInTheDocument()
    expect(screen.getByText('汽笛が聞こえる')).toBeInTheDocument()

    // Check full text display
    expect(screen.getByText('"春風にぽっぽーという汽笛が聞こえる"')).toBeInTheDocument()
    expect(screen.getByText('5-8-5音律')).toBeInTheDocument()
  })

  it('displays multiple results correctly', () => {
    const results = [mockValidResult, mockInvalidResult]
    render(<SenryuDisplay results={results} originalText="複数の俳句" />)

    expect(screen.getByText('検出結果 (2件)')).toBeInTheDocument()

    // Check both results are displayed
    expect(screen.getByText('✓ 有効')).toBeInTheDocument()
    expect(screen.getByText('⚠ 字余り')).toBeInTheDocument()
    expect(screen.getByText('"古池や蛙飛び込む水の音"')).toBeInTheDocument()
    expect(screen.getByText('"春風にぽっぽーという汽笛が聞こえる"')).toBeInTheDocument()
  })

  it('applies correct CSS classes for valid and invalid results', () => {
    const results = [mockValidResult, mockInvalidResult]
    const { container } = render(<SenryuDisplay results={results} originalText="テスト" />)

    const resultCards = container.querySelectorAll('.result-card')
    expect(resultCards).toHaveLength(2)
    expect(resultCards[0]).toHaveClass('valid')
    expect(resultCards[1]).toHaveClass('invalid')
  })
})
