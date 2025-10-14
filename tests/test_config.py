import os
import yaml
from dotenv import load_dotenv

def test_load_env_file():
    """Tests if the .env file loads and contains the API key."""
    assert os.path.exists(".env"), ".env file not found"
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY not found in .env"
    assert "your-openai-api-key" not in api_key, "Please replace the placeholder API key"

def test_load_config_yaml():
    """Tests if the main config.yaml can be loaded and parsed."""
    assert os.path.exists("config.yaml"), "config.yaml not found"
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert "agent_config_path" in config, "'agent_config_path' key is missing"
    assert config["agent_config_path"] == "agents/"

def test_load_coder_agent_yaml():
    """Tests if the CoderAgent's config can be loaded and parsed."""
    agent_path = "agents/coder.yaml"
    assert os.path.exists(agent_path), "agents/coder.yaml not found"
    with open(agent_path, "r") as f:
        config = yaml.safe_load(f)
    assert config["class_name"] == "CoderAgent"
    assert config["model"] == "gpt-5"
    assert "system_prompt" in config
    assert isinstance(config["tools"], list)
