'use client';

import { TeamMember, TeamRoleType } from '@/lib/types/team';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardBody } from '@/components/ui/Card';
import { EmptyState } from '@/components/shared/EmptyState';

interface MemberListProps {
  members: TeamMember[];
  currentUserId?: string;
  currentUserRole?: TeamRoleType;
  onChangeRole?: (userId: string, newRole: TeamRoleType) => void;
  onRemoveMember?: (userId: string) => void;
  loading?: boolean;
}

/**
 * MemberList component - displays team members with roles
 * Shows role badges and action buttons based on permissions
 */
export function MemberList({
  members,
  currentUserId,
  currentUserRole,
  onChangeRole,
  onRemoveMember,
  loading = false,
}: MemberListProps) {
  if (loading) {
    return (
      <Card>
        <CardBody>
          <div className="text-center py-8 text-gray-500">Loading members...</div>
        </CardBody>
      </Card>
    );
  }

  if (members.length === 0) {
    return (
      <EmptyState
        title="No members yet"
        description="Invite team members to start collaborating"
      />
    );
  }

  // Check if current user can manage members (owner or admin)
  const canManageMembers = currentUserRole === 'owner' || currentUserRole === 'admin';

  const getRoleBadgeVariant = (role: TeamRoleType) => {
    switch (role) {
      case 'owner':
        return 'success';
      case 'admin':
        return 'info';
      case 'member':
        return 'default';
      case 'viewer':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-3">
      {members.map((member) => {
        const isCurrentUser = member.user_id === currentUserId;
        const isOwner = member.role === 'owner';
        const canRemove = canManageMembers && !isOwner && !isCurrentUser;
        const canChangeRole = currentUserRole === 'owner' && !isCurrentUser;

        return (
          <Card key={member.user_id} variant="bordered">
            <CardBody className="py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {/* Avatar */}
                  <div className="h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-gray-600 font-medium">
                      {member.user_id.substring(0, 2).toUpperCase()}
                    </span>
                  </div>

                  {/* Member Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">
                        User {member.user_id.substring(0, 8)}
                      </span>
                      {isCurrentUser && (
                        <Badge variant="info">You</Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">
                      Joined {new Date(member.joined_at).toLocaleDateString()}
                    </p>
                  </div>

                  {/* Role Badge */}
                  <Badge variant={getRoleBadgeVariant(member.role)}>
                    {member.role}
                  </Badge>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 ml-4">
                  {canChangeRole && onChangeRole && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        // Cycle through roles (excluding owner)
                        const roles: TeamRoleType[] = ['admin', 'member', 'viewer'];
                        const currentIndex = roles.indexOf(member.role);
                        const nextRole = roles[(currentIndex + 1) % roles.length];
                        onChangeRole(member.user_id, nextRole);
                      }}
                    >
                      Change Role
                    </Button>
                  )}
                  {canRemove && onRemoveMember && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to remove this member?')) {
                          onRemoveMember(member.user_id);
                        }
                      }}
                    >
                      Remove
                    </Button>
                  )}
                </div>
              </div>
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
}
