import type { Metadata, Viewport } from 'next'
import { IBM_Plex_Serif, Space_Mono, Ultra } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const ibmPlexSerif = IBM_Plex_Serif({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-ibm-plex-serif',
})

const spaceMono = Space_Mono({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-monoid',
})

// Ultra is a heavy display serif similar to Cooper Black
const ultra = Ultra({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-cooper-black',
})

export const metadata: Metadata = {
  title: 'FrameForge: Scene-to-Storyboard Diffuser',
  description: 'Transform your scene descriptions into cinematic storyboards with AI-powered visualization',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  themeColor: '#0A0A0A',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="bg-[#0A0A0A]">
      <body className={`${ibmPlexSerif.variable} ${spaceMono.variable} ${ultra.variable} font-sans antialiased bg-[#0A0A0A] text-[#F5F5F0]`}>
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
