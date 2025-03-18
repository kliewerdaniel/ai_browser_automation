/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#33e7ff",
          dark: "#00a8c4",
          light: "#7affff",
        },
        secondary: {
          DEFAULT: "#ff3366",
          dark: "#c4004f",
          light: "#ff7a99",
        },
        dark: {
          DEFAULT: "#0d1117",
          lighter: "#161b22",
          lightest: "#21262d",
        },
      },
      animation: {
        'glow': 'glow 1.5s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          from: { 'text-shadow': '0 0 10px #33e7ff, 0 0 20px #33e7ff' },
          to: { 'text-shadow': '0 0 20px #33e7ff, 0 0 30px #33e7ff, 0 0 40px #33e7ff' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
};
