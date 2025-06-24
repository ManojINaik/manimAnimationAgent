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
            description: "Explain the three fundamental laws of motion with visual demonstrations...", 
            icon: "🍎",
            gradient: "from-red-400 to-orange-500"
        },
        { 
            topic: "The Pythagorean Theorem", 
            description: "Visual proof and applications of a² + b² = c²...", 
            icon: "📐",
            gradient: "from-blue-400 to-indigo-500"
        },
        { 
            topic: "DNA Structure", 
            description: "Animated explanation of the double helix structure...", 
            icon: "🧬",
            gradient: "from-green-400 to-emerald-500"
        },
        { 
            topic: "How Neural Networks Learn", 
            description: "Visualize how artificial neurons process information...", 
            icon: "🧠",
            gradient: "from-purple-400 to-pink-500"
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
        <div className="section-container">
            <div className="mx-auto max-w-2xl text-center">
                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Let's Create a Video</h2>
                <p className="mt-6 text-lg leading-8 text-gray-600">
                    Start with a topic and optional description. Our AI will handle the rest.
                </p>
            </div>
            
            <div className="mt-16 grid grid-cols-1 gap-4 md:grid-cols-4">
                {exampleTopics.map((example, index) => (
                    <button
                        key={index}
                        onClick={() => handleExampleClick(example)}
                        disabled={isGenerating}
                        className="example-card group"
                    >
                        <span className="text-2xl">{example.icon}</span>
                        <h3 className="mt-2 font-semibold">{example.topic}</h3>
                    </button>
                ))}
            </div>

            <div className="mx-auto mt-8 max-w-2xl">
                <form onSubmit={handleSubmit} className="glass-card space-y-6">
                    <div>
                        <label htmlFor="topic" className="block text-sm font-medium text-gray-700">Topic</label>
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
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description (Optional)</label>
                        <textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Provide additional context or requirements..."
                            className="input-field"
                            rows={3}
                            disabled={isGenerating}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isGenerating || !topic}
                        className="btn-primary w-full"
                    >
                        {isGenerating ? (
                            <>
                                <svg className="mr-3 h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Generating Video...
                            </>
                        ) : (
                            <>
                                <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                                </svg>
                                Generate Video
                            </>
                        )}
                    </button>
                </form>
            </div>

            {error && (
                <div className="mx-auto mt-8 max-w-2xl rounded-md bg-red-50 p-4">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800">Error</h3>
                            <p className="mt-2 text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}

            {currentVideo && (
                <div className="mx-auto mt-16 max-w-4xl space-y-8">
                    <div className="rounded-xl border bg-white p-6 shadow-sm">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold">{currentVideo.topic}</h3>
                            <div className={`flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium text-white ${getStatusInfo(currentVideo.status).color}`}>
                                {getStatusInfo(currentVideo.status).icon}
                                <span>{getStatusInfo(currentVideo.status).text}</span>
                            </div>
                        </div>
                        {currentVideo.status === 'rendering' && currentVideo.progress !== undefined && (
                            <div className="mt-4">
                                <span className="text-sm text-gray-600">Overall Progress: {currentVideo.progress}%</span>
                                <div className="progress-bar">
                                    <div className="progress-fill" style={{ width: `${currentVideo.progress}%` }}></div>
                                </div>
                            </div>
                        )}
                    </div>

                    {scenes.length > 0 && (
                        <div className="rounded-xl border bg-white p-6 shadow-sm">
                            <h4 className="flex items-center gap-3 text-xl font-bold text-gray-900 mb-6">
                                <svg className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75A1.125 1.125 0 0 1 2.25 18.375m0-12.75C2.25 4.004 2.754 3.5 3.375 3.5s1.125.504 1.125 1.125M3.375 18.375V5.625m18 12.75c.621 0 1.125-.504 1.125-1.125V5.625M21 18.375m0-12.75c0-.621-.504-1.125-1.125-1.125s-1.125.504-1.125 1.125m1.125 12.75V5.625m0 0H3.375" />
                                </svg>
                                Scenes ({scenes.length})
                            </h4>
                            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                {scenes.map((scene) => (
                                    <div key={scene.$id} className="rounded-lg border p-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium">Scene {scene.scene_number}</span>
                                            <div className={clsx(
                                                'flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium text-white',
                                                getStatusInfo(scene.status).color
                                            )}>
                                                {getStatusInfo(scene.status).icon}
                                                <span>{scene.status}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {currentVideo.status === 'completed' && currentVideo.combined_video_url && (
                        <div className="rounded-xl border-2 border-green-500 bg-green-50 p-8 text-center shadow-lg">
                             <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-6">
                                <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                </svg>
                            </div>
                            <h2 className="mt-4 text-2xl font-bold">Video Ready!</h2>
                            <p className="mt-2 text-gray-600">Your video has been successfully generated and is ready to watch.</p>
                            
                            <div className="mt-6 rounded-lg overflow-hidden border-2 border-gray-200 shadow-lg bg-black">
                                <video 
                                    controls 
                                    className="w-full max-h-96 object-contain"
                                    preload="metadata"
                                >
                                    <source src={getFileUrl(FINAL_VIDEOS_BUCKET_ID, currentVideo.combined_video_url)} type="video/mp4" />
                                    Your browser does not support the video tag.
                                </video>
                            </div>

                            <div className="mt-6">
                            <a
                                href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, currentVideo.combined_video_url)}
                                download
                                className="btn-primary inline-flex items-center gap-3 text-lg"
                            >
                                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                </svg>
                                Download Video
                            </a>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
} 