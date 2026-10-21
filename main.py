"""CLI demo for PawPal+: builds an owner, pets and tasks, then exercises the Scheduler."""
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title, tasks):
    print(f"\n=== {title} ===")
    if not tasks:
        print("  (nothing scheduled)")
    for t in tasks:
        mark = "x" if t.completed else " "
        print(f"  [{mark}] {t.due_date} {t.time}  {t.pet_name:<8} {t.description} ({t.frequency})")


def main():
    owner = Owner("Jordan")
    buddy = Pet("Buddy", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(buddy)
    owner.add_pet(mochi)

    # Added deliberately out of order, with one clash at 08:00.
    buddy.add_task(Task("Vet appointment", "15:00"))
    mochi.add_task(Task("Breakfast", "08:00", "daily"))
    buddy.add_task(Task("Morning walk", "07:30", "daily"))
    buddy.add_task(Task("Flea medication", "08:00", "weekly"))

    scheduler = Scheduler(owner)
    print(f"PawPal+ demo for {owner.name}")
    print_schedule("Today's Schedule (sorted)", scheduler.get_todays_schedule())

    print("\n=== Conflict check ===")
    for warning in scheduler.detect_conflicts() or ["No conflicts."]:
        print(f"  WARNING: {warning}")

    walk = next(t for t in buddy.tasks if t.description == "Morning walk")
    nxt = scheduler.mark_task_complete(walk)
    print(f"\nCompleted '{walk.description}'. Next occurrence created for {nxt.due_date}.")

    print_schedule("Buddy's tasks (filter by pet)", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Buddy")))
    print_schedule("Completed tasks (filter by status)", scheduler.filter_tasks(completed=True))


if __name__ == "__main__":
    main()
