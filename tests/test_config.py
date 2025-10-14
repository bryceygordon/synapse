import os
import yaml
from dotenv import load_dotenv

def test_load_env_file():
    assert os.path.exists(".env"), ".env file not found"
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None, "OPENAI_API_KEY not found in .env"
    assert "your-openai-api-key" not in api_key, "Please replace the placeholder API key"

def test_load_config_yaml():
    assert os.path.exists("config.yaml"), "config.yaml not found"
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    assert "agent_config_path" in config
    assert config["agent_config_path"] == "agents/"

def test_load_coder_agent_yaml():
    agent_path = "agents/coder.yaml"
    assert os.path.exists(agent_path), "agents/coder.yaml not found"
    with open(agent_path, "r") as f:
        config = yaml.safe_load(f)
    assert config["name"] == "CoderAgent" # New test
    assert config["class_name"] == "CoderAgent"
    assert config["model"] == "gpt-5"
    assert "system_prompt" in config
    assert isinstance(config["tools"], list)
