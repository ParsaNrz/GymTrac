from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.exercise import Exercise
from app.schemas.exercise import VALID_MUSCLE_GROUPS


SEED_EXERCISES = [
    # Chest
    ("Bench Press", "Chest", "Barbell", "Compound horizontal push. The staple chest exercise."),
    ("Incline Bench Press", "Chest", "Barbell", "Upper chest focus with bench set to 30-45 degrees."),
    ("Dumbbell Fly", "Chest", "Dumbbell", "Isolation movement for chest stretch and contraction."),
    ("Cable Crossover", "Chest", "Cable", "Constant-tension chest isolation at various angles."),
    ("Push-Up", "Chest", "Bodyweight", "Compound bodyweight push. Can be done anywhere."),

    # Back
    ("Deadlift", "Back", "Barbell", "Full posterior chain compound. The king of lifts."),
    ("Barbell Row", "Back", "Barbell", "Mid-back thickness exercise with overhand grip."),
    ("Pull-Up", "Back", "Bodyweight", "Wide-grip vertical pull for lat width."),
    ("Lat Pulldown", "Back", "Cable", "Machine-assisted vertical pull targeting the lats."),
    ("Seated Cable Row", "Back", "Cable", "Horizontal pull for mid-back thickness."),
    ("Dumbbell Row", "Back", "Dumbbell", "Single-arm row for unilateral back development."),
    ("T-Bar Row", "Back", "Barbell", "Thick-bar row for heavy mid-back loading."),

    # Shoulders
    ("Overhead Press", "Shoulders", "Barbell", "Standing barbell press for overall shoulder mass."),
    ("Lateral Raise", "Shoulders", "Dumbbell", "Isolation for lateral deltoid width."),
    ("Front Raise", "Shoulders", "Dumbbell", "Anterior deltoid isolation."),
    ("Face Pull", "Shoulders", "Cable", "Rear delt and rotator cuff health exercise."),
    ("Arnold Press", "Shoulders", "Dumbbell", "Rotating dumbbell press for full delt stimulation."),

    # Biceps
    ("Barbell Curl", "Biceps", "Barbell", "Standing compound bicep exercise."),
    ("Dumbbell Curl", "Biceps", "Dumbbell", "Standing or seated unilateral bicep work."),
    ("Hammer Curl", "Biceps", "Dumbbell", "Neutral grip curl targeting brachialis and forearms."),
    ("Preacher Curl", "Biceps", "Barbell", "Isolation curl with arm supported on pad."),
    ("Concentration Curl", "Biceps", "Dumbbell", "Focused peak contraction curl."),
    ("Cable Curl", "Biceps", "Cable", "Constant-tension bicep isolation."),

    # Triceps
    ("Tricep Pushdown", "Triceps", "Cable", "Rope or bar pushdown for tricep isolation."),
    ("Skull Crusher", "Triceps", "Barbell", "Lying tricep extension with barbell."),
    ("Dips", "Triceps", "Bodyweight", "Parallel bar compound tricep and chest exercise."),
    ("Close-Grip Bench Press", "Triceps", "Barbell", "Narrow-grip bench shifting emphasis to triceps."),
    ("Overhead Tricep Extension", "Triceps", "Dumbbell", "Standing or seated overhead extension."),

    # Legs
    ("Squat", "Legs", "Barbell", "The king of leg exercises. Full lower body compound."),
    ("Leg Press", "Legs", "Machine", "Machine-based heavy leg compound."),
    ("Leg Extension", "Legs", "Machine", "Quad isolation on machine."),
    ("Romanian Deadlift", "Legs", "Barbell", "Hip-hinge hamstring and glute focus."),
    ("Walking Lunge", "Legs", "Barbell", "Unilateral leg movement with barbell."),
    ("Leg Curl", "Legs", "Machine", "Hamstring isolation on machine."),
    ("Goblet Squat", "Legs", "Dumbbell", "Front-loaded squat with dumbbell."),

    # Calves
    ("Standing Calf Raise", "Calves", "Machine", "Standing machine calf raise for gastrocnemius."),
    ("Seated Calf Raise", "Calves", "Machine", "Seated calf raise targeting soleus."),

    # Abs
    ("Cable Crunch", "Abs", "Cable", "Kneeling cable crunch for abs under load."),
    ("Hanging Leg Raise", "Abs", "Bodyweight", "Hanging knee or leg raise for lower abs."),
    ("Plank", "Abs", "Bodyweight", "Isometric core stability hold."),
    ("Ab Wheel Rollout", "Abs", "Bodyweight", "Dynamic ab wheel extension for core strength."),

    # Forearms
    ("Wrist Curl", "Forearms", "Dumbbell", "Seated wrist curl for forearm flexion."),
    ("Reverse Wrist Curl", "Forearms", "Dumbbell", "Reverse grip wrist curl for extensors."),
]


async def seed_exercises() -> None:
    """Seed the database with a standard set of exercises.

    This is idempotent — it checks whether exercises already exist before
    inserting, so restarting the server will not create duplicates.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Exercise)
        result = await session.execute(stmt)
        existing = result.scalars().all()

        if len(existing) > 0:
            return  # Already seeded

        for name, muscle_group, equipment, description in SEED_EXERCISES:
            exercise = Exercise(
                name=name,
                primary_muscle_group=muscle_group,
                equipment=equipment,
                description=description,
            )
            session.add(exercise)

        await session.commit()
