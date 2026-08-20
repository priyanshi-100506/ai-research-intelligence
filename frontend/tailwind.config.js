/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        journal: {
          bg:         '#FAF7F2',   // warm parchment
          surface:    '#F5EFE6',   // slightly deeper parchment
          card:       '#EFE6D8',   // warm sand card
          cardHover:  '#E8DDD0',   // card hover
          border:     '#D9C7A8',   // warm tan border
          muted:      '#C9B49A',   // muted warm
          primary:    '#2E211A',   // deep espresso
          secondary:  '#5C4033',   // medium warm brown
          tertiary:   '#7A5C48',   // lighter warm brown
          caption:    '#9C7E6E',   // caption/subtext
          terracotta: '#B5652D',   // terracotta accent
          rust:       '#8B3A1E',   // deep rust
          blush:      '#E8C4A8',   // soft blush
          olive:      '#7A7248',   // muted olive
          sage:       '#9A9B7A',   // soft sage
          gold:       '#C9A84C',   // warm gold
        }
      },
      fontFamily: {
        serif: ['Fraunces', 'Lora', 'Georgia', 'serif'],
        sans:  ['IBM Plex Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'sm':  '6px',
        DEFAULT: '8px',
        'lg':  '12px',
        'xl':  '16px',
      },
      boxShadow: {
        'card':  '0 1px 4px 0 rgba(46,33,26,0.06), 0 4px 16px 0 rgba(46,33,26,0.04)',
        'card-hover': '0 4px 12px 0 rgba(46,33,26,0.10), 0 8px 24px 0 rgba(46,33,26,0.06)',
        'toast': '0 8px 32px 0 rgba(46,33,26,0.14)',
        'nav':   '0 1px 0 0 rgba(46,33,26,0.08)',
      },
      animation: {
        'fade-up':         'fade-up 0.45s cubic-bezier(.22,.61,.36,1) both',
        'slide-in-right':  'slide-in-right 0.35s cubic-bezier(.22,.61,.36,1) both',
        'pulse-soft':      'pulse-soft 2s ease-in-out infinite',
        'spin-slow':       'spin 2s linear infinite',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(.22,.61,.36,1)',
      },
    },
  },
  plugins: [],
}
