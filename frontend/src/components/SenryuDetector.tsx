import React, { useState } from 'react';
import { InputArea } from './InputArea';
import { SenryuDisplay } from './SenryuDisplay';
import { useSenryuAPI } from '../hooks/useSenryuAPI';
import type { DetectionResult } from '../types/api';

export const SenryuDetector: React.FC = () => {
  const { detect, loading, error, clearError } = useSenryuAPI();
  const [results, setResults] = useState<DetectionResult[]>([]);
  const [lastText, setLastText] = useState<string>('');

  const handleDetect = async (text: string) => {
    clearError();
    try {
      const response = await detect(text);
      setResults(response.results);
      setLastText(text);
    } catch {
      // Error is handled by the hook
      setResults([]);
      setLastText(text);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>俳句・川柳検出ツール</h1>
        <p>日本語テキストから5-7-5音律の俳句・川柳を検出します</p>
      </header>

      <InputArea onSubmit={handleDetect} loading={loading} />

      {error && (
        <div className="error-message">
          <p>エラー: {error}</p>
          <button onClick={clearError}>閉じる</button>
        </div>
      )}

      {(results.length > 0 || lastText) && (
        <SenryuDisplay results={results} originalText={lastText} />
      )}
    </div>
  );
};
