"""
Module entry point so `python -m resume_parser` launches the CLI.
"""

from resume_parser.cli import main


def run():
    """Invoke the CLI main to support `python -m resume_parser`."""
    main()


if __name__ == "__main__":
    run()
