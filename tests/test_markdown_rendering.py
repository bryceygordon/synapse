"""
Tests for markdown rendering in main.py.

Verifies that:
1. render_assistant_message detects markdown correctly
2. Markdown content is rendered with Rich's Markdown renderer
3. Plain text falls back to simple Panel display
4. All markdown patterns are properly detected
"""

import pytest
from unittest.mock import Mock, patch, call
from rich.markdown import Markdown
from rich.panel import Panel

from core.main import render_assistant_message


class TestMarkdownDetection:
    """Test markdown pattern detection."""

    @patch('core.main.console')
    def test_detects_headers(self, mock_console):
        """Test that headers trigger markdown rendering."""
        text = "# Main Header\n\nSome content"
        render_assistant_message(text)

        # Verify console.print was called with Panel containing Markdown
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg, Panel)
        # The renderable inside the panel should be Markdown
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_code_blocks(self, mock_console):
        """Test that code blocks trigger markdown rendering."""
        text = "Here's some code:\n```python\nprint('hello')\n```"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_unordered_lists(self, mock_console):
        """Test that unordered lists trigger markdown rendering."""
        text = "Items:\n- First\n- Second\n- Third"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_ordered_lists(self, mock_console):
        """Test that numbered lists trigger markdown rendering."""
        text = "Steps:\n1. First step\n2. Second step"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_bold_text(self, mock_console):
        """Test that bold text triggers markdown rendering."""
        text = "This has **bold text** in it."
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_inline_code(self, mock_console):
        """Test that inline code triggers markdown rendering."""
        text = "Use the `create_task` method."
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_blockquotes(self, mock_console):
        """Test that blockquotes trigger markdown rendering."""
        text = "A quote:\n> This is quoted text."
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_detects_horizontal_rules(self, mock_console):
        """Test that horizontal rules trigger markdown rendering."""
        text = "Section one\n---\nSection two"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)


class TestPlainTextFallback:
    """Test that plain text renders without markdown."""

    @patch('core.main.console')
    def test_plain_text_no_markdown(self, mock_console):
        """Test that plain text uses simple Panel, not Markdown."""
        text = "This is just plain text with no markdown."
        render_assistant_message(text)

        # Verify Panel was used, but NOT with Markdown
        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg, Panel)
        # The renderable should be the plain string, not Markdown
        assert isinstance(panel_arg.renderable, str)
        assert panel_arg.renderable == text

    @patch('core.main.console')
    def test_plain_text_with_asterisk(self, mock_console):
        """Test that single asterisk doesn't trigger markdown."""
        text = "This costs $5 * 3 = $15"
        render_assistant_message(text)

        # Should still be plain text (single * is not markdown)
        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, str)


class TestPanelStyling:
    """Test that panel styling is correct."""

    @patch('core.main.console')
    def test_default_title(self, mock_console):
        """Test that default title is 'Assistant'."""
        text = "Hello"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert "[bold green]Assistant[/bold green]" in str(panel_arg.title)

    @patch('core.main.console')
    def test_custom_title(self, mock_console):
        """Test that custom title is used."""
        text = "Hello"
        custom_title = "[bold cyan]Custom Title[/bold cyan]"
        render_assistant_message(text, title=custom_title)

        panel_arg = mock_console.print.call_args[0][0]
        assert custom_title in str(panel_arg.title)

    @patch('core.main.console')
    def test_border_style(self, mock_console):
        """Test that border style is green."""
        text = "Hello"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert panel_arg.border_style == "green"

    @patch('core.main.console')
    def test_box_style(self, mock_console):
        """Test that box style is ROUNDED."""
        text = "Hello"
        render_assistant_message(text)

        from rich import box
        panel_arg = mock_console.print.call_args[0][0]
        assert panel_arg.box == box.ROUNDED


class TestMarkdownEdgeCases:
    """Test edge cases in markdown detection."""

    @patch('core.main.console')
    def test_header_at_start(self, mock_console):
        """Test header at the beginning of text."""
        text = "# Header at start"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_list_at_start(self, mock_console):
        """Test list at the beginning of text."""
        text = "- Item one\n- Item two"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_blockquote_at_start(self, mock_console):
        """Test blockquote at the beginning of text."""
        text = "> Quoted text at start"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_empty_text(self, mock_console):
        """Test that empty text doesn't crash."""
        text = ""
        render_assistant_message(text)

        # Should still render (as plain text panel)
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg, Panel)

    @patch('core.main.console')
    def test_whitespace_only(self, mock_console):
        """Test text with only whitespace."""
        text = "   \n   \n   "
        render_assistant_message(text)

        # Should render as plain text
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg, Panel)


class TestComplexMarkdown:
    """Test complex markdown combinations."""

    @patch('core.main.console')
    def test_mixed_markdown_elements(self, mock_console):
        """Test text with multiple markdown elements."""
        text = """# Main Header

Here's some **bold** text and `code`.

- List item one
- List item two

```python
def example():
    return True
```

> A blockquote to finish."""

        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)

    @patch('core.main.console')
    def test_markdown_with_special_chars(self, mock_console):
        """Test markdown with special characters."""
        text = "Use `@label` and `#project` syntax.\n\n**Note:** This is important!"
        render_assistant_message(text)

        panel_arg = mock_console.print.call_args[0][0]
        assert isinstance(panel_arg.renderable, Markdown)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
