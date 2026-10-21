from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


@pytest.fixture
def setup():
    owner = Owner("Jordan")
    buddy, mochi = Pet("Buddy", "dog"), Pet("Mochi", "cat")
    owner.add_pet(buddy)
    owner.add_pet(mochi)
    return owner, buddy, mochi, Scheduler(owner)


# --- basics -----------------------------------------------------------
def test_mark_complete_changes_status():
    task = Task("Walk", "07:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("Feed", "08:00"))
    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Buddy"


def test_owner_get_all_tasks_spans_pets(setup):
    owner, buddy, mochi, _ = setup
    buddy.add_task(Task("Walk", "07:00"))
    mochi.add_task(Task("Feed", "08:00"))
    assert len(owner.get_all_tasks()) == 2


# --- sorting ----------------------------------------------------------
def test_sort_by_time_is_chronological(setup):
    _, buddy, mochi, sched = setup
    buddy.add_task(Task("Vet", "15:00"))
    mochi.add_task(Task("Breakfast", "08:00"))
    buddy.add_task(Task("Walk", "07:30"))
    assert [t.time for t in sched.sort_by_time()] == ["07:30", "08:00", "15:00"]


def test_sort_handles_zero_padded_times(setup):
    _, buddy, _, sched = setup
    buddy.add_task(Task("Late", "10:00"))
    buddy.add_task(Task("Early", "09:00"))
    assert sched.sort_by_time()[0].description == "Early"


def test_pet_with_no_tasks_gives_empty_schedule(setup):
    _, _, _, sched = setup
    assert sched.get_todays_schedule() == []
    assert sched.sort_by_time() == []


def test_todays_schedule_excludes_completed_and_other_days(setup):
    _, buddy, _, sched = setup
    done = Task("Done", "07:00")
    done.mark_complete()
    buddy.add_task(done)
    buddy.add_task(Task("Tomorrow", "07:00", due_date=date.today() + timedelta(days=1)))
    buddy.add_task(Task("Now", "09:00"))
    assert [t.description for t in sched.get_todays_schedule()] == ["Now"]


# --- filtering --------------------------------------------------------
def test_filter_by_pet_and_status(setup):
    _, buddy, mochi, sched = setup
    a, b = Task("Walk", "07:00"), Task("Feed", "08:00")
    buddy.add_task(a)
    mochi.add_task(b)
    a.mark_complete()
    assert sched.filter_tasks(pet_name="Mochi") == [b]
    assert sched.filter_tasks(completed=True) == [a]
    assert sched.filter_tasks(pet_name="Buddy", completed=False) == []


# --- recurrence -------------------------------------------------------
def test_daily_task_creates_next_day(setup):
    _, buddy, _, sched = setup
    task = Task("Walk", "07:00", "daily")
    buddy.add_task(task)
    nxt = sched.mark_task_complete(task)
    assert task.completed
    assert nxt.due_date == date.today() + timedelta(days=1)
    assert nxt in buddy.tasks and not nxt.completed


def test_weekly_task_creates_next_week(setup):
    _, buddy, _, sched = setup
    task = Task("Bath", "10:00", "weekly")
    buddy.add_task(task)
    assert sched.mark_task_complete(task).due_date == date.today() + timedelta(days=7)


def test_one_off_task_does_not_recur(setup):
    _, buddy, _, sched = setup
    task = Task("Vet", "15:00")
    buddy.add_task(task)
    assert sched.mark_task_complete(task) is None
    assert len(buddy.tasks) == 1


# --- conflicts --------------------------------------------------------
def test_conflict_detected_across_pets(setup):
    _, buddy, mochi, sched = setup
    buddy.add_task(Task("Walk", "08:00"))
    mochi.add_task(Task("Feed", "08:00"))
    warnings = sched.detect_conflicts()
    assert len(warnings) == 1 and "08:00" in warnings[0]


def test_conflict_detected_for_same_pet(setup):
    _, buddy, _, sched = setup
    buddy.add_task(Task("Walk", "08:00"))
    buddy.add_task(Task("Meds", "08:00"))
    assert len(sched.detect_conflicts()) == 1


def test_no_conflict_for_different_times_or_completed(setup):
    _, buddy, mochi, sched = setup
    buddy.add_task(Task("Walk", "08:00"))
    mochi.add_task(Task("Feed", "09:00"))
    done = Task("Old", "09:00")
    done.mark_complete()
    buddy.add_task(done)
    assert sched.detect_conflicts() == []
