import React from 'react';

function LoadingOverlay({ isVisible }) {
  if (!isVisible) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 z-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-primary-600 border-opacity-100 bg-white bg-opacity-10 shadow-lg"></div>
    </div>
  );
}

export default LoadingOverlay;