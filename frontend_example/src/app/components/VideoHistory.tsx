'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    getAllVideos, 
    VideoDocument, 
    getFileUrl, 
    FINAL_VIDEOS_BUCKET_ID,
    testConnection,
    checkFileExists
} from '../services/appwrite';

export default function VideoHistory() {
    const [videos, setVideos] = useState<VideoDocument[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedVideo, setSelectedVideo] = useState<VideoDocument | null>(null);
    const [debugInfo, setDebugInfo] = useState<any>(null);
    const [videoFileStatus, setVideoFileStatus] = useState<Record<string, boolean>>({});

    useEffect(() => {
        loadVideos();
    }, []);

    // Check if video file exists when videos are loaded
    useEffect(() => {
        if (videos.length > 0) {
            checkVideoFiles();
        }
    }, [videos]);

    const checkVideoFiles = async () => {
        const statusMap: Record<string, boolean> = {};
        
        for (const video of videos) {
            if (video.status === 'completed' && video.combined_video_url) {
                console.log('🎬 Checking file for video:', video.topic, video.combined_video_url);
                const exists = await checkFileExists(FINAL_VIDEOS_BUCKET_ID, video.combined_video_url);
                statusMap[video.$id] = exists;
            } else {
                statusMap[video.$id] = false;
            }
        }
        
        setVideoFileStatus(statusMap);
        console.log('🎬 Video file status map:', statusMap);
    };

    const loadVideos = async () => {
        try {
            setLoading(true);
            setError(null);
            
            console.log('🎬 VideoHistory: Starting to load videos...');
            
            // Test connection first
            const connectionTest = await testConnection();
            setDebugInfo(connectionTest);
            
            if (!connectionTest.success) {
                throw new Error(`Connection failed: ${connectionTest.error}`);
            }
            
            console.log('🎬 VideoHistory: Connection test passed, fetching videos...');
            const allVideos = await getAllVideos();
            
            console.log('🎬 VideoHistory: Received videos:', allVideos.length);
            setVideos(allVideos);
            
        } catch (err) {
            console.error('🎬 VideoHistory: Error loading videos:', err);
            setError(err instanceof Error ? err.message : 'Failed to load video history');
        } finally {
            setLoading(false);
        }
    };

    const getStatusInfo = (status: string) => {
        switch (status) {
            case 'queued_for_render':
            case 'queued': return { 
                icon: '⏳', 
                color: 'bg-gray-500', 
                text: 'Queued',
                textColor: 'text-gray-700'
            };
            case 'planning': return { 
                icon: '🎯', 
                color: 'bg-blue-500', 
                text: 'Planning',
                textColor: 'text-blue-700'
            };
            case 'rendering': return { 
                icon: '🎬', 
                color: 'bg-yellow-500', 
                text: 'Rendering',
                textColor: 'text-yellow-700'
            };
            case 'completed': return { 
                icon: '✅', 
                color: 'bg-green-500', 
                text: 'Completed',
                textColor: 'text-green-700'
            };
            case 'failed': return { 
                icon: '❌', 
                color: 'bg-red-500', 
                text: 'Failed',
                textColor: 'text-red-700'
            };
            default: return { 
                icon: '📹', 
                color: 'bg-gray-400', 
                text: status,
                textColor: 'text-gray-700'
            };
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="section-container">
                <div className="flex items-center justify-center py-20">
                    <div className="text-center">
                        <svg className="mx-auto h-12 w-12 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p className="mt-4 text-lg text-gray-600">Loading video history...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="section-container">
                <div className="mx-auto max-w-lg rounded-md bg-red-50 p-6">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                            </svg>
                        </div>
                        <div className="ml-3 w-full">
                            <h3 className="text-sm font-medium text-red-800">Error Loading History</h3>
                            <p className="mt-2 text-sm text-red-700">{error}</p>
                            
                            {debugInfo && (
                                <details className="mt-4">
                                    <summary className="text-xs text-red-600 cursor-pointer hover:text-red-800">
                                        Debug Information (Click to expand)
                                    </summary>
                                    <div className="mt-2 p-3 bg-red-100 rounded text-xs text-red-800">
                                        <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
                                    </div>
                                </details>
                            )}
                            
                            <button 
                                onClick={loadVideos}
                                className="mt-3 rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-800 hover:bg-red-200"
                            >
                                Try Again
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="section-container">
            <div className="mx-auto max-w-6xl">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Video History</h2>
                    <p className="mt-6 text-lg leading-8 text-gray-600">
                        All your generated videos in one place
                    </p>
                    
                    {/* Debug Info for Storage Issues */}
                    {videos.length > 0 && Object.keys(videoFileStatus).length > 0 && (
                        <div className="mt-6 mx-auto max-w-2xl">
                            <details className="bg-gray-50 rounded-lg p-4">
                                <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-800">
                                    📊 Storage Debug Info (Click to expand)
                                </summary>
                                <div className="mt-4 text-left space-y-2">
                                    <div className="grid grid-cols-2 gap-4 text-xs">
                                        <div>
                                            <strong>Total Videos:</strong> {videos.length}
                                        </div>
                                        <div>
                                            <strong>Completed:</strong> {videos.filter(v => v.status === 'completed').length}
                                        </div>
                                        <div>
                                            <strong>With Video URLs:</strong> {videos.filter(v => v.combined_video_url).length}
                                        </div>
                                        <div>
                                            <strong>Files Found:</strong> {Object.values(videoFileStatus).filter(Boolean).length}
                                        </div>
                                    </div>
                                    
                                    {videos.filter(v => v.status === 'completed' && v.combined_video_url && !videoFileStatus[v.$id]).length > 0 && (
                                        <div className="mt-4 p-3 bg-orange-50 rounded">
                                            <p className="text-xs font-medium text-orange-800 mb-2">
                                                ⚠️ Videos marked as completed but missing files:
                                            </p>
                                            <div className="space-y-1">
                                                {videos
                                                    .filter(v => v.status === 'completed' && v.combined_video_url && !videoFileStatus[v.$id])
                                                    .map(v => (
                                                        <div key={v.$id} className="text-xs text-orange-700">
                                                            • {v.topic} → {v.combined_video_url}
                                                        </div>
                                                    ))
                                                }
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </details>
                        </div>
                    )}
                </div>

                {videos.length === 0 ? (
                    <div className="text-center py-12">
                        <svg className="mx-auto h-24 w-24 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                        </svg>
                        <h3 className="mt-6 text-xl font-medium text-gray-900">No videos yet</h3>
                        <p className="mt-2 text-gray-500">Start creating your first video to see it here!</p>
                        
                        {debugInfo && !debugInfo.success && (
                            <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                                <h4 className="text-sm font-medium text-yellow-800">Configuration Issue Detected</h4>
                                <p className="text-sm text-yellow-700 mt-1">
                                    It looks like there might be a connection issue. Check the debug guide.
                                </p>
                                <details className="mt-2">
                                    <summary className="text-xs text-yellow-600 cursor-pointer">
                                        Show details
                                    </summary>
                                    <pre className="text-xs mt-2 text-yellow-800 overflow-auto">
                                        {JSON.stringify(debugInfo, null, 2)}
                                    </pre>
                                </details>
                            </div>
                        )}
                        
                        <div className="mt-6 flex gap-3 justify-center">
                            <button
                                onClick={() => {
                                    // Switch to generator tab
                                    const generatorTab = document.querySelector('[data-tab="generator"]') as HTMLButtonElement;
                                    if (generatorTab) generatorTab.click();
                                }}
                                className="btn-primary"
                            >
                                Create Your First Video
                            </button>
                            <button
                                onClick={loadVideos}
                                className="btn-secondary"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {videos.map((video, index) => {
                            const statusInfo = getStatusInfo(video.status);
                            return (
                                <motion.div
                                    key={video.$id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.3, delay: index * 0.1 }}
                                    className="glass-card overflow-hidden"
                                >
                                    <div className="p-6">
                                        <div className="flex items-start justify-between mb-4">
                                            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                                                {video.topic}
                                            </h3>
                                            <div className={`flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium text-white ${statusInfo.color}`}>
                                                <span>{statusInfo.icon}</span>
                                                <span>{statusInfo.text}</span>
                                            </div>
                                        </div>

                                        {video.description && (
                                            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                                                {video.description}
                                            </p>
                                        )}

                                        <div className="space-y-2 text-xs text-gray-500">
                                            <div className="flex justify-between">
                                                <span>Created:</span>
                                                <span>{formatDate(video.created_at)}</span>
                                            </div>
                                            {video.scene_count > 0 && (
                                                <div className="flex justify-between">
                                                    <span>Scenes:</span>
                                                    <span>{video.scene_count}</span>
                                                </div>
                                            )}
                                            {video.total_duration && (
                                                <div className="flex justify-between">
                                                    <span>Duration:</span>
                                                    <span>{Math.round(video.total_duration)}s</span>
                                                </div>
                                            )}
                                        </div>

                                        {video.status === 'completed' && video.combined_video_url && (
                                            <div className="mt-4 space-y-2">
                                                {videoFileStatus[video.$id] === true ? (
                                                    <>
                                                        <button
                                                            onClick={() => setSelectedVideo(video)}
                                                            className="w-full rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-100 transition-colors"
                                                        >
                                                            Watch Video
                                                        </button>
                                                        <a
                                                            href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, video.combined_video_url)}
                                                            download
                                                            className="block w-full rounded-lg bg-gray-50 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors text-center"
                                                        >
                                                            Download
                                                        </a>
                                                    </>
                                                ) : videoFileStatus[video.$id] === false ? (
                                                    <div className="p-3 bg-orange-50 rounded-lg">
                                                        <p className="text-xs text-orange-600 text-center">
                                                            ⚠️ Video file not found in storage
                                                        </p>
                                                        <p className="text-xs text-orange-500 text-center mt-1">
                                                            File: {video.combined_video_url}
                                                        </p>
                                                    </div>
                                                ) : (
                                                    <div className="p-3 bg-gray-50 rounded-lg">
                                                        <p className="text-xs text-gray-500 text-center">
                                                            🔍 Checking video availability...
                                                        </p>
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {video.status === 'failed' && video.error_message && (
                                            <div className="mt-4 p-3 bg-red-50 rounded-lg">
                                                <p className="text-xs text-red-600">{video.error_message}</p>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Video Modal */}
            <AnimatePresence>
                {selectedVideo && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-75"
                        onClick={() => setSelectedVideo(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-auto"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-semibold">{selectedVideo.topic}</h3>
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            {selectedVideo.combined_video_url && (
                                <div className="rounded-lg overflow-hidden bg-black mb-4">
                                    <video 
                                        controls 
                                        className="w-full max-h-96 object-contain"
                                        preload="metadata"
                                        onError={(e) => {
                                            console.error('🎬 Video playback error:', e);
                                            const video = e.target as HTMLVideoElement;
                                            video.style.display = 'none';
                                            // Show error message
                                            const errorDiv = video.parentElement?.querySelector('.video-error') as HTMLDivElement;
                                            if (errorDiv) {
                                                errorDiv.style.display = 'block';
                                            }
                                        }}
                                        onLoadStart={() => {
                                            console.log('🎬 Video loading started for:', selectedVideo.topic);
                                        }}
                                        onLoadedData={() => {
                                            console.log('🎬 Video loaded successfully for:', selectedVideo.topic);
                                        }}
                                    >
                                        <source src={getFileUrl(FINAL_VIDEOS_BUCKET_ID, selectedVideo.combined_video_url)} type="video/mp4" />
                                        Your browser does not support the video tag.
                                    </video>
                                    
                                    {/* Error Message (hidden by default) */}
                                    <div className="video-error p-6 text-center text-white" style={{ display: 'none' }}>
                                        <div className="space-y-3">
                                            <div className="text-red-400">
                                                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                                                </svg>
                                            </div>
                                            <h3 className="text-lg font-medium">Video Playback Error</h3>
                                            <p className="text-sm text-gray-300">
                                                The video file could not be loaded. This might be due to:
                                            </p>
                                            <ul className="text-xs text-gray-400 text-left space-y-1 max-w-md mx-auto">
                                                <li>• File not uploaded to storage yet</li>
                                                <li>• Incorrect file permissions</li>
                                                <li>• Video still being processed</li>
                                                <li>• Network connectivity issues</li>
                                            </ul>
                                            <p className="text-xs text-gray-500 mt-4">
                                                File: {selectedVideo.combined_video_url}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {selectedVideo.description && (
                                <div className="mb-4">
                                    <h4 className="font-medium mb-2">Description</h4>
                                    <p className="text-gray-600">{selectedVideo.description}</p>
                                </div>
                            )}

                            <div className="flex gap-3">
                                {selectedVideo.combined_video_url && (
                                    <a
                                        href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, selectedVideo.combined_video_url)}
                                        download
                                        className="btn-primary flex-1"
                                    >
                                        <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                        </svg>
                                        Download Video
                                    </a>
                                )}
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="btn-secondary flex-1"
                                >
                                    Close
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
} 