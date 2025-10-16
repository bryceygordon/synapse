"""
Main CLI application for Synapse AI Orchestration Engine.

This module provides the command-line interface for interacting with
AI agents through multiple providers (Claude, OpenAI, Gemini, etc.).
"""

import json
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.agent_loader import load_agent
from core.providers import get_provider
from core.logger import setup_logging

# Global Rich console
console = Console()

app = typer.Typer(help="A modular, command-line-first AI orchestration engine.")


def render_assistant_message(text: str, title: str = "[bold green]Assistant[/bold green]") -> None:
    """
    Render assistant message with markdown support if detected.

    Automatically detects markdown patterns and renders them beautifully
    using Rich's Markdown renderer. Falls back to plain text if no markdown.

    Args:
        text: The assistant's message text
        title: Panel title (default: "[bold green]Assistant[/bold green]")
    """
    # Simple markdown detection heuristic
    has_markdown = any([
        '\n#' in text or text.startswith('#'),     # Headers
        '```' in text,                              # Code blocks
        '\n- ' in text or text.startswith('- '),   # Unordered lists
        '\n* ' in text or text.startswith('* '),   # Unordered lists
        '\n+ ' in text or text.startswith('+ '),   # Unordered lists
        '\n1. ' in text or text.startswith('1. '), # Numbered lists
        '**' in text,                               # Bold
        '__' in text,                               # Bold
        text.count('`') >= 2,                       # Inline code
        '\n> ' in text or text.startswith('> '),   # Blockquotes
        '---' in text or '___' in text,             # Horizontal rules
    ])

    if has_markdown:
        # Render as markdown with syntax highlighting
        console.print(Panel(
            Markdown(text),
            title=title,
            border_style="green",
            box=box.ROUNDED
        ))
    else:
        # Render as plain text (faster for simple responses)
        console.print(Panel(
            text,
            title=title,
            border_style="green",
            box=box.ROUNDED
        ))


def display_token_usage(session_tokens: dict, agent_name: str, model: str):
    """Display comprehensive token usage statistics."""
    if session_tokens["total"] == 0:
        return

    # Calculate averages
    avg_input = session_tokens["input"] / session_tokens["turns"] if session_tokens["turns"] > 0 else 0
    avg_output = session_tokens["output"] / session_tokens["turns"] if session_tokens["turns"] > 0 else 0
    avg_total = session_tokens["total"] / session_tokens["turns"] if session_tokens["turns"] > 0 else 0

    # Create usage table
    table = Table(
        title="📊 Token Usage Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )

    table.add_column("Metric", style="white", no_wrap=True)
    table.add_column("Session Total", style="yellow", justify="right")
    table.add_column("Per Turn (avg)", style="dim", justify="right")

    table.add_row("Input Tokens", f"{session_tokens['input']:,}", f"{avg_input:,.1f}")
    table.add_row("Output Tokens", f"{session_tokens['output']:,}", f"{avg_output:,.1f}")
    table.add_row("Total Tokens", f"[bold]{session_tokens['total']:,}[/bold]", f"[bold]{avg_total:,.1f}[/bold]")
    table.add_row("API Calls", f"{session_tokens['turns']}", "-")

    # Add cache statistics if any tokens were cached
    if session_tokens["cached"] > 0:
        cache_pct = (session_tokens["cached"] / session_tokens["input"] * 100) if session_tokens["input"] > 0 else 0
        table.add_row(
            "[green]Cached Tokens[/green]",
            f"[green]{session_tokens['cached']:,}[/green]",
            f"[green]{cache_pct:.1f}% cache hit[/green]"
        )

    console.print("\n")
    console.print(table)
    console.print(f"[dim]Agent: {agent_name} | Model: {model}[/dim]")

    # Show savings message if caching was used
    if session_tokens["cached"] > 0:
        console.print(f"[green]💰 Prompt caching saved ~{session_tokens['cached']} tokens from being charged at full price![/green]")


def display_tool_result(tool_name: str, result: str):
    """Display tool execution result with Rich formatting."""
    try:
        # Try to parse as JSON for better display
        data = json.loads(result)

        # If it's a Todoist response with tasks, create a table
        if data.get("status") == "success" and "tasks" in data.get("data", {}):
            tasks = data["data"]["tasks"]

            table = Table(
                title=f"📋 {tool_name} - {data.get('message', '')}",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )

            table.add_column("Content", style="white", no_wrap=False)
            table.add_column("Labels", style="yellow")
            table.add_column("Priority", style="magenta", justify="center")
            table.add_column("Due", style="green")
            table.add_column("Created", style="dim")

            for task in tasks[:10]:  # Show first 10 tasks
                labels = ", ".join(f"@{l}" for l in task.get("labels", []))
                priority = f"P{task.get('priority', 1)}" if task.get('priority', 1) > 1 else ""
                due = task.get("due") or ""
                created = task.get("created_at", "")[:10] if task.get("created_at") else ""  # Just the date

                table.add_row(
                    task.get("content", ""),
                    labels,
                    priority,
                    due,
                    created
                )

            if len(tasks) > 10:
                console.print(f"[dim]... and {len(tasks) - 10} more tasks[/dim]")

            console.print(table)
            return

        # For other JSON responses, use syntax highlighting
        syntax = Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            line_numbers=False
        )
        console.print(
            Panel(
                syntax,
                title=f"[bold cyan]🔧 {tool_name}[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED
            )
        )

    except json.JSONDecodeError:
        # Not JSON, display as plain text in a panel
        console.print(
            Panel(
                result[:500],  # Truncate long results
                title=f"[bold cyan]🔧 {tool_name}[/bold cyan]",
                border_style="cyan",
                box=box.ROUNDED
            )
        )


