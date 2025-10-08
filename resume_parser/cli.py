"""
CLI for parsing resumes and analyzing skills.
"""

# pylint: disable=line-too-long,too-many-locals,too-many-return-statements,too-many-branches,too-many-statements

import argparse
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from pyfiglet import Figlet

from resume_parser.extractors.summary_extractor import SummaryExtractor
from resume_parser.extractors.contact_extractor import ContactExtractor
from resume_parser.extractors.experience_extractor import ExperienceExtractor
from resume_parser.extractors.education_extractor import EducationExtractor
from resume_parser.utils.skills_checker import SkillsChecker
from resume_parser.utils.display import Display

console = Console()
display = Display()

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".md", ".html", ".htm"
}

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Resume Parser CLI")
    parser.add_argument("--mode", choices=["profile", "skills"], help="Mode to run")
    parser.add_argument("--sub-mode", choices=["general", "role", "job"], help="Skills sub-mode")
    parser.add_argument("--file", help="Path to resume file")
    parser.add_argument("--job-file", help="Path to job description text file")
    return parser.parse_args()

def prompt(question: str, default: Optional[str] = None) -> Optional[str]:
    """Prompt user for input with optional default."""
    q_text = Text(question, style="bold cyan")
    if default:
        q_text.append(f" ({default})", style="dim")
    console.print(q_text, end=" ")
    try:
        response = input()
    except EOFError as exc:
        if default is not None:
            return default
        raise exc
    return response.strip() or default

def print_section_title(title: str) -> None:
    """Print a section title in a styled panel."""
    panel = Panel(
        Align.center(f"[bold white]{title}[/bold white]", vertical="middle"),
        style="bold blue",
        padding=(0, 2),
        expand=True
    )
    console.print(panel)

def print_roles_menu(roles: list[str]) -> None:
    """Display available roles in a multi-column layout."""
    if not roles:
        return
    columns = 3 if len(roles) >= 15 else 2 if len(roles) > 7 else 1
    table = Table(show_header=False, box=None, pad_edge=False, expand=False)
    for _ in range(columns):
        table.add_column(justify="left", no_wrap=True)

    rows = (len(roles) + columns - 1) // columns
    for row_idx in range(rows):
        cells = []
        for col_idx in range(columns):
            role_idx = row_idx + rows * col_idx
            if role_idx < len(roles):
                cells.append(f"[cyan]{role_idx + 1:>2}.[/cyan] {roles[role_idx]}")
            else:
                cells.append("")
        table.add_row(*cells)
    console.print(table)

def select_role(roles: list[str]) -> Optional[str]:
    """Prompt the user to select a role by number or keyword search."""
    indexed_roles = list(enumerate(roles, start=1))
    while True:
        selection = prompt("Select role by number or keyword (q to cancel)")
        if selection is None:
            console.print("[yellow]Please enter a number, keyword, or 'q' to exit.[/yellow]")
            continue

        selection = selection.strip()
        if not selection:
            console.print("[yellow]Please enter a number, keyword, or 'q' to exit.[/yellow]")
            continue

        lowered = selection.lower()
        if lowered in {"q", "quit", "exit"}:
            return None
        if lowered in {"list", "ls", "show"}:
            print_roles_menu(roles)
            continue
        if selection.isdigit():
            idx = int(selection)
            if 1 <= idx <= len(roles):
                return roles[idx - 1]
            console.print("[red]Invalid role number. Try again.[/red]")
            continue

        matches = [(idx, name) for idx, name in indexed_roles if lowered in name.lower()]
        if len(matches) == 1:
            return matches[0][1]
        if len(matches) > 1:
            console.print("[yellow]Multiple roles matched your search:[/yellow]")
            for idx, name in matches:
                console.print(f" [cyan]{idx}[/cyan]. {name}")
            console.print("[yellow]Enter the matching number or refine your keyword.[/yellow]")
            continue

        console.print("[red]No matching role found. Try again or type 'list' to see options.[/red]")

