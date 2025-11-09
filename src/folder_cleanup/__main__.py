"""Entry point for folder-cleanup when run as a module."""

from .cli.app import app

if __name__ == "__main__":
    app()
