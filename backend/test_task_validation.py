#!/usr/bin/env python3
"""Test script to verify Task validation behavior."""

from app.models.task import Task
from pydantic import ValidationError

print("=" * 60)
print("Testing Task Model Validation")
print("=" * 60)

# Test 1: Empty title
print("\n1. Testing empty title:")
try:
    task = Task(title='', user_id='test')
    print(f"   FAIL: No error raised. Task created with title: '{task.title}'")
except ValidationError as e:
    print(f"   PASS: ValidationError raised")
except Exception as e:
    print(f"   PASS: Error raised: {type(e).__name__}: {e}")

# Test 2: Whitespace-only title
print("\n2. Testing whitespace-only title:")
try:
    task = Task(title='   ', user_id='test')
    print(f"   FAIL: No error raised. Task created with title: '{task.title}'")
except ValidationError as e:
    print(f"   PASS: ValidationError raised")
except Exception as e:
    print(f"   PASS: Error raised: {type(e).__name__}: {e}")

# Test 3: Valid title
print("\n3. Testing valid title:")
try:
    task = Task(title='Valid Task', user_id='test')
    print(f"   PASS: Task created successfully with title: '{task.title}'")
except Exception as e:
    print(f"   FAIL: Error: {type(e).__name__}: {e}")

# Test 4: Too long title (201 chars)
print("\n4. Testing too long title (201 chars):")
try:
    task = Task(title='x' * 201, user_id='test')
    print(f"   FAIL: No error raised. Task created with {len(task.title)} char title")
except ValidationError as e:
    print(f"   PASS: ValidationError raised")
except Exception as e:
    print(f"   PASS: Error raised: {type(e).__name__}: {e}")

# Test 5: Too long description (1001 chars)
print("\n5. Testing too long description (1001 chars):")
try:
    task = Task(title='Valid', description='x' * 1001, user_id='test')
    print(f"   FAIL: No error raised. Task created with {len(task.description)} char description")
except ValidationError as e:
    print(f"   PASS: ValidationError raised")
except Exception as e:
    print(f"   PASS: Error raised: {type(e).__name__}: {e}")

# Test 6: Too long user_id (37 chars)
print("\n6. Testing too long user_id (37 chars):")
try:
    task = Task(title='Valid', user_id='x' * 37)
    print(f"   FAIL: No error raised. Task created with {len(task.user_id)} char user_id")
except ValidationError as e:
    print(f"   PASS: ValidationError raised")
except Exception as e:
    print(f"   PASS: Error raised: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
