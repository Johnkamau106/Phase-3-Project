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
    # Strip trailing hex suffixes from names like 'username_abc123'
    return re.sub(r'_[a-f0-9]{6,}$', '', name)


def main():
    init_db()
    db = get_db_session()

    typer.echo("Welcome to Health Simplified CLI!\n")
    users = User.get_all(db)

    # Filter out first 15 users and show only from 16 onwards (as per your request)
    filtered_users = [u for u in users if u.id > 15]

    # Display filtered users with remapped numbering starting from 1
    if not filtered_users:
        typer.echo("No users found. Let's create one.\n")
        name = typer.prompt("Enter your name")
        user = User.create(db, name)
        typer.secho(f"✓ Created user: {user.name} (ID: {user.id})", fg="green")
    else:
        typer.echo("Existing users:")
        # Create a mapping from displayed number to real user object
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
        typer.echo("5. Exit")
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
            week = typer.prompt("Enter week number (e.g., 1)", type=int)
            details = typer.prompt("Enter meal plan details")
            MealPlan.create(db, user.id, week, details)
            typer.secho(f"✓ Created meal plan for week {week}", fg="green")

        elif choice == "4":
            entry_date = typer.prompt("Enter date (YYYY-MM-DD) or leave blank", default="").strip()
            try:
                report = ReportService.generate_daily_report(
                    db,
                    user.id,  # Pass user ID here (fix)
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
            typer.echo("Goodbye!")
            raise typer.Exit()

        else:
            typer.secho("Invalid option. Please select 1-5.", fg="red")


if __name__ == "__main__":
    main()
