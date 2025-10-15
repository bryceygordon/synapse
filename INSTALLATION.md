# Synapse Installation Guide

## Global CLI Access (Recommended)

To use Synapse from anywhere on your system without manually activating the virtual environment:

### 1. Add the shell function to your `.zshrc`

```bash
# Append the shell function to your .zshrc
cat /home/bryceg/synapse/synapse_shell_function.sh >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc
```

### 2. Usage

Now you can use `synapse` from any directory:

```bash
# From anywhere on your system:
synapse chat todoist          # Chat with TodoistAgent
synapse chat coder            # Chat with CoderAgent
synapse run "your goal" coder # Autonomous mode

# No need to cd into synapse directory or activate venv!
```

---

## Alternative: Manual Installation (Not Recommended)

If you prefer to install synapse globally via pip (not recommended because it's harder to maintain):

```bash
cd /home/bryceg/synapse
source .venv/bin/activate
pip install -e .
```

Then you can use:
```bash
source /home/bryceg/synapse/.venv/bin/activate
synapse chat todoist
deactivate
```

---

## How It Works

The shell function:
1. Activates the synapse virtual environment
2. Changes to the synapse directory (needed to find agents/knowledge files)
3. Runs your command
4. Returns you to your original directory
5. Deactivates the virtual environment

All of this happens transparently - you just type `synapse` and it works!

---

## Testing the Installation

```bash
# Test help
synapse --help

# Test listing inbox (should work from any directory)
cd ~
synapse chat todoist
> Can you list my inbox?
```

---

## Updating Synapse

When you pull new changes from git:

```bash
cd /home/bryceg/synapse
git pull
source .venv/bin/activate
pip install -e .  # Reinstall if dependencies changed
```

The shell function automatically uses the latest code since it's installed in editable mode.
