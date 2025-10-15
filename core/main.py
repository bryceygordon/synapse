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
        tool_names = [t.get("name") for t in tools]
        console.print(f"   [cyan]Tools:[/cyan] [dim]{', '.join(tool_names)}[/dim]\n")

    except Exception as e:
        console.print(f"[bold red]❌ Error loading agent:[/bold red] {e}")
        raise typer.Exit()

    console.print("[dim]Type your message below. Press Ctrl+C to exit.[/dim]\n")

    # Conversation state
    messages = []

    # For TodoistAgent, trigger startup sequence automatically
    if agent_name == "todoist":
        console.print("🚀 [bold yellow]Initializing TodoistAgent...[/bold yellow]\n")

        # Send initial startup message
        messages.append({
            "role": "user",
            "content": "Initialize - get current time and load rules"
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

        # Execute startup tool calls
        if response.tool_calls:
            console.print(f"🛠️  [cyan]Running startup sequence ({len(response.tool_calls)} tool(s))...[/cyan]\n")

            messages.append({
                "role": "assistant",
                "content": response.raw_response.content
            })

            tool_results = []
            for tool_call in response.tool_calls:
                console.print(f"  [dim]→[/dim] [cyan]{tool_call.name}()[/cyan]")
                tool_method = getattr(agent, tool_call.name)
                result = tool_method(**tool_call.arguments)
                tool_results.append(
                    provider.format_tool_results(tool_call.id, str(result))
                )

            messages.append({
                "role": "user",
                "content": tool_results
            })

            # Get greeting
            with console.status("[bold green]Preparing greeting...", spinner="dots"):
                response = provider.send_message(
                    client=client,
                    messages=messages,
                    system_prompt=agent.system_prompt,
                    model=agent.model,
                    tools=tools
                )

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

            # Handle tool calls
            if response.tool_calls:
                console.print(f"🛠️  [cyan]Invoking {len(response.tool_calls)} tool(s)...[/cyan]\n")

                # Add assistant's tool use message to history
                # Use raw_response.content for provider-specific format
                messages.append({
                    "role": "assistant",
                    "content": response.raw_response.content
                })

                # Execute each tool
                tool_results = []
                for tool_call in response.tool_calls:
                    console.print(f"  [dim]→[/dim] [cyan]{tool_call.name}[/cyan]([yellow]{tool_call.arguments}[/yellow])")

                    # Invoke the tool method on the agent
                    tool_method = getattr(agent, tool_call.name)
                    result = tool_method(**tool_call.arguments)

                    # Display the result beautifully
                    display_tool_result(tool_call.name, result)

                    # Format result for provider
                    tool_results.append(
                        provider.format_tool_results(tool_call.id, str(result))
                    )

                # Add tool results to message history
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Get next response after tool execution
                console.print()
                with console.status("[bold green]Processing results...", spinner="dots"):
                    response = provider.send_message(
                        client=client,
                        messages=messages,
                        system_prompt=agent.system_prompt,
                        model=agent.model,
                        tools=tools
                    )

            # Display text response if present
            if response.text:
                console.print()
                render_assistant_message(response.text)
                console.print()
                messages.append({"role": "assistant", "content": response.text})

        except KeyboardInterrupt:
            console.print("\n\n[yellow]Exiting chat. Goodbye![/yellow]")
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

                # Execute tool
                tool_method = getattr(agent, tool_call.name)
                result = tool_method(**tool_call.arguments)

                # Display result beautifully
                display_tool_result(tool_call.name, result)

                tool_results.append(
                    provider.format_tool_results(tool_call.id, str(result))
                )

            # Update conversation with tool results
            messages.append({
                "role": "assistant",
                "content": response.raw_response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

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
