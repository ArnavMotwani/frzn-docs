import os
from pathlib import Path

# -------------------------------------------------------------------------
# Constants for indexing rules
# -------------------------------------------------------------------------

# 1. Exact filenames to index
INDEXABLE_FILENAMES = {
    "Dockerfile",
    "Makefile",
    "CMakeLists.txt",
    "pom.xml",
    "build.gradle",
    "docker-compose.yml",
}

# 2. File extensions to index
INDEXABLE_EXTENSIONS = {
    ".py",   # Python
    ".js",   # JavaScript
    ".ts",   # TypeScript
    ".jsx",  # React JSX
    ".tsx",  # React TSX
    ".java", # Java
    ".go",   # Go
    ".rs",   # Rust
    ".cpp",  # C++
    ".c",    # C
    ".h",    # C/C++ headers
    ".rb",   # Ruby
    ".php",  # PHP
    ".swift",# Swift
    ".kt",   # Kotlin
    ".graphql", # GraphQL schemas
    ".json", # JSON
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".md",   # Markdown
    ".rst",  # reStructuredText
    ".adoc", # AsciiDoc
    ".txt",  # Plain text
    ".html",
    ".sql",  # SQL
    ".sh",   # Shell scripts
    ".bash",
    ".ps1",  # PowerShell
    ".css",  # CSS
}

# 3. Path prefixes or patterns to index
INDEXABLE_PATH_PREFIXES = (
    ".github/workflows/",  # GitHub Actions
    ".gitlab-ci.yml",      # GitLab CI
)


# -------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------

def should_index(path: str) -> bool:
    name = os.path.basename(path)
    suffix = Path(path).suffix.lower()

    if name in INDEXABLE_FILENAMES:
        # print(f"Matched filename: {name}")
        return True

    if suffix in INDEXABLE_EXTENSIONS:
        # print(f"Matched extension: {suffix} in {path}")
        return True

    for prefix in INDEXABLE_PATH_PREFIXES:
        if prefix in path:
            # print(f"Matched path prefix: {prefix} in {path}")
            return True

    return False
