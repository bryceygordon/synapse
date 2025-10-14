import os, yaml
from dotenv import load_dotenv

def test_load_env_file():
    load_dotenv()
    assert os.getenv("OPENAI_API_KEY")

def test_load_config_yaml():
    with open("config.yaml", "r") as f: config = yaml.safe_load(f)
    assert config["agent_config_path"] == "agents/"

def test_load_coder_agent_yaml():
    with open("agents/coder.yaml", "r") as f: config = yaml.safe_load(f)
    assert config["name"] == "CoderAgent"
    assert config["class_name"] == "CoderAgent"
    assert config["model"] == "gpt-4o", "The agent's model should be gpt-4o"