def run_cli(mode_choice: str, sub_mode: Optional[str], file_path: str,
            job_file_path: Optional[str] = None) -> None: # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
    """Run the CLI logic based on mode and file path."""
    file_path_obj = Path(file_path)
    ext = file_path_obj.suffix.lower()

    if not file_path_obj.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        return
    if ext not in SUPPORTED_EXTENSIONS:
        console.print(
            f"[red]Error:[/red] Unsupported file type: '{ext}'.\n"
            f"Please use one of: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
        return

    summary_ex = SummaryExtractor()
    contact_ex = ContactExtractor()
    exp_ex = ExperienceExtractor()
    edu_ex = EducationExtractor()
    skills_checker = SkillsChecker()

    if mode_choice == "profile":
        console.clear()
        print_section_title("ATS Profile Check")

        summary_res = summary_ex.extract(file_path)
        display.display_section_text("Professional Summary", summary_res.get("section", ""))

        contact_res = contact_ex.extract(file_path)
        display.display_contact(contact_res)

        console.print("\n")
        print_section_title("Education & Work Experience Check")

        edu_res = edu_ex.extract(file_path)
        exp_res = exp_ex.extract(file_path)

        display.display_education(edu_res, show_gpa=True)
        display.display_experience(exp_res)

    elif mode_choice == "skills":
        if sub_mode == "general":
            console.clear()
            print_section_title("General Skills Review")
            extracted = skills_checker.extract_general_skills(file_path)
            display.display_skills_table(extracted, title="")

        elif sub_mode == "role":
            console.clear()
            roles = sorted(skills_checker.load_roles())
            if not roles:
                console.print("[red]No roles found in skills_master.json[/red]")
                return

            print_section_title("Available Roles")
            print_roles_menu(roles)
            console.print("[dim]Tip: type a number, enter keywords to filter, or 'list' to redisplay options.[/dim]")

            role_name = select_role(roles)
            if role_name is None:
                console.print("[red]No role selected[/red]")
                return

            console.print("\n")
            print_section_title(f"Role-Specific Skills Review: {role_name}")
            extracted = skills_checker.extract_role_skills(file_path, role_name)
            display.display_skills_table(extracted)

        elif sub_mode == "job":
            console.clear()
            if not job_file_path:
                console.print("[red]Job description file is required for job-specific analysis.[/red]")
                return
            job_path_obj = Path(job_file_path)
            if not job_path_obj.exists():
                console.print(f"[red]Error:[/red] Job description file not found: {job_file_path}")
                return
            if job_path_obj.suffix.lower() not in SUPPORTED_EXTENSIONS:
                console.print(
                    f"[red]Error:[/red] Unsupported job description file type: '{job_path_obj.suffix}'.\n"
                    f"Please use one of: {', '.join(SUPPORTED_EXTENSIONS)}"
                )
                return

            print_section_title("Job Description Alignment")
            comparison = skills_checker.compare_with_job_description(file_path, job_file_path)
            if not comparison:
                console.print("[yellow]No overlapping skills detected between the resume and job description.[/yellow]")
            else:
                display.display_job_match_table(comparison)

def interactive_cli():
    """Run the interactive CLI mode."""
    example_resume_path = str(
        Path(__file__).parent.parent
        / "tests" / "data" / "fake_resumes" / "fake_resume.pdf"
    )
    last_resume_path = example_resume_path
    example_job_path = str(
        Path(__file__).parent.parent
        / "tests" / "data" / "job_descriptions" / "sample_job.txt"
    )
    last_job_path = example_job_path

    while True:
        console.clear()
        fig = Figlet(font="standard")
        console.print(Align.center(fig.renderText("Resume Parser")), style="bold green")
        console.print("\n")

        console.print("[bold cyan]Select an option:[/bold cyan]")
        console.print(" [green]1[/green]. Profile / Readability Check")
        console.print(" [green]2[/green]. Skills Analysis")

        mode_choice = prompt("Enter choice", "1")
        mode_choice = (mode_choice or "1").lower()
        mode_choice = "profile" if mode_choice in {"1", "r", "readability", "profile"} else "skills"

        sub_mode = None
        if mode_choice == "skills":
            console.print("\n[bold cyan]Select skills analysis mode:[/bold cyan]")
            console.print(" [green]g[/green]. General")
            console.print(" [green]r[/green]. Role-specific")
            console.print(" [green]j[/green]. Job description specific\n")
            sub_mode_choice = prompt("Enter choice", "g")
            sub_mode_choice = (sub_mode_choice or "g").lower()
            if sub_mode_choice in {"g", "general"}:
                sub_mode = "general"
            elif sub_mode_choice in {"r", "role"}:
                sub_mode = "role"
            else:
                sub_mode = "job"

        file_path = prompt("Enter path to resume file", last_resume_path) or last_resume_path
        last_resume_path = file_path
        job_file_path = None
        if sub_mode == "job":
            job_file_path = prompt("Enter path to job description file", last_job_path) or last_job_path
            last_job_path = job_file_path

        run_cli(mode_choice, sub_mode, file_path, job_file_path)

        console.print("\n")
        try:
            next_action = prompt("Press Enter to return to the main menu or type 'q' to quit")
        except EOFError:
            console.print("[green]Goodbye![/green]")
            break
        if next_action and next_action.lower() in {"q", "quit", "exit"}:
            console.print("[green]Goodbye![/green]")
            break

def main():
    """Main entry point for CLI."""
    args = parse_args()
    if args.mode and args.file:
        run_cli(args.mode, args.sub_mode, args.file, args.job_file)
    else:
        interactive_cli()

if __name__ == "__main__":
    main()
