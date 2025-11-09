# Contributing to Folder Cleanup

Thank you for considering contributing to Folder Cleanup! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/folder-cleanup.git
   cd folder-cleanup
   ```

2. **Install dependencies**
   ```bash
   # Using Poetry (recommended)
   poetry install

   # Or using pip
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install Ollama**
   - Download from [ollama.ai](https://ollama.ai)
   - Pull a model: `ollama pull deepseek-r1:7b`

## Code Quality

We maintain high code quality standards:

### Formatting
```bash
# Format code with Black
poetry run black src/ tests/

# Or
black src/ tests/
```

### Linting
```bash
# Check code with Ruff
poetry run ruff check src/ tests/

# Auto-fix issues
poetry run ruff check --fix src/ tests/
```

### Type Checking
```bash
# Run mypy
poetry run mypy src/
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=folder_cleanup --cov-report=html

# Run specific test file
poetry run pytest tests/test_file_utils.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Maximum line length: 100 characters

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        bool: Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Project Structure

```
folder-cleanup/
├── src/folder_cleanup/
│   ├── cli/           # CLI application (Typer commands)
│   ├── core/          # Core business logic
│   │   ├── scanner.py     # File scanning
│   │   └── organizer.py   # File organization
│   ├── ai/            # AI integration
│   │   ├── ollama_client.py
│   │   ├── analyzer.py
│   │   └── prompts.py
│   ├── models/        # Data models (Pydantic)
│   ├── utils/         # Utilities
│   └── __init__.py
├── tests/             # Test suite
├── docs/              # Documentation
└── examples/          # Example usage
```

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**
   ```bash
   poetry run pytest
   poetry run ruff check .
   poetry run black --check .
   poetry run mypy src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add awesome new feature"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a pull request on GitHub.

## Areas for Contribution

We welcome contributions in these areas:

### Features
- [ ] TUI (Terminal User Interface) with Textual
- [ ] Undo functionality with operation history
- [ ] Watch mode for automatic organization
- [ ] Custom rules and user-defined patterns
- [ ] Similarity-based file grouping
- [ ] Configuration file support (YAML/TOML)

### Improvements
- [ ] Better error messages
- [ ] Performance optimizations
- [ ] More comprehensive tests
- [ ] Better documentation
- [ ] Example use cases
- [ ] Video tutorials

### Bug Fixes
- Report bugs via GitHub Issues
- Include reproduction steps
- Provide system information

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Use meaningful test names

Example:
```python
def test_file_scanner_respects_ignore_patterns():
    """Test that FileScanner correctly ignores .git directories."""
    # Setup
    config = Config(ignore_patterns=[".git"])
    scanner = FileScanner(config)

    # Test
    result = scanner.should_ignore(Path(".git/config"), Path("/home"))

    # Assert
    assert result is True
```

## Questions?

- Open a GitHub Issue for questions
- Check existing issues and discussions
- Read the documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
