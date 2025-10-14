#!/bin/bash

# This script gathers all relevant project files into a single handover.txt file.

OUTPUT_FILE="handover.txt"

# The complete and corrected list of all files to include.
FILES_TO_INCLUDE=(
    "pyproject.toml"
    "config.yaml"
    "agents/coder.yaml"
    "README.md"
    "PROJECT_VISION.md"
    "ARCHITECTURAL_BLUEPRINT.md"
    "ROADMAP.md"
    "core/main.py"
    "core/agent_loader.py"
    "core/schema_generator.py"
    "core/logger.py"
    "core/secure_executor.py"
    "core/agents/base.py"
    "core/agents/coder.py"
    "scripts/manage_vector_stores.py"
    "tests/test_agent_classes.py"
    "tests/test_agent_loader.py"
    "tests/test_coder_agent_methods.py"
    "tests/test_config.py"
    "tests/test_knowledge_integration.py"
    "tests/test_schema_generator.py"
    "tests/test_tool_loop.py"
)

# Start with a clean file
> "$OUTPUT_FILE"

# Loop through the files and append their content with a header
for file in "${FILES_TO_INCLUDE[@]}"; do
    if [ -f "$file" ]; then
        echo "--- FILE: $file ---" >> "$OUTPUT_FILE"
        cat "$file" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    else
        echo "--- WARNING: File not found: $file ---" >> "$OUTPUT_FILE"
    fi
done

echo "✅ Handover file created at $OUTPUT_FILE"
