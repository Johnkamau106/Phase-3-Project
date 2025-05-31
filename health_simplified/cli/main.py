import typer
from datetime import date
from typing import Optional

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

# --------- USER COMMANDS ---------

@app.command("user create")
def create_user(name: str):
    db = get_db_session()
    try:
        user = User.create(db, name)
        typer.secho(f"✓ Created user: {user.name} (ID: {user.id})", fg="green")
    except ValueError as e:
        exit_with_error(str(e))

@app.command("user list")
def list_users():
    db = get_db_session()
    users = User.get_all(db)
    if not users:
        typer.secho("No users found", fg="yellow")
        return
    for user in users:
        typer.echo(f"• {user.name} (ID: {user.id})")

@app.command("user delete")
def delete_user(user_id: int):
    db = get_db_session()
    if User.delete(db, user_id):
        typer.secho(f"✓ Deleted user ID: {user_id}", fg="green")
    else:
        exit_with_error(f"User ID {user_id} not found")

# --------- FOOD ENTRY COMMANDS ---------

@app.command("entry add")
def add_entry(
    user: str,
    food: str,
    calories: int,
    entry_date: Optional[str] = typer.Option(None, "--date", "-d")
):
    db = get_db_session()
    if calories <= 0:
        exit_with_error("Calories must be a positive integer")

    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    try:
        date_obj = date.fromisoformat(entry_date) if entry_date else date.today()
    except ValueError:
        exit_with_error("Date must be in YYYY-MM-DD format")

    entry = FoodEntry.create(db, user_obj.id, food, calories, date_obj)
    typer.secho(f"✓ Added: {entry.food} ({entry.calories} kcal) on {entry.date}", fg="green")

@app.command("entry list")
def list_entries(
    user: Optional[str] = typer.Option(None, "--user", "-u"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d")
):
    db = get_db_session()

    user_obj = None
    if user:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            exit_with_error(f"User '{user}' not found")

    try:
        date_obj = date.fromisoformat(entry_date) if entry_date else None
    except ValueError:
        exit_with_error("Date must be in YYYY-MM-DD format")

    entries = FoodEntry.get_all(db, user_obj.id if user_obj else None, date_obj)
    if not entries:
        typer.echo("No entries found")
        return

    for entry in entries:
        user_name = User.get_by_id(db, entry.user_id).name
        typer.echo(f"• {entry.date}: {user_name} ate {entry.food} ({entry.calories} kcal) [ID: {entry.id}]")

@app.command("entry update")
def update_entry(
    entry_id: int,
    food: Optional[str] = typer.Option(None, "--food", "-f"),
    calories: Optional[int] = typer.Option(None, "--calories", "-c"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d")
):
    db = get_db_session()
    updates = {}

    if food is not None:
        updates["food"] = food
    if calories is not None:
        if calories <= 0:
            exit_with_error("Calories must be a positive integer")
        updates["calories"] = calories
    if entry_date is not None:
        try:
            updates["date"] = date.fromisoformat(entry_date)
        except ValueError:
            exit_with_error("Date must be in YYYY-MM-DD format")

    if not updates:
        exit_with_error("No fields to update provided")

    entry = FoodEntry.update(db, entry_id, **updates)
    if entry:
        typer.secho(f"✓ Updated entry ID: {entry_id}", fg="green")
    else:
        exit_with_error("Entry not found")

@app.command("entry delete")
def delete_entry(entry_id: int):
    db = get_db_session()
    if FoodEntry.delete(db, entry_id):
        typer.secho(f"✓ Deleted entry ID: {entry_id}", fg="green")
    else:
        exit_with_error(f"Entry ID {entry_id} not found")

# --------- GOAL COMMANDS ---------

@app.command("goal set")
def set_goal(user: str, daily: int, weekly: int):
    db = get_db_session()
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    goal = Goal.create_or_update(db, user_obj.id, daily, weekly)
    typer.secho(f"✓ Goals set for {user}: {goal.daily_calories} daily / {goal.weekly_calories} weekly calories", fg="green")

@app.command("goal show")
def show_goal(user: str):
    db = get_db_session()
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    goal = Goal.get_by_user(db, user_obj.id)
    if not goal:
        typer.secho(f"No goals set for {user}", fg="yellow")
        return

    typer.echo(f"\nNutrition Goals for {user}:")
    typer.echo("=" * 40)
    typer.echo(f"Daily Target: {goal.daily_calories} kcal")
    typer.echo(f"Weekly Target: {goal.weekly_calories} kcal")

@app.command("goal list")
def list_goals(user: str):
    db = get_db_session()
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    goal = Goal.get_by_user(db, user_obj.id)
    if not goal:
        typer.secho(f"No goals set for {user}", fg="yellow")
        return

    typer.echo(f"Daily: {goal.daily_calories} kcal")
    typer.echo(f"Weekly: {goal.weekly_calories} kcal")

# --------- MEAL PLAN COMMANDS ---------

@app.command("plan-meal create")
def create_plan(user: str, week: int, details: str):
    db = get_db_session()
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    plan = MealPlan.create(db, user_obj.id, week, details)
    typer.secho(f"✓ Created meal plan for week {week}", fg="green")

@app.command("plan-meal show")
def show_plan(user: str, week: int):
    db = get_db_session()
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        exit_with_error(f"User '{user}' not found")

    plan = MealPlan.get_by_week(db, user_obj.id, week)
    if not plan:
        typer.secho(f"No meal plan found for week {week}", fg="yellow")
        return

    typer.echo(f"\nMeal Plan - Week {week}:")
    typer.echo("=" * 40)
    typer.echo(plan.plan_details)

@app.command("plan-meal update")
def update_plan(
    plan_id: int,
    week: Optional[int] = typer.Option(None, "--week", "-w"),
    details: Optional[str] = typer.Option(None, "--details", "-d")
):
    db = get_db_session()
    updates = {}
    
    if week is not None:
        updates["week_number"] = week
    if details is not None:
        updates["plan_details"] = details

    if not updates:
        exit_with_error("No fields to update provided")

    plan = MealPlan.update(db, plan_id, **updates)
    if plan:
        typer.secho(f"✓ Updated meal plan ID: {plan_id}", fg="green")
    else:
        exit_with_error("Meal plan not found")

# --------- REPORT COMMANDS ---------

@app.command("report daily")
def daily_report(user: str, report_date: Optional[str] = typer.Option(None, "--date", "-d")):
    db = get_db_session()
    try:
        report = ReportService.generate_daily_report(db, user, date.fromisoformat(report_date) if report_date else None)
    except ValueError:
        exit_with_error("Date must be in YYYY-MM-DD format")

    typer.echo(f"\nDaily Report for {user} - {report['date']}")
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

if __name__ == "__main__":
    init_db()
    app()