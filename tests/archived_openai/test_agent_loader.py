import pytest
from core.agent_loader import load_agent
from core.agents.coder import CoderAgent

def test_load_agent_success():
    """Tests that the loader can successfully find and instantiate the CoderAgent."""
    agent = load_agent(agent_name="coder")
    assert isinstance(agent, CoderAgent)
    assert agent.model == "gpt-4o", "The agent's model should be gpt-4o"

def test_load_agent_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_agent(agent_name="non_existent_agent")

def test_load_agent_class_not_found(tmp_path):
    p = tmp_path / "bad.yaml"; p.write_text("class_name: BadClass")
    with pytest.raises(AttributeError):
        load_agent(agent_name="bad", config_path=tmp_path)
