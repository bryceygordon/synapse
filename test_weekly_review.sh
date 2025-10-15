#!/bin/bash
# Interactive test script for Todoist Agent weekly review workflow

echo "=========================================="
echo "  Todoist Agent - Weekly Review Test"
echo "=========================================="
echo ""
echo "This will start an interactive session with the TodoistAgent."
echo "You can test the following:"
echo ""
echo "1. Pattern learning: Say '5 d' to complete task 5"
echo "   - Teach: 'From now on, when I say {number} d, complete that task'"
echo "   - Agent should propose saving this pattern"
echo ""
echo "2. Weekly review workflow:"
echo "   - Say: 'Let's do a weekly review'"
echo "   - Agent should:"
echo "     * Call query_knowledge('learned_rules')"
echo "     * Present inbox tasks in batches of 5 or less"
echo "     * Intuit contexts, energy, duration, next actions"
echo "     * No preamble or unnecessary summaries"
echo ""
echo "3. Knowledge queries:"
echo "   - Agent can query any topic: context_labels, processing_rules, etc."
echo ""
echo "Press Ctrl+C to exit when done."
echo ""
read -p "Press Enter to start the agent..."
echo ""

# Activate venv and run
source .venv/bin/activate
python -m core.main todoist_openai
