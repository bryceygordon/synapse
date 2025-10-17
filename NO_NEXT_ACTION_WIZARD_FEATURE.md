# Enhancement: Interactive Wizard for Tasks Without Next Actions

**Date**: 2025-10-17
**Status**: ✅ IMPLEMENTED - Ready to test
**Feature Request**: Add complete/delete/process options to find_tasks_without_next_actions
**Current Behavior**: Function only lists tasks, no interaction
**Desired Behavior**: Two-phase interactive wizard (matches inbox wizard)

---

## ✅ IMPLEMENTATION COMPLETE

**Files Created**:
1. `core/wizard/no_next_action_wizard.py` - NoNextActionWizard class (Phase 1)

**Files Modified**:
2. `core/agents/todoist.py` - Added review_tasks_without_next_actions() and helper
3. `agents/todoist.yaml` - Added tool to list

**What was built**:
- Phase 1 wizard with (a)dd/(c)omplete/(d)elete/(s)kip/(p)ause/(q)uit options
- Phase 2 integration (reuses SubtaskTagWizard from inbox wizard)
- Creates subtasks with ONLY @next label in Phase 1
- AI suggests tags in Phase 2, user approves/overrides
- Batch execution of all actions

**Ready for**: Testing and commit

---

## ✅ KEY INSIGHT: TWO-PHASE WORKFLOW

**This wizard follows the SAME PATTERN as the inbox wizard:**

**Phase 1 (NoNextActionWizard)**: Quick review
- User reviews each task, decides action
- For "add next action": Just type the text, move on
- Creates subtasks with ONLY @next label
- Executes complete/delete immediately

**Phase 2 (SubtaskTagWizard - REUSED from inbox wizard)**: Tag approval
- AI generates tag suggestions (energy, duration, labels)
- User reviews each next action with parent context
- Can approve (ENTER) or override
- Batch applies all tags

**Why reuse SubtaskTagWizard?**
- ✅ Same logic: Next actions need tags regardless of origin
- ✅ Consistent UX: User sees same prompts
- ✅ Less code: No duplication
- ✅ Maintainable: Single wizard for all next action tagging

---

## 📋 CURRENT BEHAVIOR

**Function**: `find_tasks_without_next_actions()`
**Location**: `core/agents/todoist.py:1693`

**What it does**:
1. Finds all tasks in "processed" project
2. Checks each task for @next label (or subtask with @next)
3. Returns JSON list of tasks without next actions

**Output example**:
```
⚠️  Found 4 task(s) without next actions:

1. revist the Minecraft server script [@computer]
2. back dotfiles up to github [@AI, @computer]
3. conversation compacting for agents [@agentic, @idea]
4. review quarterly budget reports
```

**Problem**: User sees the list but has to manually process each task via separate commands.

---

## 🎯 NEW FEATURE: Interactive Wizard (TWO-PHASE)

### Two-Phase Workflow (MATCHES INBOX WIZARD)

**Phase 1**: Quick review - declare actions
- User reviews each task
- Options: (a)dd next action, (c)omplete, (d)elete, (s)kip
- For "add next action": Just type the action text, move to next task
- Creates subtasks with ONLY @next label (no other tags yet)

**Phase 2**: Tag approval (only if next actions added)
- AI generates tag suggestions for all created next actions
- User reviews each next action with AI suggestions
- Can approve (ENTER) or override suggestions
- Batch applies all tags

**Why two-phase?**
- ✅ Fast Phase 1: Just declare what needs to be done
- ✅ Smart Phase 2: AI suggests tags based on context
- ✅ Consistent: Matches inbox wizard pattern exactly
- ✅ Efficient: Batch operations at end

**Usage**:
```
> review tasks without next actions
```

### Option 2: Add Flag to Existing Function

Add `interactive=True` parameter to `find_tasks_without_next_actions()`

**Why this might work**:
- Single function does both
- Backward compatible (default interactive=False)

