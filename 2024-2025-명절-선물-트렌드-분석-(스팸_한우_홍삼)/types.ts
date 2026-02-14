import React from 'react';

export interface InsightData {
  title: string;
  insight: string;
  interpretation: string;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  fill: string;
  [key: string]: string | number;
}

export interface TableRow {
  [key: string]: string | number;
}

export interface SlideProps {
  isActive: boolean;
  pageNumber: number;
  totalPages: number;
  title: string;
  subTitle?: string;
  children: React.ReactNode;
}