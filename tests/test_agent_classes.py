from core.agents.base import BaseAgent
from core.agents.coder import CoderAgent

def test_coder_agent_instantiation():
    """
    Tests if a CoderAgent can be instantiated and correctly
    assigns attributes from a config dictionary.
    """
    mock_config = {
        "class_name": "CoderAgent",
        "model": "gpt-5-test",
        "system_prompt": "Test prompt",
        "tools": ["tool_one", "tool_two"]
    }

    agent = CoderAgent(config=mock_config)

    # Verify it's an instance of both CoderAgent and the parent BaseAgent
    assert isinstance(agent, CoderAgent)
    assert isinstance(agent, BaseAgent)

    # Verify attributes were set correctly
    assert agent.model == "gpt-5-test"
    assert agent.system_prompt == "Test prompt"
    assert agent.tools == ["tool_one", "tool_two"]

