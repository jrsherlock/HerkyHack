/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'iowa-gold': '#FFCD00',
        'iowa-black': '#000000',
      },
    },
  },
  plugins: [],
}
