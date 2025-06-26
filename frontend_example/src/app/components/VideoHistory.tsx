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
                        <p className="mt-4 text-lg text-gray-600">Loading video files from storage...</p>
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
                            <h3 className="text-sm font-medium text-red-800">Error Loading Video Files</h3>
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
                                onClick={loadVideoFiles}
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
                    <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Video Storage</h2>
                    <p className="mt-6 text-lg leading-8 text-gray-600">
                        All video files in the storage bucket ({videoFiles.length} files)
                    </p>
                </div>

                {videoFiles.length === 0 ? (
                    <div className="text-center py-12">
                        <svg className="mx-auto h-24 w-24 text-gray-300" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026C6.923 9.75 8.25 11.077 8.25 12.75c0 .414.336.75.75.75s.75-.336.75-.75c0-1.673 1.327-3 3-3 .117 0 .232.009.344.026m-7.838 3.47c.395.442.903.814 1.479 1.068.113.05.23.094.351.133.132.042.268.078.409.11.126.028.256.05.388.067.014.002.027.004.041.006.14.018.283.028.428.028 2.484 0 4.5-2.016 4.5-4.5s-2.016-4.5-4.5-4.5c-.145 0-.288.01-.428.028-.014.002-.027.004-.041.006-.132.017-.262.039-.388.067-.141.032-.277.068-.409.11-.121.039-.238.083-.351.133-.576.254-1.084.626-1.479 1.068z" />
                        </svg>
                        <h3 className="mt-6 text-xl font-medium text-gray-900">No video files found</h3>
                        <p className="mt-2 text-gray-500">No videos are currently stored in the final_videos bucket</p>
                        
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
                                onClick={loadVideoFiles}
                                className="btn-secondary"
                            >
                                Refresh
                            </button>
                        </div>
                    </div>
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
                                        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                                            {file.name.replace(/\.(mp4|mov|avi|mkv)$/i, '')}
                                        </h3>
                                        <div className="flex items-center gap-1.5 rounded-full px-2 py-1 text-xs font-medium text-white bg-green-500">
                                            <span>✅</span>
                                            <span>Available</span>
                                        </div>
                                    </div>

                                    <div className="space-y-2 text-xs text-gray-500">
                                        <div className="flex justify-between">
                                            <span>File Size:</span>
                                            <span>{formatFileSize(file.sizeOriginal)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Created:</span>
                                            <span>{formatDate(file.$createdAt)}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Type:</span>
                                            <span>{file.mimeType}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>File ID:</span>
                                            <span className="font-mono text-xs">{file.$id.substring(0, 8)}...</span>
                                        </div>
                                    </div>

                                    <div className="mt-4 space-y-2">
                                        <button
                                            onClick={() => setSelectedVideo(file)}
                                            className="w-full rounded-lg bg-blue-50 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-100 transition-colors"
                                        >
                                            Watch Video
                                        </button>
                                        <a
                                            href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, file.$id)}
                                            download={file.name}
                                            className="block w-full rounded-lg bg-gray-50 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors text-center"
                                        >
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
                                <h3 className="text-xl font-semibold">{selectedVideo.name}</h3>
                                <button
                                    onClick={() => setSelectedVideo(null)}
                                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
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

                            <div className="mb-4">
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="font-medium">File Size:</span> {formatFileSize(selectedVideo.sizeOriginal)}
                                    </div>
                                    <div>
                                        <span className="font-medium">Created:</span> {formatDate(selectedVideo.$createdAt)}
                                    </div>
                                    <div>
                                        <span className="font-medium">Type:</span> {selectedVideo.mimeType}
                                    </div>
                                    <div>
                                        <span className="font-medium">File ID:</span> {selectedVideo.$id}
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-3">
                                <a
                                    href={getFileUrl(FINAL_VIDEOS_BUCKET_ID, selectedVideo.$id)}
                                    download={selectedVideo.name}
                                    className="btn-primary flex-1"
                                >
                                    <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                    </svg>
                                    Download Video
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