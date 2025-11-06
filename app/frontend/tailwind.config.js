/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    colors: {
      transparent: 'transparent',
      white: '#ffffff',
      red: {
        50: '#fef2f2',
        200: '#fecaca',
        600: '#dc2626',
        700: '#b91c1c',
      },
      gray: {
        400: '#9ca3af',
        500: '#6b7280',
        600: '#4b5563',
      },
      cream: {
        50: '#fefdf9',
        100: '#fefcf3',
        200: '#fef9e7',
        300: '#fef5db',
        400: '#fef0c3',
        500: '#f5e6d3',
        600: '#e8d5ba',
        700: '#dcc4a1',
        800: '#cdb388',
        900: '#bea26f',
      },
      primary: '#8b7355',
      secondary: '#d4a574',
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      serif: ['Playfair Display', 'serif'],
    },
    extend: {
      backgroundColor: {
        'gradient-cream': 'linear-gradient(135deg, #fefdf9 0%, #fef9e7 100%)',
      },
    },
  },
  plugins: [],
}
