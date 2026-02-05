'use client';

import { useState, FormEvent } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import type { CreateTeamRequest, UpdateTeamRequest } from '@/lib/types/team';
import { sanitizeInput } from '@/lib/utils/sanitize';

interface TeamFormProps {
  initialData?: UpdateTeamRequest;
  onSubmit: (data: CreateTeamRequest | UpdateTeamRequest) => Promise<void>;
  onCancel?: () => void;
  submitLabel?: string;
  isLoading?: boolean;
}

/**
 * TeamForm component - create or edit team form
 * Handles validation and submission
 */
export function TeamForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Create Team',
  isLoading = false,
}: TeamFormProps) {
  const [formData, setFormData] = useState<CreateTeamRequest>({
    name: initialData?.name || '',
    description: initialData?.description || '',
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!formData.name.trim()) {
      setError('Team name is required');
      return;
    }

    if (formData.name.length < 3) {
      setError('Team name must be at least 3 characters');
      return;
    }

    if (formData.name.length > 100) {
      setError('Team name must be less than 100 characters');
      return;
    }

    try {
      // Sanitize user input before submission
      const sanitizedData: CreateTeamRequest = {
        name: sanitizeInput(formData.name.trim()),
        description: formData.description?.trim()
          ? sanitizeInput(formData.description.trim())
          : undefined,
      };

      await onSubmit(sanitizedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save team');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <Alert variant="error">
          {error}
        </Alert>
      )}

      <Input
        label="Team Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Enter team name"
        required
        disabled={isLoading}
        maxLength={100}
      />

      <div>
        <label
          htmlFor="description"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Description (optional)
        </label>
        <textarea
          id="description"
          value={formData.description || ''}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Team description"
          rows={3}
          disabled={isLoading}
          maxLength={500}
          className="block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        {formData.description && (
          <p className="mt-1 text-xs text-gray-500">
            {formData.description.length}/500 characters
          </p>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-4">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
        )}
        <Button type="submit" variant="primary" isLoading={isLoading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
}
