import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { SenryuDisplay } from './SenryuDisplay'
import type { DetectionResult } from '../types/api'

const mockValidResult: DetectionResult = {
  pattern: '5-7-5',
  upper_phrase: {
    tokens: [{ surface: '古池', reading: 'フルイケ', mora_count: 4, pos: '名詞' }, { surface: 'や', reading: 'ヤ', mora_count: 1, pos: '助詞' }],
    mora_count: 5,
    text: '古池や',
    reading: 'フルイケヤ'
  },
  middle_phrase: {
    tokens: [{ surface: '蛙', reading: 'カエル', mora_count: 3, pos: '名詞' }, { surface: '飛び込む', reading: 'トビコム', mora_count: 4, pos: '動詞' }],
    mora_count: 7,
    text: '蛙飛び込む',
    reading: 'カエルトビコム'
  },
  lower_phrase: {
    tokens: [{ surface: '水', reading: 'ミズ', mora_count: 2, pos: '名詞' }, { surface: 'の', reading: 'ノ', mora_count: 1, pos: '助詞' }, { surface: '音', reading: 'オト', mora_count: 2, pos: '名詞' }],
    mora_count: 5,
    text: '水の音',
    reading: 'ミズノオト'
  },
  start_position: 0,
  end_position: 11,
  original_text: '古池や蛙飛び込む水の音',
  is_valid: true,
  mora_pattern: [5, 7, 5],
  full_reading: 'フルイケヤカエルトビコムミズノオト',
  is_standard_pattern: true
}

const mockInvalidResult: DetectionResult = {
  pattern: '5-8-5',
  upper_phrase: {
    tokens: [{ surface: '春風', reading: 'ハルカゼ', mora_count: 4, pos: '名詞' }, { surface: 'に', reading: 'ニ', mora_count: 1, pos: '助詞' }],
    mora_count: 5,
    text: '春風に',
    reading: 'ハルカゼニ'
  },
  middle_phrase: {
    tokens: [{ surface: 'ぽっぽー', reading: 'ポッポー', mora_count: 4, pos: '感動詞' }, { surface: 'という', reading: 'トイウ', mora_count: 4, pos: '助詞' }],
    mora_count: 8,
    text: 'ぽっぽーという',
    reading: 'ポッポートイウ'
  },
  lower_phrase: {
    tokens: [{ surface: '汽笛', reading: 'キテキ', mora_count: 3, pos: '名詞' }, { surface: 'が', reading: 'ガ', mora_count: 1, pos: '助詞' }, { surface: '聞こえる', reading: 'キコエル', mora_count: 4, pos: '動詞' }],
    mora_count: 8,
    text: '汽笛が聞こえる',
    reading: 'キテキガキコエル'
  },
  start_position: 0,
  end_position: 14,
  original_text: '春風にぽっぽーという汽笛が聞こえる',
  is_valid: false,
  mora_pattern: [5, 8, 8],
  full_reading: 'ハルカゼニポッポートイウキテキガキコエル',
  is_standard_pattern: false
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
