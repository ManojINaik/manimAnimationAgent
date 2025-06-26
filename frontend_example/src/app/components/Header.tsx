'use client';

import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <>
      {/* Spotlight Effects */}
      <div className="spotlight-container">
        <div className="spotlight"></div>
        <div className="spotlight"></div>
        <div className="spotlight"></div>
      </div>

      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="fixed top-0 z-40 w-full backdrop-blur-xl bg-gray-900/20 border-b border-gray-800/50"
      >
        <div className="flex h-20 w-full max-w-7xl mx-auto items-center justify-between px-6 py-4">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="flex items-center z-50"
          >
            <Link href="/" className="group flex items-center gap-3 relative">
              <motion.div
                whileHover={{ scale: 1.1, rotate: 3 }}
                whileTap={{ scale: 0.95 }}
                className="relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur-md opacity-40 group-hover:opacity-60 transition-opacity"></div>
                <div className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-3 rounded-2xl shadow-2xl">
                  {/* Enhanced ManimGen Logo */}
                  <svg className="h-8 w-8 text-white" viewBox="0 0 32 32" fill="none">
                    {/* Mathematical curve/wave */}
                    <path 
                      d="M2 16 C6 8, 10 24, 16 16 C22 8, 26 24, 30 16" 
                      stroke="currentColor" 
                      strokeWidth="2.5" 
                      strokeLinecap="round" 
                      fill="none"
                      className="drop-shadow-sm"
                    />
                    {/* Geometric elements with improved positioning */}
                    <circle cx="6" cy="12" r="1.5" fill="currentColor" className="animate-pulse" style={{animationDelay: '0s', animationDuration: '2s'}} />
                    <circle cx="16" cy="16" r="2" fill="currentColor" className="animate-pulse" style={{animationDelay: '0.5s', animationDuration: '2s'}} />
                    <circle cx="26" cy="12" r="1.5" fill="currentColor" className="animate-pulse" style={{animationDelay: '1s', animationDuration: '2s'}} />
                    {/* Connection lines */}
                    <path 
                      d="M6 12 L16 16 L26 12" 
                      stroke="currentColor" 
                      strokeWidth="1.5" 
                      strokeLinecap="round" 
                      opacity="0.6"
                      className="animate-pulse"
                      style={{animationDelay: '1.5s', animationDuration: '3s'}}
                    />
                    {/* Additional geometric accents */}
                    <path 
                      d="M4 20 L12 8 M20 8 L28 20" 
                      stroke="currentColor" 
                      strokeWidth="1" 
                      strokeLinecap="round" 
                      opacity="0.3"
                    />
                  </svg>
                </div>
              </motion.div>
              <motion.span 
                className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent hover:from-blue-300 hover:via-purple-300 hover:to-pink-300 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
              >
                ManimGen
              </motion.span>
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-8 md:flex">
            {[
              { href: "#features", label: "Features" },
              { href: "#app", label: "Generator" },
              { href: "#app", label: "History", onClick: () => {
                document.getElementById('app')?.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                  const historyTab = document.querySelector('[data-tab="history"]') as HTMLButtonElement;
                  if (historyTab) historyTab.click();
                }, 500);
              }},
            ].map((item, index) => (
              <motion.div
                key={item.href + item.label}
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.9 + index * 0.1 }}
              >
                {item.onClick ? (
                  <button
                    onClick={item.onClick}
                    className="relative text-sm font-medium text-gray-300 transition-all duration-300 hover:text-white group"
                  >
                    {item.label}
                    <span className="absolute -bottom-1 left-0 h-0.5 w-0 bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300 group-hover:w-full"></span>
                  </button>
                ) : (
                  <Link 
                    href={item.href} 
                    className="relative text-sm font-medium text-gray-300 transition-all duration-300 hover:text-white group"
                  >
                    {item.label}
                    <span className="absolute -bottom-1 left-0 h-0.5 w-0 bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-300 group-hover:w-full"></span>
                  </Link>
                )}
              </motion.div>
            ))}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            
            {/* Contact Button with Glow Effect */}
            <motion.div
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.4 }}
              className="relative"
            >
              <button className="btn-primary">
                <span className="glow"></span>
                <span className="relative z-10 flex items-center gap-2">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                  </svg>
                  Get Started
                </span>
              </button>
            </motion.div>

            {/* Mobile menu button */}
            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.6 }}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-gray-800/50 transition-colors text-gray-300 backdrop-blur-sm"
            >
              {isMobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              )}
            </motion.button>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="md:hidden absolute top-full left-0 right-0 backdrop-blur-xl bg-gray-900/90 border-b border-gray-800/50 m-4 rounded-2xl shadow-2xl"
            >
              <div className="p-6 space-y-4">
                {[
                  { href: "#features", label: "Features" },
                  { href: "#app", label: "Generator" },
                  { href: "#app", label: "History", onClick: () => {
                    setIsMobileMenuOpen(false);
                    document.getElementById('app')?.scrollIntoView({ behavior: 'smooth' });
                    setTimeout(() => {
                      const historyTab = document.querySelector('[data-tab="history"]') as HTMLButtonElement;
                      if (historyTab) historyTab.click();
                    }, 500);
                  }},
                ].map((item, index) => (
                  item.onClick ? (
                    <motion.button
                      key={item.href + item.label}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      onClick={item.onClick}
                      className="block py-3 text-base font-medium text-gray-300 hover:text-white w-full text-left transition-colors hover:bg-gray-800/30 rounded-lg px-3"
                    >
                      {item.label}
                    </motion.button>
                  ) : (
                    <motion.div
                      key={item.href}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Link
                        href={item.href}
                        className="block py-3 text-base font-medium text-gray-300 hover:text-white transition-colors hover:bg-gray-800/30 rounded-lg px-3"
                        onClick={() => setIsMobileMenuOpen(false)}
                      >
                        {item.label}
                      </Link>
                    </motion.div>
                  )
                ))}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  className="pt-4 space-y-3 border-t border-gray-800/50"
                >
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      document.getElementById('app')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="btn-primary w-full justify-center"
                  >
                    <span className="glow"></span>
                    <span className="relative z-10 flex items-center justify-center gap-2">
                      <svg className="h-4 w-4" viewBox="0 0 32 32" fill="none">
                        <path 
                          d="M2 16 C6 8, 10 24, 16 16 C22 8, 26 24, 30 16" 
                          stroke="currentColor" 
                          strokeWidth="2.5" 
                          strokeLinecap="round" 
                          fill="none"
                        />
                        <circle cx="16" cy="16" r="1.5" fill="currentColor" />
                      </svg>
                      Get Started
                    </span>
                  </button>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>
    </>
  );
} 