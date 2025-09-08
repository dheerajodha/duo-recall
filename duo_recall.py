import json
import typer
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt
from playwright.sync_api import sync_playwright
import random
import re

# Use Rich for better terminal output
console = Console()

# Define the CLI app
app = typer.Typer(
    help="A command-line tool for Duolingo users to practice vocabulary.",
    add_completion=False,
)

# File path for data
VOCAB_FILE = Path("my-vocab.json")
TRANSLATED_VOCAB_FILE = Path("my-vocab-translated.json")


# --- Utility Functions ---
def save_vocab_to_file(vocab: List[str]):
    """Saves the vocabulary list to a JSON file."""
    try:
        with open(VOCAB_FILE, "w", encoding="utf-8") as f:
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
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        console.print(f"[red]Error reading '{VOCAB_FILE}': {e}[/red]")
        raise typer.Exit(code=1)


def load_translated_vocab() -> Dict[str, Any]:
    """Loads the translated vocabulary list from a JSON file."""
    if TRANSLATED_VOCAB_FILE.exists():
        try:
            with open(TRANSLATED_VOCAB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            console.print(f"[red]Error reading translated vocabulary file: {e}[/red]")
            return {}
    return {}


def save_translated_vocab(translated_vocab: Dict[str, Any]):
    """Saves the translated vocabulary to a JSON file."""
    try:
        with open(TRANSLATED_VOCAB_FILE, "w", encoding="utf-8") as f:
            json.dump(translated_vocab, f, indent=2, ensure_ascii=False)
        console.print(
            f"[green]Successfully saved translated vocabulary to '{TRANSLATED_VOCAB_FILE}'[/green]"
        )
    except IOError as e:
        console.print(f"[red]Error saving translated vocabulary file: {e}[/red]")
        raise typer.Exit(code=1)


# -------------------------------
# Subcommand 1: vocab-refresh
# -------------------------------
@app.command(name="vocab-refresh")
def vocab_refresh(
    username: str = typer.Option(
        ..., "--username", "-u", help="Your Duolingo username."
    ),
    headless: bool = typer.Option(
        False, "-h", "--headless", help="Run browser in headless mode (no GUI)."
    ),
):
    """
    Refreshes the local vocabulary list by scraping Duome.eu.
    """
    console.print(
        f"[yellow]Starting vocabulary refresh for user: [bold]{username}[/bold]...[/yellow]"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
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

    # Load existing translations
    translated_vocab = load_translated_vocab()

    # Find words that need to be translated
    words_to_translate = [word for word in vocab if word not in translated_vocab]

    if not words_to_translate and translated_vocab:
        console.print("[green]All words already translated. Starting quiz.[/green]")
        pass  # Skip the translation scraping
    else:
        console.print(
            f"[cyan]Translating {len(words_to_translate)} new words...[/cyan]"
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://duome.eu/vocabulary/en/es")
            page.wait_for_selector("input#seek")

            search_input = page.locator("input#seek")

            for spanish_word in words_to_translate:
                try:
                    search_input.fill(spanish_word)
                    page.keyboard.press("Enter")

                    match_span = page.locator(
                        f'span.wA:text-is("{spanish_word}")'
                    ).first
                    match_span.wait_for(state="visible", timeout=50000)

                    title_attr = match_span.get_attribute("title")

                    translations_string = re.sub(r"\[.*?\]", "", title_attr).strip()
                    translations_list = [
                        t.strip() for t in translations_string.split(",") if t.strip()
                    ]

                    translated_vocab[spanish_word] = translations_list

                    console.print(
                        f"[green]Found translations for '{spanish_word}': {translations_list}[/green]"
                    )

                except Exception as e:
                    console.print(
                        f"[red]Could not find translation for '{spanish_word}'. Skipping... ({e})[/red]"
                    )

            browser.close()
            save_translated_vocab(translated_vocab)

    if not translated_vocab:
        console.print("[red]No translations found. Cannot start quiz.[/red]")
        raise typer.Exit()

    console.print("[green]Translations loaded. Starting quiz.[/green]")

    correct_count = 0
    total_questions = 0
    question_index = 0

    # Get a list of words to quiz from the translated dictionary
    quiz_words = list(translated_vocab.keys())
    random.shuffle(quiz_words)

    while question_index < len(quiz_words):
        batch_size = min(10, len(quiz_words) - question_index)
        questions = quiz_words[question_index : question_index + batch_size]
        question_index += batch_size

        for spanish_word in questions:
            english_translations = translated_vocab[spanish_word]

            user_input = Prompt.ask(f"Translate '{spanish_word}'")
            total_questions += 1

            if user_input.lower().strip() in [t.lower() for t in english_translations]:
                console.print("[green]Correct![/green]")
                correct_count += 1
            else:
                console.print(
                    f"[red]Incorrect.[/red] The correct translations are '[bold]{', '.join(english_translations)}[/bold]'."
                )

        question_index += batch_size

        # Ask if user wants to continue (only if there are more questions)
        if question_index < len(quiz_words):
            continue_prompt = Prompt.ask(
                f"[yellow]You've completed {total_questions} questions. Continue with more? (y/n)[/yellow]"
            )
            if continue_prompt.lower() != "y":
                break

    console.print("\n[bold]Practice session ended.[/bold]")
    console.print(
        f"🏆 Score: [bold]{correct_count}[/bold]/[bold]{total_questions}[/bold] ({(correct_count / total_questions * 100):.1f}%)"
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
