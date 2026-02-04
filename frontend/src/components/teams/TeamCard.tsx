'use client';

import { Team, TeamRoleType } from '@/lib/types/team';
import { Card, CardBody } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

interface TeamCardProps {
  team: Team;
  role?: TeamRoleType;
  memberCount?: number;
  onView?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

/**
 * TeamCard component - displays team summary with actions
 * Used in team lists and dashboards
 */
export function TeamCard({
  team,
  role,
  memberCount,
  onView,
  onEdit,
  onDelete
}: TeamCardProps) {
  return (
    <Card variant="elevated" className="hover:shadow-lg transition-shadow">
      <CardBody>
        <div className="space-y-4">
          {/* Team Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {team.name}
              </h3>
              {team.description && (
                <p className="text-sm text-gray-600 line-clamp-2">
                  {team.description}
                </p>
              )}
            </div>
            <div className="ml-3 h-10 w-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-xl">👥</span>
            </div>
          </div>

          {/* Team Metadata */}
          <div className="flex items-center gap-2 flex-wrap">
            {role && (
              <Badge variant={role === 'owner' ? 'success' : role === 'admin' ? 'info' : 'default'}>
                {role}
              </Badge>
            )}
            {memberCount !== undefined && (
              <Badge variant="default">
                {memberCount} {memberCount === 1 ? 'member' : 'members'}
              </Badge>
            )}
          </div>

          {/* Team Footer */}
          <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
            Created {new Date(team.created_at).toLocaleDateString()}
          </div>

          {/* Actions */}
          {(onView || onEdit || onDelete) && (
            <div className="flex gap-2 pt-2">
              {onView && (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={onView}
                >
                  View
                </Button>
              )}
              {onEdit && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={onEdit}
                >
                  Edit
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={onDelete}
                >
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </CardBody>
    </Card>
  );
}
