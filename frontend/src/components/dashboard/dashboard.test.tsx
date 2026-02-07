import { render, screen, waitFor } from '@testing-library/react';
import { StatisticsCard } from '@/components/dashboard/StatisticsCard';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import type { StatisticCardData } from '@/lib/types/dashboard';

// Mock SWR
jest.mock('swr', () => ({
  __esModule: true,
  default: jest.fn(),
}));

// Mock dashboard hook
jest.mock('@/hooks/useDashboard', () => ({
  useDashboard: jest.fn(),
}));

import useSWR from 'swr';
import { useDashboard } from '@/hooks/useDashboard';

const mockUseSWR = useSWR as jest.MockedFunction<typeof useSWR>;
const mockUseDashboard = useDashboard as jest.MockedFunction<typeof useDashboard>;

describe('Dashboard Components', () => {
  describe('StatisticsCard', () => {
    const mockCardData: StatisticCardData = {
      label: 'Total Tasks',
      value: 42,
      icon: '📋',
      color: 'primary',
      bgColor: 'bg-primary-100',
    };

    it('renders card with correct data', () => {
      render(<StatisticsCard data={mockCardData} loading={false} />);

      expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('📋')).toBeInTheDocument();
    });

    it('shows loading state', () => {
      render(<StatisticsCard data={mockCardData} loading={true} />);

      expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      // Loading skeleton should be present
      const loadingSkeleton = screen.getByText('Total Tasks').parentElement?.querySelector('.animate-pulse');
      expect(loadingSkeleton).toBeInTheDocument();
    });

    it('applies correct color classes', () => {
      const { container } = render(<StatisticsCard data={mockCardData} loading={false} />);

      // Check if primary color is applied
      const valueElement = screen.getByText('42');
      expect(valueElement).toHaveClass('text-gray-900');
    });
  });

  describe('DashboardLayout', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('renders statistics cards with data', () => {
      mockUseDashboard.mockReturnValue({
        statistics: {
          total_tasks: 15,
          pending_tasks: 8,
          completed_tasks: 7,
          shared_tasks: 3,
        },
        loading: false,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      render(<DashboardLayout />);

      expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('Pending Tasks')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      expect(screen.getByText('7')).toBeInTheDocument();
      expect(screen.getByText('Shared Tasks')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('shows loading state', () => {
      mockUseDashboard.mockReturnValue({
        statistics: null,
        loading: true,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      render(<DashboardLayout />);

      // Should show loading skeletons
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('shows error state with retry button', () => {
      const mockRetry = jest.fn();
      mockUseDashboard.mockReturnValue({
        statistics: null,
        loading: false,
        error: new Error('Failed to fetch'),
        mutate: jest.fn(),
        retry: mockRetry,
      });

      render(<DashboardLayout />);

      expect(screen.getByText('Failed to Load Dashboard Statistics')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();

      // Click retry button
      const retryButton = screen.getByText('Retry');
      retryButton.click();
      expect(mockRetry).toHaveBeenCalledTimes(1);
    });

    it('shows live update indicator when data is loaded', () => {
      mockUseDashboard.mockReturnValue({
        statistics: {
          total_tasks: 15,
          pending_tasks: 8,
          completed_tasks: 7,
          shared_tasks: 3,
        },
        loading: false,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      render(<DashboardLayout />);

      expect(screen.getByText('Live updates every 5 seconds')).toBeInTheDocument();
      expect(screen.getByText('Refresh Now')).toBeInTheDocument();
    });

    it('renders all four statistics cards', () => {
      mockUseDashboard.mockReturnValue({
        statistics: {
          total_tasks: 10,
          pending_tasks: 5,
          completed_tasks: 3,
          shared_tasks: 2,
        },
        loading: false,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      const { container } = render(<DashboardLayout />);

      // Check for grid layout
      const grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();

      // Check for all card labels
      expect(screen.getByText('Total Tasks')).toBeInTheDocument();
      expect(screen.getByText('Pending Tasks')).toBeInTheDocument();
      expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
      expect(screen.getByText('Shared Tasks')).toBeInTheDocument();
    });
  });

  describe('Dashboard Integration', () => {
    it('displays zero values when no data', () => {
      mockUseDashboard.mockReturnValue({
        statistics: {
          total_tasks: 0,
          pending_tasks: 0,
          completed_tasks: 0,
          shared_tasks: 0,
        },
        loading: false,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      render(<DashboardLayout />);

      // All values should be 0
      const zeros = screen.getAllByText('0');
      expect(zeros.length).toBe(4);
    });

    it('handles large numbers correctly', () => {
      mockUseDashboard.mockReturnValue({
        statistics: {
          total_tasks: 9999,
          pending_tasks: 5000,
          completed_tasks: 4999,
          shared_tasks: 1234,
        },
        loading: false,
        error: null,
        mutate: jest.fn(),
        retry: jest.fn(),
      });

      render(<DashboardLayout />);

      expect(screen.getByText('9999')).toBeInTheDocument();
      expect(screen.getByText('5000')).toBeInTheDocument();
      expect(screen.getByText('4999')).toBeInTheDocument();
      expect(screen.getByText('1234')).toBeInTheDocument();
    });
  });
});
