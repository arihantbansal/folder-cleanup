"""Prompt templates for AI interactions."""

RENAME_PROMPT_TEMPLATE = """You are a file organization assistant. Analyze this file and suggest a better, more descriptive filename.

File Information:
- Current name: {filename}
- Extension: {extension}
- Type: {file_type}
- Size: {size_mb:.2f} MB
- Modified: {modified_time}

{content_section}

Instructions:
1. Suggest a clear, descriptive filename that describes the content
2. Keep the same extension
3. Use lowercase with underscores (snake_case) or hyphens
4. Keep it concise (max 50 characters before extension)
5. Remove redundant words like "document", "file", "copy", version numbers if not meaningful
6. Include key identifiers like dates, names, topics

Respond with ONLY a JSON object in this format:
{{"suggested_name": "better_filename{extension}", "confidence": 0.85, "reasoning": "Brief explanation"}}"""

ORGANIZE_PROMPT_TEMPLATE = """You are a file organization assistant. Analyze this file and suggest the best folder structure for it.

File Information:
- Current name: {filename}
- Extension: {extension}
- Type: {file_type}
- Size: {size_mb:.2f} MB
- Modified: {modified_time}

{content_section}

Instructions:
1. Suggest a logical folder path (e.g., "Documents/Work/Projects" or "Photos/2024/Vacation")
2. Use clear category names
3. Maximum 3 levels of nesting
4. Use common organizational patterns (by type, date, project, category)

Respond with ONLY a JSON object in this format:
{{"folder_path": "Category/Subcategory", "category": "main_category", "confidence": 0.9, "reasoning": "Brief explanation"}}"""

COMBINED_PROMPT_TEMPLATE = """You are a file organization assistant. Analyze this file and suggest both a better filename AND the best folder location.

File Information:
- Current name: {filename}
- Extension: {extension}
- Type: {file_type}
- Size: {size_mb:.2f} MB
- Modified: {modified_time}

{content_section}

Instructions:
1. Suggest a clear, descriptive filename (snake_case or hyphens, max 50 chars before extension)
2. Suggest a logical folder path (max 3 levels, e.g., "Documents/Work/Projects")
3. Use the same extension
4. Categorize by content, not just file type

Respond with ONLY a JSON object in this format:
{{"suggested_name": "better_filename{extension}", "folder_path": "Category/Subcategory", "category": "main_category", "confidence": 0.85, "reasoning": "Brief explanation"}}"""


def format_content_section(content: str | None, max_length: int = 1000) -> str:
    """
    Format the content preview section of the prompt.

    Args:
        content: File content preview
        max_length: Maximum content length to include

    Returns:
        str: Formatted content section
    """
    if not content:
        return "Content: [Binary file or content not available]"

    # Truncate if needed
    if len(content) > max_length:
        content = content[:max_length] + "\n... [truncated]"

    return f"Content Preview:\n```\n{content}\n```"


def build_rename_prompt(
    filename: str,
    extension: str,
    file_type: str,
    size_mb: float,
    modified_time: str,
    content: str | None = None,
) -> str:
    """
    Build a prompt for file renaming.

    Args:
        filename: Current filename
        extension: File extension
        file_type: File type category
        size_mb: File size in MB
        modified_time: Last modified timestamp
        content: Optional file content preview

    Returns:
        str: Formatted prompt
    """
    content_section = format_content_section(content)

    return RENAME_PROMPT_TEMPLATE.format(
        filename=filename,
        extension=extension,
        file_type=file_type,
        size_mb=size_mb,
        modified_time=modified_time,
        content_section=content_section,
    )


def build_organize_prompt(
    filename: str,
    extension: str,
    file_type: str,
    size_mb: float,
    modified_time: str,
    content: str | None = None,
) -> str:
    """
    Build a prompt for file organization.

    Args:
        filename: Current filename
        extension: File extension
        file_type: File type category
        size_mb: File size in MB
        modified_time: Last modified timestamp
        content: Optional file content preview

    Returns:
        str: Formatted prompt
    """
    content_section = format_content_section(content)

    return ORGANIZE_PROMPT_TEMPLATE.format(
        filename=filename,
        extension=extension,
        file_type=file_type,
        size_mb=size_mb,
        modified_time=modified_time,
        content_section=content_section,
    )


def build_combined_prompt(
    filename: str,
    extension: str,
    file_type: str,
    size_mb: float,
    modified_time: str,
    content: str | None = None,
) -> str:
    """
    Build a combined prompt for both renaming and organizing.

    Args:
        filename: Current filename
        extension: File extension
        file_type: File type category
        size_mb: File size in MB
        modified_time: Last modified timestamp
        content: Optional file content preview

    Returns:
        str: Formatted prompt
    """
    content_section = format_content_section(content)

    return COMBINED_PROMPT_TEMPLATE.format(
        filename=filename,
        extension=extension,
        file_type=file_type,
        size_mb=size_mb,
        modified_time=modified_time,
        content_section=content_section,
    )
