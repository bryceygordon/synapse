"""Language-aware code chunking with semantic boundary preservation."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
from pathlib import Path

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
except ImportError:
    raise ImportError("langchain-text-splitters required. Install with: pip install langchain-text-splitters")


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""

    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", "method", etc.
    metadata: Dict[str, Any]
    content_hash: str  # For caching/deduplication


class CodeChunker:
    """Language-aware chunking that preserves semantic boundaries."""

    PYTHON_SEPARATORS = [
        # First, try to split along class definitions
        "\nclass ",
        "\n    class ",

        # Then function definitions
        "\n    def ",
        "\ndef ",

        # Then nested or other definitions
        "\n        def ",

        # Try to keep related methods together
        "\n    ",

        # Then tokenize by line
        "\n",

        # Finally, split by character
        " ",
        ""
    ]

    def __init__(self, language: str = "python", chunk_size: int = 1000, chunk_overlap: int = 100):
        """Initialize chunker with language-specific settings.

        Args:
            language: Programming language (python, javascript, etc.)
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks
        """
        self.language = language.lower()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Configure text splitter based on language
        if self.language == "python":
            # For Python, use the base splitter with our custom separators for fine-tuned control
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.PYTHON_SEPARATORS,
            )
        else:
            # For other languages, attempt to use the language-aware constructor
            try:
                lang_enum = Language[self.language.upper()]
                self.splitter = RecursiveCharacterTextSplitter.from_language(
                    language=lang_enum,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
            except (KeyError, AttributeError):
                # If the language is not supported by from_language, use a generic splitter
                self.splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=["\n\n", "\n", " ", ""],  # Generic separators
                )

    def chunk_code(self, code: str, file_path: str) -> List[CodeChunk]:
        """Chunk code while preserving semantic boundaries.

        Args:
            code: Source code content
            file_path: Path to source file

        Returns:
            List of CodeChunks with line numbers and types
        """
        # Split into documents using LangChain
        documents = self.splitter.create_documents([code])

        chunks = []
        current_line = 1

        for doc in documents:
            chunk_content = doc.page_content.strip()

            if not chunk_content:
                continue

            # Estimate chunk type and line numbers
            chunk_type = self._classify_chunk(chunk_content)
            end_line = current_line + len(chunk_content.split('\n')) - 1

            # Generate content hash for deduplication
            content_hash = hashlib.md5(chunk_content.encode()).hexdigest()[:8]

            # Extract minimal metadata
            metadata = {
                "chunk_id": f"{Path(file_path).stem}_{current_line}_{content_hash}",
                "token_count_est": len(chunk_content.split()) * 1.3  # Rough token estimate
            }

            chunk = CodeChunk(
                content=chunk_content,
                file_path=file_path,
                start_line=current_line,
                end_line=end_line,
                chunk_type=chunk_type,
                metadata=metadata,
                content_hash=content_hash
            )

            chunks.append(chunk)
            current_line = end_line + 1

        return chunks

    def _classify_chunk(self, content: str) -> str:
        """Classify chunk type based on content patterns.

        Args:
            content: Chunk content

        Returns:
            Chunk type classification
        """
        lines = content.split('\n')

        # Look at first non-empty line
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('class '):
                return 'class'
            elif line.startswith('def ') or line.startswith('    def '):
                return 'function'
            elif line.startswith('async def ') or line.startswith('    async def '):
                return 'async_function'
            elif '__init__(' in line and 'def ' in line:
                return 'constructor'
            elif any(keyword in line for keyword in ['if __name__', 'import ', 'from ']):
                return 'module_setup'
            else:
                return 'code_block'

        return 'unknown'

    def chunk_file(self, file_path: str) -> List[CodeChunk]:
        """Chunk an entire file from disk.

        Args:
            file_path: Path to source file

        Returns:
            List of chunks or empty list if file not found/skipped
        """
        try:
            # --- FIX: Ensure absolute path for reliable reads ---
            absolute_path = str(Path(file_path).resolve())
            # --- END FIX ---

            with open(absolute_path, 'r', encoding='utf-8') as f:
                code = f.read()

            return self.chunk_code(code, absolute_path)

        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Skipping {file_path}: {e}")
            return []