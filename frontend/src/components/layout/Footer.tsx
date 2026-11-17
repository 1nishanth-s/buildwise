import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer
      data-testid="global-ai-disclaimer"
      className="shrink-0 py-2.5 px-6 border-t border-canvas-border/60 bg-canvas-panel/90 backdrop-blur-sm text-center select-none z-10"
    >
      <p className="text-[11px] text-slate-400 font-normal tracking-wide">
        AI-generated recommendations may contain mistakes. Please verify component specifications, compatibility, prices and availability before purchasing.
      </p>
    </footer>
  );
};
