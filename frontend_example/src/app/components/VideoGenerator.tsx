'use client';

import React, { useState, useEffect } from 'react';
import {
    generateVideo,
    getVideo,
    getVideoScenes,
    subscribeToVideo,
    subscribeToVideoScenes,
    VideoDocument,
    SceneDocument,
    getFileUrl,
    FINAL_VIDEOS_BUCKET_ID,
    SCENE_VIDEOS_BUCKET_ID
} from '../services/appwrite';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

export default function VideoGenerator() {
    const [topic, setTopic] = useState('');
    const [description, setDescription] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [currentVideo, setCurrentVideo] = useState<VideoDocument | null>(null);
    const [scenes, setScenes] = useState<SceneDocument[]>([]);
    const [error, setError] = useState<string | null>(null);

    const exampleTopics = [
        { 
            topic: "Newton's Laws of Motion", 
            description: "Explain the three fundamental laws of motion with visual demonstrations and real-world examples...", 
            icon: (
                <div className="w-12 h-12 p-3 rounded-xl bg-gradient-to-br from-red-500/30 to-orange-500/30 border border-red-500/40">
                    <svg className="w-full h-full text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z" />
                    </svg>
                </div>
            ),
            gradient: "from-red-500/20 to-orange-500/20"
        },
        { 
            topic: "The Pythagorean Theorem", 
            description: "Visual proof and applications of a² + b² = c² with interactive geometric demonstrations...", 
            icon: (
                <div className="w-12 h-12 p-3 rounded-xl bg-gradient-to-br from-blue-500/30 to-indigo-500/30 border border-blue-500/40">
                    <svg className="w-full h-full text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7.864 4.243A7.5 7.5 0 0 1 19.5 10.5c0 2.92-.556 5.709-1.568 8.268M5.742 6.364A7.465 7.465 0 0 0 4.5 10.5a7.464 7.464 0 0 1-1.15 3.993m1.989 3.559A11.209 11.209 0 0 0 8.25 10.5a3.75 3.75 0 1 1 7.5 0c0 .527-.021 1.049-.064 1.565M12 10.5a14.94 14.94 0 0 1-3.6 9.75m6.633-4.596a18.666 18.666 0 0 1-2.485 5.33" />
                    </svg>
                </div>
            ),
            gradient: "from-blue-500/20 to-indigo-500/20"
        },
        { 
            topic: "DNA Structure", 
            description: "Animated explanation of the double helix structure with molecular interactions...", 
            icon: (
                <div className="w-12 h-12 p-3 rounded-xl bg-gradient-to-br from-green-500/30 to-emerald-500/30 border border-green-500/40">
                    <svg className="w-full h-full text-green-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0 1 12 15a9.065 9.065 0 0 0-6.23-.693L5 14.5m14.8.8 1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0 1 12 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                    </svg>
                </div>
            ),
            gradient: "from-green-500/20 to-emerald-500/20"
        },
        { 
            topic: "How Neural Networks Learn", 
            description: "Visualize how artificial neurons process information and adapt through training...", 
            icon: (
                <div className="w-12 h-12 p-3 rounded-xl bg-gradient-to-br from-purple-500/30 to-pink-500/30 border border-purple-500/40">
                    <svg className="w-full h-full text-purple-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5 10.5 6.75 14.25 10.5 21 3.75m-6.22 8.348a2.25 2.25 0 0 1-2.944 2.944l-6.75-6.75a2.25 2.25 0 0 1 2.944-2.944l6.75 6.75ZM12 2.25c2.9 0 5.25 2.35 5.25 5.25S14.9 12.75 12 12.75 6.75 10.4 6.75 7.5 9.1 2.25 12 2.25ZM12 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" />
                    </svg>
                </div>
            ),
            gradient: "from-purple-500/20 to-pink-500/20"
        },
    ];

    const handleExampleClick = (example: typeof exampleTopics[0]) => {
        setTopic(example.topic);
        setDescription(example.description);
        document.getElementById('topic')?.focus();
    };

    useEffect(() => {
        if (!currentVideo || ['completed', 'failed'].includes(currentVideo.status)) {
            return;
        }

        const unsubscribeVideo = subscribeToVideo(currentVideo.$id, (updatedVideo) => {
            console.log('Video update:', updatedVideo);
            setCurrentVideo(updatedVideo);
            if (['completed', 'failed'].includes(updatedVideo.status)) {
                setIsGenerating(false);
                if (updatedVideo.status === 'failed') {
                    setError(updatedVideo.error_message || 'Video generation failed');
                }
            }
        });

        const unsubscribeScenes = subscribeToVideoScenes(currentVideo.$id, (updatedScene) => {
            setScenes(prev => {
                const existingIndex = prev.findIndex(s => s.$id === updatedScene.$id);
                if (existingIndex >= 0) {
                    const newScenes = [...prev];
                    newScenes[existingIndex] = updatedScene;
                    return newScenes;
                }
                return [...prev, updatedScene].sort((a, b) => a.scene_number - b.scene_number);
            });
        });

        getVideoScenes(currentVideo.$id).then(setScenes);

        return () => {
            unsubscribeVideo();
            unsubscribeScenes();
        };
    }, [currentVideo]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (isGenerating) return;

        setError(null);
        setIsGenerating(true);
        setCurrentVideo(null);
        setScenes([]);

        try {
            const result = await generateVideo(topic, description);
            if (result.success && result.videoId) {
                const video = await getVideo(result.videoId);
                if (video) setCurrentVideo(video);
            } else {
                throw new Error(result.error || 'Failed to start video generation');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setIsGenerating(false);
        }
    };
    
    const getStatusInfo = (status: string) => {
        switch (status) {
            case 'queued_for_render':
            case 'queued': return { 
                icon: (
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                ), 
                color: 'bg-gray-500', 
                text: 'Queued' 
            };
            case 'planning': return { 
                icon: (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                ), 
                color: 'bg-blue-500', 
                text: 'Planning' 
            };
            case 'rendering': return { 
                icon: (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                    </svg>
                ), 
                color: 'bg-yellow-500', 
                text: 'Rendering' 
            };
            case 'completed': return { 
                icon: (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                ), 
                color: 'bg-green-500', 
                text: 'Completed' 
            };
            case 'failed': return { 
                icon: (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                    </svg>
                ), 
                color: 'bg-red-500', 
                text: 'Failed' 
            };
            default: return { 
                icon: (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M12 18.75H4.5a2.25 2.25 0 0 1-2.25-2.25v-9a2.25 2.25 0 0 1 2.25-2.25h4.372" />
                    </svg>
                ), 
                color: 'bg-gray-400', 
                text: status 
            };
        }
    };

    return (
        <div className="space-y-12">
            {/* Introduction */}
            <div className="text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="relative mx-auto w-fit mb-6"
                >
                    <p className="text-sm font-medium text-gray-400 relative">
                        <span className="absolute -left-16 top-1/2 w-12 h-px bg-gradient-to-r from-transparent to-blue-400 opacity-50"></span>
                        Let's Create Something Amazing
                        <span className="absolute -right-16 top-1/2 w-12 h-px bg-gradient-to-l from-transparent to-blue-400 opacity-50"></span>
                    </p>
                </motion.div>
                <motion.h2 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="text-3xl md:text-4xl font-bold text-gradient mb-4"
                >
                    Transform Ideas into Animations
                </motion.h2>
                <motion.p 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    className="text-lg text-gray-400 max-w-2xl mx-auto"
                >
                    Start with a topic and optional description. Our AI will handle the rest.
                </motion.p>
            </div>
            
            {/* Example Topics */}
            <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
            >
                {exampleTopics.map((example, index) => (
                    <motion.button
                        key={index}
                        onClick={() => handleExampleClick(example)}
                        disabled={isGenerating}
                        className={clsx(
                            "example-card group text-left h-full",
                            "bg-gradient-to-br", example.gradient,
                            "hover:border-blue-400/40 disabled:opacity-50 disabled:cursor-not-allowed"
                        )}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
                    >
                        <div className="mb-4 group-hover:scale-110 transition-transform duration-300">
                            {example.icon}
                        </div>
                        <h3 className="font-semibold text-white mb-2 group-hover:text-gradient transition-all duration-300">
                            {example.topic}
                        </h3>
                        <p className="text-sm text-gray-400 line-clamp-2 group-hover:text-gray-300 transition-colors duration-300">
                            {example.description}
                        </p>
                    </motion.button>
                ))}
            </motion.div>

            {/* Form */}
            <motion.div 
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="max-w-2xl mx-auto"
            >
                <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
                    <div>
                        <label htmlFor="topic" className="block text-sm font-medium text-gray-300 mb-3">
                            Topic <span className="text-red-400">*</span>
                        </label>
                        <input
                            id="topic"
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="e.g., Newton's Laws of Motion"
                            className="input-field"
                            required
                            disabled={isGenerating}
                        />
                    </div>
                    
                    <div>
                        <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-3">
                            Description <span className="text-gray-500">(Optional)</span>
                        </label>
                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Provide additional context, specific requirements, or teaching objectives..."
                            className="input-field min-h-[120px] resize-y"
                            rows={4}
                            disabled={isGenerating}
                        />
                    </div>
                    
                    <button
                        type="submit"
                        disabled={isGenerating || !topic}
                        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <span className="glow"></span>
                        <span className="relative z-10 flex items-center justify-center gap-3">
                            {isGenerating ? (
                                <>
                                    <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Generating Your Video...
                                </>
                            ) : (
                                <>
                                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                                    </svg>
                                    Generate Video
                                </>
                            )}
                        </span>
                    </button>
                </form>
            </motion.div>

            {/* Error Display */}
            <AnimatePresence>
                {error && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="max-w-2xl mx-auto glass-card border-red-500/20 p-6"
                    >
                        <div className="flex items-start gap-4">
                            <div className="flex-shrink-0">
                                <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                                </svg>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-sm font-medium text-red-300 mb-2">Generation Error</h3>
                                <p className="text-sm text-red-400">{error}</p>
                                <button 
                                    onClick={() => setError(null)}
                                    className="mt-3 text-xs text-red-300 hover:text-red-200 underline"
                                >
                                    Dismiss
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Video Status */}
            <AnimatePresence>
                {currentVideo && (
                    <motion.div 
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -30 }}
                        className="max-w-4xl mx-auto space-y-6"
                    >
                        {/* Main Status Card */}
                        <div className="glass-card p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-xl font-semibold text-white">{currentVideo.topic}</h3>
                                <div className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium text-white ${getStatusInfo(currentVideo.status).color}`}>
                                    {getStatusInfo(currentVideo.status).icon}
                                    <span>{getStatusInfo(currentVideo.status).text}</span>
                                </div>
                            </div>
                            
                            {currentVideo.description && (
                                <p className="text-gray-400 mb-4">{currentVideo.description}</p>
                            )}
                            
                            {currentVideo.status === 'rendering' && currentVideo.progress !== undefined && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Overall Progress</span>
                                        <span className="text-white font-medium">{currentVideo.progress}%</span>
                                    </div>
                                    <div className="progress-bar">
                                        <div 
                                            className="progress-fill" 
                                            style={{ width: `${currentVideo.progress}%` }}
                                        ></div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Scenes Grid */}
                        {scenes.length > 0 && (
                            <div className="glass-card p-6">
                                <h4 className="flex items-center gap-3 text-xl font-bold text-white mb-6">
                                    <svg className="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75A1.125 1.125 0 0 1 2.25 18.375m0-12.75C2.25 4.004 2.754 3.5 3.375 3.5s1.125.504 1.125 1.125M3.375 18.375V5.625m18 12.75c.621 0 1.125-.504 1.125-1.125V5.625M21 18.375m0-12.75c0-.621-.504-1.125-1.125-1.125s-1.125.504-1.125 1.125m1.125 12.75V5.625m0 0H3.375" />
                                    </svg>
                                    Scenes ({scenes.length})
                                </h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {scenes.map((scene) => (
                                        <div key={scene.$id} className="glass-card p-4 border-gray-700/50">
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-sm font-medium text-white">Scene {scene.scene_number}</span>
                                                <div className={clsx(
                                                    'flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium text-white',
                                                    getStatusInfo(scene.status).color
                                                )}>
                                                    {getStatusInfo(scene.status).icon}
                                                    <span>{scene.status}</span>
                                                </div>
                                            </div>
                                            {scene.duration && (
                                                <div className="text-xs text-gray-400">
                                                    Duration: {scene.duration}s
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Completed Video */}
                        {currentVideo.status === 'completed' && currentVideo.combined_video_url && (
                            <motion.div 
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="glass-card p-8 text-center border-green-500/20"
                            >
                                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 mb-6">
                                    <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                    </svg>
                                </div>
                                <h2 className="text-2xl font-bold text-green-400 mb-2">Video Ready!</h2>
                                <p className="text-gray-400 mb-6">Your animation has been successfully generated and is ready to watch.</p>
                                
                                <div className="rounded-2xl overflow-hidden border border-gray-700/50 shadow-2xl bg-black mb-6">
                                    <video 
                                        controls 
                                        className="w-full max-h-96 object-contain"
                                        preload="metadata"
                                    >
                                        <source src={getFileUrl(FINAL_VIDEOS_BUCKET_ID, currentVideo.combined_video_url)} type="video/mp4" />
                                        Your browser does not support the video tag.
                                    </video>
                                </div>

                                <div className="flex gap-4 justify-center">
                                    <a
                                        href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, currentVideo.combined_video_url)}
                                        download
                                        className="btn-primary"
                                    >
                                        <span className="glow"></span>
                                        <span className="relative z-10 flex items-center gap-2">
                                            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                            </svg>
                                            Download Video
                                        </span>
                                    </a>
                                    <button
                                        onClick={() => {
                                            setCurrentVideo(null);
                                            setScenes([]);
                                            setTopic('');
                                            setDescription('');
                                            setIsGenerating(false);
                                        }}
                                        className="btn-secondary"
                                    >
                                        Create Another
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
} 