# Agent Configuration Examples

This directory contains example agent configurations for different providers.

## Switching to Anthropic/Claude

1. **Edit the main config** `agents/todoist.yaml`:
   ```yaml
   provider: anthropic
   model: claude-sonnet-4-20250514
   ```

2. **Set your API key** in `.env`:
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Run the agent:**
   ```bash
   synapse-todoist
   ```

## Switching to OpenAI (Current Default)

1. **Edit the main config** `agents/todoist.yaml`:
   ```yaml
   provider: openai
   model: gpt-4o
   ```

2. **Set your API key** in `.env`:
   ```bash
   OPENAI_API_KEY=your_key_here
   ```

## Notes

- Both providers use the same system prompt and tools
- Knowledge files in `knowledge/todoistagent/` work with both
- Token usage and caching may differ between providers
- The agent is provider-agnostic - switching is just 2 lines of YAML
