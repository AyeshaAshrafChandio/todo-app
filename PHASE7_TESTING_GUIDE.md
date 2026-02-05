# Phase 7: Task Sharing API Testing Guide

**Feature**: Direct Task Sharing Between Users
**Date**: 2026-02-05
**Status**: Ready for Testing

## Prerequisites

1. **Database Migration**: Ensure Phase 2 migration has been run
   ```bash
   cd backend
   python run_migration.py
   ```

2. **Start FastAPI Server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

3. **API Documentation**: Available at http://localhost:8000/docs

4. **Test Users**: You'll need at least 2 users for testing
   - User A (Task Owner)
   - User B (Share Recipient)

## Environment Setup

Create test users and get JWT tokens:

```bash
# Register User A
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usera@example.com",
    "password": "password123"
  }'

# Register User B
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "userb@example.com",
    "password": "password123"
  }'

# Login as User A (save the token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usera@example.com",
    "password": "password123"
  }'
# Response: {"access_token": "TOKEN_A", "token_type": "bearer"}

# Login as User B (save the token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "userb@example.com",
    "password": "password123"
  }'
# Response: {"access_token": "TOKEN_B", "token_type": "bearer"}
```

## Test Scenarios

### Scenario 1: Share Task with View Permission

**Step 1**: User A creates a task
```bash
curl -X POST http://localhost:8000/api/USER_A_ID/tasks \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review documentation",
    "description": "Review API documentation for accuracy",
    "team_id": null
  }'
# Response: {"id": 1, "title": "Review documentation", ...}
# Save the task_id (e.g., 1)
```

**Step 2**: User A shares task with User B (view permission)
```bash
curl -X POST http://localhost:8000/api/tasks/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_B_ID",
    "permission": "view"
  }'
# Expected: 201 Created
# Response: {
#   "id": "share-uuid",
#   "task_id": 1,
#   "shared_with_user_id": "USER_B_ID",
#   "shared_by_user_id": "USER_A_ID",
#   "permission": "view",
#   "shared_at": "2026-02-05T..."
# }
```

**Step 3**: User B views shared tasks
```bash
curl -X GET http://localhost:8000/api/tasks/shared-with-me \
  -H "Authorization: Bearer TOKEN_B"
# Expected: 200 OK
# Response: [
#   {
#     "id": 1,
#     "title": "Review documentation",
#     "description": "Review API documentation for accuracy",
#     "completed": false,
#     "owner_email": "usera@example.com",
#     "permission": "view",
#     "shared_at": "2026-02-05T...",
#     "created_at": "2026-02-05T...",
#     "updated_at": "2026-02-05T..."
#   }
# ]
```

**Step 4**: User B attempts to edit task (should fail)
```bash
curl -X PUT http://localhost:8000/api/USER_B_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Modified title",
    "description": "Modified description",
    "completed": false
  }'
# Expected: 403 Forbidden
# Response: {"detail": "User does not have permission to edit task 1"}
```

**Step 5**: User A views task with sharing info
```bash
curl -X GET http://localhost:8000/api/USER_A_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN_A"
# Expected: 200 OK
# Response: {
#   "id": 1,
#   "title": "Review documentation",
#   ...,
#   "access_type": "owner",
#   "shared_with": [
#     {
#       "user_id": "USER_B_ID",
#       "email": "userb@example.com",
#       "permission": "view",
#       "shared_at": "2026-02-05T..."
#     }
#   ]
# }
```

### Scenario 2: Share Task with Edit Permission

**Step 1**: User A creates another task
```bash
curl -X POST http://localhost:8000/api/USER_A_ID/tasks \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Update API endpoints",
    "description": "Add new endpoints for task sharing",
    "team_id": null
  }'
# Response: {"id": 2, ...}
```

**Step 2**: User A shares task with User B (edit permission)
```bash
curl -X POST http://localhost:8000/api/tasks/2/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_B_ID",
    "permission": "edit"
  }'
# Expected: 201 Created
```

**Step 3**: User B edits the shared task (should succeed)
```bash
curl -X PUT http://localhost:8000/api/USER_B_ID/tasks/2 \
  -H "Authorization: Bearer TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Update API endpoints",
    "description": "Added task sharing endpoints - DONE",
    "completed": true
  }'
# Expected: 200 OK
# Response: {
#   "id": 2,
#   "title": "Update API endpoints",
#   "description": "Added task sharing endpoints - DONE",
#   "completed": true,
#   ...,
#   "access_type": "shared_edit"
# }
```

