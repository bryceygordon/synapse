# Archived OpenAI Tests

These tests were written for the original OpenAI Responses API implementation and are being preserved for future reference.

## Status: ARCHIVED

These tests are **not currently maintained** and will not run against the new multi-provider architecture.

## Purpose

When OpenAI provider support is reintegrated (Phase 6 of the refactoring roadmap), these tests will serve as reference for:
- Expected OpenAI-specific behavior
- Test patterns that worked
- Edge cases that were covered

## Files

- `test_agent_classes.py` - Agent class hierarchy tests
- `test_agent_loader.py` - Dynamic agent loading tests
- `test_coder_agent_methods.py` - CoderAgent method tests
- `test_config.py` - Configuration loading tests
- `test_hardening.py` - Error handling and retry tests
- `test_knowledge_integration.py` - OpenAI vector store integration tests
- `test_schema_generator.py` - Tool schema generation tests

## Migration Notes

When reintegrating OpenAI:
1. Review these tests for coverage patterns
2. Adapt tests for new provider abstraction layer
3. Ensure OpenAI provider passes equivalent tests to Anthropic provider
4. Move tests back to main test suite once adapted

## Date Archived

2025-10-15 - Multi-provider refactoring Phase 1
