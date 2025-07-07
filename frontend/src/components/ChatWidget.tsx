import React, { useState } from 'react';
import ChatWindow from './ChatWindow';

export type Theme = 'light' | 'dark' | 'auto';

function useTheme(theme: Theme): 'light' | 'dark' {
  const [systemTheme, setSystemTheme] = React.useState<'light' | 'dark'>(
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  );
  React.useEffect(() => {
    if (theme !== 'auto') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => setSystemTheme(e.matches ? 'dark' : 'light');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);
  return theme === 'auto' ? systemTheme : theme;
}

const bubbleStyle: React.CSSProperties = {
  width: 56,
  height: 56,
  borderRadius: '50%',
  background: 'var(--chat-bubble-bg)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  cursor: 'pointer',
  transition: 'background 0.2s',
};

interface ChatWidgetProps {
  theme?: Theme;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ theme = 'auto' }) => {
  const [open, setOpen] = useState(false);
  const effectiveTheme = useTheme(theme);

  return (
    <div className={`chat-widget-root chat-theme-${effectiveTheme}`} style={{ position: 'relative' }}>
      {open && <ChatWindow onClose={() => setOpen(false)} theme={effectiveTheme} />}
      <div style={bubbleStyle} onClick={() => setOpen(true)}>
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
    </div>
  );
};

export default ChatWidget; 