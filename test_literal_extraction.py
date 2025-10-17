#!/usr/bin/env python3
"""Test that Literal types are being extracted to enums in schemas."""

from core.providers.openai_provider import OpenAIProvider
from core.agents.todoist import TodoistAgent
from dotenv import load_dotenv
import json

load_dotenv()

config = {
    'name': 'TodoistAgent',
    'provider': 'openai',
    'model': 'gpt-4o',
    'system_prompt': 'test',
    'tools': ['make_actionable']
}

provider = OpenAIProvider()
agent = TodoistAgent(config)

# Generate schemas
tools_for_api = provider.format_tool_schemas(agent)

# Find make_actionable schema
make_actionable_schema = None
for tool in tools_for_api:
    if tool['function']['name'] == 'make_actionable':
        make_actionable_schema = tool['function']
        break

if not make_actionable_schema:
    print("❌ FAILED: make_actionable not found in schemas")
    exit(1)

# Check location parameter
location_param = make_actionable_schema['parameters']['properties'].get('location')
if not location_param:
    print("❌ FAILED: location parameter not found")
    exit(1)

if 'enum' not in location_param:
    print("❌ FAILED: location parameter missing 'enum' field")
    print(f"   Current schema: {json.dumps(location_param, indent=2)}")
    exit(1)

expected_enum = ["home", "house", "yard", "errand", "bunnings", "parents"]
actual_enum = location_param['enum']

if actual_enum != expected_enum:
    print("❌ FAILED: enum values don't match")
    print(f"   Expected: {expected_enum}")
    print(f"   Actual: {actual_enum}")
    exit(1)

# Check activity parameter
activity_param = make_actionable_schema['parameters']['properties'].get('activity')
if 'enum' not in activity_param:
    print("❌ FAILED: activity parameter missing 'enum' field")
    exit(1)

expected_activity = ["chore", "maintenance", "call", "email", "computer"]
if activity_param['enum'] != expected_activity:
    print("❌ FAILED: activity enum values don't match")
    exit(1)

print("✅ SUCCESS: Literal types correctly extracted to enums!")
print(f"   location enum: {actual_enum}")
print(f"   activity enum: {activity_param['enum']}")
print(f"\nEstimated token savings: ~200-300 tokens per API call")
