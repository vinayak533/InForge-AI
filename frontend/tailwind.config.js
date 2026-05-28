/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          dark: '#080B14',
        },
        card: {
          bg: '#0E1320',
          border: '#1C2333',
        },
        accent: {
          cyan: '#00D4FF',
          blue: '#0080FF',
        },
        text: {
          primary: '#F0F4FF',
          secondary: '#8B9CC8',
        },
        state: {
          success: '#00E5A0',
          warning: '#FFB340',
          error: '#FF4D6A',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        cyanGlow: '0 0 40px rgba(0, 212, 255, 0.04)',
        cyanGlowHover: '0 0 45px rgba(0, 212, 255, 0.09)',
        cyanPulse: '0 0 20px rgba(0, 212, 255, 0.2)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 1.2s infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { transform: 'scale(1)', boxShadow: '0 0 0 0 rgba(0, 212, 255, 0.4)' },
          '50%': { transform: 'scale(1.15)', boxShadow: '0 0 20px 4px rgba(0, 212, 255, 0)' },
        }
      }
    },
  },
  plugins: [],
}