**Problem**: Mixes lookup logic with interaction logic

---

## 🔧 RECOMMENDED IMPLEMENTATION (Option 1)

### NEW FUNCTION: review_tasks_without_next_actions()

**Flow**:
1. Call `find_tasks_without_next_actions()` to get task list
2. If no tasks found → return success message
3. For each task, show interactive prompt:
   ```
   [1/4] revist the Minecraft server script
     Labels: @computer
     Subtasks: 0

     (a)dd next action | (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit:
   ```

4. Handle each option:
   - **`a`** = Add next action (prompt for action text, create subtask with @next)
   - **`c`** = Complete task (mark done)
   - **`d`** = Delete task
   - **`s`** = Skip (continue to next)
   - **`p`** = Pause (save progress, exit)
   - **`q`** = Quit (discard, exit)

5. After wizard finishes, execute all actions in batch

---

## 📝 IMPLEMENTATION PLAN

### ✅ TODO LIST

- [x] **TASK 1**: Create wizard class `NoNextActionWizard` in `core/wizard/no_next_action_wizard.py` ✅
- [x] **TASK 2**: Implement interactive prompt with a/c/d/s/p/q options ✅
- [x] **TASK 3**: Add `review_tasks_without_next_actions()` method to TodoistAgent ✅
- [x] **TASK 4**: Add `_process_no_next_action_review()` helper method ✅
- [x] **TASK 5**: Add to tools list in `agents/todoist.yaml` ✅
- [ ] **TASK 6**: Test the workflow
- [ ] **TASK 7**: Commit and push

**Status**: Implementation complete - Ready to test and commit

---

## 🔧 TASK 1: Create Wizard Class

**File**: `core/wizard/no_next_action_wizard.py` (NEW FILE)

**Structure** (similar to inbox_wizard.py):

