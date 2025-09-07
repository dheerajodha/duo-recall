import json
import typer
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt

# Use Rich for better terminal output
console = Console()

# Define the CLI app
app = typer.Typer(
    help="A command-line tool for Duolingo users to practice vocabulary.",
    add_completion=False 
)

# --- Fake Data ---
FAKE_VOCAB_DATA = [
    {"spanish": "casa", "english": "house"},
    {"spanish": "perro", "english": "dog"},
    {"spanish": "gato", "english": "cat"},
    {"spanish": "manzana", "english": "apple"},
    {"spanish": "agua", "english": "water"},
]
# File path for the fake vocab data
VOCAB_FILE = Path("my-vocab.json")

# --- Utility Functions (Mocked) ---
def get_fake_vocab() -> List[Dict[str, str]]:
    """Returns a list of fake vocabulary words."""
    return FAKE_VOCAB_DATA

def save_vocab_to_file(vocab: List[Dict[str, str]]):
    """Saves the vocabulary list to a JSON file."""
    try:
        with open(VOCAB_FILE, "w") as f:
            json.dump(vocab, f, indent=2)
        console.print(f"[green]Successfully saved vocabulary to '{VOCAB_FILE}'[/green]")
    except IOError as e:
        console.print(f"[red]Error saving file: {e}[/red]")
        raise typer.Exit(code=1)

def load_vocab_from_file() -> List[Dict[str, str]]:
    """Loads the vocabulary list from a JSON file."""
    if not VOCAB_FILE.exists():
        console.print(f"[yellow]'{VOCAB_FILE}' not found. Please run 'duo-recall vocab-refresh' first.[/yellow]")
        raise typer.Exit(code=1)
    
    try:
        with open(VOCAB_FILE, "r") as f:
            vocab = json.load(f)
            console.print(f"[green]Loaded {len(vocab)} words from {VOCAB_FILE}[/green]")
            return vocab
    except (IOError, json.JSONDecodeError) as e:
        console.print(f"[red]Error reading '{VOCAB_FILE}': {e}[/red]")
        raise typer.Exit(code=1)

# --- CLI Subcommands ---

# -------------------------------
# Subcommand 1: vocab-refresh
# -------------------------------
@app.command(name="vocab-refresh")
def vocab_refresh():
    """
    Refreshes the local vocabulary list by scraping Duolingo.
    (MOCKED IN PHASE 1)
    """
    console.print("[yellow]Starting Duolingo vocabulary refresh... (MOCKED)[/yellow]")
    
    # Simulate scraping and login process
    console.print("Logging in to Duolingo account... (MOCKED)")
    console.print("Fetching words from the 'Words' section... (MOCKED)")
    
    # Get the fake data
    vocab = get_fake_vocab()
    save_vocab_to_file(vocab)

# -------------------------------
# Subcommand 2: write
# -------------------------------
@app.command(name="write")
def write():
    """
    Practice writing vocabulary by translating words.
    (MOCKED IN PHASE 1)
    """
    console.print("[yellow]Starting vocabulary writing practice... (MOCKED)[/yellow]")
    
    # Load fake data
    vocab = load_vocab_from_file()
    
    if not vocab:
        console.print("[yellow]No words to practice. The vocab file is empty.[/yellow]")
        raise typer.Exit()

    correct_count = 0
    total_questions = 0

    for i, entry in enumerate(vocab, start=1):
        spanish_word = entry["spanish"]
        english_translation = entry["english"]

        console.print(f"\nWord {i}: Translate this → {spanish_word}")
        user_input = Prompt.ask("Your answer (English)").strip().lower()

        total_questions += 1

        # Simple verification
        if user_input == english_translation.lower():
            console.print("[green]✅ Correct![/green]")
            correct_count += 1
        else:
            console.print(f"[red]❌ Wrong! Correct answer: {english_translation}[/red]")

        # Stop every 5 questions for demo
        if i % 2 == 0:
            cont = Prompt.ask("Would you like to continue?")
            if cont.lower().strip() not in ["y", "yes"]:
                break

    # Mocking the session end logic
    console.print("\n[bold]Practice session ended.[/bold]")
    console.print(f"\n🏆 Score: {correct_count}/{total_questions} ({(correct_count/total_questions*100):.1f}%)")

# -------------------------------
# Subcommand 3: speak
# -------------------------------
@app.command(name="speak")
def speak():
    """
    Practice speaking vocabulary by listening and responding.
    (MOCKED IN PHASE 1)
    """

    # Load fake data
    vocab = load_vocab_from_file()
    
    if not vocab:
        console.print("[yellow]No words to practice. The vocab file is empty.[/yellow]")
        raise typer.Exit()
        
    console.print("[yellow]Starting vocabulary speaking practice... (MOCKED)[/yellow]")
    console.print("This feature is not yet implemented. Please check back in a future release!")
    console.print("You can run 'duo-recall vocab-refresh' and 'duo-recall write' for now.")
    
if __name__ == "__main__":
    app()
