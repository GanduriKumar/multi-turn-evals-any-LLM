/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Google brand-inspired palette
        google: {
          blue:   '#1a73e8',
          green:  '#188038',
          yellow: '#f9ab00',
          red:    '#d93025',
        },
        slate: {
          25: '#f9fbfc'
        }
      },
      boxShadow: {
        card: '0 1px 2px rgba(0,0,0,0.05), 0 1px 1px rgba(0,0,0,0.03)'
      }
    },
  },
  plugins: [],
}