@app.command("chat", help="Starts an interactive chat session with the agent.")
@app.command("", hidden=True)
def chat(agent_name: str = "coder"):
    """
    Starts an interactive chat session with the configured Synapse agent.

    Args:
        agent_name: Name of the agent to load (default: coder)
    """
    console.print(Panel("[bold cyan]Synapse AI Chat[/bold cyan]", box=box.DOUBLE))
    setup_logging()
    load_dotenv()

    try:
        # Load agent configuration
        agent = load_agent(agent_name=agent_name)
        console.print(f"✅ [bold green]Agent '{agent.name}' loaded successfully[/bold green]")
        console.print(f"   [cyan]Provider:[/cyan] {agent.provider}")
        console.print(f"   [cyan]Model:[/cyan] {agent.model}")

        # Get the appropriate provider
        provider = get_provider(agent.provider)
        client = provider.create_client()

        # Generate tool schemas for this provider
        tools = provider.format_tool_schemas(agent)
        # Handle different schema formats (Anthropic vs OpenAI)
        tool_names = [
            t.get("name") or t.get("function", {}).get("name")
            for t in tools
        ]
        console.print(f"   [cyan]Tools:[/cyan] [dim]{', '.join(tool_names)}[/dim]\n")

    except Exception as e:
        console.print(f"[bold red]❌ Error loading agent:[/bold red] {e}")
        raise typer.Exit()

    console.print("[dim]Type your message below. Press Ctrl+C to exit.[/dim]\n")

    # Conversation state
    messages = []

    # Token usage tracking
    session_tokens = {
        "input": 0,
        "output": 0,
        "total": 0,
        "cached": 0,
        "turns": 0
    }

    # For TodoistAgent, trigger startup sequence automatically
    if agent_name.startswith("todoist"):
        console.print("🚀 [bold yellow]Initializing TodoistAgent...[/bold yellow]\n")

        # Send initial startup message (Just-In-Time architecture: AI loads knowledge on-demand)
        messages.append({
            "role": "user",
            "content": "Initialize - get current time and reset overdue daily routines"
        })

        with console.status("[bold green]Loading context...", spinner="dots"):
            # Get initial response with startup tools
            response = provider.send_message(
                client=client,
                messages=messages,
                system_prompt=agent.system_prompt,
                model=agent.model,
                tools=tools
            )

            # Track token usage
            if response.usage:
                session_tokens["input"] += response.usage.input_tokens
                session_tokens["output"] += response.usage.output_tokens
                session_tokens["total"] += response.usage.total_tokens
                session_tokens["cached"] += response.usage.cached_tokens
                session_tokens["turns"] += 1

        # Execute startup tool calls
        if response.tool_calls:
            console.print(f"🛠️  [cyan]Running startup sequence ({len(response.tool_calls)} tool(s))...[/cyan]\n")

            # Add assistant's tool use message using provider-specific format
            messages.append(provider.get_assistant_message(response))

            tool_results = []
            for tool_call in response.tool_calls:
                console.print(f"  [dim]→[/dim] [cyan]{tool_call.name}()[/cyan]")
                try:
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )
                except TypeError as e:
                    error_msg = f"{{\"status\": \"error\", \"error\": \"Invalid function call: {str(e)}\"}}"
                    console.print(f"[bold red]❌ Startup error:[/bold red] {e}")
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, error_msg)
                    )

            # Add tool results to message history
            # Provider-specific handling for different message formats
            if agent.provider == "anthropic":
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                messages.extend(tool_results)

            # Get greeting
            with console.status("[bold green]Preparing greeting...", spinner="dots"):
                response = provider.send_message(
                    client=client,
                    messages=messages,
                    system_prompt=agent.system_prompt,
                    model=agent.model,
                    tools=tools
                )

                # Track token usage
                if response.usage:
                    session_tokens["input"] += response.usage.input_tokens
                    session_tokens["output"] += response.usage.output_tokens
                    session_tokens["total"] += response.usage.total_tokens
                    session_tokens["cached"] += response.usage.cached_tokens
                    session_tokens["turns"] += 1

            if response.text:
                console.print()
                render_assistant_message(response.text)
                console.print()
                messages.append({"role": "assistant", "content": response.text})

    while True:
        try:
            # Get user input
            user_text = console.input("[bold blue]>[/bold blue] ")
            if not user_text.strip():
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_text})

            console.print()
            with console.status("[bold green]Thinking...", spinner="dots"):
                # Send message to provider
                response = provider.send_message(
                    client=client,
                    messages=messages,
                    system_prompt=agent.system_prompt,
                    model=agent.model,
                    tools=tools
                )

                # Track token usage
                if response.usage:
                    session_tokens["input"] += response.usage.input_tokens
                    session_tokens["output"] += response.usage.output_tokens
                    session_tokens["total"] += response.usage.total_tokens
                    session_tokens["cached"] += response.usage.cached_tokens
                    session_tokens["turns"] += 1

            # Handle tool calls - continue until agent returns text instead of more tool calls
            while response.tool_calls:
                console.print(f"🛠️  [cyan]Invoking {len(response.tool_calls)} tool(s)...[/cyan]\n")

                # Add assistant's tool use message using provider-specific format
                messages.append(provider.get_assistant_message(response))

                # Execute each tool
                tool_results = []
                for tool_call in response.tool_calls:
                    console.print(f"  [dim]→[/dim] [cyan]{tool_call.name}[/cyan]([yellow]{tool_call.arguments}[/yellow])")

                    try:
                        # Invoke the tool method on the agent
                        tool_method = getattr(agent, tool_call.name)
                        result = tool_method(**tool_call.arguments)

                        # Display the result beautifully
                        display_tool_result(tool_call.name, result)

                        # Format result for provider
                        tool_results.append(
                            provider.format_tool_results(tool_call.id, str(result))
                        )
                    except TypeError as e:
                        # Catch incorrect function call arguments
                        error_msg = f"{{\"status\": \"error\", \"error\": \"Invalid function call: {str(e)}\", \"hint\": \"Check that parameters are passed directly, not wrapped in 'parameters' dict\"}}"
                        console.print(f"[bold red]❌ Function call error:[/bold red] {e}")
                        tool_results.append(
                            provider.format_tool_results(tool_call.id, error_msg)
                        )

                # Add tool results to message history
                # For Anthropic: single user message with list of tool results
                # For OpenAI: tool results are already individual message dicts
                if agent.provider == "anthropic":
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                else:
                    # OpenAI: extend messages with tool result messages
                    messages.extend(tool_results)

                # Get next response after tool execution (may be more tool calls or final text)
                console.print()
                with console.status("[bold green]Processing results...", spinner="dots"):
                    response = provider.send_message(
                        client=client,
                        messages=messages,
                        system_prompt=agent.system_prompt,
                        model=agent.model,
                        tools=tools
                    )

                    # Track token usage
                    if response.usage:
                        session_tokens["input"] += response.usage.input_tokens
                        session_tokens["output"] += response.usage.output_tokens
                        session_tokens["total"] += response.usage.total_tokens
                        session_tokens["cached"] += response.usage.cached_tokens
                        session_tokens["turns"] += 1

                # Loop will continue if response has more tool_calls, otherwise break to display text

            # Display text response if present
            if response.text:
                console.print()
                render_assistant_message(response.text)
                console.print()
                messages.append({"role": "assistant", "content": response.text})

            # Show token usage for this turn if available
            if response.usage:
                cache_info = ""
                if response.usage.cached_tokens > 0:
                    cache_pct = (response.usage.cached_tokens / response.usage.input_tokens * 100) if response.usage.input_tokens > 0 else 0
                    cache_info = f" [green]({response.usage.cached_tokens} cached = {cache_pct:.0f}% cache hit)[/green]"
                console.print(
                    f"[dim]Tokens: {response.usage.input_tokens} in{cache_info} + {response.usage.output_tokens} out = "
                    f"{response.usage.total_tokens} total[/dim]"
                )

        except KeyboardInterrupt:
            console.print("\n")
            display_token_usage(session_tokens, agent.name, agent.model)
            console.print("\n[yellow]Exiting chat. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ An error occurred:[/bold red] {e}")
            console.print("[dim]Continuing conversation...[/dim]\n")


