import React from 'react';

export const Skeleton = ({
  width = '100%',
  height = 16,
  className = '',
  rounded = 'rounded-md',
}) => {
  return (
    <div
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
      className={`bg-slate-800/80 animate-pulse ${rounded} ${className}`}
    />
  );
};