```python
"""
Interactive wizard for reviewing tasks without next actions.
"""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class TaskAction:
    """Action to take on a task."""
    task_id: str
    action: str  # "add_next", "complete", "delete", "skip"
    next_action_text: str = None  # For "add_next" action

class NoNextActionWizard:
    """
    Interactive wizard for reviewing tasks without next actions.

    Flow:
    1. Present each task one at a time
    2. User chooses: add next action, complete, delete, skip, pause, quit
    3. Wizard collects all actions
    4. Returns structured instructions for batch execution
    """

    def __init__(self, tasks: List[Dict]):
        """
        Initialize wizard with tasks.

        Args:
            tasks: List of task dicts from find_tasks_without_next_actions()
                   Each has: id, content, labels, has_subtasks, subtask_count
        """
        self.tasks = tasks
        self.actions: List[TaskAction] = []
        self.current_index = 0

    def run(self) -> str:
        """
        Run the wizard interactively.

        Returns:
            Structured instructions for AI to execute
        """
        print("\n" + "="*60)
        print("  REVIEW TASKS WITHOUT NEXT ACTIONS")
        print("="*60)
        print(f"\nReviewing {len(self.tasks)} task(s)")
        print("Options: (a)dd next action, (c)omplete, (d)elete, (s)kip\n")

        for i, task in enumerate(self.tasks):
            self.current_index = i
            task_id = task['id']

            print(f"\n[{i+1}/{len(self.tasks)}] " + "-"*50)
            print(f"Task: {task['content']}")
            if task.get('labels'):
                labels_str = ', '.join('@' + l for l in task['labels'])
                print(f"Labels: {labels_str}")
            if task.get('has_subtasks'):
                print(f"Subtasks: {task['subtask_count']} (none have @next)")

            # Prompt for action
            print(f"\n  (a)dd next action | (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: ", end="")
            action = input().strip().lower()

            if action == 'a':
                # Prompt for next action text
                print(f"  What's the next action? ", end="")
                next_action_text = input().strip()
                if next_action_text:
                    print(f"  ✓ Will add next action: {next_action_text}")
                    self.actions.append(TaskAction(
                        task_id=task_id,
                        action="add_next",
                        next_action_text=next_action_text
                    ))
                else:
                    print("  ⊘ Skipped (no action text provided)")
            elif action == 'c':
                print("  ✓ Marked for completion")
                self.actions.append(TaskAction(task_id=task_id, action="complete"))
            elif action == 'd':
                print("  ✓ Marked for deletion")
                self.actions.append(TaskAction(task_id=task_id, action="delete"))
            elif action == 's':
                print("  ⊘ Skipped")
            elif action == 'p' or action == 'pause':
                print("\n⏸️  Pausing wizard...")
                return self._generate_instructions()
            elif action == 'q' or action == 'quit':
                print("\n❌ Wizard cancelled.")
                return "CANCELLED"
            else:
                print("  ⊘ Invalid option, skipping")

        print(f"\n{'='*60}")
        print("  REVIEW COMPLETE")
        print(f"{'='*60}\n")

        return self._generate_instructions()

    def _generate_instructions(self) -> str:
        """
        Generate structured instructions for AI to execute.

        Format:
        ```
        NO_NEXT_ACTION_REVIEW_OUTPUT

        TASKS_TO_ADD_NEXT_ACTION:
        task_id: 123
        - next_action: "Research options"

        task_id: 456
        - next_action: "Call to confirm"

        TASKS_TO_COMPLETE: ['789', '012']
        TASKS_TO_DELETE: ['345']
        ```
        """
        if not self.actions:
            return "NO_ACTIONS"

        instructions = []
        instructions.append("NO_NEXT_ACTION_REVIEW_OUTPUT\n")

        # Group by action type
        add_next = [a for a in self.actions if a.action == "add_next"]
        complete = [a.task_id for a in self.actions if a.action == "complete"]
        delete = [a.task_id for a in self.actions if a.action == "delete"]

        # Add next actions section
        if add_next:
            instructions.append("TASKS_TO_ADD_NEXT_ACTION:")
            for action in add_next:
                instructions.append(f"task_id: {action.task_id}")
                instructions.append(f"- next_action: \"{action.next_action_text}\"")
                instructions.append("")

        # Complete section
        if complete:
            instructions.append(f"TASKS_TO_COMPLETE: {complete}\n")

        # Delete section
        if delete:
            instructions.append(f"TASKS_TO_DELETE: {delete}\n")

        instructions.append(f"Total actions: {len(self.actions)}")

        return "\n".join(instructions)


def run_no_next_action_wizard(tasks: List[Dict]) -> str:
    """
    Convenience function to run the no-next-action wizard.

    Args:
        tasks: List of tasks without next actions

    Returns:
        Structured instructions for AI to process
    """
    wizard = NoNextActionWizard(tasks)
    return wizard.run()
```

---

## 🔧 TASK 2: Add Agent Method

**File**: `core/agents/todoist.py`

**Add new method** (after `find_tasks_without_next_actions()`, around line 1771):

