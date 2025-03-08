import React from 'react';

function LoadingOverlay({ isVisible }) {
  if (!isVisible) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white"></div>
    </div>
  );
}

export default LoadingOverlay;
