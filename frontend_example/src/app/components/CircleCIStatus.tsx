'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface PipelineStatus {
  status: 'success' | 'running' | 'failed' | 'canceled' | 'pending';
  branch: string;
  buildNumber: string;
  sha: string;
  duration?: number;
  triggeredBy?: string;
  createdAt: string;
}

const CircleCIStatus: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);

  useEffect(() => {
    // Mock pipeline status - in real implementation, you'd fetch from CircleCI API
    if (process.env.CIRCLE_BUILD_NUM) {
      setPipelineStatus({
        status: 'success',
        branch: process.env.CIRCLE_BRANCH || 'main',
        buildNumber: process.env.CIRCLE_BUILD_NUM,
        sha: process.env.CIRCLE_SHA1 || '',
        duration: 180, // seconds
        triggeredBy: process.env.CIRCLE_USERNAME || 'CircleCI',
        createdAt: new Date().toISOString(),
      });
    }
  }, []);

  if (!pipelineStatus) {
    return null;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return (
          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'running':
        return (
          <svg className="w-4 h-4 text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      case 'failed':
        return (
          <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'border-green-200 bg-green-50';
      case 'running': return 'border-blue-200 bg-blue-50';
      case 'failed': return 'border-red-200 bg-red-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="fixed top-4 right-4 z-50"
    >
      <div className={`border rounded-lg shadow-lg ${getStatusColor(pipelineStatus.status)}`}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 p-3 w-full text-left"
        >
          {getStatusIcon(pipelineStatus.status)}
          <span className="text-sm font-medium">
            Build #{pipelineStatus.buildNumber}
          </span>
          <motion.svg
            className="w-4 h-4 ml-auto"
            animate={{ rotate: isExpanded ? 180 : 0 }}
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </motion.svg>
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-current/10"
            >
              <div className="p-3 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Branch:</span>
                  <span className="font-mono">{pipelineStatus.branch}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Commit:</span>
                  <span className="font-mono">{pipelineStatus.sha.substring(0, 7)}</span>
                </div>
                
                {pipelineStatus.duration && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span>{Math.floor(pipelineStatus.duration / 60)}m {pipelineStatus.duration % 60}s</span>
                  </div>
                )}
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Triggered:</span>
                  <span>{new Date(pipelineStatus.createdAt).toLocaleTimeString()}</span>
                </div>
                
                <div className="pt-2 border-t border-current/10">
                  <a
                    href={`https://app.circleci.com/pipelines/github/your-org/your-repo/${pipelineStatus.buildNumber}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    View in CircleCI
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                    </svg>
                  </a>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default CircleCIStatus; 