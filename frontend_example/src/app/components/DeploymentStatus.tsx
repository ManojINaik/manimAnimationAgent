'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface BuildInfo {
  branch?: string;
  buildNumber?: string;
  sha?: string;
  timestamp?: string;
}

const DeploymentStatus: React.FC = () => {
  const buildInfo: BuildInfo = {
    branch: process.env.CIRCLE_BRANCH || process.env.NEXT_PUBLIC_BRANCH || 'main',
    buildNumber: process.env.CIRCLE_BUILD_NUM || process.env.NEXT_PUBLIC_BUILD_NUM,
    sha: process.env.CIRCLE_SHA1 || process.env.NEXT_PUBLIC_SHA,
    timestamp: process.env.NEXT_PUBLIC_BUILD_TIME || new Date().toISOString(),
  };

  const isProduction = process.env.NODE_ENV === 'production';
  const isCircleCI = !!process.env.CIRCLE_BUILD_NUM;

  if (!isProduction && !process.env.NEXT_PUBLIC_SHOW_BUILD_INFO) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-4 right-4 z-50"
    >
      <div className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg p-3 min-w-[200px]">
        <div className="flex items-center gap-2 mb-2">
          <div className={`w-2 h-2 rounded-full ${isCircleCI ? 'bg-green-500' : 'bg-blue-500'}`}></div>
          <span className="text-sm font-medium text-gray-700">
            {isCircleCI ? 'CircleCI Deploy' : 'Local Build'}
          </span>
        </div>
        
        <div className="space-y-1 text-xs text-gray-600">
          {buildInfo.branch && (
            <div className="flex justify-between">
              <span>Branch:</span>
              <span className="font-mono">{buildInfo.branch}</span>
            </div>
          )}
          
          {buildInfo.buildNumber && (
            <div className="flex justify-between">
              <span>Build:</span>
              <span className="font-mono">#{buildInfo.buildNumber}</span>
            </div>
          )}
          
          {buildInfo.sha && (
            <div className="flex justify-between">
              <span>Commit:</span>
              <span className="font-mono">{buildInfo.sha.substring(0, 7)}</span>
            </div>
          )}
          
          {buildInfo.timestamp && (
            <div className="flex justify-between">
              <span>Built:</span>
              <span className="font-mono">
                {new Date(buildInfo.timestamp).toLocaleDateString()}
              </span>
            </div>
          )}
        </div>
        
        {isCircleCI && (
          <div className="mt-2 pt-2 border-t border-gray-100">
            <a
              href={`https://app.circleci.com/pipelines/github/your-org/your-repo/${buildInfo.buildNumber}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              View Build
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
              </svg>
            </a>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default DeploymentStatus; 