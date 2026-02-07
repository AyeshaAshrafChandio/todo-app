'use client';

import { Card, CardBody } from '@/components/ui/Card';
import type { StatisticCardData } from '@/lib/types/dashboard';

interface StatisticsCardProps {
  data: StatisticCardData;
  loading?: boolean;
}

/**
 * StatisticsCard Component
 *
 * Displays a single statistic with icon, label, and value
 * Supports loading state and responsive design
 *
 * @param data - Statistic data to display
 * @param loading - Loading state
 */
export function StatisticsCard({ data, loading }: StatisticsCardProps) {
  const { label, value, icon, color, bgColor } = data;

  // Color mapping for text
  const textColorMap = {
    primary: 'text-gray-900',
    yellow: 'text-yellow-600',
    green: 'text-green-600',
    blue: 'text-blue-600',
  };

  const textColor = textColorMap[color];

  return (
    <Card variant="elevated" className="h-full">
      <CardBody>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm text-gray-600 font-medium">{label}</p>
            <p className={`text-3xl font-bold mt-2 ${textColor}`}>
              {loading ? (
                <span className="inline-block w-12 h-8 bg-gray-200 animate-pulse rounded"></span>
              ) : (
                value
              )}
            </p>
          </div>
          <div
            className={`h-12 w-12 ${bgColor} rounded-full flex items-center justify-center flex-shrink-0 ml-4`}
            aria-hidden="true"
          >
            <span className="text-2xl" role="img" aria-label={label}>
              {icon}
            </span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
