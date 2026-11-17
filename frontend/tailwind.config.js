/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: {
          bg: '#0a0e1a',
          panel: '#111827',
          panelAlt: '#0f172a',
          border: '#1f2937',
          borderAlt: '#334155',
        },
        accent: {
          DEFAULT: '#6366f1',
          soft: '#818cf8',
          dim: '#4f46e5',
        },
        status: {
          ok: '#10b981',
          warn: '#f59e0b',
          err: '#ef4444',
          info: '#06b6d4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
