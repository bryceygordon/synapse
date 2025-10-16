#!/usr/bin/env python3
"""
Test enum constraint schema generation without needing API token
"""
import json
from typing import Literal
from core.schema_generator import generate_tool_schemas

# Create a mock agent class with Literal-typed methods
class MockAgent:
    tools = ["constrained_method", "flexible_method"]

    def constrained_method(
        self,
        location: Literal["home", "house", "yard"],
        energy: Literal["low", "medium", "high"]
    ) -> str:
        """
        Test method with enum constraints.

        Args:
            location: WHERE the task happens
            energy: Energy level required
        """
        return f"{location} - {energy}"

    def flexible_method(self, any_string: str, any_number: int) -> str:
        """
        Test method without constraints.

        Args:
            any_string: Any string value
            any_number: Any number value
        """
        return f"{any_string} - {any_number}"

print("=" * 80)
print("ENUM CONSTRAINT SCHEMA GENERATION TEST")
print("=" * 80)

# Generate schemas
mock_agent = MockAgent()
schemas = generate_tool_schemas(mock_agent)

print(f"\n✓ Generated {len(schemas)} tool schemas\n")

for schema in schemas:
    print("-" * 80)
    print(f"Tool: {schema['name']}")
    print(f"Description: {schema['description']}")

    params = schema.get('parameters', {}).get('properties', {})
    required = schema.get('parameters', {}).get('required', [])

    print(f"\nParameters:")
    for param_name, param_def in params.items():
        req_str = " (required)" if param_name in required else ""
        print(f"  - {param_name}{req_str}:")
        print(f"      type: {param_def.get('type')}")

        if 'enum' in param_def:
            print(f"      enum: {param_def.get('enum')}")
            print(f"      ✅ ENUM CONSTRAINT DETECTED!")
        else:
            print(f"      (no enum constraint)")

        print(f"      description: {param_def.get('description')}")

print("\n" + "=" * 80)
print("ENUM SCHEMA TEST RESULT:")
print("=" * 80)

# Verify enum constraints exist
constrained_schema = next((s for s in schemas if s['name'] == 'constrained_method'), None)
if constrained_schema:
    params = constrained_schema.get('parameters', {}).get('properties', {})
    location_has_enum = 'enum' in params.get('location', {})
    energy_has_enum = 'enum' in params.get('energy', {})

    print(f"✓ constrained_method found")
    print(f"  - location parameter has enum: {location_has_enum}")
    print(f"  - energy parameter has enum: {energy_has_enum}")

    if location_has_enum and energy_has_enum:
        print("\n🎉 SUCCESS: Enum constraints are working!")
        print(f"   location options: {params['location']['enum']}")
        print(f"   energy options: {params['energy']['enum']}")
    else:
        print("\n❌ FAILED: Enum constraints not generated")
else:
    print("❌ constrained_method schema not found")

print("\n" + "=" * 80)
