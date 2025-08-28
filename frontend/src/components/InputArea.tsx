import React, { useState } from 'react';

interface InputAreaProps {
  onSubmit: (text: string) => void;
  loading: boolean;
}

export const InputArea: React.FC<InputAreaProps> = ({ onSubmit, loading }) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !loading) {
      onSubmit(text.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (text.trim() && !loading) {
        onSubmit(text.trim());
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-area">
      <div className="input-container">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="俳句・川柳を入力してください（Enterキーで検出）"
          rows={4}
          disabled={loading}
          className="text-input"
        />
        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="submit-button"
        >
          {loading ? '検出中...' : '俳句検出'}
        </button>
      </div>
    </form>
  );
};
