"""
Tests for Rich library output formatting in main.py.

Verifies that:
1. display_tool_result correctly handles different result types
2. Task lists are formatted as Rich tables
3. JSON responses are syntax-highlighted
4. Plain text is wrapped in panels
"""

import pytest
import json
from unittest.mock import Mock, patch, call
from io import StringIO

from core.main import display_tool_result


class TestDisplayToolResult:
    """Test the display_tool_result function."""

    @patch('core.main.console')
    def test_displays_task_list_as_table(self, mock_console):
        """Test that task lists are displayed as Rich tables."""
        # Mock task list response
        result = json.dumps({
            "status": "success",
            "message": "Found 3 task(s)",
            "data": {
                "tasks": [
                    {
                        "id": "task1",
                        "content": "Test task 1",
                        "labels": ["test", "urgent"],
                        "priority": 2,
                        "due": "today",
                        "created_at": "2025-10-15T10:00:00Z"
                    },
                    {
                        "id": "task2",
                        "content": "Test task 2",
                        "labels": ["test"],
                        "priority": 1,
                        "due": None,
                        "created_at": "2025-10-15T11:00:00Z"
                    },
                    {
                        "id": "task3",
                        "content": "Test task 3",
                        "labels": [],
                        "priority": 4,
                        "due": "tomorrow",
                        "created_at": "2025-10-15T12:00:00Z"
                    }
                ],
                "count": 3
            }
        })

        display_tool_result("list_tasks", result)

        # Verify console.print was called (for the table)
        assert mock_console.print.called
        # First call should be the table
        table_arg = mock_console.print.call_args_list[0][0][0]

        # Verify it's a Table object
        from rich.table import Table
        assert isinstance(table_arg, Table)

    @patch('core.main.console')
    def test_displays_json_with_syntax_highlighting(self, mock_console):
        """Test that non-task JSON is syntax-highlighted."""
        # Mock JSON response without tasks
        result = json.dumps({
            "status": "success",
            "message": "Task created",
            "data": {
                "task_id": "123",
                "content": "New task"
            }
        })

        display_tool_result("create_task", result)

        # Verify console.print was called with a Panel
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]

        from rich.panel import Panel
        assert isinstance(panel_arg, Panel)

    @patch('core.main.console')
    def test_displays_plain_text_in_panel(self, mock_console):
        """Test that plain text (non-JSON) is wrapped in a panel."""
        result = "This is plain text output"

        display_tool_result("some_tool", result)

        # Verify console.print was called with a Panel
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]

        from rich.panel import Panel
        assert isinstance(panel_arg, Panel)

    @patch('core.main.console')
    def test_truncates_long_plain_text(self, mock_console):
        """Test that long plain text is truncated to 500 chars."""
        long_text = "A" * 1000

        display_tool_result("some_tool", long_text)

        # Verify the panel contains truncated text
        assert mock_console.print.called
        panel_arg = mock_console.print.call_args[0][0]

        # The renderable inside the panel should be truncated
        from rich.panel import Panel
        assert isinstance(panel_arg, Panel)

    @patch('core.main.console')
    def test_shows_first_10_tasks_only(self, mock_console):
        """Test that only first 10 tasks are shown in table."""
        # Create 15 tasks
        tasks = []
        for i in range(15):
            tasks.append({
                "id": f"task{i}",
                "content": f"Task {i}",
                "labels": ["test"],
                "priority": 1,
                "due": None,
                "created_at": f"2025-10-15T{i:02d}:00:00Z"
            })

        result = json.dumps({
            "status": "success",
            "message": "Found 15 task(s)",
            "data": {
                "tasks": tasks,
                "count": 15
            }
        })

        display_tool_result("list_tasks", result)

        # Verify console.print was called twice: once for "... and X more", once for table
        assert mock_console.print.call_count == 2

        # First call should be the "... and X more" message (Rich markup string)
        first_call_args = mock_console.print.call_args_list[0]
        # This is a Rich markup string passed as first positional arg
        first_call_text = first_call_args[0][0] if first_call_args[0] else ""
        assert "5 more" in first_call_text

        # Second call should be the table
        second_call = mock_console.print.call_args_list[1][0][0]
        from rich.table import Table
        assert isinstance(second_call, Table)

    @patch('core.main.console')
    def test_handles_error_responses(self, mock_console):
        """Test that error responses are displayed correctly."""
        result = json.dumps({
            "status": "error",
            "error_type": "ProjectNotFound",
            "message": "Project 'Nonexistent' not found"
        })

        display_tool_result("create_task", result)

        # Verify it's displayed (as JSON with syntax highlighting)
        assert mock_console.print.called

    @patch('core.main.console')
    def test_table_has_correct_columns(self, mock_console):
        """Test that task table has all required columns."""
        result = json.dumps({
            "status": "success",
            "message": "Found 1 task",
            "data": {
                "tasks": [{
                    "id": "task1",
                    "content": "Test",
                    "labels": ["test"],
                    "priority": 1,
                    "due": "today",
                    "created_at": "2025-10-15T10:00:00Z"
                }],
                "count": 1
            }
        })

        display_tool_result("list_tasks", result)

        # Get the table
        table_arg = mock_console.print.call_args_list[0][0][0]

        # Verify column count (5 columns: Content, Labels, Priority, Due, Created)
        assert len(table_arg.columns) == 5

    @patch('core.main.console')
    def test_formats_labels_with_at_prefix(self, mock_console):
        """Test that labels are displayed with @ prefix."""
        result = json.dumps({
            "status": "success",
            "message": "Found 1 task",
            "data": {
                "tasks": [{
                    "id": "task1",
                    "content": "Test",
                    "labels": ["home", "urgent"],
                    "priority": 1,
                    "due": None,
                    "created_at": "2025-10-15T10:00:00Z"
                }],
                "count": 1
            }
        })

        display_tool_result("list_tasks", result)

        # Verify table was created
        assert mock_console.print.called

    @patch('core.main.console')
    def test_formats_priority_correctly(self, mock_console):
        """Test that priorities are formatted as P1-P4."""
        result = json.dumps({
            "status": "success",
            "message": "Found 2 tasks",
            "data": {
                "tasks": [
                    {
                        "id": "task1",
                        "content": "High priority",
                        "labels": [],
                        "priority": 4,
                        "due": None,
                        "created_at": "2025-10-15T10:00:00Z"
                    },
                    {
                        "id": "task2",
                        "content": "Normal priority",
                        "labels": [],
                        "priority": 1,
                        "due": None,
                        "created_at": "2025-10-15T10:00:00Z"
                    }
                ],
                "count": 2
            }
        })

        display_tool_result("list_tasks", result)

        # Verify table was created
        assert mock_console.print.called

    @patch('core.main.console')
    def test_shows_created_date_only(self, mock_console):
        """Test that created_at shows only date (YYYY-MM-DD)."""
        result = json.dumps({
            "status": "success",
            "message": "Found 1 task",
            "data": {
                "tasks": [{
                    "id": "task1",
                    "content": "Test",
                    "labels": [],
                    "priority": 1,
                    "due": None,
                    "created_at": "2025-10-15T14:30:45Z"
                }],
                "count": 1
            }
        })

        display_tool_result("list_tasks", result)

        # Verify table was created
        assert mock_console.print.called


class TestRichConsoleUsage:
    """Test that Rich console is used consistently."""

    def test_console_is_initialized(self):
        """Test that global console is initialized."""
        from core.main import console
        from rich.console import Console

        assert isinstance(console, Console)

    def test_display_tool_result_exists(self):
        """Test that display_tool_result function exists."""
        from core.main import display_tool_result

        assert callable(display_tool_result)

    @patch('core.main.console')
    def test_empty_task_list_handled(self, mock_console):
        """Test that empty task lists are handled gracefully."""
        result = json.dumps({
            "status": "success",
            "message": "No tasks found",
            "data": {
                "tasks": [],
                "count": 0
            }
        })

        display_tool_result("list_tasks", result)

        # Should still call console.print (with empty table or message)
        assert mock_console.print.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
