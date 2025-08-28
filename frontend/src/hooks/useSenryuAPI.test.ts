import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSenryuAPI } from './useSenryuAPI'
import type { DetectResponse } from '../types/api'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

const mockSuccessResponse: DetectResponse = {
  success: true,
  text: '古池や蛙飛び込む水の音',
  results: [
    {
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
  ],
  count: 1
}

describe('useSenryuAPI', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    // Mock the global constant for tests
    ;(globalThis as any).__API_BASE_URL__ = 'http://localhost:8000'
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('initial state is correct', () => {
    const { result } = renderHook(() => useSenryuAPI())

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
    expect(typeof result.current.detect).toBe('function')
    expect(typeof result.current.clearError).toBe('function')
  })

  it('successful API call updates state correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuccessResponse,
    })

    const { result } = renderHook(() => useSenryuAPI())

    let response: DetectResponse | undefined
    await act(async () => {
      response = await result.current.detect('古池や蛙飛び込む水の音')
    })

    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/detect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: '古池や蛙飛び込む水の音',
        only_valid: false,
      }),
    })

    expect(response).toEqual(mockSuccessResponse)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
  })

  it('sends only_valid parameter correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuccessResponse,
    })

    const { result } = renderHook(() => useSenryuAPI())

    await act(async () => {
      await result.current.detect('テスト', true)
    })

    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/detect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: 'テスト',
        only_valid: true,
      }),
    })
  })

  it('handles HTTP error response correctly', async () => {
    const errorResponse = {
      success: false,
      error: 'テキストが空です',
      detail: 'Empty text provided'
    }

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => errorResponse,
    })

    const { result } = renderHook(() => useSenryuAPI())

    await act(async () => {
      try {
        await result.current.detect('')
      } catch (error) {
        expect(error).toBeInstanceOf(Error)
        expect((error as Error).message).toBe('テキストが空です')
      }
    })

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe('テキストが空です')
  })

  it('handles network error correctly', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useSenryuAPI())

    await act(async () => {
      try {
        await result.current.detect('テスト')
      } catch (error) {
        expect(error).toBeInstanceOf(Error)
        expect((error as Error).message).toBe('Network error')
      }
    })

    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe('Network error')
  })

  it('clearError resets error state', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Test error'))

    const { result } = renderHook(() => useSenryuAPI())

    // Trigger an error
    await act(async () => {
      try {
        await result.current.detect('テスト')
      } catch {
        // Error is expected
      }
    })

    expect(result.current.error).toBe('Test error')

    // Clear the error
    act(() => {
      result.current.clearError()
    })

    expect(result.current.error).toBe(null)
  })

  it('sets loading state during API call', async () => {
    let resolvePromise: (value: any) => void
    const pendingPromise = new Promise(resolve => {
      resolvePromise = resolve
    })

    mockFetch.mockReturnValueOnce(pendingPromise)

    const { result } = renderHook(() => useSenryuAPI())

    // Start the API call
    act(() => {
      result.current.detect('テスト')
    })

    // Check loading state is true
    expect(result.current.loading).toBe(true)

    // Resolve the promise
    await act(async () => {
      resolvePromise!({
        ok: true,
        json: async () => mockSuccessResponse,
      })
    })

    // Check loading state is false
    expect(result.current.loading).toBe(false)
  })
})