```python
def review_tasks_without_next_actions(self) -> str:
    """
    Launch interactive two-phase wizard to review and fix tasks without next actions.

    This is a TWO-PHASE workflow (matches inbox wizard pattern):

    Phase 1: Quick review
    - Finds all tasks in processed project without @next label
    - Presents each task with options:
      * (a) Add next action - just type action text, continue
      * (c) Complete task
      * (d) Delete task
      * (s) Skip task
      * (p) Pause and save progress
      * (q) Quit without saving
    - Creates subtasks with ONLY @next label (no other tags yet)
    - Executes complete/delete actions

    Phase 2: Tag approval (only if next actions were added)
    - AI generates tag suggestions for all created next actions
    - User reviews each next action with parent context
    - Can approve (ENTER) or override AI suggestions
    - Batch applies all tag updates

    Returns:
        Success message with summary of all actions taken
    """
    try:
        from core.wizard.no_next_action_wizard import run_no_next_action_wizard

        # Step 1: Find tasks without next actions
        result = self.find_tasks_without_next_actions()
        result_data = json.loads(result)

        if result_data["status"] != "success":
            return result  # Return error as-is

        tasks = result_data["data"]["tasks"]

        if not tasks:
            return self._success("✓ All tasks in processed have next actions")

        # Step 2: Run Phase 1 wizard
        print(f"\n🔍 Phase 1: Reviewing {len(tasks)} task(s)...\n")
        wizard_output = run_no_next_action_wizard(tasks)

        if wizard_output == "CANCELLED":
            return self._success("❌ Review cancelled")

        if wizard_output == "NO_ACTIONS":
            return self._success("⊘ No actions taken")

        # Step 3: Process Phase 1 output (create subtasks, complete, delete)
        phase1_result = self._process_no_next_action_review(wizard_output)
        phase1_data = json.loads(phase1_result)

        if phase1_data["status"] != "success":
            return phase1_result  # Return error

        created_subtasks = phase1_data['data'].get('created_subtasks', [])

        # Step 4: If subtasks were created, run Phase 2 (tag approval)
        if created_subtasks:
            print(f"\n🏷️  Phase 2: Tag approval for {len(created_subtasks)} next action(s)...\n")

            # Generate tag suggestions
            suggest_result = self.suggest_next_action_tags(created_subtasks)
            suggest_data = json.loads(suggest_result)

            if suggest_data["status"] == "success":
                from core.wizard.inbox_wizard import run_subtask_tag_wizard
                suggestions = suggest_data['data']['suggestions']

                # Run tag wizard (reuses SubtaskTagWizard from inbox wizard)
                tag_output = run_subtask_tag_wizard(suggestions)

                # Apply tags
                tag_result = self.process_subtask_tags(tag_output)
                tag_data = json.loads(tag_result)

                if tag_data["status"] == "success":
                    return self._success(
                        f"✅ Review complete!\n"
                        f"   • Added {phase1_data['data']['added_next_actions']} next action(s)\n"
                        f"   • Tagged {tag_data['data']['successful']} next action(s)\n"
                        f"   • Completed {phase1_data['data']['completed']} task(s)\n"
                        f"   • Deleted {phase1_data['data']['deleted']} task(s)",
                        data={
                            "added_next_actions": phase1_data['data']['added_next_actions'],
                            "tagged": tag_data['data']['successful'],
                            "completed": phase1_data['data']['completed'],
                            "deleted": phase1_data['data']['deleted']
                        }
                    )
                else:
                    return tag_result  # Return error
            else:
                return suggest_result  # Return error
        else:
            # No subtasks created, just return Phase 1 results
            return phase1_result

    except Exception as e:
        return self._error("WizardError", f"Failed to run review wizard: {str(e)}")


def _process_no_next_action_review(self, wizard_output: str) -> str:
    """
    Process the output from no-next-action review wizard.

    Args:
        wizard_output: Structured instructions from wizard

    Returns:
        JSON with success/failure summary
    """
    try:
        # Parse wizard output
        tasks_to_add_next = []
        tasks_to_complete = []
        tasks_to_delete = []
        current_task = None

        for line in wizard_output.strip().split('\n'):
            line = line.strip()

            if not line or line.startswith('NO_NEXT_ACTION') or line.startswith('Total'):
                continue

            if line == 'TASKS_TO_ADD_NEXT_ACTION:':
                continue

            if line.startswith('TASKS_TO_COMPLETE:'):
                complete_str = line.split(':', 1)[1].strip()
                tasks_to_complete = eval(complete_str) if complete_str != '[]' else []
                continue

            if line.startswith('TASKS_TO_DELETE:'):
                delete_str = line.split(':', 1)[1].strip()
                tasks_to_delete = eval(delete_str) if delete_str != '[]' else []
                continue

            if line.startswith('task_id:'):
                if current_task:
                    tasks_to_add_next.append(current_task)
                current_task = {'task_id': line.split(':', 1)[1].strip()}
            elif line.startswith('- next_action:') and current_task:
                next_action = line.split(':', 1)[1].strip().strip('"')
                current_task['next_action'] = next_action

        if current_task:
            tasks_to_add_next.append(current_task)

        # Execute actions
        added_count = 0
        completed_count = 0
        deleted_count = 0

        # Add next actions (Phase 1: Create with ONLY @next label)
        created_subtasks = []  # Track for Phase 2
        if tasks_to_add_next:
            print(f"\n📝 Adding next actions to {len(tasks_to_add_next)} task(s)...")
            for task_info in tasks_to_add_next:
                try:
                    task_id = task_info['task_id']
                    next_action = task_info['next_action']

                    # Get parent task for context
                    parent_task = self.api.get_task(task_id)

                    # Create subtask with ONLY @next label (tags will be added in Phase 2)
                    subtask = self.api.add_task(
                        content=next_action,
                        parent_id=task_id,
                        labels=['next']
                    )

                    # Track for Phase 2 tagging
                    created_subtasks.append({
                        'subtask_id': subtask.id,
                        'parent_id': task_id,
                        'parent_content': parent_task.content,
                        'subtask_content': next_action
                    })

                    print(f"  ✓ Added next action to {task_id}: {next_action}")
                    added_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to add next action to {task_id}: {str(e)}")

        # Complete tasks
        if tasks_to_complete:
            print(f"\n✅ Completing {len(tasks_to_complete)} task(s)...")
            for task_id in tasks_to_complete:
                try:
                    result = self.complete_task(task_id)
                    result_data = json.loads(result)
                    if result_data['status'] == 'success':
                        print(f"  ✓ Completed task {task_id}")
                        completed_count += 1
                    else:
                        print(f"  ❌ Failed to complete {task_id}: {result_data.get('message', 'Unknown error')}")
                except Exception as e:
                    print(f"  ❌ Error completing {task_id}: {str(e)}")

        # Delete tasks
        if tasks_to_delete:
            print(f"\n🗑️  Deleting {len(tasks_to_delete)} task(s)...")
            for task_id in tasks_to_delete:
                try:
                    result = self.delete_task(task_id)
                    result_data = json.loads(result)
                    if result_data['status'] == 'success':
                        print(f"  ✓ Deleted task {task_id}")
                        deleted_count += 1
                    else:
                        print(f"  ❌ Failed to delete {task_id}: {result_data.get('message', 'Unknown error')}")
                except Exception as e:
                    print(f"  ❌ Error deleting {task_id}: {str(e)}")

        # Build summary
        summary_parts = []
        if added_count > 0:
            summary_parts.append(f"📝 Added {added_count} next action(s)")
        if completed_count > 0:
            summary_parts.append(f"✔️  Completed {completed_count} task(s)")
        if deleted_count > 0:
            summary_parts.append(f"🗑️  Deleted {deleted_count} task(s)")

        summary = " | ".join(summary_parts) if summary_parts else "No actions taken"

        return self._success(
            f"✅ Phase 1 complete! {summary}",
            data={
                "added_next_actions": added_count,
                "completed": completed_count,
                "deleted": deleted_count,
                "total_actions": added_count + completed_count + deleted_count,
                "created_subtasks": created_subtasks  # For Phase 2 processing
            }
        )

    except Exception as e:
        return self._error("ProcessingError", f"Failed to process review output: {str(e)}")
```

