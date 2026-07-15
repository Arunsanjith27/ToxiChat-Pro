/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        background: '#0b0f19',
        surface: '#111827',
        surfaceHover: '#1f2937',
        border: 'rgba(255, 255, 255, 0.1)',
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          900: '#064e3b',
        },
        toxic: {
          dark: '#1a0505',
          border: '#ff3333',
          glow: 'rgba(255, 51, 51, 0.5)',
          bg: '#2b0a0a',
        },
        safe: {
          primary: '#10b981',
          bg: '#064e3b',
        },
        space: {
          bg: '#0b0f19',
          panel: 'rgba(17, 24, 39, 0.7)',
          border: 'rgba(255, 255, 255, 0.1)'
        }
      },
      animation: {
        'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
      keyframes: {
        'accordion-down': {
          from: { height: 0 },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: 0 },
        },
      }
    },
  },
  plugins: [],
};
