from app.models.task import Task
from pydantic import ValidationError
import traceback

print("Testing Task validation...")

# Test 1: Empty title
print("\n1. Testing empty title:")
try:
    t = Task(title='', user_id='test')
    print(f"  No error raised. Task created: {t}")
except ValidationError as e:
    print(f"  ValidationError raised: {e}")
except Exception as e:
    print(f"  Other error: {type(e).__name__}: {e}")

# Test 2: Valid title
print("\n2. Testing valid title:")
try:
    t = Task(title='Valid Task', user_id='test')
    print(f"  Task created successfully: {t}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")

# Test 3: Long title
print("\n3. Testing too long title:")
try:
    t = Task(title='x' * 201, user_id='test')
    print(f"  No error raised. Task created: {t}")
except ValidationError as e:
    print(f"  ValidationError raised: {e}")
except Exception as e:
    print(f"  Other error: {type(e).__name__}: {e}")
