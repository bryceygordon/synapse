# scripts/check_google_models.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables from .env file
load_dotenv()

console = Console()

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)

    console.print("[bold green]Fetching available Gemini models...[/bold green]")

    model_list = []
    for m in genai.list_models():
        # Check if the model supports the 'generateContent' method needed for this workflow
        if 'generateContent' in m.supported_generation_methods:
            model_list.append(m.name)

    if model_list:
        console.print(Panel("\n".join(model_list), title="[bold cyan]Available Models Supporting 'generateContent'[/bold cyan]", border_style="cyan"))
    else:
        console.print("[bold yellow]No models found that support the required 'generateContent' method.[/bold yellow]")

except Exception as e:
    console.print(Panel(f"[bold red]An error occurred:[/bold red] {e}", border_style="red"))
