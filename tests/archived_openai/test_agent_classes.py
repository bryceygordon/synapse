from core.agents.base import BaseAgent
from core.agents.coder import CoderAgent

def test_coder_agent_instantiation():
    mock_config = {
        "name": "TestAgent", # New test
        "class_name": "CoderAgent",
        "model": "gpt-5-test",
        "system_prompt": "Test prompt",
        "tools": ["tool_one", "tool_two"]
    }

    agent = CoderAgent(config=mock_config)

    assert isinstance(agent, CoderAgent)
    assert isinstance(agent, BaseAgent)
    assert agent.name == "TestAgent" # New test
    assert agent.model == "gpt-5-test"
    assert agent.system_prompt == "Test prompt"
    assert agent.tools == ["tool_one", "tool_two"]
