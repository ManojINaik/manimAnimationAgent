import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Header from './components/Header';
import Footer from './components/Footer';

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter'
});

export const metadata: Metadata = {
  title: 'ManimGen | AI-Powered Educational Animations',
  description: 'Transform your ideas into stunning educational animations. Create professional Manim videos with automatic scene generation, voice-over, and real-time progress tracking.',
  keywords: 'manim, video generation, AI, educational animations, mathematics, physics, programming',
  authors: [{ name: 'Manim Animation Agent' }],
  robots: 'index, follow',
  openGraph: {
    title: 'ManimGen | AI-Powered Educational Animations',
    description: 'Transform your ideas into stunning educational animations powered by AI',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ManimGen',
    description: 'AI-Powered Educational Animations',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#ffffff',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.className} antialiased min-h-screen`}>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-grow">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
} 