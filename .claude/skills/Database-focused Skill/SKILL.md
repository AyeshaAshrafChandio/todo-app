---
name: database-core
description: Design and manage databases including schema design, table creation, and migrations. Use for backend and data-driven applications.
---

# Database Core Skill

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Normalize data (avoid redundancy)
   - Choose appropriate data types
   - Define primary and foreign keys

2. **Table Creation**
   - Write clean and readable SQL
   - Use constraints (NOT NULL, UNIQUE, CHECK)
   - Apply indexes for performance
   - Follow consistent naming conventions

3. **Migrations**
   - Version-control database changes
   - Create up and down migration scripts
   - Avoid destructive changes without backups
   - Test migrations on staging before production

4. **Relationships**
   - One-to-One
   - One-to-Many
   - Many-to-Many (junction tables)

## Best Practices
- Use snake_case for table and column names
- Always define primary keys
- Add indexes on frequently queried columns
- Keep migrations small and incremental
- Never edit old migrations; create new ones
- Document schema decisions

## Example Structure

### SQL Schema
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
