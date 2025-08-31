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
        {results.map((result, index) => {
          const phrases = [result.upper_phrase, result.middle_phrase, result.lower_phrase].filter(Boolean);

          return (
            <div key={index} className={`result-card ${result.is_valid ? 'valid' : 'invalid'}`}>
              <div className="senryu-text">
                <div className="segments">
                  {phrases.length > 0 ? (
                    phrases.map((phrase, segIndex) => (
                      <div key={segIndex} className="segment">
                        <div className="segment-text">{phrase!.text}</div>
                        {phrase!.reading && (
                          <div className="segment-reading">{phrase!.reading}</div>
                        )}
                        <div className="mora-count">{phrase!.mora_count}音</div>
                      </div>
                    ))
                  ) : (
                    <div className="segment">
                      <div className="segment-text">{result.original_text}</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
