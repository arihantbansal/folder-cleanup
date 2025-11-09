"""Prompt templates for AI interactions with intelligent context-aware analysis."""

# PHASE 1: Pattern Discovery - Analyze entire collection to find patterns
PATTERN_DISCOVERY_PROMPT = """You are an expert file organization analyst. Analyze this ENTIRE collection of files to discover organizational patterns, themes, and relationships.

FILES COLLECTION ({total_files} files):
{file_list}

TASK: Discover patterns across the ENTIRE collection:
1. **Temporal Patterns**: Are there files from specific time periods that should be grouped?
2. **Project/Topic Clusters**: What projects, topics, or themes emerge across files?
3. **Semantic Groups**: Which files are semantically related based on content?
4. **Naming Conventions**: What naming patterns exist that indicate relationships?
5. **Folder Structure**: What logical folder hierarchy would best organize these files?

THINK HOLISTICALLY - you're looking at the forest, not individual trees.

Respond with JSON:
{{
  "patterns": [
    {{"type": "temporal|project|topic|semantic", "description": "...", "file_indices": [0, 5, 12], "suggested_folder": "..."}},
    ...
  ],
  "suggested_categories": ["category1", "category2", ...],
  "folder_structure": {{"parent": ["sub1", "sub2"], ...}},
  "insights": "Overall organizational strategy explanation"
}}"""

# PHASE 2: Contextual File Analysis - Analyze individual files WITH context
CONTEXTUAL_ANALYSIS_PROMPT = """You are a file organization assistant with FULL CONTEXT of the file collection.

TARGET FILE:
- Name: {filename}
- Extension: {extension}
- Type: {file_type}
- Size: {size_mb:.2f} MB
- Modified: {modified_time}
{content_section}

COLLECTION CONTEXT:
- Total files: {total_files}
- Discovered patterns: {patterns}
- Related files: {related_files}
- Suggested folder structure: {folder_structure}

INSTRUCTIONS:
Given the ENTIRE collection context above, suggest the BEST name and location for this specific file.
- Consider relationships to other files
- Use consistent naming with related files
- Place in folder hierarchy that makes sense for the WHOLE collection
- Extract meaningful information from content

Respond with JSON:
{{
  "suggested_name": "descriptive_name{extension}",
  "folder_path": "Category/Subcategory/Specific",
  "category": "main_category",
  "confidence": 0.95,
  "reasoning": "Why this placement, considering context",
  "related_files": ["file1.ext", "file2.ext"],
  "tags": ["tag1", "tag2"]
}}"""

# PHASE 3: Semantic Similarity - For clustering similar files
SIMILARITY_PROMPT = """You are analyzing files for semantic similarity to enable intelligent clustering.

FILE 1:
Name: {file1_name}
Type: {file1_type}
Content: {file1_content}

FILE 2:
Name: {file2_name}
Type: {file2_type}
Content: {file2_content}

TASK: Determine if these files are semantically related and should be grouped together.
Consider:
- Topic similarity
- Temporal relationship (same event/period)
- Project relationship (part of same work)
- Content themes

Respond with JSON:
{{
  "similarity_score": 0.85,
  "are_related": true,
  "relationship_type": "same_project|same_topic|same_event|temporal|none",
  "reasoning": "Why these files are or aren't related",
  "suggested_group": "GroupName"
}}"""

# PHASE 4: Embeddings Analysis - For files without readable content
EMBEDDING_SUMMARY_PROMPT = """Analyze this file and create a semantic summary for embedding-based similarity.

File: {filename}
Type: {file_type}
Metadata: {metadata}
Content: {content_preview}

Create a dense semantic summary (2-3 sentences) that captures:
- What this file is about
- Its purpose or context
- Key identifying information

This summary will be used for vector similarity matching.

Summary:"""


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


def build_pattern_discovery_prompt(files: list[dict]) -> str:
    """
    Build prompt for Phase 1: Pattern discovery across entire collection.

    Args:
        files: List of file info dicts with keys: name, type, size, modified, content_preview

    Returns:
        str: Formatted pattern discovery prompt
    """
    file_list = []
    for i, f in enumerate(files):
        content_preview = f.get("content_preview", "")
        if content_preview:
            content_preview = content_preview[:200] + "..." if len(content_preview) > 200 else content_preview

        file_list.append(
            f"[{i}] {f['name']} | {f['type']} | {f.get('size_mb', 0):.2f}MB | {f.get('modified', 'unknown')}"
            + (f"\n    Content: {content_preview}" if content_preview else "")
        )

    return PATTERN_DISCOVERY_PROMPT.format(
        total_files=len(files), file_list="\n".join(file_list)
    )


def build_contextual_analysis_prompt(
    filename: str,
    extension: str,
    file_type: str,
    size_mb: float,
    modified_time: str,
    content: str | None,
    total_files: int,
    patterns: str,
    related_files: str,
    folder_structure: str,
) -> str:
    """
    Build prompt for Phase 2: Contextual file analysis with collection awareness.

    Args:
        filename: Current filename
        extension: File extension
        file_type: File type category
        size_mb: File size in MB
        modified_time: Last modified timestamp
        content: Optional file content preview
        total_files: Total number of files in collection
        patterns: Discovered patterns from Phase 1
        related_files: List of related files
        folder_structure: Suggested folder hierarchy

    Returns:
        str: Formatted contextual analysis prompt
    """
    content_section = format_content_section(content)

    return CONTEXTUAL_ANALYSIS_PROMPT.format(
        filename=filename,
        extension=extension,
        file_type=file_type,
        size_mb=size_mb,
        modified_time=modified_time,
        content_section=content_section,
        total_files=total_files,
        patterns=patterns,
        related_files=related_files,
        folder_structure=folder_structure,
    )


def build_similarity_prompt(
    file1_name: str,
    file1_type: str,
    file1_content: str | None,
    file2_name: str,
    file2_type: str,
    file2_content: str | None,
) -> str:
    """
    Build prompt for Phase 3: Semantic similarity analysis.

    Args:
        file1_name: First file name
        file1_type: First file type
        file1_content: First file content
        file2_name: Second file name
        file2_type: Second file type
        file2_content: Second file content

    Returns:
        str: Formatted similarity prompt
    """
    content1 = file1_content[:500] if file1_content else "[No content]"
    content2 = file2_content[:500] if file2_content else "[No content]"

    return SIMILARITY_PROMPT.format(
        file1_name=file1_name,
        file1_type=file1_type,
        file1_content=content1,
        file2_name=file2_name,
        file2_type=file2_type,
        file2_content=content2,
    )


def build_embedding_summary_prompt(
    filename: str, file_type: str, metadata: str, content_preview: str | None
) -> str:
    """
    Build prompt for Phase 4: Creating semantic summaries for embeddings.

    Args:
        filename: File name
        file_type: File type
        metadata: File metadata string
        content_preview: Content preview

    Returns:
        str: Formatted embedding summary prompt
    """
    return EMBEDDING_SUMMARY_PROMPT.format(
        filename=filename,
        file_type=file_type,
        metadata=metadata,
        content_preview=content_preview or "[No content available]",
    )