---

## 🔧 TASK 3: Add to Tools List

**File**: `agents/todoist.yaml`

**Add** after `process_inbox` (line ~61):

```yaml
  - process_inbox            # Launch interactive inbox processing wizard
  - review_tasks_without_next_actions  # Review tasks missing next actions
```

---

## 🔧 TASK 4: Update System Prompt (Optional)

**File**: `agents/todoist.yaml`

**Add** after line 22 (Inbox Processing workflow):

```yaml
  4. **Review Tasks**: User says "review tasks without next actions" → call `review_tasks_without_next_actions()` to launch wizard
```

---

## 🧪 TEST PLAN

### Test Case 1: Add Next Action

```bash
./synapse to
> review tasks without next actions
```

When wizard shows:
```
[1/4] revist the Minecraft server script
  Labels: @computer
  Subtasks: 0

  (a)dd next action | (c)omplete | (d)elete | (s)kip | (p)ause | (q)uit: a
  What's the next action? Review current server creation script
  ✓ Will add next action: Review current server creation script
```

**Expected**:
- Continues to next task
- After wizard: Creates subtask with @next label
- Summary shows "📝 Added 1 next action(s)"

---

### Test Case 2: Complete Task

Type `c` at prompt.

**Expected**:
- Task marked for completion
- After wizard: Task completed in Todoist
- Summary shows "✔️  Completed 1 task(s)"

