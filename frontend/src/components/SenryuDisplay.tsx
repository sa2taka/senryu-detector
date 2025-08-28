import React from 'react';
import type { DetectionResult } from '../types/api';

interface SenryuDisplayProps {
  results: DetectionResult[];
  originalText: string;
}

export const SenryuDisplay: React.FC<SenryuDisplayProps> = ({ results, originalText }) => {
  if (results.length === 0) {
    return (
      <div className="senryu-display">
        <div className="no-results">
          <h3>検出結果</h3>
          <p>「{originalText}」からは俳句・川柳が検出されませんでした。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="senryu-display">
      <h3>検出結果 ({results.length}件)</h3>
      <div className="results-container">
        {results.map((result, index) => (
          <div key={index} className={`result-card ${result.is_valid ? 'valid' : 'invalid'}`}>
            <div className="result-header">
              <span className="pattern-type">{result.pattern}</span>
              <span className="confidence">信頼度: {(result.confidence * 100).toFixed(1)}%</span>
              <span className={`validity ${result.is_valid ? 'valid' : 'invalid'}`}>
                {result.is_valid ? '✓ 有効' : '⚠ 字余り'}
              </span>
            </div>

            <div className="senryu-text">
              <div className="segments">
                {result.segments.map((segment, segIndex) => (
                  <div key={segIndex} className="segment">
                    <div className="segment-text">{segment.text}</div>
                    <div className="mora-count">{segment.mora_count}音</div>
                  </div>
                ))}
              </div>

              <div className="full-text">
                <div className="text-display">"{result.text}"</div>
                <div className="mora-pattern">
                  {result.mora_counts.join('-')}音律
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
