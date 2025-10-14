import pytest
from core.agent_loader import load_agent
from core.agents.coder import CoderAgent

def test_load_agent_success():
    """Tests that the loader can successfully find and instantiate the CoderAgent."""
    agent = load_agent(agent_name="coder")

    assert isinstance(agent, CoderAgent), "The loaded agent should be an instance of CoderAgent"
    assert agent.model == "gpt-5", "The agent's model was not loaded correctly from YAML"
    assert "expert-level software development" in agent.system_prompt

def test_load_agent_file_not_found():
    """Tests that the loader raises FileNotFoundError for a non-existent agent."""
    with pytest.raises(FileNotFoundError):
        load_agent(agent_name="non_existent_agent")

def test_load_agent_class_not_found(tmp_path):
    """Tests that the loader raises AttributeError for a non-existent class."""
    # Create a temporary bad config file
    bad_config_content = """
    class_name: ThisClassDoesNotExist
    model: gpt-4
    """
    p = tmp_path / "bad_agent.yaml"
    p.write_text(bad_config_content)

    # We must load using the temporary path
    with pytest.raises(AttributeError):
        load_agent(agent_name="bad_agent", config_path=tmp_path)

