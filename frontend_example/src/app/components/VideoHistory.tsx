'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    getAllVideoFiles, 
    getFileUrl, 
    FINAL_VIDEOS_BUCKET_ID,
    testConnection
} from '../services/appwrite';

interface VideoFile {
    $id: string;
    name: string;
    signature: string;
    mimeType: string;
    sizeOriginal: number;
    $createdAt: string;
    $updatedAt: string;
}

export default function VideoHistory() {
    const [videoFiles, setVideoFiles] = useState<VideoFile[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedVideo, setSelectedVideo] = useState<VideoFile | null>(null);
    const [debugInfo, setDebugInfo] = useState<any>(null);

    useEffect(() => {
        loadVideoFiles();
    }, []);

    // Handle body scroll and modal classes
    useEffect(() => {
        if (selectedVideo) {
            document.body.classList.add('video-modal-open');
        } else {
            document.body.classList.remove('video-modal-open');
        }
        
        return () => {
            document.body.classList.remove('video-modal-open');
        };
    }, [selectedVideo]);

    const loadVideoFiles = async () => {
        try {
            setLoading(true);
            setError(null);
            
            console.log('🎬 VideoHistory: Starting to load video files from storage...');
            
            // Test connection first
            const connectionTest = await testConnection();
            setDebugInfo(connectionTest);
            
            if (!connectionTest.success) {
                throw new Error(`Connection failed: ${connectionTest.error}`);
            }
            
            console.log('🎬 VideoHistory: Connection test passed, fetching files from storage...');
            const files = await getAllVideoFiles();
            
            console.log('🎬 VideoHistory: Received files:', files.length);
            setVideoFiles(files);
            
        } catch (err) {
            console.error('🎬 VideoHistory: Error loading video files:', err);
            setError(err instanceof Error ? err.message : 'Failed to load video files');
        } finally {
            setLoading(false);
        }
    };

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
                        <p className="mt-4 text-lg text-gray-300">Loading video files from storage...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="section-container">
                <div className="mx-auto max-w-lg glass-card border-red-500/20 p-6">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                            </svg>
                        </div>
                        <div className="ml-3 w-full">
                            <h3 className="text-sm font-medium text-red-300">Error Loading Video Files</h3>
                            <p className="mt-2 text-sm text-red-400">{error}</p>
                            
                            {debugInfo && (
                                <details className="mt-4">
                                    <summary className="text-xs text-red-300 cursor-pointer hover:text-red-200">
                                        Debug Information (Click to expand)
                                    </summary>
                                    <div className="mt-2 p-3 bg-red-900/20 rounded text-xs text-red-300 border border-red-500/20">
                                        <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
                                    </div>
                                </details>
                            )}
                            
                            <button 
                                onClick={loadVideoFiles}
                                className="btn-secondary mt-3"
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
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="relative mx-auto w-fit mb-6"
                    >
                        <p className="text-sm font-medium text-gray-400 relative">
                            <span className="absolute -left-16 top-1/2 w-12 h-px bg-gradient-to-r from-transparent to-blue-400 opacity-50"></span>
                            Your Animation Library
                            <span className="absolute -right-16 top-1/2 w-12 h-px bg-gradient-to-l from-transparent to-blue-400 opacity-50"></span>
                        </p>
                    </motion.div>
                    <h2 className="text-3xl md:text-4xl font-bold text-gradient mb-4">Video Storage</h2>
                    <p className="text-lg text-gray-400">
                        All video files in the storage bucket ({videoFiles.length} files)
                    </p>
                </div>

                {videoFiles.length === 0 ? (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center py-12"
                    >
                        <div className="relative mb-8">
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-32 h-32 bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-full blur-xl"></div>
                            </div>
                            <svg className="relative mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
                            </svg>
                        </div>
                        <h3 className="text-2xl font-bold text-gradient mb-3">No Videos Yet</h3>
                        <p className="text-gray-400 mb-8 max-w-md mx-auto">
                            Your animation library is empty. Create your first educational video to get started!
                        </p>
                        
                        <div className="flex gap-4 justify-center">
                            <button
                                onClick={() => {
                                    // Switch to generator tab
                                    const generatorTab = document.querySelector('[data-tab="generator"]') as HTMLButtonElement;
                                    if (generatorTab) generatorTab.click();
                                }}
                                className="btn-primary"
                            >
                                <span className="glow"></span>
                                <span className="relative z-10 flex items-center gap-2">
                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                                    </svg>
                                    Create Your First Video
                                </span>
                            </button>
                            <button
                                onClick={loadVideoFiles}
                                className="btn-secondary"
                            >
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
                                </svg>
                                Refresh
                            </button>
                        </div>
                    </motion.div>
                ) : (
                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {videoFiles.map((file, index) => (
                            <motion.div
                                key={file.$id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.3, delay: index * 0.1 }}
                                className="glass-card overflow-hidden"
                            >
                                <div className="p-6">
                                    <div className="flex items-start justify-between mb-4">
                                        <h3 className="text-lg font-semibold text-white line-clamp-2">
                                            {file.name.replace(/\.(mp4|mov|avi|mkv)$/i, '')}
                                        </h3>
                                        <div className="flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium bg-green-500/20 border border-green-500/30 text-green-300">
                                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                            <span>Available</span>
                                        </div>
                                    </div>

                                    <div className="space-y-2 text-xs text-gray-400">
                                        <div className="flex justify-between">
                                            <span>File Size:</span>
                                            <span className="text-gray-300">{formatFileSize(file.sizeOriginal)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Created:</span>
                                            <span className="text-gray-300">{formatDate(file.$createdAt)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Type:</span>
                                            <span className="text-gray-300">{file.mimeType}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>File ID:</span>
                                            <span className="font-mono text-xs text-gray-300">{file.$id.substring(0, 8)}...</span>
                                        </div>
                                    </div>

                                    <div className="mt-6 space-y-3">
                                        <button
                                            onClick={() => setSelectedVideo(file)}
                                            className="btn-primary w-full"
                                        >
                                            <span className="glow"></span>
                                            <span className="relative z-10 flex items-center justify-center gap-2">
                                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                                                </svg>
                                                Watch Video
                                            </span>
                                        </button>
                                        <a
                                            href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, file.$id)}
                                            download={file.name}
                                            className="btn-secondary w-full flex items-center justify-center gap-2"
                                        >
                                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                            </svg>
                                            Download
                                        </a>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
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
                        className="video-modal fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md"
                        onClick={() => setSelectedVideo(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="glass-card max-w-4xl w-full max-h-[90vh] overflow-auto p-8 relative z-[10000]"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-xl font-semibold text-white">{selectedVideo.name}</h3>
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="p-2 hover:bg-gray-700/50 rounded-lg transition-colors text-gray-300 hover:text-white"
                                >
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="rounded-lg overflow-hidden bg-black mb-4">
                                <video 
                                    controls 
                                    className="w-full max-h-96 object-contain"
                                    preload="metadata"
                                    onError={(e) => {
                                        console.error('🎬 Video playback error:', e);
                                    }}
                                    onLoadStart={() => {
                                        console.log('🎬 Video loading started for:', selectedVideo.name);
                                    }}
                                    onLoadedData={() => {
                                        console.log('🎬 Video loaded successfully for:', selectedVideo.name);
                                    }}
                                >
                                    <source src={getFileUrl(FINAL_VIDEOS_BUCKET_ID, selectedVideo.$id)} type="video/mp4" />
                                    Your browser does not support the video tag.
                                </video>
                            </div>

                            <div className="mb-6">
                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-400">
                                    <div>
                                        <span className="font-medium text-gray-300">File Size:</span> {formatFileSize(selectedVideo.sizeOriginal)}
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-300">Created:</span> {formatDate(selectedVideo.$createdAt)}
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-300">Type:</span> {selectedVideo.mimeType}
                                    </div>
                                    <div>
                                        <span className="font-medium text-gray-300">File ID:</span> {selectedVideo.$id}
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <a
                                    href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, selectedVideo.$id)}
                                    download={selectedVideo.name}
                                    className="btn-primary flex-1"
                                >
                                    <span className="glow"></span>
                                    <span className="relative z-10 flex items-center justify-center gap-2">
                                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                        </svg>
                                        Download Video
                                    </span>
                                </a>
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