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
    FINAL_VIDEOS_BUCKET_ID,
    getFileUrl
} from '../services/appwrite';

export default function VideoGenerator() {
    const [topic, setTopic] = useState('');
    const [description, setDescription] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [currentVideo, setCurrentVideo] = useState<VideoDocument | null>(null);
    const [scenes, setScenes] = useState<SceneDocument[]>([]);
    const [error, setError] = useState<string | null>(null);

    // Example topics for quick start
    const exampleTopics = [
        {
            topic: "Newton's Laws of Motion",
            description: "Explain the three fundamental laws of motion with visual demonstrations of objects in motion, forces, and acceleration.",
            icon: "🍎",
            category: "Physics"
        },
        {
            topic: "The Pythagorean Theorem",
            description: "Visual proof and applications of a² + b² = c² with geometric animations and real-world examples.",
            icon: "📐",
            category: "Mathematics"
        },
        {
            topic: "DNA Structure and Replication",
            description: "Animated explanation of the double helix structure and the process of DNA replication at the molecular level.",
            icon: "🧬",
            category: "Biology"
        },
        {
            topic: "How Neural Networks Learn",
            description: "Visualize how artificial neurons process information, backpropagation, and gradient descent optimization.",
            icon: "🧠",
            category: "Computer Science"
        },
        {
            topic: "The Water Cycle",
            description: "Animated journey of water through evaporation, condensation, precipitation, and collection processes.",
            icon: "💧",
            category: "Earth Science"
        },
        {
            topic: "Binary Number System",
            description: "Convert between decimal and binary, show how computers represent numbers and perform basic arithmetic.",
            icon: "💻",
            category: "Computer Science"
        },
        {
            topic: "Photosynthesis Process",
            description: "Step-by-step animation of how plants convert sunlight, water, and CO2 into glucose and oxygen.",
            icon: "🌱",
            category: "Biology"
        },
        {
            topic: "Calculus: Limits and Derivatives",
            description: "Visual approach to understanding limits, instantaneous rate of change, and the derivative concept.",
            icon: "📊",
            category: "Mathematics"
        }
    ];

    const handleExampleClick = (example: typeof exampleTopics[0]) => {
        setTopic(example.topic);
        setDescription(example.description);
        // Smooth scroll to form
        document.getElementById('topic')?.focus();
    };

    // Subscribe to real-time updates when video is being generated
    useEffect(() => {
        if (!currentVideo) {
            return;
        }
        
        console.log('Setting up real-time subscription for video:', currentVideo.$id, 'status:', currentVideo.status);
        
        if (currentVideo.status === 'completed' || currentVideo.status === 'failed') {
            return;
        }

        // Subscribe to video updates
        const unsubscribeVideo = subscribeToVideo(currentVideo.$id, (updatedVideo) => {
            console.log('Video update:', updatedVideo);
            setCurrentVideo(updatedVideo);
            
            // Stop generating if completed or failed
            if (updatedVideo.status === 'completed' || updatedVideo.status === 'failed') {
                setIsGenerating(false);
                if (updatedVideo.status === 'failed') {
                    setError(updatedVideo.error_message || 'Video generation failed');
                }
            }
        });

        // Subscribe to scene updates
        const unsubscribeScenes = subscribeToVideoScenes(currentVideo.$id, (updatedScene) => {
            console.log('Scene update:', updatedScene);
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

        // Load initial scenes
        getVideoScenes(currentVideo.$id).then(setScenes);

        return () => {
            unsubscribeVideo();
            unsubscribeScenes();
        };
    }, [currentVideo]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsGenerating(true);
        setCurrentVideo(null);
        setScenes([]);

        try {
            const result = await generateVideo(topic, description);
            console.log('generateVideo result:', result);

            if (result.success && result.videoId) {
                const video = await getVideo(result.videoId);
                console.log('Fetched video:', video);
                if (video) {
                    setCurrentVideo(video);
                }
            } else {
                throw new Error(result.error || 'Failed to start video generation');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            setIsGenerating(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'queued':
            case 'queued_for_render': return 'from-gray-400 to-gray-600';
            case 'planning': return 'from-blue-400 to-blue-600';
            case 'rendering': return 'from-yellow-400 to-orange-500';
            case 'completed': return 'from-green-400 to-green-600';
            case 'failed': return 'from-red-400 to-red-600';
            default: return 'from-gray-300 to-gray-500';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'queued':
            case 'queued_for_render': return '⏳';
            case 'planning': return '🧠';
            case 'rendering': return '🎬';
            case 'completed': return '✅';
            case 'failed': return '❌';
            default: return '📄';
        }
    };

    const getStatusText = (video: VideoDocument) => {
        if (video.status === 'rendering' && video.current_scene) {
            return `Rendering Scene ${video.current_scene}/${video.scene_count}`;
        }
        return video.status.charAt(0).toUpperCase() + video.status.slice(1);
    };

    return (
        <div className="min-h-screen">
            <div className="container mx-auto px-4 py-8 max-w-6xl">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-8 shadow-glow animate-float" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)' }}>
                        <span className="text-4xl">🎬</span>
                    </div>
                    <h1 className="text-6xl font-bold text-gradient mb-6">
                        Manim Video Generator
                    </h1>
                    <p className="text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                        Transform your ideas into stunning educational animations powered by AI
                    </p>
                </div>

                {/* Example Topics */}
                <div className="mb-12">
                    <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
                        ✨ Quick Start Examples
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {exampleTopics.map((example, index) => (
                            <button
                                key={index}
                                onClick={() => handleExampleClick(example)}
                                disabled={isGenerating}
                                className="example-card disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className="flex items-center space-x-3 mb-4">
                                    <span className="text-3xl transition-transform duration-300 group-hover:scale-110">
                                        {example.icon}
                                    </span>
                                    <span className="text-xs font-bold text-white bg-gradient-to-r from-blue-500 to-purple-600 px-3 py-1 rounded-full">
                                        {example.category}
                                    </span>
                                </div>
                                <h3 className="font-bold text-gray-800 text-lg mb-3 text-left">
                                    {example.topic}
                                </h3>
                                <p className="text-sm text-gray-600 text-left leading-relaxed line-clamp-3">
                                    {example.description.substring(0, 100)}...
                                </p>
                            </button>
                        ))}
                    </div>
                </div>
                
                {/* Input Form */}
                <div className="glass-card rounded-3xl p-10 mb-12">
                    <form onSubmit={handleSubmit} className="space-y-8">
                        <div>
                            <label htmlFor="topic" className="block text-xl font-bold text-gray-700 mb-4">
                                📚 What would you like to animate?
                            </label>
                            <input
                                id="topic"
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g., Newton's Laws of Motion, Quantum Mechanics, Calculus..."
                                className="modern-input w-full text-lg"
                                required
                                disabled={isGenerating}
                            />
                        </div>
                        
                        <div>
                            <label htmlFor="description" className="block text-xl font-bold text-gray-700 mb-4">
                                ✨ Additional Details (Optional)
                            </label>
                            <textarea
                                id="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="Provide additional context, specific concepts to cover, target audience, or any special requirements..."
                                className="modern-input w-full text-lg resize-none"
                                rows={4}
                                disabled={isGenerating}
                            />
                        </div>
                        
                        <button
                            type="submit"
                            disabled={isGenerating || !topic}
                            className={`btn-gradient w-full text-xl ${
                                isGenerating || !topic
                                    ? 'opacity-50 cursor-not-allowed'
                                    : 'hover:shadow-glow'
                            }`}
                        >
                            {isGenerating ? (
                                <div className="flex items-center justify-center space-x-3">
                                    <div className="spinner"></div>
                                    <span>Creating Magic...</span>
                                </div>
                            ) : (
                                <div className="flex items-center justify-center space-x-3">
                                    <span>🚀</span>
                                    <span>Generate Video</span>
                                </div>
                            )}
                        </button>
                    </form>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="mb-8 p-6 bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-200 rounded-2xl shadow-lg">
                        <div className="flex items-center space-x-3">
                            <span className="text-2xl">🚨</span>
                            <div>
                                <h3 className="text-lg font-semibold text-red-800">Something went wrong</h3>
                                <p className="text-red-700">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Video Status */}
                {currentVideo && (
                    <div className="space-y-8">
                        {/* Main Status Card */}
                        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-white/20">
                            <div className="flex items-center space-x-4 mb-6">
                                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                    <span className="text-2xl">📊</span>
                                </div>
                                <h2 className="text-3xl font-bold text-gray-800">Video Status</h2>
                            </div>
                            
                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <div className="flex flex-col space-y-2">
                                        <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Topic</span>
                                        <span className="text-xl font-semibold text-gray-800">{currentVideo.topic}</span>
                                    </div>
                                    
                                    <div className="flex flex-col space-y-2">
                                        <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Status</span>
                                        <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r ${getStatusColor(currentVideo.status)} text-white font-semibold w-fit`}>
                                            <span className="text-lg">{getStatusIcon(currentVideo.status)}</span>
                                            <span>{getStatusText(currentVideo)}</span>
                                        </div>
                                    </div>
                                </div>
                                
                                {currentVideo.progress !== undefined && (
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Progress</span>
                                            <span className="text-2xl font-bold text-gray-800">{currentVideo.progress}%</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                                            <div 
                                                className="bg-gradient-to-r from-blue-500 to-purple-600 h-4 rounded-full transition-all duration-1000 ease-out"
                                                style={{ width: `${currentVideo.progress}%` }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Scenes Progress */}
                        {scenes.length > 0 && (
                            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-white/20">
                                <div className="flex items-center space-x-4 mb-6">
                                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                                        <span className="text-2xl">🎭</span>
                                    </div>
                                    <h2 className="text-3xl font-bold text-gray-800">Scene Progress</h2>
                                </div>
                                
                                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                    {scenes.map((scene) => (
                                        <div key={scene.$id} className="bg-gradient-to-br from-white to-gray-50 p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300">
                                            <div className="flex items-center justify-between mb-3">
                                                <span className="text-lg font-bold text-gray-800">Scene {scene.scene_number}</span>
                                                <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${getStatusColor(scene.status)}`}></div>
                                            </div>
                                            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-gradient-to-r ${getStatusColor(scene.status)} text-white text-sm font-medium`}>
                                                <span>{getStatusIcon(scene.status)}</span>
                                                <span>{scene.status}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Download Section */}
                        {currentVideo.status === 'completed' && currentVideo.combined_video_url && (
                            <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-8 rounded-3xl border-2 border-green-200 shadow-2xl">
                                <div className="text-center">
                                    <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl">
                                        <span className="text-4xl">🎉</span>
                                    </div>
                                    <h2 className="text-4xl font-bold text-green-800 mb-4">Your Video is Ready!</h2>
                                    <p className="text-xl text-green-700 mb-8">Your educational animation has been generated successfully</p>
                                    
                                    <div className="space-y-4">
                                        <a
                                            href={currentVideo.combined_video_url}
                                            download
                                            className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xl font-bold rounded-2xl hover:from-green-600 hover:to-emerald-700 transform hover:scale-105 transition-all duration-300 shadow-xl hover:shadow-2xl"
                                        >
                                            <span>⬇️</span>
                                            <span>Download Video</span>
                                        </a>
                                        
                                        {currentVideo.total_duration && (
                                            <p className="text-lg text-green-600 font-semibold">
                                                ⏱️ Duration: {Math.floor(currentVideo.total_duration / 60)}:{String(Math.floor(currentVideo.total_duration % 60)).padStart(2, '0')}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
} 