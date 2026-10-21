from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("Walk", "07:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Buddy", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feed", "08:00"))
    assert len(pet.tasks) == 1
