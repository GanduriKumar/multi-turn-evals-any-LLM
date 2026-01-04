/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#edf5ff',
          100: '#d8e9ff',
          200: '#b0d2ff',
          300: '#7fb7ff',
          400: '#4a98ff',
          500: '#2d7dff',
          600: '#225fd6',
          700: '#1a49a6',
          800: '#153a85',
          900: '#102a61',
        },
        slate: {
          25: '#f9fbfc'
        }
      },
    },
  },
  plugins: [],
}
