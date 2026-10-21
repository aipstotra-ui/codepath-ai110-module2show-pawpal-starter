# 🐾 PawPal+

PawPal+ is a pet care planner. An owner can add pets, schedule feedings, walks, medications and appointments, and see one clean, time-ordered plan for the day with warnings when two things collide.

## Features

- **Multiple pets, one owner** - `Owner.get_all_tasks()` flattens every pet's tasks so the scheduler always sees the whole picture.
- **Sorting by time** - `Scheduler.sort_by_time()` orders tasks by (date, "HH:MM").
- **Filtering** - `Scheduler.filter_tasks()` narrows tasks by pet name and/or completion status.
- **Conflict warnings** - `Scheduler.detect_conflicts()` returns readable warnings (never raises) when pending tasks share a date and time, for the same pet or different pets.
- **Daily / weekly recurrence** - `Scheduler.mark_task_complete()` completes a task and, via `Task.next_occurrence()`, creates the next one (`+1 day` / `+7 days`).
- **Streamlit UI** - add pets and tasks, view the sorted schedule, see `st.warning` conflict alerts, mark tasks done, and browse with filters.

## Implementation summary

| Class | Responsibility |
|---|---|
| `Task` (dataclass) | One activity: description, time, frequency, due date, completed flag, owning pet's name. |
| `Pet` (dataclass) | Name, species and its own task list. `add_task` stamps the task with the pet's name. |
| `Owner` | Holds pets; `get_all_tasks()` returns every pet's tasks together. |
| `Scheduler` | The "brain". Takes an `Owner` and only reads tasks through `get_all_tasks()`. |

The logic lives in `pawpal_system.py` and has no UI code. `main.py` is a CLI demo, `app.py` is the Streamlit front end (the `Owner` is kept in `st.session_state` so it survives reruns), and `tests/test_pawpal.py` is the pytest suite. Diagrams are in `diagrams/` (`uml_draft.mmd`, `uml_final.mmd`).

## Smarter Scheduling

| Feature | Method | Behavior |
|---|---|---|
| Sorting | `Scheduler.sort_by_time()` | `sorted()` with a `lambda` key of `(due_date, time)`. Zero-padded "HH:MM" strings sort correctly as text. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter may be `None` (= any). |
| Conflict detection | `Scheduler.detect_conflicts()` | Groups pending tasks by exact (date, time); any group with 2+ tasks yields a warning string. Completed tasks are ignored. |
| Recurring tasks | `Scheduler.mark_task_complete()` / `Task.next_occurrence()` | Daily adds `timedelta(days=1)`, weekly `timedelta(days=7)`; one-off tasks return `None`. |

## Demo Walkthrough

**UI features:** add a pet, schedule a task (pet, description, time, frequency), see today's schedule as a sorted table, read conflict warnings, mark a task complete, and browse all tasks filtered by pet and status.

**Example workflow:**
1. Add a pet called Buddy (dog) and another called Mochi (cat).
2. Schedule "Morning walk" for Buddy at 08:00 (daily) and "Breakfast" for Mochi at 08:00 (daily).
3. Today's schedule appears sorted by time, with a yellow warning that both tasks are at 08:00.
4. Mark "Morning walk" complete: a new walk is scheduled for tomorrow.

**Scheduler behaviors shown:** sorting, conflict warnings, recurrence, filtering.

### Sample Output

Output of `python main.py` (tasks are added out of order, with a deliberate clash at 08:00):

```
PawPal+ demo for Jordan

=== Today's Schedule (sorted) ===
  [ ] 2026-10-21 07:30  Buddy    Morning walk (daily)
  [ ] 2026-10-21 08:00  Buddy    Flea medication (weekly)
  [ ] 2026-10-21 08:00  Mochi    Breakfast (daily)
  [ ] 2026-10-21 15:00  Buddy    Vet appointment (once)

=== Conflict check ===
  WARNING: Conflict on 2026-10-21 at 08:00: Buddy: Flea medication, Mochi: Breakfast

Completed 'Morning walk'. Next occurrence created for 2026-10-22.

=== Buddy's tasks (filter by pet) ===
  [x] 2026-10-21 07:30  Buddy    Morning walk (daily)
  [ ] 2026-10-21 08:00  Buddy    Flea medication (weekly)
  [ ] 2026-10-21 15:00  Buddy    Vet appointment (once)
  [ ] 2026-10-22 07:30  Buddy    Morning walk (daily)

=== Completed tasks (filter by status) ===
  [x] 2026-10-21 07:30  Buddy    Morning walk (daily)
```

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py          # CLI demo
streamlit run app.py    # web app
```

## Testing PawPal+

```bash
python -m pytest
```

The 14 tests cover: task completion and adding tasks to a pet; the owner aggregating tasks across pets; chronological sorting (including zero-padded times); empty pets/schedules; today's schedule excluding completed and other-day tasks; filtering by pet and status; daily, weekly and one-off recurrence; and conflict detection for same-pet, cross-pet, and non-conflicting/completed cases.

```
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0 -- python
cachedir: .pytest_cache
rootdir: PawPal
plugins: anyio-4.15.1
collecting ... collected 14 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  7%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 14%]
tests/test_pawpal.py::test_owner_get_all_tasks_spans_pets PASSED         [ 21%]
tests/test_pawpal.py::test_sort_by_time_is_chronological PASSED          [ 28%]
tests/test_pawpal.py::test_sort_handles_zero_padded_times PASSED         [ 35%]
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_schedule PASSED [ 42%]
tests/test_pawpal.py::test_todays_schedule_excludes_completed_and_other_days PASSED [ 50%]
tests/test_pawpal.py::test_filter_by_pet_and_status PASSED               [ 57%]
tests/test_pawpal.py::test_daily_task_creates_next_day PASSED            [ 64%]
tests/test_pawpal.py::test_weekly_task_creates_next_week PASSED          [ 71%]
tests/test_pawpal.py::test_one_off_task_does_not_recur PASSED            [ 78%]
tests/test_pawpal.py::test_conflict_detected_across_pets PASSED          [ 85%]
tests/test_pawpal.py::test_conflict_detected_for_same_pet PASSED         [ 92%]
tests/test_pawpal.py::test_no_conflict_for_different_times_or_completed PASSED [100%]

============================== 14 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** The core behaviors and edge cases I thought of all pass. I held back a star because conflicts only match exact times and the UI itself is only lightly tested.
