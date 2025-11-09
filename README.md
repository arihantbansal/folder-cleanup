# 📁 Folder Cleanup

> AI-powered file organizer that intelligently renames and organizes your files using local LLMs

Folder Cleanup is a smart command-line tool that uses AI (via Ollama) to analyze your messy folders and automatically organize them. It renames cryptic filenames into descriptive ones and sorts files into logical folder structures.

## ✨ Features

- 🤖 **AI-Powered Analysis**: Uses local LLMs (DeepSeek, Llama, Qwen, etc.) to understand file content
- 📝 **Smart Renaming**: Transforms `IMG_2034.jpg` → `vacation_paris_eiffel_tower_2024.jpg`
- 📂 **Intelligent Organization**: Automatically sorts files into category-based folders
- 🔒 **Privacy-First**: Everything runs locally - your files never leave your machine
- 🎯 **Dry-Run Mode**: Preview all changes before applying them
- 🎨 **Beautiful CLI**: Rich, colorful terminal interface with progress bars
- ⚡ **Fast & Efficient**: Scans thousands of files quickly with smart filtering

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Ollama** - [Install from ollama.ai](https://ollama.ai)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/folder-cleanup.git
cd folder-cleanup

# Install with Poetry
poetry install

# Or install with pip (in a virtual environment)
pip install -e .
```

### Setup Ollama

```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai

# Pull a recommended model
ollama pull deepseek-r1:7b

# Or use a smaller/faster model
ollama pull llama3.2:3b
```

### Basic Usage

```bash
# Check if everything is working
folder-cleanup check

# Scan a directory to see what's there
folder-cleanup scan ~/Downloads

# Preview organization (dry-run mode)
folder-cleanup organize ~/Downloads

# Actually organize files (requires confirmation)
folder-cleanup organize ~/Downloads --execute
```

## 📖 Commands

### `scan` - Scan Directory

Scan a directory and show file information without making changes.

```bash
folder-cleanup scan <directory> [OPTIONS]

# Examples
folder-cleanup scan ~/Downloads
folder-cleanup scan ~/Documents --recursive
folder-cleanup scan ~/Desktop --verbose
```

**Options:**
- `-r, --recursive` - Scan subdirectories (default: True)
- `--verbose` - Show detailed logging

### `organize` - Organize Files

Analyze files with AI and organize them intelligently.

```bash
folder-cleanup organize <directory> [OPTIONS]

# Examples
folder-cleanup organize ~/Downloads              # Preview only (dry-run)
folder-cleanup organize ~/Downloads --execute    # Actually apply changes
folder-cleanup organize ~/Documents -m llama3.2:3b  # Use different model
```

**Options:**
- `-d, --dry-run` - Preview changes without executing (default: True)
- `-e, --execute` - Execute changes (requires confirmation)
- `-m, --model` - Specify Ollama model to use
- `-r, --recursive` - Scan subdirectories recursively
- `--verbose` - Enable verbose logging

### `check` - Health Check

Verify Ollama connection and model availability.

```bash
folder-cleanup check [OPTIONS]

# Examples
folder-cleanup check
folder-cleanup check --model qwen2.5:7b
```

**Options:**
- `-m, --model` - Check specific model availability

## ⚙️ Configuration

Create a `.env` file in your project directory or working directory:

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

## 🎯 How It Works

1. **Scan**: Recursively scans the specified directory, respecting ignore patterns
2. **Analyze**: Sends file metadata and content previews to local LLM via Ollama
3. **Plan**: AI suggests better filenames and folder structures
4. **Preview**: Shows you all proposed changes in a beautiful table
5. **Execute**: Applies changes (only if you confirm with `--execute`)

### Example Transformation

**Before:**
```
Downloads/
├── IMG_2034.jpg
├── document.pdf
├── Screenshot 2024-03-15.png
└── random_file_v2_final.docx
```

**After:**
```
Downloads/
├── Photos/
│   └── Travel/
│       └── France/
│           └── vacation_paris_eiffel_tower_2024.jpg
├── Documents/
│   ├── Finance/
│   │   └── Taxes/
│   │       └── tax_return_2024_final.pdf
│   └── Projects/
│       └── project_proposal_final.docx
└── Screenshots/
    └── database_schema_design.png
```

## 🤖 Recommended Models

| Model | Speed | Quality | RAM | Best For |
|-------|-------|---------|-----|----------|
| `deepseek-r1:1.5b` | ⚡⚡⚡ | ⭐⭐ | 2GB | Quick scans, testing |
| `deepseek-r1:7b` | ⚡⚡ | ⭐⭐⭐⭐ | 8GB | **Recommended** |
| `llama3.2:3b` | ⚡⚡⚡ | ⭐⭐⭐ | 4GB | Good balance |
| `qwen2.5:7b` | ⚡⚡ | ⭐⭐⭐⭐ | 8GB | Excellent categorization |

## 🛡️ Safety Features

- ✅ **Dry-run by default** - Preview before making changes
- ✅ **Confirmation prompts** - Asks before executing operations
- ✅ **Collision detection** - Handles duplicate filenames automatically
- ✅ **Ignore patterns** - Skips `.git`, `node_modules`, etc.
- ✅ **Size limits** - Won't try to read huge files
- ✅ **Error handling** - Continues processing even if some files fail

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .

# Format code
poetry run black .

# Type checking
poetry run mypy src/
```

### Project Structure

```
folder-cleanup/
├── src/folder_cleanup/
│   ├── cli/           # CLI application
│   ├── core/          # Core logic (scanner, organizer)
│   ├── ai/            # AI integration (Ollama client, analyzer)
│   ├── models/        # Data models and schemas
│   └── utils/         # Utilities (config, logging, file utils)
├── tests/             # Test suite
├── pyproject.toml     # Project configuration
└── README.md          # This file
```

## 🐛 Troubleshooting

### "Cannot connect to Ollama"

Make sure Ollama is installed and running:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama service
# On macOS/Linux: Ollama runs as a background service
# Just open the Ollama app or run: ollama serve
```

### "Model not found"

Pull the model you want to use:
```bash
ollama pull deepseek-r1:7b
```

### "Permission denied"

Ensure you have write permissions to the target directory:
```bash
ls -la /path/to/directory
chmod +w /path/to/directory  # If needed
```

### Files not being detected

Check ignore patterns in your config. By default, these are ignored:
- `.git`, `.gitignore`
- `node_modules`, `__pycache__`
- `.DS_Store`, `.env`
- `venv`, `*.pyc`

## 📝 Examples

### Organize Downloads Folder

```bash
# Preview what would happen
folder-cleanup organize ~/Downloads

# Actually do it
folder-cleanup organize ~/Downloads --execute
```

### Use Different Model

```bash
# Use a faster, smaller model
folder-cleanup organize ~/Documents --model llama3.2:3b --execute
```

### Scan Only (No AI Analysis)

```bash
# Just see what files are in a directory
folder-cleanup scan ~/Desktop
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Pydantic](https://docs.pydantic.dev/) - Data validation

## 🗺️ Roadmap

- [ ] TUI (Terminal User Interface) with Textual
- [ ] Undo functionality with operation history
- [ ] Watch mode for automatic organization
- [ ] Custom rules and patterns
- [ ] Similarity-based file grouping
- [ ] Batch processing optimization
- [ ] Export/import organization rules
- [ ] Integration with cloud storage

---

**Made with ❤️ for people with messy Downloads folders**
