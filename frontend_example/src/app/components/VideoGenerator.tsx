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

    // Subscribe to real-time updates when video is being generated
    useEffect(() => {
        if (!currentVideo || currentVideo.status === 'completed' || currentVideo.status === 'failed') {
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
            
            if (result.success && result.videoId) {
                // Get the initial video document
                const video = await getVideo(result.videoId);
                if (video) {
                    setCurrentVideo(video);
                } else {
                    throw new Error('Failed to retrieve video information');
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
            case 'queued': return 'bg-gray-500';
            case 'planning': return 'bg-blue-500';
            case 'rendering': return 'bg-yellow-500';
            case 'completed': return 'bg-green-500';
            case 'failed': return 'bg-red-500';
            default: return 'bg-gray-400';
        }
    };

    const getStatusText = (video: VideoDocument) => {
        if (video.status === 'rendering' && video.current_scene) {
            return `Rendering Scene ${video.current_scene}/${video.scene_count}`;
        }
        return video.status.charAt(0).toUpperCase() + video.status.slice(1);
    };

    return (
        <div className="max-w-4xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-8">Manim Video Generator</h1>
            
            {/* Input Form */}
            <form onSubmit={handleSubmit} className="mb-8 space-y-4">
                <div>
                    <label htmlFor="topic" className="block text-sm font-medium mb-2">
                        Topic
                    </label>
                    <input
                        id="topic"
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="e.g., Newton's Laws of Motion"
                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        disabled={isGenerating}
                    />
                </div>
                
                <div>
                    <label htmlFor="description" className="block text-sm font-medium mb-2">
                        Description (Optional)
                    </label>
                    <textarea
                        id="description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Provide additional details about what you want to cover..."
                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={3}
                        disabled={isGenerating}
                    />
                </div>
                
                <button
                    type="submit"
                    disabled={isGenerating || !topic}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                        isGenerating || !topic
                            ? 'bg-gray-300 cursor-not-allowed'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                >
                    {isGenerating ? 'Generating...' : 'Generate Video'}
                </button>
            </form>

            {/* Error Display */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    {error}
                </div>
            )}

            {/* Video Status */}
            {currentVideo && (
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h2 className="text-xl font-semibold mb-4">Video Status</h2>
                        
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="font-medium">Topic:</span>
                                <span>{currentVideo.topic}</span>
                            </div>
                            
                            <div className="flex items-center justify-between">
                                <span className="font-medium">Status:</span>
                                <span className={`px-3 py-1 rounded-full text-white text-sm ${getStatusColor(currentVideo.status)}`}>
                                    {getStatusText(currentVideo)}
                                </span>
                            </div>
                            
                            {currentVideo.progress !== undefined && (
                                <div>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-medium">Progress:</span>
                                        <span>{currentVideo.progress}%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                        <div 
                                            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                                            style={{ width: `${currentVideo.progress}%` }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Scenes Progress */}
                    {scenes.length > 0 && (
                        <div className="bg-white p-6 rounded-lg shadow-md">
                            <h2 className="text-xl font-semibold mb-4">Scene Progress</h2>
                            
                            <div className="space-y-2">
                                {scenes.map((scene) => (
                                    <div key={scene.$id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                        <span className="font-medium">Scene {scene.scene_number}</span>
                                        <span className={`px-3 py-1 rounded-full text-white text-sm ${getStatusColor(scene.status)}`}>
                                            {scene.status}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Download Link */}
                    {currentVideo.status === 'completed' && currentVideo.combined_video_url && (
                        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                            <h2 className="text-xl font-semibold mb-4 text-green-700">Video Ready!</h2>
                            
                            <div className="space-y-3">
                                <a
                                    href={currentVideo.combined_video_url}
                                    download
                                    className="inline-block px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                                >
                                    Download Video
                                </a>
                                
                                {currentVideo.total_duration && (
                                    <p className="text-sm text-gray-600">
                                        Duration: {Math.floor(currentVideo.total_duration / 60)}:{String(Math.floor(currentVideo.total_duration % 60)).padStart(2, '0')}
                                    </p>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
} 