---

### Test Case 3: Mixed Actions

Process 4 tasks:
1. Add next action (a)
2. Complete (c)
3. Delete (d)
4. Skip (s)

**Expected**:
- 1 subtask created
- 1 task completed
- 1 task deleted
- 1 task unchanged
- Summary: "📝 Added 1 next action(s) | ✔️  Completed 1 task(s) | 🗑️  Deleted 1 task(s)"

---

## 🎯 VERIFICATION CHECKLIST

After implementation:

- [ ] Wizard file created: `core/wizard/no_next_action_wizard.py`
- [ ] Method added: `review_tasks_without_next_actions()`
- [ ] Tool added to agents/todoist.yaml
- [ ] Wizard shows correct prompt options
- [ ] 'a' adds next action (creates subtask with @next)
- [ ] 'c' completes task
- [ ] 'd' deletes task
- [ ] 's' skips task
- [ ] 'p' pauses and saves progress
- [ ] 'q' quits without saving
- [ ] Summary shows correct counts
- [ ] Error handling works

---

## 🚨 RESUME INSTRUCTIONS

If interrupted:

**Check progress**:
```bash
ls core/wizard/no_next_action_wizard.py  # Does file exist?
grep -n "review_tasks_without_next_actions" core/agents/todoist.py  # Method added?
grep -n "review_tasks_without_next_actions" agents/todoist.yaml  # Tool added?
```

**Resume at**:
- File doesn't exist = Start TASK 1
- File exists, no method = Start TASK 2
- Method exists, not in tools = Start TASK 3
- All done = Start TASK 5 (test)

**Quick reference**:
- Wizard file: `core/wizard/no_next_action_wizard.py` (NEW)
- Agent method: `core/agents/todoist.py` (line ~1771, after find_tasks_without_next_actions)
- Tools list: `agents/todoist.yaml` (line ~61)
- This doc: `NO_NEXT_ACTION_WIZARD_FEATURE.md`

---

## 📊 BENEFITS

### User Experience
- ✅ **Faster**: Fix tasks without manually calling separate commands
- ✅ **Interactive**: See each task and decide on action
- ✅ **Flexible**: Mix add/complete/delete in single session
- ✅ **Guided**: Clear prompts for each option

### Technical
- ✅ **Consistent**: Uses same pattern as inbox wizard
- ✅ **Reliable**: Batch execution with error handling
- ✅ **Maintainable**: Separate wizard class, clean code structure

---

## 💡 FUTURE ENHANCEMENTS (Not in Scope)

Ideas for later:
- Allow editing task content in wizard
- Show AI suggestions for next actions
- Allow adding multiple next actions per task
- Integration with calendar for scheduling

---

**Status**: Ready to implement
**Next action**: TASK 1 - Create wizard file
**Estimated time**: 25-30 minutes
