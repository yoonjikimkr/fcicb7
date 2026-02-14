import React from 'react';
import { InsightData } from '../types';

interface GlassCardProps extends Partial<InsightData> {
  children: React.ReactNode;
  className?: string;
  showInsight?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({ 
  title, 
  children, 
  insight, 
  interpretation,
  className = "",
  showInsight = true
}) => {
  return (
    <div className={`h-full flex flex-col gap-4 ${className}`}>
      {/* Visual Area */}
      <div className="flex-grow min-h-0 relative rounded-xl border border-white/10 bg-slate-900/30 overflow-hidden p-4">
        {children}
      </div>

      {/* Text Area */}
      {showInsight && (insight || interpretation) && (
        <div className="flex-none grid grid-cols-1 md:grid-cols-2 gap-4 bg-white/5 p-4 rounded-xl border border-white/5">
          {insight && (
            <div className="space-y-1">
              <h4 className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
                비즈니스 인사이트
              </h4>
              <p className="text-slate-300 text-xs leading-relaxed text-justify opacity-90 break-keep">
                {insight}
              </p>
            </div>
          )}
          
          {interpretation && (
            <div className="space-y-1">
              <h4 className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                분석 해석 및 방법론
              </h4>
              <p className="text-slate-400 text-xs leading-relaxed text-justify opacity-80 break-keep">
                {interpretation}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
