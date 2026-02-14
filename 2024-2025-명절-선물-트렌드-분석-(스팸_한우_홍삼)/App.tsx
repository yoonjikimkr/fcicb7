import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart
} from 'recharts';
import { Slide } from './components/Slide';
import { GlassCard } from './components/GlassCard';
import { PrintContext } from './contexts';
import * as CONST from './constants';
import { 
  ChevronLeft, ChevronRight, Activity, TrendingUp, TrendingDown,
  Play, RotateCcw, Printer, X, ShoppingBag, Calendar, Users, Database, CheckCircle
} from 'lucide-react';

const App: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [isPrintMode, setIsPrintMode] = useState(false);
  const totalSlides = 7;

  const nextSlide = () => setCurrentSlide(prev => Math.min(prev + 1, totalSlides));
  const prevSlide = () => setCurrentSlide(prev => Math.max(prev - 1, 1));
  
  // Keyboard Navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isPrintMode) return; // Disable keyboard nav in print mode
      if (e.key === 'ArrowRight' || e.key === 'Space') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isPrintMode]);

  return (
    <PrintContext.Provider value={isPrintMode}>
      <div className={`
        bg-[#0f172a] text-slate-100 font-sans relative
        ${isPrintMode ? 'min-h-screen w-full overflow-y-auto' : 'h-screen w-screen overflow-hidden flex flex-col'}
      `}>
        
        {/* CSS for Print */}
        <style>{`
          @media print {
            @page { size: landscape; margin: 0; }
            body { 
              -webkit-print-color-adjust: exact !important; 
              print-color-adjust: exact !important; 
              background-color: #0f172a !important; 
            }
            .no-print { display: none !important; }
            .page-break-after-always { break-after: always; page-break-after: always; }
            /* Force background colors in print */
            * { text-shadow: none !important; }
          }
          /* Custom Scrollbar for non-print mode */
          ::-webkit-scrollbar { width: 8px; height: 8px; }
          ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); }
          ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }
        `}</style>

        {/* Background Gradient Animation */}
        {!isPrintMode && (
          <div className="absolute inset-0 z-0 bg-[radial-gradient(circle_at_50%_50%,_rgba(56,189,248,0.1),_rgba(15,23,42,1))] pointer-events-none animate-pulse duration-[10000ms]"></div>
        )}

        {/* Slide Container */}
        <div className={`
          z-10 mx-auto w-full
          ${isPrintMode ? 'max-w-none p-0' : 'flex-grow p-4 md:p-8 max-w-[1600px] h-full'}
        `}>
          
          {/* Slide 1: Cover */}
          <Slide isActive={currentSlide === 1} pageNumber={1} totalPages={totalSlides} title="">
            <div className="h-full flex flex-col items-center justify-center text-center space-y-8">
              <div className="p-6 bg-pink-500/10 rounded-full border border-pink-500/30 shadow-[0_0_50px_rgba(244,114,182,0.3)] animate-bounce">
                <ShoppingBag className="w-20 h-20 text-pink-400" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-400 via-rose-400 to-orange-400 mb-4 tracking-tight">
                  2024-2025 명절(설날/추석) 선물 트렌드 분석
                </h1>
                <p className="text-xl md:text-3xl text-slate-300 font-light mt-4">
                  주요 품목 3종 비교: <span className="font-bold text-red-400">스팸</span> vs <span className="font-bold text-pink-400">한우</span> vs <span className="font-bold text-yellow-400">홍삼</span>
                </p>
                <p className="text-lg text-slate-500 mt-2">
                  가설 검증(Verification) 및 데이터 출처 포함
                </p>
              </div>
              <div className="mt-12 p-4 bg-white/5 rounded-xl border border-white/10 backdrop-blur text-sm text-slate-400">
                <p>Period: 2024 - 2025 (Lunar New Year & Chuseok)</p>
                <p>Focus: Ranking, Demographics, Purchase Timing</p>
              </div>
              {!isPrintMode && (
                <button onClick={nextSlide} className="flex items-center gap-2 px-6 py-3 bg-rose-600 hover:bg-rose-500 rounded-full font-bold transition-all shadow-lg hover:shadow-rose-500/50 mt-8">
                  <Play className="w-4 h-4" /> 분석 결과 보기
                </button>
              )}
            </div>
          </Slide>

        {/* Slide 2: Rank Validation */}
        <Slide isActive={currentSlide === 2} pageNumber={2} totalPages={totalSlides} title="순위 검증 (Rank Verification)" subTitle="실제 상위 1-3위 품목이 맞는가?">
           <GlassCard {...CONST.INSIGHT_TEXTS.rank_validation}>
              <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={CONST.categoryRankData} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#ffffff10" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#e2e8f0" width={120} tick={{fontSize: 14, fontWeight: 'bold'}} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                    <Bar dataKey="value" name="점유율 (%)" radius={[0, 4, 4, 0]} barSize={40}>
                       {CONST.categoryRankData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
           </GlassCard>
        </Slide>

        {/* Slide 3: Timing Analysis */}
        <Slide isActive={currentSlide === 3} pageNumber={3} totalPages={totalSlides} title="구매 시점 분석 (Timing)" subTitle="품목별로 구매 피크 타임이 언제인가?">
            <GlassCard {...CONST.INSIGHT_TEXTS.timing_analysis}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={CONST.itemTimingData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                        <XAxis dataKey="date" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" label={{ value: 'Search Interest', angle: -90, position: 'insideLeft' }} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                        <Legend verticalAlign="top" height={36}/>
                        <Line type="monotone" dataKey="hanwoo" name="한우 (Hanwoo)" stroke="#f472b6" strokeWidth={3} dot={{r: 4}} />
                        <Line type="monotone" dataKey="spam" name="스팸 (Spam)" stroke="#f43f5e" strokeWidth={3} dot={{r: 4}} />
                        <Line type="monotone" dataKey="ginseng" name="홍삼 (Ginseng)" stroke="#fbbf24" strokeWidth={3} dot={{r: 4}} />
                    </LineChart>
                </ResponsiveContainer>
            </GlassCard>
        </Slide>

        {/* Slide 4: Age Preference */}
        <Slide isActive={currentSlide === 4} pageNumber={4} totalPages={totalSlides} title="연령별 선호도 (Age Demographics)" subTitle="연령대에 따른 주 관심 품목 비교">
            <GlassCard {...CONST.INSIGHT_TEXTS.age_gender}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
                    {/* Radar Chart for Overall Shape */}
                    <div className="h-full min-h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="70%" data={CONST.agePreferenceData}>
                                <PolarGrid stroke="#ffffff20" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 14 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#ffffff20" />
                                <Radar name="스팸 (2030 Pick)" dataKey="A" stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.4} />
                                <Radar name="한우 (4050 Pick)" dataKey="B" stroke="#f472b6" fill="#f472b6" fillOpacity={0.4} />
                                <Legend />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Stacked Bar for Detail */}
                    <div className="h-full min-h-[300px]">
                         <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={CONST.agePreferenceData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                <XAxis dataKey="subject" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                <Legend />
                                <Bar dataKey="A" name="스팸" stackId="a" fill="#f43f5e" />
                                <Bar dataKey="B" name="한우" stackId="a" fill="#f472b6" />
                                <Bar dataKey="C" name="홍삼" stackId="a" fill="#fbbf24" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </GlassCard>
        </Slide>

         {/* Slide 5: Gender & Keyword */}
        <Slide isActive={currentSlide === 5} pageNumber={5} totalPages={totalSlides} title="성별 선호 및 연관 키워드" subTitle="남녀 관심도 차이와 구매 목적(Why)">
            <GlassCard title="" insight="스팸은 '자취생/가성비' 키워드와, 한우는 '부모님/시댁' 키워드와 강하게 결합되어 있습니다. 이는 스팸이 실용적 목적, 한우가 의례적(Ceremonial) 목적으로 구매됨을 증명합니다. 홍삼은 남성 구매 비중이 과반을 넘는 유일한 품목입니다." interpretation="성별 구매 비중 차트와 연관 검색어 상관관계 분석표입니다.">
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">
                     {/* Gender Chart */}
                    <div className="h-full">
                        <h4 className="text-center text-slate-400 mb-4 font-bold">성별 구매 비중 (Gender Ratio)</h4>
                        <ResponsiveContainer width="100%" height={250}>
                             <BarChart data={CONST.genderPreferenceData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" horizontal={false}/>
                                <XAxis type="number" hide/>
                                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} tick={{fontSize: 12}} />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                <Legend />
                                <Bar dataKey="male" name="남성 (Male)" stackId="a" fill="#60a5fa" />
                                <Bar dataKey="female" name="여성 (Female)" stackId="a" fill="#f472b6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    {/* Keyword Table */}
                    <div className="h-full overflow-auto">
                        <h4 className="text-center text-slate-400 mb-4 font-bold">주요 연관 검색어 (Keywords)</h4>
                        <table className="w-full text-left text-slate-300 text-sm">
                            <thead className="bg-white/5 border-b border-white/10">
                                <tr>
                                    <th className="p-2">Product</th>
                                    <th className="p-2">Top Keywords (Correlation)</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {CONST.keywordCorrelationTable.map((row, i) => (
                                    <tr key={i}>
                                        <td className="p-3 font-bold text-white">{row.product}</td>
                                        <td className="p-3 text-slate-400">
                                            1. {row.keyword1}<br/>
                                            2. {row.keyword2}<br/>
                                            3. {row.keyword3}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                 </div>
            </GlassCard>
        </Slide>

        {/* Slide 6: YoY Comparison */}
        <Slide isActive={currentSlide === 6} pageNumber={6} totalPages={totalSlides} title="종합 결론: 2024 vs 2025" subTitle="전년 대비 변화 흐름 (YoY)">
             <GlassCard {...CONST.INSIGHT_TEXTS.yoy_change}>
                <div className="h-full flex flex-col justify-center">
                    <ResponsiveContainer width="100%" height="50%">
                        <BarChart data={CONST.yoyGrowthData}>
                             <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                             <XAxis dataKey="name" stroke="#94a3b8" tick={{fontSize: 14, fontWeight: 'bold'}} />
                             <YAxis stroke="#94a3b8" />
                             <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                             <Bar dataKey="y2025" name="2025 Index (vs 2024=100)" fill="#818cf8" label={{ position: 'top', fill: 'white' }}>
                                {CONST.yoyGrowthData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.name === '스팸' ? '#f43f5e' : entry.name === '한우' ? '#94a3b8' : '#fbbf24'} />
                                ))}
                             </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="mt-8 grid grid-cols-3 gap-4 text-center">
                        <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                            <h4 className="text-red-400 font-bold mb-2">스팸 (Spam)</h4>
                            <p className="text-sm text-slate-300">실속형 트렌드 주도<br/>2030 남성 선호 급증</p>
                        </div>
                        <div className="p-4 bg-pink-500/10 rounded-lg border border-pink-500/20">
                            <h4 className="text-pink-400 font-bold mb-2">한우 (Hanwoo)</h4>
                            <p className="text-sm text-slate-300">고가 부담으로 소폭 하락<br/>40대 여성 핵심 타겟</p>
                        </div>
                        <div className="p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                            <h4 className="text-yellow-400 font-bold mb-2">홍삼 (Ginseng)</h4>
                            <p className="text-sm text-slate-300">스테디셀러 유지<br/>50대 이상 필수 품목</p>
                        </div>
                    </div>
                </div>
            </GlassCard>
        </Slide>

        {/* Slide 7: Verification Summary & Data Sources */}
        <Slide isActive={currentSlide === 7} pageNumber={7} totalPages={totalSlides} title="데이터 출처 및 가설 검증" subTitle="사용된 API 및 최종 검증 리포트">
            <GlassCard {...CONST.INSIGHT_TEXTS.verification_summary}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">
                    {/* Data Sources List */}
                    <div className="h-full overflow-auto">
                         <h4 className="flex items-center gap-2 text-sky-400 font-bold text-lg mb-4">
                            <Database className="w-5 h-5" /> 사용된 데이터 출처 (APIs)
                        </h4>
                        <div className="space-y-4">
                            {CONST.dataSources.map((source, i) => (
                                <div key={i} className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-sky-500/50 transition-colors">
                                    <h5 className="font-bold text-white mb-1">{source.name}</h5>
                                    <p className="text-sm text-slate-400">{source.usage}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Verification Checklist */}
                    <div className="h-full overflow-auto">
                        <h4 className="flex items-center gap-2 text-emerald-400 font-bold text-lg mb-4">
                            <CheckCircle className="w-5 h-5" /> 가설 검증 요약 (Summary)
                        </h4>
                        <div className="space-y-4">
                            {CONST.verificationStatus.map((item, i) => (
                                <div key={i} className="flex gap-4 p-4 bg-emerald-900/10 rounded-xl border border-emerald-500/20">
                                    <div className="flex-none pt-1">
                                        <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                                            <CheckCircle className="w-3 h-3 text-black font-bold" />
                                        </div>
                                    </div>
                                    <div>
                                        <h5 className="font-bold text-emerald-100">{item.hypothesis}</h5>
                                        <p className="text-xs font-bold text-emerald-400 mt-1 mb-2">[{item.result}]</p>
                                        <p className="text-sm text-slate-300 leading-snug">{item.detail}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </GlassCard>
        </Slide>

      </div>

      {/* Navigation Controls */}
      {!isPrintMode && (
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-50 flex items-center gap-6 bg-slate-900/80 backdrop-blur-md px-6 py-3 rounded-full border border-white/10 shadow-2xl">
          <button 
            onClick={prevSlide}
            disabled={currentSlide === 1}
            className="p-2 rounded-full hover:bg-white/10 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <span className="text-sm font-mono text-slate-400 min-w-[60px] text-center">
            {currentSlide} / {totalSlides}
          </span>
          <button 
            onClick={nextSlide}
            disabled={currentSlide === totalSlides}
            className="p-2 rounded-full hover:bg-white/10 disabled:opacity-30 disabled:hover:bg-transparent transition-colors"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
          <div className="w-px h-6 bg-white/10 mx-2"></div>
          <button
            onClick={() => setIsPrintMode(true)}
            className="p-2 rounded-full text-sky-400 hover:bg-sky-500/20 hover:text-sky-300 transition-colors tooltip relative group"
            title="PDF 인쇄 모드"
          >
             <Printer className="w-5 h-5" />
             <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 text-xs bg-black text-white rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
               PDF로 저장
             </span>
          </button>
        </div>
      )}

      {/* Print Mode Close Button */}
      {isPrintMode && (
        <div className="fixed bottom-8 right-8 z-50 no-print animate-in slide-in-from-bottom-4">
            <button
                onClick={() => setIsPrintMode(false)}
                className="flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-full font-bold shadow-2xl transition-all"
            >
                <X className="w-5 h-5" /> 뷰어 모드로 돌아가기
            </button>
        </div>
      )}

    </div>
    </PrintContext.Provider>
  );
};

// Helper Components
const StatCard = ({ title, value, change, trend }: { title: string, value: string, change: string, trend: 'up' | 'down' | 'neutral' }) => (
  <div className="bg-white/5 backdrop-blur-lg border border-white/10 p-6 rounded-xl hover:bg-white/10 transition-colors group cursor-pointer hover:border-sky-500/30 hover:shadow-lg hover:shadow-sky-500/10">
    <h3 className="text-slate-400 text-sm font-medium mb-2 group-hover:text-white transition-colors flex justify-between items-center">
        {title}
        {trend === 'up' && <TrendingUp className="w-4 h-4 text-emerald-500 opacity-50 group-hover:opacity-100" />}
        {trend === 'down' && <TrendingDown className="w-4 h-4 text-red-500 opacity-50 group-hover:opacity-100" />}
    </h3>
    <div className="flex items-end justify-between">
      <span className="text-4xl font-bold text-white tracking-tight">{value}</span>
      <span className={`text-sm font-medium px-2 py-1 rounded-full flex items-center gap-1 ${
        trend === 'up' ? 'bg-emerald-500/20 text-emerald-400' : 
        trend === 'down' ? 'bg-red-500/20 text-red-400' : 
        'bg-slate-500/20 text-slate-400'
      }`}>
        {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '•'} {change}
      </span>
    </div>
  </div>
);

export default App;