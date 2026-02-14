import React, { useContext } from 'react';
import { SlideProps } from '../types';
import { PrintContext } from '../contexts';

export const Slide: React.FC<SlideProps> = ({ 
  isActive, 
  pageNumber, 
  totalPages, 
  title, 
  subTitle,
  children 
}) => {
  const isPrintMode = useContext(PrintContext);

  // In standard mode, only render active slide. In print mode, render all.
  if (!isActive && !isPrintMode) return null;

  return (
    <div className={`
      flex flex-col animate-in fade-in zoom-in-95 duration-500
      ${isPrintMode ? 'h-screen w-full page-break-after-always p-8 border-b border-dashed border-slate-700' : 'h-full'}
    `}>
      {/* Header */}
      <div className="flex-none mb-4 px-2">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-sky-400 to-indigo-200">
          {title}
        </h2>
        {subTitle && (
          <p className="text-slate-400 text-sm mt-1 border-l-2 border-sky-500 pl-3">
            {subTitle}
          </p>
        )}
      </div>

      {/* Main Content Area */}
      <div className={`
        flex-grow relative rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-md shadow-2xl p-6
        ${isPrintMode ? 'overflow-visible' : 'overflow-hidden'}
      `}>
        {children}
      </div>

      {/* Footer / Page Number */}
      <div className="flex-none mt-4 flex justify-between items-center text-xs text-slate-500 font-mono px-2">
        <span>2024 - 2025 Korea Biggest Holidays Gift Trend Analysis Report</span>
        <span>{pageNumber} / {totalPages}</span>
      </div>
    </div>
  );
};
