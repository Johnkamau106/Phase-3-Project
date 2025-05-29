import typer
from datetime import date, timedelta
from typing import Optional
from DB.database import get_db, Base, engine
from models import User, FoodEntry, Goal, MealPlan

app = typer.Typer(help="Health Simplified CLI", rich_markup_mode="rich")

# ----- Database Initialization -----
def init_db():
    Base.metadata.create_all(bind=engine)

# ----- User Commands -----
@app.command("user-create", help="Create a new user")
def create_user(name: str):
    db = next(get_db())
    try:
        user = User.create(db, name)
        typer.secho(f"✓ Created user: {user.name} (ID: {user.id})", fg="green")
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("user-list", help="List all users")
def list_users():
    db = next(get_db())
    users = User.get_all(db)
    for user in users:
        typer.echo(f"• {user.name} (ID: {user.id})")

@app.command("user-delete", help="Delete a user by ID")
def delete_user(user_id: int):
    db = next(get_db())
    if User.delete(db, user_id):
        typer.secho(f"✓ Deleted user ID: {user_id}", fg="green")
    else:
        typer.secho(f"× User ID {user_id} not found", fg="red")
        raise typer.Exit(1)

# ----- Food Entry Commands -----
@app.command("entry-add", help="Add a food entry")
def add_entry(
    user: str = typer.Argument(..., help="User name"),
    food: str = typer.Argument(..., help="Food item name"),
    calories: int = typer.Argument(..., help="Calorie amount"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d", help="Date in YYYY-MM-DD format")
):
    db = next(get_db())
    try:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            raise ValueError(f"User '{user}' not found")
        
        date_obj = date.fromisoformat(entry_date) if entry_date else date.today()
        entry = FoodEntry.create(db, user_obj.id, food, calories, date_obj)
        typer.secho(
            f"✓ Added: {entry.food} ({entry.calories} kcal) on {entry.date}",
            fg="green"
        )
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("entry-list", help="List food entries")
def list_entries(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user name"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d", help="Filter by date (YYYY-MM-DD)")
):
    db = next(get_db())
    try:
        user_obj = None
        if user:
            user_obj = User.get_by_name(db, user)
            if not user_obj:
                raise ValueError(f"User '{user}' not found")
        
        date_obj = date.fromisoformat(entry_date) if entry_date else None
        entries = FoodEntry.get_all(db, user_obj.id if user_obj else None, date_obj)
        
        if not entries:
            typer.echo("No entries found")
            return
            
        for entry in entries:
            user_name = User.get_by_id(db, entry.user_id).name
            typer.echo(
                f"• {entry.date}: {user_name} ate {entry.food} "
                f"({entry.calories} kcal) [ID: {entry.id}]"
            )
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("entry-update", help="Update a food entry")
def update_entry(
    entry_id: int = typer.Argument(..., help="Entry ID to update"),
    food: Optional[str] = typer.Option(None, "--food", "-f", help="New food name"),
    calories: Optional[int] = typer.Option(None, "--calories", "-c", help="New calorie amount"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d", help="New date (YYYY-MM-DD)")
):
    db = next(get_db())
    try:
        updates = {}
        if food: updates["food"] = food
        if calories: updates["calories"] = calories
        if entry_date: updates["date"] = date.fromisoformat(entry_date)
        
        if not updates:
            raise ValueError("No fields to update provided")
            
        entry = FoodEntry.update(db, entry_id, **updates)
        if entry:
            typer.secho(f"✓ Updated entry ID: {entry_id}", fg="green")
            return
        raise ValueError("Entry not found")
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("entry-delete", help="Delete a food entry")
def delete_entry(entry_id: int):
    db = next(get_db())
    if FoodEntry.delete(db, entry_id):
        typer.secho(f"✓ Deleted entry ID: {entry_id}", fg="green")
    else:
        typer.secho(f"× Entry ID {entry_id} not found", fg="red")
        raise typer.Exit(1)

# ----- Goal Commands -----
@app.command("goal-set", help="Set nutrition goals")
def set_goal(
    user: str = typer.Argument(..., help="User name"),
    daily: int = typer.Argument(..., help="Daily calorie goal"),
    weekly: int = typer.Argument(..., help="Weekly calorie goal")
):
    db = next(get_db())
    try:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            raise ValueError(f"User '{user}' not found")
        
        goal = Goal.create_or_update(db, user_obj.id, daily, weekly)
        typer.secho(
            f"✓ Goals set for {user}: {goal.daily_calories} daily / "
            f"{goal.weekly_calories} weekly calories",
            fg="green"
        )
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("goal-list", help="List all goals")
def list_goals(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user name")
):
    db = next(get_db())
    try:
        query = db.query(Goal)
        if user:
            user_obj = User.get_by_name(db, user)
            if not user_obj:
                raise ValueError(f"User '{user}' not found")
            query = query.filter(Goal.user_id == user_obj.id)
        
        goals = query.all()
        if not goals:
            typer.echo("No goals found")
            return
            
        for goal in goals:
            user = User.get_by_id(db, goal.user_id)
            typer.echo(
                f"• User: {user.name}\n"
                f"  Daily: {goal.daily_calories} kcal\n"
                f"  Weekly: {goal.weekly_calories} kcal\n"
                f"  [ID: {goal.id}]"
            )
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

# ----- Meal Plan Commands -----
@app.command("plan-create", help="Create a meal plan")
def create_plan(
    user: str = typer.Argument(..., help="User name"),
    week: int = typer.Argument(..., help="Week number (1-52)"),
    details: str = typer.Argument(..., help="Meal plan details")
):
    db = next(get_db())
    try:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            raise ValueError(f"User '{user}' not found")
        
        plan = MealPlan.create(db, user_obj.id, week, details)
        typer.secho(f"✓ Created meal plan for week {week}", fg="green")
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("plan-update", help="Update a meal plan")
def update_plan(
    plan_id: int = typer.Argument(..., help="Plan ID to update"),
    week: Optional[int] = typer.Option(None, "--week", "-w", help="New week number"),
    details: Optional[str] = typer.Option(None, "--details", "-d", help="New plan details")
):
    db = next(get_db())
    try:
        updates = {}
        if week: updates["week_number"] = week
        if details: updates["plan_details"] = details
        
        if not updates:
            raise ValueError("No fields to update provided")
            
        plan = MealPlan.update(db, plan_id, **updates)
        if plan:
            typer.secho(f"✓ Updated plan ID: {plan_id}", fg="green")
            return
        raise ValueError("Plan not found")
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

@app.command("plan-show", help="Show a meal plan")
def show_plan(
    user: str = typer.Argument(..., help="User name"),
    week: int = typer.Argument(..., help="Week number (1-52)")
):
    db = next(get_db())
    try:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            raise ValueError(f"User '{user}' not found")
        
        plan = MealPlan.get_by_week(db, user_obj.id, week)
        if not plan:
            typer.secho(f"No meal plan found for week {week}", fg="yellow")
            return
            
        typer.echo(f"\nMeal Plan - Week {week}:")
        typer.echo("=" * 40)
        typer.echo(plan.plan_details)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

# ----- Report Commands -----
@app.command("report-daily", help="Generate daily nutrition report")
def daily_report(
    user: str = typer.Argument(..., help="User name"),
    report_date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)")
):
    db = next(get_db())
    try:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            raise ValueError(f"User '{user}' not found")
        
        date_obj = date.fromisoformat(report_date) if report_date else date.today()
        entries = FoodEntry.get_all(db, user_obj.id, date_obj)
        goal = Goal.get_by_user(db, user_obj.id)
        
        total_calories = sum(e.calories for e in entries)
        
        typer.echo(f"\nDaily Report for {user} - {date_obj}")
        typer.echo("=" * 40)
        
        if goal and goal.daily_calories:
            remaining = goal.daily_calories - total_calories
            status = "green" if remaining >= 0 else "red"
            typer.secho(f"Remaining: {remaining} kcal", fg=status)
            typer.echo(f"Consumed: {total_calories}/{goal.daily_calories} kcal")
        else:
            typer.secho("No daily goal set", fg="yellow")
            typer.echo(f"Total Calories: {total_calories} kcal")
        
        typer.echo("\nFood Entries:")
        for entry in entries:
            typer.echo(f"• {entry.food}: {entry.calories} kcal")
            
    except ValueError as e:
        typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(1)

if __name__ == "__main__":
    init_db()
    app()