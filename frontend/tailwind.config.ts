
import type { Config } from "tailwindcss";

export default {
	darkMode: ["class"],
	content: [
		"./pages/**/*.{ts,tsx}",
		"./components/**/*.{ts,tsx}",
		"./app/**/*.{ts,tsx}",
		"./src/**/*.{ts,tsx}",
	],
	prefix: "",
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px'
			}
		},
		extend: {
			colors: {
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				primary: {
					DEFAULT: 'hsl(var(--primary))',
					foreground: 'hsl(var(--primary-foreground))'
				},
				secondary: {
					DEFAULT: 'hsl(var(--secondary))',
					foreground: 'hsl(var(--secondary-foreground))'
				},
				destructive: {
					DEFAULT: 'hsl(var(--destructive))',
					foreground: 'hsl(var(--destructive-foreground))'
				},
				muted: {
					DEFAULT: 'hsl(var(--muted))',
					foreground: 'hsl(var(--muted-foreground))'
				},
				accent: {
					DEFAULT: 'hsl(var(--accent))',
					foreground: 'hsl(var(--accent-foreground))'
				},
				popover: {
					DEFAULT: 'hsl(var(--popover))',
					foreground: 'hsl(var(--popover-foreground))'
				},
				card: {
					DEFAULT: 'hsl(var(--card))',
					foreground: 'hsl(var(--card-foreground))'
				},
				sidebar: {
					DEFAULT: 'hsl(var(--sidebar-background))',
					foreground: 'hsl(var(--sidebar-foreground))',
					primary: 'hsl(var(--sidebar-primary))',
					'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
					accent: 'hsl(var(--sidebar-accent))',
					'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
					border: 'hsl(var(--sidebar-border))',
					ring: 'hsl(var(--sidebar-ring))'
				}
			},
			borderRadius: {
				lg: 'var(--radius)',
				md: 'calc(var(--radius) - 2px)',
				sm: 'calc(var(--radius) - 4px)'
			},
			backgroundImage: {
				'gradient-dark': 'linear-gradient(135deg, #0c0c0c 0%, #1a0f0f 25%, #2d0a0a 50%, #1a0f0f 75%, #0c0c0c 100%)',
				'gradient-red-orange': 'linear-gradient(135deg, #dc2626 0%, #ea580c 25%, #f97316 50%, #ea580c 75%, #dc2626 100%)',
				'gradient-deep': 'linear-gradient(135deg, #7c2d12 0%, #991b1b 25%, #dc2626 50%, #991b1b 75%, #7c2d12 100%)',
				'glow-multicolor': 'conic-gradient(from 0deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #dda0dd, #ff6b6b)',
			},
			keyframes: {
				'accordion-down': {
					from: {
						height: '0'
					},
					to: {
						height: 'var(--radix-accordion-content-height)'
					}
				},
				'accordion-up': {
					from: {
						height: 'var(--radix-accordion-content-height)'
					},
					to: {
						height: '0'
					}
				},
				'glow-pulse': {
					'0%, 100%': {
						boxShadow: '0 0 5px rgba(220, 38, 38, 0.5), 0 0 10px rgba(234, 88, 12, 0.3), 0 0 15px rgba(249, 115, 22, 0.2)'
					},
					'50%': {
						boxShadow: '0 0 10px rgba(220, 38, 38, 0.8), 0 0 20px rgba(234, 88, 12, 0.6), 0 0 30px rgba(249, 115, 22, 0.4)'
					}
				},
				'rainbow-glow': {
					'0%': {
						filter: 'hue-rotate(0deg) saturate(1.2) brightness(1.1)'
					},
					'25%': {
						filter: 'hue-rotate(90deg) saturate(1.4) brightness(1.2)'
					},
					'50%': {
						filter: 'hue-rotate(180deg) saturate(1.6) brightness(1.3)'
					},
					'75%': {
						filter: 'hue-rotate(270deg) saturate(1.4) brightness(1.2)'
					},
					'100%': {
						filter: 'hue-rotate(360deg) saturate(1.2) brightness(1.1)'
					}
				}
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
				'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
				'rainbow-glow': 'rainbow-glow 3s ease-in-out infinite'
			}
		}
	},
	plugins: [require("tailwindcss-animate")],
} satisfies Config;
