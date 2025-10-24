# tests/test_scheduler.py
import unittest
from unittest.mock import patch, MagicMock

# These imports will fail until the coder agent creates the files and classes
from scripts.plan_my_day import Scheduler
from core.weather_service import WeatherService
from core.todoist_engine.tasks import Task

class TestScheduler(unittest.TestCase):

    def setUp(self):
        """Set up mock data for tests."""
        self.mock_api = MagicMock()

        # Mock tasks from the 'processed' project
        self.mock_tasks = [
            MagicMock(id=1, content="Do the laundry", labels=["low_energy", "chore"], priority=2),
            MagicMock(id=2, content="Go to the post office", labels=["errand"], priority=3),
            MagicMock(id=3, content="Write chapter 3 of book", labels=["high_energy", "work"], priority=4),
            MagicMock(id=4, content="Mow the lawn", labels=["yard_work", "weather_dependent"], priority=2),
            MagicMock(id=5, content="Review quarterly report", labels=["work", "plan"], priority=4),
            MagicMock(id=6, content="Quickly tidy the kitchen", labels=["low_energy", "chore"], priority=1),
        ]

        self.scheduler = Scheduler(self.mock_api)

    @patch('scripts.plan_my_day.Scheduler.get_tasks_from_project')
    def test_fetches_tasks_from_processed_project(self, mock_get_tasks):
        """Test that the scheduler fetches tasks from the 'processed' project."""
        mock_get_tasks.return_value = self.mock_tasks

        # This will fail until the Scheduler class and method are implemented
        tasks = self.scheduler.get_initial_tasks()

        mock_get_tasks.assert_called_with("processed")
        self.assertEqual(len(tasks), 6)

    @patch('core.weather_service.WeatherService.get_weather')
    def test_filters_tasks_based_on_bad_weather(self, mock_get_weather):
        """Test that weather-dependent tasks are filtered out on rainy days."""
        mock_get_weather.return_value = {"condition": "rain"}

        # This will fail until the weather filtering logic is implemented
        filtered_tasks = self.scheduler.filter_tasks_by_weather(self.mock_tasks)

        self.assertEqual(len(filtered_tasks), 5)
        self.assertNotIn("Mow the lawn", [task.content for task in filtered_tasks])

    def test_identifies_plan_tag_for_prompting(self):
        """Test that tasks with the 'plan' tag are correctly identified."""
        # This will fail until the identification logic is implemented
        plan_task = self.scheduler.find_task_to_plan(self.mock_tasks)
        self.assertIsNotNone(plan_task)
        self.assertEqual(plan_task.content, "Review quarterly report")

    def test_sorts_tasks_by_priority(self):
        """Test that tasks are correctly sorted by priority (highest first)."""
        # This will fail until the sorting logic is implemented
        sorted_tasks = self.scheduler.sort_tasks_by_priority(self.mock_tasks)
        self.assertEqual(sorted_tasks[0].content, "Write chapter 3 of book")
        self.assertEqual(sorted_tasks[1].content, "Review quarterly report")
        self.assertEqual(sorted_tasks[2].content, "Go to the post office")

    @patch('builtins.input', side_effect=['yes'])
    def test_suggests_low_energy_tasks_before_9am(self, mock_input):
        """Test the scheduling heuristic for early morning tasks."""
        # This will fail until the suggestion logic is implemented
        daily_plan = self.scheduler.generate_daily_plan(self.mock_tasks)

        morning_tasks = [task for task in daily_plan if task.scheduled_time < "09:00"]
        self.assertLessEqual(len(morning_tasks), 2)
        self.assertTrue(all("low_energy" in task.labels for task in morning_tasks))

    @patch('builtins.input', side_effect=['yes', 'no'])
    def test_suggests_errands_after_930am(self, mock_input):
        """Test the scheduling heuristic for errands."""
        # This will fail until the suggestion logic is implemented
        daily_plan = self.scheduler.generate_daily_plan(self.mock_tasks)

        errand_tasks = [task for task in daily_plan if "errand" in task.labels]
        self.assertTrue(all(task.scheduled_time >= "09:30" for task in errand_tasks))

    @patch('builtins.input', side_effect=['yes', 'yes'])
    def test_suggests_high_energy_task_midday(self, mock_input):
        """Test the scheduling heuristic for high-energy tasks."""
        # This will fail until the suggestion logic is implemented
        daily_plan = self.scheduler.generate_daily_plan(self.mock_tasks)

        high_energy_tasks = [task for task in daily_plan if "high_energy" in task.labels]
        self.assertEqual(len(high_energy_tasks), 1)
        task_time = high_energy_tasks[0].scheduled_time
        self.assertTrue("10:00" <= task_time <= "13:00")

    def test_handles_in_conversation_task_addition(self):
        """Test that a new task can be added during the planning conversation."""
        # This will fail until the conversational logic is implemented
        self.scheduler.start_conversation()
        self.scheduler.add_task_interactively("Buy milk", labels=["errand"], priority=3)

        final_plan = self.scheduler.get_final_plan()
        self.assertIn("Buy milk", [task.content for task in final_plan])

    def test_submits_final_plan_to_todoist_api(self):
        """Test that the final plan is correctly submitted to the Todoist API."""
        # This will fail until the submission logic is implemented
        mock_plan = [
            MagicMock(id=1, content="Do the laundry", due={"string": "today at 8am"}),
            MagicMock(id=2, content="Go to the post office", due={"string": "today at 10am"}),
        ]
        self.scheduler.set_final_plan(mock_plan)

        self.scheduler.submit_plan()

        # Verify that update_task was called for each task with the correct due date
        self.mock_api.update_task.assert_any_call(task_id=1, due_string="today at 8am")
        self.mock_api.update_task.assert_any_call(task_id=2, due_string="today at 10am")

if __name__ == '__main__':
    unittest.main()
