'use client';

import React, { useState, useEffect } from 'react';
import VideoGenerator from './components/VideoGenerator';
import VideoHistory from './components/VideoHistory';
import ParticleCanvas from './components/ParticleCanvas';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generator' | 'history'>('generator');
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const features = [
    {
      icon: (
        <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
        </svg>
      ),
      title: 'AI-Powered Scripting',
      description: 'Generate compelling video scripts and narration from a simple topic or description.',
    },
    {
      icon: (
        <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
        </svg>
      ),
      title: 'Automated Animation',
      description: 'Our agent automatically converts scripts into beautiful Manim animations, scene by scene.',
    },
    {
      icon: (
        <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
        </svg>
      ),
      title: 'Intelligent Planning',
      description: 'Complex topics are broken down into logical scenes for a clear and concise explanation.',
    },
    {
      icon: (
        <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
        </svg>
      ),
      title: 'Real-time Progress',
      description: 'Track your video creation process from planning to final render with a live dashboard.',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
    },
  };

  return (
    <div className="min-h-screen relative">
      {/* Particle Background */}
      <ParticleCanvas />

      {/* Hero Section */}
      <section className="relative min-h-screen flex flex-col items-center justify-center pt-20 overflow-hidden">
        <div className="accent-lines">
          <div>
            <div className="accent-line-horizontal" style={{ top: '20%' }}></div>
            <div className="accent-line-horizontal" style={{ top: '80%' }}></div>
          </div>
          <div>
            <div className="accent-line-vertical" style={{ left: '10%' }}></div>
            <div className="accent-line-vertical" style={{ left: '90%' }}></div>
          </div>
        </div>
        <div className="text-center relative z-20">
          {/* Introducing Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: isLoaded ? 0.7 : 0, y: 0 }}
            transition={{ duration: 1.4, ease: "easeOut" }}
            className="mb-8"
          >
            <div className="relative mx-auto w-fit">
              <p className="text-sm font-medium text-gray-300 relative">
                <span className="absolute -left-20 top-1/2 w-16 h-px bg-gradient-to-r from-transparent to-blue-400 opacity-30"></span>
                Introducing
                <span className="absolute -right-20 top-1/2 w-16 h-px bg-gradient-to-l from-transparent to-blue-400 opacity-30"></span>
              </p>
            </div>
          </motion.div>

          {/* Main Hero Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isLoaded ? 1 : 0, y: 0 }}
            transition={{ duration: 2, delay: 0.6, ease: "easeOut" }}
            className="relative mb-8"
          >
            <h1 className="hero-title" data-text="ManimGen">
              ManimGen
            </h1>
          </motion.div>

          {/* Hero Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isLoaded ? 1 : 0, y: 0 }}
            transition={{ duration: 2, delay: 2, ease: "easeOut" }}
            className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto leading-relaxed"
          >
            The world's most advanced platform for <br />
            AI-powered educational animations
          </motion.p>

          {/* Features Section Preview */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: isLoaded ? 1 : 0, y: 0 }}
            transition={{ duration: 1.5, delay: 3, ease: "easeOut" }}
            id="features"
            className="mt-20 pt-20"
          >
            <div className="max-w-6xl mx-auto px-4">
              <div className="text-center mb-16">
                <div className="relative mx-auto w-fit mb-6">
                  <p className="text-sm font-medium text-gray-400 relative">
                    <span className="absolute -left-20 top-1/2 w-16 h-px bg-gradient-to-r from-transparent to-blue-400 opacity-50"></span>
                    Revolutionary by design
                    <span className="absolute -right-20 top-1/2 w-16 h-px bg-gradient-to-l from-transparent to-blue-400 opacity-50"></span>
                  </p>
                </div>
                <h2 className="text-4xl md:text-5xl font-bold text-gradient mb-6">
                  Harness. Empower.<br />
                  Unmatched Versatility.
                </h2>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                  At the core lies our revolutionary AI framework, <br />
                  ensuring adaptability across all educational domains.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
                {[
                  {
                    icon: (
                      <div className="w-16 h-16 mx-auto mb-4 p-4 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 border border-blue-500/30">
                        <svg className="w-full h-full text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
                        </svg>
                      </div>
                    ),
                    title: "AI-Powered Generation",
                    description: "Transform your ideas into stunning educational animations with our advanced AI engine."
                  },
                  {
                    icon: (
                      <div className="w-16 h-16 mx-auto mb-4 p-4 rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-600/20 border border-yellow-500/30">
                        <svg className="w-full h-full text-yellow-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5 10.5 6.75 14.25 10.5 21 3.75m-3-3v6.75h-6.75" />
                        </svg>
                      </div>
                    ),
                    title: "Lightning Fast",
                    description: "Generate professional-quality videos in minutes, not hours. Optimized for speed and quality."
                  },
                  {
                    icon: (
                      <div className="w-16 h-16 mx-auto mb-4 p-4 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-600/20 border border-purple-500/30">
                        <svg className="w-full h-full text-purple-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42" />
                        </svg>
                      </div>
                    ),
                    title: "Beautiful Animations",
                    description: "Create visually stunning mathematical and scientific animations that captivate your audience."
                  }
                ].map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.2 }}
                    className="feature-card text-center"
                  >
                    {feature.icon}
                    <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                    <p className="text-gray-400">{feature.description}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* App Section */}
      <section id="app" className="relative py-20">
        <div className="section-container">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gradient mb-6">Create Your Animation</h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Choose between creating a new video or browsing your animation history
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-16">
            <div className="glass-card p-2 rounded-2xl">
              <div className="flex">
                <button
                  data-tab="generator"
                  onClick={() => setActiveTab('generator')}
                  className={`px-8 py-4 rounded-xl font-medium transition-all duration-300 ${
                    activeTab === 'generator'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                    Create Video
                  </span>
                </button>
                <button
                  data-tab="history"
                  onClick={() => setActiveTab('history')}
                  className={`px-8 py-4 rounded-xl font-medium transition-all duration-300 ${
                    activeTab === 'history'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                    History
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="relative min-h-[600px]">
            {activeTab === 'generator' ? <VideoGenerator /> : <VideoHistory />}
          </div>
        </div>
      </section>

      {/* Decorative Mountains - Simplified to reduce visual artifacts */}
      <div className="fixed bottom-0 left-0 right-0 pointer-events-none z-[-2] opacity-40">
        <div className="relative w-full h-64 overflow-hidden">
          <motion.div
            initial={{ bottom: '-200%' }}
            animate={{ bottom: '-80%' }}
            transition={{ duration: 2, delay: 1, ease: "easeOut" }}
            className="absolute w-80 h-80 rotate-45 bg-gradient-to-br from-blue-500/10 to-purple-600/10 backdrop-blur-sm border border-blue-400/10 rounded-3xl"
            style={{ 
              left: 'calc(20% - 10rem)', 
              transform: 'translateX(-6rem) translateY(2rem) rotate(45deg)',
              boxShadow: '0 0 20px rgba(59, 130, 246, 0.1)'
            }}
          />
          <motion.div
            initial={{ bottom: '-200%' }}
            animate={{ bottom: '-60%' }}
            transition={{ duration: 2, delay: 0.8, ease: "easeOut" }}
            className="absolute w-56 h-80 rotate-45 bg-gradient-to-br from-purple-500/10 to-pink-600/10 backdrop-blur-sm border border-purple-400/10 rounded-3xl"
            style={{ 
              left: 'calc(50% - 7rem)', 
              transform: 'translateX(-2rem) rotate(45deg)',
              boxShadow: '0 0 20px rgba(139, 92, 246, 0.1)'
            }}
          />
          <motion.div
            initial={{ bottom: '-200%' }}
            animate={{ bottom: '-80%' }}
            transition={{ duration: 2, delay: 0.6, ease: "easeOut" }}
            className="absolute w-80 h-80 rotate-45 bg-gradient-to-br from-blue-500/10 to-purple-600/10 backdrop-blur-sm border border-blue-400/10 rounded-3xl"
            style={{ 
              right: 'calc(20% - 10rem)', 
              transform: 'translateX(6rem) translateY(3rem) rotate(45deg)',
              boxShadow: '0 0 20px rgba(59, 130, 246, 0.1)'
            }}
          />
        </div>
      </div>
    </div>
  );
} 