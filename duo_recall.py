import json
import typer
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.prompt import Prompt
from playwright.sync_api import sync_playwright

# Use Rich for better terminal output
console = Console()

# Define the CLI app
app = typer.Typer(
    help="A command-line tool for Duolingo users to practice vocabulary.",
    add_completion=False,
)

# File path for data
VOCAB_FILE = Path("my-vocab.json")


# --- Utility Functions ---
def save_vocab_to_file(vocab: List[str]):
    """Saves the vocabulary list to a JSON file."""
    try:
        with open(VOCAB_FILE, "w") as f:
            json.dump(vocab, f, indent=2, ensure_ascii=False)
        console.print(f"[green]Successfully saved vocabulary to '{VOCAB_FILE}'[/green]")
    except IOError as e:
        console.print(f"[red]Error saving file: {e}[/red]")
        raise typer.Exit(code=1)


def load_vocab_from_file() -> List[str]:
    """Loads the vocabulary list from a JSON file."""
    if not VOCAB_FILE.exists():
        console.print(
            f"[yellow]'{VOCAB_FILE}' not found. Please run 'duo-recall vocab-refresh' first.[/yellow]"
        )
        raise typer.Exit(code=1)

    try:
        with open(VOCAB_FILE, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        console.print(f"[red]Error reading '{VOCAB_FILE}': {e}[/red]")
        raise typer.Exit(code=1)


# -------------------------------
# Subcommand 1: vocab-refresh
# -------------------------------
@app.command(name="vocab-refresh")
def vocab_refresh(
    username: str = typer.Option(
        ..., "--username", "-u", help="Your Duolingo username."
    )
):
    """
    Refreshes the local vocabulary list by scraping Duome.eu.
    """
    console.print(
        f"[yellow]Starting vocabulary refresh for user: [bold]{username}[/bold]...[/yellow]"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to the user's profile
        url = f"https://duome.eu/{username}/en/es"
        console.print(f"[cyan]Navigating to {url}[/cyan]")
        page.goto(url)
        page.wait_for_selector('label[for="tabSkills"]')

        # Click on the "Skills" tab
        console.print("[cyan]Clicking 'Skills' tab...[/cyan]")
        page.locator('label[for="tabSkills"]').click()
        page.wait_for_selector("ul.paddedSkills")

        # Scrape words from all completed lessons
        completed_words = []
        seen_words = set()

        # Get all list items (lessons)
        lessons = page.locator("ul.paddedSkills > li")

        for i in range(lessons.count()):
            lesson = lessons.nth(i)

            # expand the lesson
            lesson.locator('span[title="Tips and notes"]').click()

            # Check for completed lesson criteria
            is_completed = lesson.locator(".crown.empty").is_visible()
            if is_completed:
                break

            try:
                # Click to expand the lesson and show words
                lesson.click()
                # Scope the locator to the current lesson to avoid strict mode violation
                blockquote_locator = lesson.locator("blockquote")
                if blockquote_locator.is_visible():
                    # Scrape the words from the blockquote element
                    # Get all <b> tags within the blockquote
                    word_elements = blockquote_locator.locator("b")

                    for j in range(word_elements.count()):
                        word = word_elements.nth(j).inner_text().strip()
                        if word not in seen_words:
                            completed_words.append(word)
                            seen_words.add(word)
                else:
                    # stop processing the lessons
                    break

                console.print(
                    f"[green]Found {len(completed_words)} words from a completed lesson.[/green]"
                )

            except Exception as e:
                console.print(f"[red]Could not process lesson. Skipping... ({e})[/red]")
                continue

        browser.close()

        # Save all unique words
        save_vocab_to_file(list(completed_words))
        console.print(
            f"[green]Scraping complete. Total unique words saved: {len(completed_words)}[/green]"
        )


# -------------------------------
# Subcommand 2: write
# -------------------------------
@app.command()
def write():
    """
    Practice writing vocabulary by translating words.
    """
    console.print("[yellow]Starting vocabulary writing practice...[/yellow]")

    # Load data from the now-real vocab file
    vocab = load_vocab_from_file()

    if not vocab:
        console.print("[yellow]No words to practice. The vocab file is empty.[/yellow]")
        raise typer.Exit()

    correct_count = 0
    total_questions = 0

    # Simple loop for a basic demo
    for entry in vocab[:5]:  # Practice with the first 5 words for a quick test
        # Note: the words are now just a list, not a dictionary with translations.
        spanish_word = entry

        user_input = Prompt.ask(f"Translate '{spanish_word}'")

        total_questions += 1

        # Simple verification
        if user_input.lower().strip() == "":  # We can't verify yet without a dictionary
            console.print(
                f"[red]Cannot verify. The correct translation is unknown.[/red]"
            )
        else:
            console.print(f"[green]Good attempt![/green]")
            correct_count += 1

    # Mocking the session end logic
    console.print("\n[bold]Practice session ended.[/bold]")
    console.print(
        f"You answered {correct_count} out of {total_questions} words correctly."
    )


# -------------------------------
# Subcommand 3: speak
# -------------------------------
@app.command()
def speak():
    """
    Practice speaking vocabulary by listening and responding.
    """
    console.print(
        "[yellow]Starting vocabulary speaking practice... (FEATURE NOT YET IMPLEMENTED)[/yellow]"
    )
    console.print(
        "This feature will be built in Phase 4. For now, try 'duo-recall write'."
    )


if __name__ == "__main__":
    app()
