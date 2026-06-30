/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
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
      }
    },
  },
  plugins: [],
};
