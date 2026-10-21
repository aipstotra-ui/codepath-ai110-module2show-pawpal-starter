"""CLI demo for PawPal+: builds an owner, pets and tasks, then prints today's schedule."""
from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title, tasks):
    print(f"\n=== {title} ===")
    if not tasks:
        print("  (nothing scheduled)")
    for t in tasks:
        mark = "x" if t.completed else " "
        print(f"  [{mark}] {t.time}  {t.pet_name:<8} {t.description} ({t.frequency})")


def main():
    owner = Owner("Jordan")
    buddy = Pet("Buddy", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(buddy)
    owner.add_pet(mochi)

    buddy.add_task(Task("Morning walk", "07:30", "daily"))
    mochi.add_task(Task("Breakfast", "08:00", "daily"))
    buddy.add_task(Task("Vet appointment", "15:00"))

    scheduler = Scheduler(owner)
    print(f"Today's Schedule for {owner.name}")
    print_schedule("Today's Schedule", scheduler.get_todays_schedule())


if __name__ == "__main__":
    main()