**Step 4**: User B attempts to delete task (should fail)
```bash
curl -X DELETE http://localhost:8000/api/USER_B_ID/tasks/2 \
  -H "Authorization: Bearer TOKEN_B"
# Expected: 403 Forbidden
# Response: {"detail": "User does not have permission to delete task 2"}
```

### Scenario 3: Self-Sharing Prevention

**Step 1**: User A attempts to share task with themselves
```bash
curl -X POST http://localhost:8000/api/tasks/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_A_ID",
    "permission": "edit"
  }'
# Expected: 400 Bad Request
# Response: {"detail": "Cannot share task with yourself"}
```

### Scenario 4: Duplicate Share Prevention

**Step 1**: User A attempts to share task 1 with User B again
```bash
curl -X POST http://localhost:8000/api/tasks/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_B_ID",
    "permission": "edit"
  }'
# Expected: 409 Conflict
# Response: {"detail": "Task 1 is already shared with user USER_B_ID"}
```

### Scenario 5: Revoke Share

**Step 1**: User A revokes User B's access to task 1
```bash
curl -X DELETE http://localhost:8000/api/tasks/1/share/USER_B_ID \
  -H "Authorization: Bearer TOKEN_A"
# Expected: 204 No Content
# Response: (empty body)
```

**Step 2**: User B verifies they no longer have access
```bash
curl -X GET http://localhost:8000/api/USER_B_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN_B"
# Expected: 403 Forbidden
# Response: {"detail": "User does not have access to task 1"}
```

**Step 3**: User B checks shared tasks list
```bash
curl -X GET http://localhost:8000/api/tasks/shared-with-me \
  -H "Authorization: Bearer TOKEN_B"
# Expected: 200 OK
# Response: [
#   {
#     "id": 2,
#     "title": "Update API endpoints",
#     ...
#   }
# ]
# Note: Task 1 is no longer in the list
```

### Scenario 6: Non-Owner Cannot Share

**Step 1**: User B attempts to share task 2 (which they have edit access to)
```bash
curl -X POST http://localhost:8000/api/tasks/2/share \
  -H "Authorization: Bearer TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_C_ID",
    "permission": "view"
  }'
# Expected: 403 Forbidden
# Response: {"detail": "Only the task owner can share this task"}
```

### Scenario 7: Invalid Permission Value

**Step 1**: User A attempts to share with invalid permission
```bash
curl -X POST http://localhost:8000/api/tasks/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_B_ID",
    "permission": "admin"
  }'
# Expected: 422 Unprocessable Entity
# Response: {
#   "detail": [
#     {
#       "loc": ["body", "permission"],
#       "msg": "Permission must be either 'view' or 'edit'",
#       "type": "value_error"
#     }
#   ]
# }
```

### Scenario 8: Share with Non-Existent User

**Step 1**: User A attempts to share with non-existent user
```bash
curl -X POST http://localhost:8000/api/tasks/1/share \
  -H "Authorization: Bearer TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000000",
    "permission": "view"
  }'
# Expected: 404 Not Found
# Response: {"detail": "User 00000000-0000-0000-0000-000000000000 not found"}
```

### Scenario 9: Privacy - Non-Owner Cannot See Sharing Info

**Step 1**: User B views task 2 (which they have edit access to)
```bash
curl -X GET http://localhost:8000/api/USER_B_ID/tasks/2 \
  -H "Authorization: Bearer TOKEN_B"
# Expected: 200 OK
# Response: {
#   "id": 2,
#   "title": "Update API endpoints",
#   ...,
#   "access_type": "shared_edit",
#   "shared_with": null  // User B cannot see who else has access
# }
```

## Postman Collection

Import this JSON into Postman for easier testing:

```json
{
  "info": {
    "name": "Task Sharing API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token_a",
      "value": "YOUR_TOKEN_A"
    },
    {
      "key": "token_b",
      "value": "YOUR_TOKEN_B"
    },
    {
      "key": "user_a_id",
      "value": "YOUR_USER_A_ID"
    },
    {
      "key": "user_b_id",
      "value": "YOUR_USER_B_ID"
    },
    {
      "key": "task_id",
      "value": "1"
    }
  ],
  "item": [
    {
      "name": "Share Task",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token_a}}"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"user_id\": \"{{user_b_id}}\",\n  \"permission\": \"edit\"\n}",
          "options": {
            "raw": {
              "language": "json"
            }
          }
        },
        "url": {
          "raw": "{{base_url}}/api/tasks/{{task_id}}/share",
          "host": ["{{base_url}}"],
          "path": ["api", "tasks", "{{task_id}}", "share"]
        }
      }
    },
    {
      "name": "Revoke Share",
      "request": {
        "method": "DELETE",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token_a}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/tasks/{{task_id}}/share/{{user_b_id}}",
          "host": ["{{base_url}}"],
          "path": ["api", "tasks", "{{task_id}}", "share", "{{user_b_id}}"]
        }
      }
    },
    {
      "name": "Get Shared Tasks",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token_b}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/tasks/shared-with-me",
          "host": ["{{base_url}}"],
          "path": ["api", "tasks", "shared-with-me"]
        }
      }
    }
  ]
}
```

