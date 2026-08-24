/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./templates/**/*.html', './static/**/*.js'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F3EEFA',
          100: '#E3D6F3',
          200: '#C9B0E6',
          300: '#A88AD4',
          400: '#8B5CF6',
          500: '#6B3FA0',
          600: '#4C2893',
          700: '#3B1F73',
          800: '#2A1652',
          900: '#1E0E3A',
          950: '#0F0620',
        },
      },
    },
  },
  plugins: [],
};
