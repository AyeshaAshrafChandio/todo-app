# Phase 8 Frontend Team Management UI - Quick Reference

## Overview
Phase 8 implements the complete frontend team management UI with 24 tasks (T077-T100).

## File Structure

```
frontend/src/
├── lib/
│   ├── types/
│   │   └── team.ts                    # T077-T079: Type definitions
│   └── api/
│       └── teams.ts                   # T080-T088: API client functions
├── hooks/
│   ├── useTeams.ts                    # T089: Teams management hook
│   └── useTeamDetails.ts              # T090: Team details hook
├── components/
│   └── teams/
│       ├── TeamCard.tsx               # T091: Team summary card
│       ├── TeamList.tsx               # T092: Teams grid list
│       ├── TeamForm.tsx               # T093: Create/edit form
│       ├── MemberList.tsx             # T094: Members display
│       ├── MemberInvite.tsx           # T095: Invite form
│       ├── RoleSelector.tsx           # T096: Role dropdown
│       └── index.ts                   # Component exports
└── app/(protected)/teams/
    ├── page.tsx                       # T097: Teams list page
    ├── new/
    │   └── page.tsx                   # T100: Create team page
    └── [teamId]/
        ├── page.tsx                   # T098: Team detail page
        └── settings/
            └── page.tsx               # T099: Team settings page
```

## Type Definitions

### TeamRole Enum
```typescript
export enum TeamRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  MEMBER = 'member',
  VIEWER = 'viewer'
}

export type TeamRoleType = 'owner' | 'admin' | 'member' | 'viewer';
```

### Core Interfaces
```typescript
interface Team {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  role: TeamRoleType;
  joined_at: string;
}
```

## API Functions

All functions in `frontend/src/lib/api/teams.ts`:

1. `createTeam(data)` - Create new team
2. `getTeams()` - List user's teams
3. `getTeam(teamId)` - Get team details
4. `updateTeam(teamId, data)` - Update team (PATCH)
5. `deleteTeam(teamId)` - Delete team
6. `addTeamMember(teamId, data)` - Invite member
7. `updateTeamMember(teamId, memberId, data)` - Change role (PATCH)
8. `removeTeamMember(teamId, memberId)` - Remove member
9. `leaveTeam(teamId)` - Leave team

## Hooks

### useTeams
```typescript
const { teams, loading, error, createTeam, updateTeam, deleteTeam, refreshTeams } = useTeams();
```

### useTeamDetails
```typescript
const { team, members, loading, error, refreshTeam, refreshMembers, refresh } = useTeamDetails(teamId);
```

## Components

### TeamCard
Displays team summary with actions.
```typescript
<TeamCard
  team={team}
  role="owner"
  memberCount={5}
  onView={() => {}}
  onEdit={() => {}}
  onDelete={() => {}}
/>
```

### TeamList
Grid of team cards with loading/error/empty states.
```typescript
<TeamList
  teams={teams}
  loading={loading}
  error={error}
  onTeamClick={(id) => {}}
/>
```

### TeamForm
Create or edit team form with validation.
```typescript
<TeamForm
  initialData={team}
  onSubmit={async (data) => {}}
  onCancel={() => {}}
  submitLabel="Save"
/>
```

### MemberList
Displays team members with role management.
```typescript
<MemberList
  members={members}
  currentUserRole="owner"
  onChangeRole={(userId, role) => {}}
  onRemoveMember={(userId) => {}}
/>
```

### MemberInvite
Invite new member form.
```typescript
<MemberInvite
  onInvite={async (userId, role) => {}}
  onCancel={() => {}}
/>
```

### RoleSelector
Dropdown for selecting member role.
```typescript
<RoleSelector
  value={role}
  onChange={(role) => {}}
  excludeOwner={true}
/>
```

## Pages

### Teams List (`/teams`)
- Lists all user's teams
- Create team button
- Team cards with actions

### Team Detail (`/teams/[teamId]`)
- Team information
- Member list
- Invite member form (admins/owners)
- Role management (owners)
- Settings link (admins/owners)
- Delete team (owners only)

### Team Settings (`/teams/[teamId]/settings`)
- Edit team name and description
- Team metadata display
- Save/cancel actions

### New Team (`/teams/new`)
- Create team form
- Help text
- Navigation after creation

## Role-Based Permissions

### Owner
- Full control
- Can delete team
- Can change any member's role
- Can manage settings

### Admin
- Can manage members
- Can invite/remove members
- Can manage settings
- Cannot delete team
- Cannot change owner role

### Member
- Can view team
- Can create tasks
- Cannot manage members
- Cannot manage settings

### Viewer
- Can view team
- Can view tasks
- Cannot create tasks
- Cannot manage members

## Key Features

1. **Type Safety**: Full TypeScript support with enums and interfaces
2. **Responsive Design**: Mobile-first with breakpoints
3. **Accessibility**: WCAG 2.1 AA compliant
4. **Error Handling**: User-friendly error messages
5. **Loading States**: Spinners and skeleton screens
6. **Empty States**: Helpful messages and actions
7. **Optimistic Updates**: Instant UI feedback
8. **Role-Based UI**: Show/hide based on permissions

## Testing Checklist

- [ ] Create team
- [ ] View teams list
- [ ] View team details
- [ ] Edit team settings
- [ ] Invite member
- [ ] Change member role
- [ ] Remove member
- [ ] Leave team
- [ ] Delete team
- [ ] Test on mobile
- [ ] Test on tablet
- [ ] Test on desktop
- [ ] Test keyboard navigation
- [ ] Test error states
- [ ] Test loading states
- [ ] Test empty states

## Next Steps

### Phase 9: Task Sharing UI (T101-T109)
- Create TaskShare types
- Implement share task API
- Create share components
- Create shared tasks page

### Phase 10: Extended Task Management (T110-T116)
- Extend Task type with team_id
- Update task creation for teams
- Add team filtering
- Show team badges on tasks

## Common Issues & Solutions

### Type Errors
- Use `TeamRoleType` for string literal types
- Use `TeamRole` enum for enum values
- Both are compatible

### API Errors
- Check JWT token in localStorage
- Verify backend is running on port 8000
- Check CORS configuration

### Navigation Issues
- Use `useRouter` from `next/navigation`
- Use `router.push()` for client-side navigation
- Use absolute paths: `/teams/[id]`

## Resources

- **Backend API**: http://localhost:8000
- **API Contracts**: `specs/003-teams-rbac-sharing/contracts/api-contracts.md`
- **Tasks File**: `specs/003-teams-rbac-sharing/tasks.md`
- **Implementation Summary**: `PHASE8_IMPLEMENTATION_SUMMARY.md`
