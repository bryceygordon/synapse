# Synapse Shell Function
# Add this to your ~/.zshrc to use Synapse from anywhere without activating venv manually

# Function to run synapse commands
synapse() {
    # Store current directory
    local current_dir="$(pwd)"

    # Activate the synapse virtual environment
    source /home/bryceg/synapse/.venv/bin/activate

    # Change to synapse directory (needed for loading agents/knowledge files)
    cd /home/bryceg/synapse

    # Run the synapse command with all arguments
    python -m core.main "$@"

    # Store exit code
    local exit_code=$?

    # Return to original directory
    cd "$current_dir"

    # Deactivate venv
    deactivate

    # Return original exit code
    return $exit_code
}

# Optional: Add autocomplete for synapse command
# This provides tab completion for chat/run commands and agent names
_synapse_completion() {
    local -a commands agents
    commands=('chat:Start interactive chat' 'run:Execute autonomous goal')
    agents=('coder:Coding assistant' 'todoist:GTD task manager')

    _arguments -C \
        '1: :->command' \
        '*:: :->args'

    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            case ${words[1]} in
                chat|run)
                    _describe 'agent' agents
                    ;;
            esac
            ;;
    esac
}

compdef _synapse_completion synapse
