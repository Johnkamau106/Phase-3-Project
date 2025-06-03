import typer
from datetime import date
from typing import Optional
import re

from health_simplified.db.database import get_db, Base, engine
from health_simplified.models.user_model import User
from health_simplified.models.food_entry_model import FoodEntry
from health_simplified.models.goal_model import Goal
from health_simplified.models.meal_plan_model import MealPlan
from health_simplified.models.report_model import ReportService

app = typer.Typer(help="Health Simplified CLI", rich_markup_mode="rich")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return next(get_db())

def exit_with_error(message: str):
    typer.secho(f"Error: {message}", fg="red")
    raise typer.Exit(1)

def normalize_name(name: str) -> str:
    return re.sub(r'_[a-f0-9]{6,}$', '', name)

def main():
    init_db()
    db = get_db_session()

    typer.echo("Welcome to Health Simplified CLI!\n")
    users = User.get_all(db)
    filtered_users = [u for u in users if u.id > 15]

    if not filtered_users:
        typer.echo("No users found. Let's create one.\n")
        name = typer.prompt("Enter your name")
        user = User.create(db, name)
        typer.secho(f"✓ Created user: {user.name} (ID: {user.id})", fg="green")
    else:
        typer.echo("Existing users:")
        display_to_user = {}
        for idx, u in enumerate(filtered_users, start=1):
            display_name = normalize_name(u.name)
            typer.echo(f"  {idx}: {display_name}")
            display_to_user[idx] = u

        while True:
            choice = typer.prompt("\nEnter your User number to select or type 'new' to create a new user")
            if choice.lower() == "new":
                name = typer.prompt("Enter your name")
                existing = User.get_by_name(db, name)
                if existing:
                    typer.secho("User with that name already exists. Selecting existing user.", fg="yellow")
                    user = existing
                else:
                    user = User.create(db, name)
                    typer.secho(f"✓ Created user: {user.name} (ID: {user.id})", fg="green")
                break
            else:
                try:
                    sel_num = int(choice)
                    if sel_num not in display_to_user:
                        typer.secho("Invalid user number. Try again.", fg="red")
                        continue
                    user = display_to_user[sel_num]
                    typer.secho(f"✓ Selected user: {user.name} (ID: {user.id})", fg="green")
                    break
                except ValueError:
                    typer.secho("Invalid input. Please enter a number or 'new'.", fg="red")

    while True:
        typer.echo("\nMain Menu - Choose an option:")
        typer.echo("1. Add a food entry")
        typer.echo("2. Set nutrition goals")
        typer.echo("3. Create a meal plan")
        typer.echo("4. Show daily report")
        typer.echo("5. Update nutrition goal")
        typer.echo("6. Delete nutrition goal")
        typer.echo("7. Update meal plan")
        typer.echo("8. Delete meal plan")
        typer.echo("9. Exit")
        typer.echo("10. Update user")
        typer.echo("11. Delete user")
        choice = typer.prompt("Enter number")

        if choice == "1":
            food = typer.prompt("Food name")
            calories = typer.prompt("Calories", type=int)
            entry_date = typer.prompt("Date (YYYY-MM-DD) or leave blank", default="").strip()
            try:
                date_obj = date.fromisoformat(entry_date) if entry_date else date.today()
                FoodEntry.create(db, user.id, food, calories, date_obj)
                typer.secho(f"✓ Added {food} ({calories} kcal) on {date_obj}", fg="green")
            except Exception as e:
                exit_with_error(str(e))

        elif choice == "2":
            daily = typer.prompt("Enter daily calorie goal", type=int)
            weekly = typer.prompt("Enter weekly calorie goal", type=int)
            Goal.create_or_update(db, user.id, daily, weekly)
            typer.secho(f"✓ Set goals: {daily} daily / {weekly} weekly", fg="green")

        elif choice == "3":
            week = typer.prompt("Enter week number (1-52)", type=int)
            for day in range(1, 8):
                day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day - 1]
                details = typer.prompt(f"Enter meal plan for {day_name} (leave blank to skip)", default="").strip()
                if details:
                    MealPlan.create(db, user.id, week, day, details)
            typer.secho(f"✓ Created meal plans for week {week}", fg="green")

        elif choice == "4":
            entry_date = typer.prompt("Enter date (YYYY-MM-DD) or leave blank", default="").strip()
            try:
                report = ReportService.generate_daily_report(
                    db,
                    user.id,
                    date.fromisoformat(entry_date) if entry_date else None
                )
                typer.echo(f"\nDaily Report for {user.name} - {report['date']}")
                typer.echo("=" * 40)

                if report["daily_goal"] is not None:
                    remaining = report["calorie_diff"]
                    status = "green" if remaining >= 0 else "red"
                    typer.secho(f"Remaining: {remaining} kcal", fg=status)
                    typer.echo(f"Consumed: {report['total_calories']}/{report['daily_goal']} kcal")
                else:
                    typer.secho("No daily goal set", fg="yellow")
                    typer.echo(f"Total Calories: {report['total_calories']} kcal")

                typer.echo("\nFood Entries:")
                for entry in report["entries"]:
                    typer.echo(f"• {entry.food}: {entry.calories} kcal")

            except Exception as e:
                exit_with_error(str(e))

        elif choice == "5":
            goal = Goal.get_by_user(db, user.id)
            if not goal:
                typer.secho("No goal found to update.", fg="yellow")
            else:
                daily = typer.prompt(f"New daily goal [{goal.daily_calories}]", default=str(goal.daily_calories), type=int)
                weekly = typer.prompt(f"New weekly goal [{goal.weekly_calories}]", default=str(goal.weekly_calories), type=int)
                Goal.create_or_update(db, user.id, daily, weekly)
                typer.secho(f"✓ Updated goals: {daily} daily / {weekly} weekly", fg="green")

        elif choice == "6":
            goal = Goal.get_by_user(db, user.id)
            if not goal:
                typer.secho("No goal found to delete.", fg="yellow")
            else:
                db.delete(goal)
                db.commit()
                typer.secho("✓ Deleted nutrition goal", fg="green")

        elif choice == "7":
            week = typer.prompt("Enter week number to update", type=int)
            day = typer.prompt("Enter day of the week (1=Mon, 7=Sun)", type=int)
            plan = MealPlan.get_by_day(db, user.id, week, day)
            if not plan:
                typer.secho("No meal plan found for that day.", fg="yellow")
            else:
                new_details = typer.prompt("Enter new plan details", default=plan.plan_details)
                MealPlan.update(db, plan.id, plan_details=new_details)
                typer.secho(f"✓ Updated meal plan for week {week}, day {day}", fg="green")

        elif choice == "8":
            week = typer.prompt("Enter week number to delete", type=int)
            day = typer.prompt("Enter day of the week (1=Mon, 7=Sun)", type=int)
            plan = MealPlan.get_by_day(db, user.id, week, day)
            if not plan:
                typer.secho("No meal plan found for that day.", fg="yellow")
            else:
                MealPlan.delete(db, plan.id)
                typer.secho(f"✓ Deleted meal plan for week {week}, day {day}", fg="green")

        elif choice == "9":
            typer.echo("Goodbye!")
            raise typer.Exit()

        elif choice == "10":
            new_name = typer.prompt(f"Enter new name for user [{user.name}]", default=user.name).strip()
            if new_name != user.name:
                user.name = new_name
                db.commit()
                typer.secho(f"✓ User renamed to {new_name}", fg="green")
            else:
                typer.echo("No changes made.")

        elif choice == "11":
            confirm = typer.confirm(f"Are you sure you want to delete user '{user.name}' and all their data?")
            if confirm:
                FoodEntry.delete_all_by_user(db, user.id)
                Goal.delete_by_user(db, user.id)
                MealPlan.delete_all_by_user(db, user.id)
                db.delete(user)
                db.commit()
                typer.secho(f"✓ User '{user.name}' and related data deleted", fg="green")
                raise typer.Exit()
            else:
                typer.echo("User deletion canceled.")

        else:
            typer.secho("Invalid option. Please select 1-11.", fg="red")

if __name__ == "__main__":
    main()