## Expected Results Summary

| Test Case | Expected Status | Expected Behavior |
|-----------|----------------|-------------------|
| Share with view permission | 201 Created | Share record created, user can view |
| Share with edit permission | 201 Created | Share record created, user can edit |
| View shared tasks | 200 OK | Returns list with owner emails |
| Edit with view permission | 403 Forbidden | Edit denied |
| Edit with edit permission | 200 OK | Edit succeeds |
| Delete with edit permission | 403 Forbidden | Delete denied (owner only) |
| Self-sharing | 400 Bad Request | Prevented with error message |
| Duplicate share | 409 Conflict | Prevented with error message |
| Revoke share | 204 No Content | Share removed, access revoked |
| Non-owner share attempt | 403 Forbidden | Only owner can share |
| Invalid permission | 422 Unprocessable | Validation error |
| Non-existent user | 404 Not Found | User not found error |
| Owner sees sharing info | 200 OK | shared_with list populated |
| Non-owner privacy | 200 OK | shared_with is null |

## Troubleshooting

### Issue: 401 Unauthorized
**Cause**: JWT token expired or invalid
**Solution**: Re-login to get a fresh token

### Issue: 403 Forbidden
**Cause**: User doesn't have required permission
**Solution**: Verify user is task owner for sharing operations

### Issue: 404 Not Found
**Cause**: Task or user doesn't exist
**Solution**: Verify IDs are correct and resources exist

### Issue: 409 Conflict
**Cause**: Task already shared with user
**Solution**: Revoke existing share first, or update permission (not implemented)

### Issue: 422 Unprocessable Entity
**Cause**: Invalid request data
**Solution**: Check request body matches schema (permission must be "view" or "edit")

## Database Verification

Check shares in database:

```sql
-- View all task shares
SELECT
  ts.id,
  ts.task_id,
  t.title as task_title,
  u1.email as shared_with,
  u2.email as shared_by,
  ts.permission,
  ts.shared_at
FROM task_shares ts
JOIN tasks t ON ts.task_id = t.id
JOIN users u1 ON ts.shared_with_user_id = u1.id
JOIN users u2 ON ts.shared_by_user_id = u2.id
ORDER BY ts.shared_at DESC;

-- Count shares per task
SELECT
  t.id,
  t.title,
  COUNT(ts.id) as share_count
FROM tasks t
LEFT JOIN task_shares ts ON t.id = ts.task_id
GROUP BY t.id, t.title
ORDER BY share_count DESC;

-- View shares for specific user
SELECT
  t.id,
  t.title,
  u.email as owner,
  ts.permission,
  ts.shared_at
FROM task_shares ts
JOIN tasks t ON ts.task_id = t.id
JOIN users u ON t.user_id = u.id
WHERE ts.shared_with_user_id = 'USER_B_ID'
ORDER BY ts.shared_at DESC;
```

## Performance Testing

Test with multiple shares:

```bash
# Share task with 10 users
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/tasks/1/share \
    -H "Authorization: Bearer TOKEN_A" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"user${i}_id\", \"permission\": \"view\"}"
done

# Verify owner sees all shares
curl -X GET http://localhost:8000/api/USER_A_ID/tasks/1 \
  -H "Authorization: Bearer TOKEN_A"
# Should return shared_with array with 10 entries
```

## Next Steps

1. **Manual Testing**: Run through all test scenarios
2. **Integration Testing**: Test with team tasks and permissions
3. **Load Testing**: Test with many shares per task
4. **Frontend Integration**: Build UI for sharing features
5. **Notifications**: Add email notifications when tasks are shared (future enhancement)

## Success Criteria

- ✅ All API endpoints return correct status codes
- ✅ Permission levels enforced correctly (view vs edit)
- ✅ Self-sharing prevented
- ✅ Duplicate shares prevented
- ✅ Owner-only operations enforced
- ✅ Privacy maintained (non-owners don't see sharing info)
- ✅ Cascade deletes work (user deletion removes shares)
- ✅ Error messages are clear and helpful
- ✅ OpenAPI documentation is accurate
