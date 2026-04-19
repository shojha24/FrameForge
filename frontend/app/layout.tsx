import type { Metadata, Viewport } from 'next'
import { IBM_Plex_Mono, Josefin_Sans } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

// IBM Plex Mono for monospace text
const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-ibm-plex-mono',
})

// Josefin Sans as Futura alternative - geometric sans-serif
const josefinSans = Josefin_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '700'],
  variable: '--font-futura',
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
  themeColor: '#F0F0F0',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="bg-[#F0F0F0]">
      <body className={`${ibmPlexMono.variable} ${josefinSans.variable} font-sans antialiased bg-[#F0F0F0] text-[#1A1A1A]`}>
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
