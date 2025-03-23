/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'court-blue': '#3b82f6',
        'court-light-blue': '#93c5fd',
        'court-dark': '#1e293b',
        'court-light': '#f8fafc',
        'court-gray': '#64748b',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
