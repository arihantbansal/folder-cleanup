# 🚀 Setup Guide

Complete step-by-step guide to get Folder Cleanup running on your system.

## Prerequisites

Before starting, ensure you have:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Ollama** - [Download Ollama](https://ollama.ai)

### Check Your Python Version

```bash
python3 --version
# Should show Python 3.11.x or higher
```

## Step 1: Install Ollama

### macOS
```bash
# Download from ollama.ai or use Homebrew
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows
Download the installer from [ollama.ai](https://ollama.ai)

### Verify Ollama Installation
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve  # In a separate terminal
```

## Step 2: Pull an AI Model

Choose one of these models based on your system:

### Recommended: DeepSeek R1 7B (8GB RAM)
```bash
ollama pull deepseek-r1:7b
```

### Alternative Models

**Fast & Light** (4GB RAM):
```bash
ollama pull llama3.2:3b
```

**Smallest** (2GB RAM):
```bash
ollama pull deepseek-r1:1.5b
```

**Best Quality** (8GB RAM):
```bash
ollama pull qwen2.5:7b
```

### Verify Model Download
```bash
ollama list
# Should show your downloaded model
```

## Step 3: Install Folder Cleanup

### Option A: Install with Poetry (Recommended)

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Clone repository
git clone https://github.com/yourusername/folder-cleanup.git
cd folder-cleanup

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Test installation
folder-cleanup --version
```

### Option B: Install with pip

```bash
# Clone repository
git clone https://github.com/yourusername/folder-cleanup.git
cd folder-cleanup

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .

# Test installation
folder-cleanup --version
```

### Option C: Install from PyPI (Future)

```bash
# Once published to PyPI
pip install folder-cleanup

# Or with pipx for isolated installation
pipx install folder-cleanup
```

## Step 4: Configuration (Optional)

Create a `.env` file in your home directory or project directory:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env  # or your preferred editor
```

Example `.env`:
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:7b

# File Processing
MAX_FILE_SIZE_MB=10
MAX_CONTENT_LENGTH=50000

# Logging
LOG_LEVEL=INFO
```

## Step 5: Verify Installation

Run the health check:

```bash
folder-cleanup check
```

Expected output:
```
✓ Ollama is running
✓ Model 'deepseek-r1:7b' is available
✓ Ready to organize files!
```

## Step 6: First Test Run

Let's do a safe dry-run test:

```bash
# Scan a directory
folder-cleanup scan ~/Downloads

# Preview organization (safe - no changes)
folder-cleanup organize ~/Downloads

# The output will show what would happen without making any changes
```

## Step 7: Organize Your Files

When you're ready to actually organize files:

```bash
# This will ask for confirmation
folder-cleanup organize ~/Downloads --execute
```

## Troubleshooting

### "Command not found: folder-cleanup"

**Problem**: Poetry/pip installation path not in PATH

**Solution**:
```bash
# If using Poetry
poetry run folder-cleanup --version

# Or activate the virtual environment first
poetry shell
folder-cleanup --version

# If using pip, activate venv
source venv/bin/activate  # macOS/Linux
folder-cleanup --version
```

### "Cannot connect to Ollama"

**Problem**: Ollama service not running

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Or on macOS, just open the Ollama app
```

### "Model not found"

**Problem**: Model not downloaded

**Solution**:
```bash
# List available models
ollama list

# Pull the model you want
ollama pull deepseek-r1:7b
```

### "Permission denied"

**Problem**: No write permissions to target directory

**Solution**:
```bash
# Check permissions
ls -la /path/to/directory

# Fix permissions (be careful!)
chmod u+w /path/to/directory
```

### Import Errors

**Problem**: Missing dependencies

**Solution**:
```bash
# Reinstall dependencies
poetry install
# or
pip install -e .

# Check if all dependencies are installed
pip list
```

## Development Setup

For contributors:

```bash
# Clone repository
git clone https://github.com/yourusername/folder-cleanup.git
cd folder-cleanup

# Install with dev dependencies
poetry install

# Install pre-commit hooks (optional)
poetry run pre-commit install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .

# Format code
poetry run black .
```

## Next Steps

- Read the [README.md](README.md) for usage examples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- Try the example script in `examples/basic_usage.py`
- Report issues on GitHub

## Uninstall

```bash
# If installed with Poetry
poetry env remove python

# If installed with pip
pip uninstall folder-cleanup

# Remove the repository
cd ..
rm -rf folder-cleanup
```

## Getting Help

- 📖 Read the [README](README.md)
- 🐛 Report bugs: [GitHub Issues](https://github.com/yourusername/folder-cleanup/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/folder-cleanup/discussions)

---

**Ready to organize your files! 🎉**
