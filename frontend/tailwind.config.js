/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: 'rgba(232, 237, 245, 0.1)',
          100: 'rgba(197, 210, 232, 0.15)',
          200: 'rgba(157, 179, 215, 0.2)',
          300: 'rgba(116, 148, 197, 0.3)',
          400: '#527BB8',
          500: '#2F62AB',
          600: '#1E4A8A',
          700: '#0F3269',
          800: '#071E47',
          900: '#0A1628',
          950: '#030811',
        },
        space: {
          900: '#000000',
          800: '#050B14',
          700: '#091324',
          600: '#0D1C34',
          500: '#142A4D',
        },
        cosmic: {
          blue: '#4B9CD3',
          cyan: '#06B6D4',
          purple: '#8B5CF6',
          gold: '#F59E0B',
          red: '#EF4444',
          green: '#10B981',
          glow: '#00F0FF',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in-right': 'slideInRight 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
        'shimmer': 'shimmer 2s infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(24px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        slideInRight: { from: { opacity: 0, transform: 'translateX(24px)' }, to: { opacity: 1, transform: 'translateX(0)' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, rgba(10,22,40,0.8) 0%, rgba(15,50,105,0.4) 50%, rgba(30,74,138,0.1) 100%)',
        'orange-blue': 'linear-gradient(90deg, #8B5CF6, #06B6D4)',
        'shimmer-gradient': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent)',
        'glass-gradient': 'linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.4)',
        'glow-purple': '0 0 20px rgba(139, 92, 246, 0.4)',
        'glow-blue': '0 0 30px rgba(75, 156, 211, 0.3)',
        'card': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'card-hover': '0 8px 32px 0 rgba(6, 182, 212, 0.15)',
        'neon': '0 0 10px rgba(0, 240, 255, 0.5), inset 0 0 10px rgba(0, 240, 255, 0.2)',
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
      }
    },
  },
  plugins: [],
}
