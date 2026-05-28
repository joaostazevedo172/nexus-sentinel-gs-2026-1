import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        nexus: {
          bg:       'var(--nexus-bg)',
          'bg-deep':'var(--nexus-bg-deep)',
          'bg-elev':'var(--nexus-bg-elev)',
          fg:       'var(--nexus-fg)',
          'fg-muted': 'var(--nexus-fg-muted)',
          'fg-dim':   'var(--nexus-fg-dim)',
          border:   'var(--nexus-border)',
          cyan:     'var(--nexus-cyan)',
          amber:    'var(--nexus-amber)',
          magenta:  'var(--nexus-magenta)'
        }
      },
      fontFamily: {
        display: ['var(--font-orbitron)', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif']
      },
      transitionTimingFunction: {
        'nexus': 'cubic-bezier(0.16, 1, 0.3, 1)'
      }
    }
  },
  plugins: []
};
export default config;