@app.command("run", help="Executes a high-level goal autonomously.")
def run(goal: str, max_steps: int = 15, agent_name: str = "coder"):
    """
    Takes a goal and lets the agent work autonomously to achieve it.

    Args:
        goal: The goal for the agent to achieve
        max_steps: Maximum number of reasoning steps (default: 15)
        agent_name: Name of the agent to use (default: coder)
    """
    console.print(Panel(
        f"[bold cyan]Synapse AI Run[/bold cyan]\n\n🎯 [yellow]Goal:[/yellow] {goal}",
        box=box.DOUBLE
    ))
    setup_logging()
    load_dotenv()

    try:
        # Load agent and provider
        agent = load_agent(agent_name=agent_name)
        provider = get_provider(agent.provider)
        client = provider.create_client()
        tools = provider.format_tool_schemas(agent)

        console.print(f"✅ [bold green]Agent:[/bold green] {agent.name} ([cyan]{agent.provider}/{agent.model}[/cyan])")
        console.print(f"📋 [bold]Max steps:[/bold] {max_steps}\n")

    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit()

    # Initialize conversation with the goal
    messages = [{"role": "user", "content": goal}]

    for step in range(max_steps):
        console.print(Panel(
            f"[bold cyan]Step {step + 1}/{max_steps}[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        ))

        try:
            with console.status("[bold green]Thinking...", spinner="dots"):
                # Send message to provider
                response = provider.send_message(
                    client=client,
                    messages=messages,
                    system_prompt=agent.system_prompt,
                    model=agent.model,
                    tools=tools
                )

            # If no tool calls, agent is done
            if not response.tool_calls:
                if response.text:
                    render_assistant_message(response.text, title="[bold green]✅ Final Response[/bold green]")
                console.print("\n[bold green]✅ Run Finished:[/bold green] [dim]Goal achieved or no further tools needed.[/dim]")
                break

            # Execute tools
            console.print(f"🛠️  [cyan]Invoking {len(response.tool_calls)} tool(s)...[/cyan]\n")

            tool_results = []
            commit_requested = False

            for tool_call in response.tool_calls:
                console.print(f"  [dim]→[/dim] [cyan]{tool_call.name}[/cyan]([yellow]{tool_call.arguments}[/yellow])")

                if tool_call.name == "git_commit":
                    commit_requested = True

                try:
                    # Execute tool
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)

                    # Display result beautifully
                    display_tool_result(tool_call.name, result)

                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )
                except TypeError as e:
                    error_msg = f"{{\"status\": \"error\", \"error\": \"Invalid function call: {str(e)}\"}}"
                    console.print(f"[bold red]❌ Function call error:[/bold red] {e}")
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, error_msg)
                    )

            # Update conversation with tool results
            messages.append(provider.get_assistant_message(response))
            # Provider-specific handling for different message formats
            if agent.provider == "anthropic":
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                messages.extend(tool_results)

            # If commit was requested, consider goal achieved
            if commit_requested:
                console.print("\n[bold green]✅ Run Finished:[/bold green] [dim]Commit task completed.[/dim]")
                break

        except Exception as e:
            console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
            break

    else:
        console.print("\n[bold yellow]⚠️  Run Finished:[/bold yellow] [dim]Maximum steps reached.[/dim]")


if __name__ == "__main__":
    app()
