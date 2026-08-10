"""Exercise 2: Space Crew Management.

Master nested Pydantic models and complex data relationships by
validating mission crews against safety and launch requirements.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


EXPERIENCED_YEARS = 5
LONG_MISSION_DAYS = 365
EXPERIENCED_CREW_RATIO = 0.5


class Rank(str, Enum):
    """Crew ranks recognised across the observatory."""

    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    """Individual crew member flying on a space mission."""

    member_id: str = Field(
        min_length=3,
        max_length=10,
        description="Crew identifier, 3 to 10 characters",
    )
    name: str = Field(
        min_length=2,
        max_length=50,
        description="Crew member name, 2 to 50 characters",
    )
    rank: Rank = Field(description="Crew rank of the member")
    age: int = Field(
        ge=18, le=80, description="Member age in years, 18 to 80"
    )
    specialization: str = Field(
        min_length=3,
        max_length=30,
        description="Area of expertise, 3 to 30 characters",
    )
    years_experience: int = Field(
        ge=0, le=50, description="Years of experience, 0 to 50"
    )
    is_active: bool = Field(
        default=True, description="Active duty status, defaults to True"
    )


class SpaceMission(BaseModel):
    """A space mission together with its validated crew roster."""

    mission_id: str = Field(
        min_length=5,
        max_length=15,
        description="Mission identifier, 5 to 15 characters",
    )
    mission_name: str = Field(
        min_length=3,
        max_length=100,
        description="Mission name, 3 to 100 characters",
    )
    destination: str = Field(
        min_length=3,
        max_length=50,
        description="Mission destination, 3 to 50 characters",
    )
    launch_date: datetime = Field(description="Planned launch moment")
    duration_days: int = Field(
        ge=1, le=3650, description="Mission duration in days, max 10 years"
    )
    crew: list[CrewMember] = Field(
        min_length=1,
        max_length=12,
        description="Crew roster, 1 to 12 members",
    )
    mission_status: str = Field(
        default="planned", description="Current mission status"
    )
    budget_millions: float = Field(
        ge=1.0,
        le=10000.0,
        description="Budget in millions of dollars, 1 to 10000",
    )

    @model_validator(mode="after")
    def enforce_mission_rules(self) -> "SpaceMission":
        """Apply mission safety requirements across the whole model."""
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')
        has_leader = any(
            member.rank in (Rank.commander, Rank.captain)
            for member in self.crew
        )
        if not has_leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )
        if not all(member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")
        needs_experienced_crew = self.duration_days > LONG_MISSION_DAYS
        if needs_experienced_crew and self._experienced_ratio() < (
                EXPERIENCED_CREW_RATIO):
            raise ValueError(
                "Long missions (> 365 days) need 50% experienced crew "
                "(5+ years)"
            )
        return self

    def _experienced_ratio(self) -> float:
        """Fraction of crew with the required seniority level."""
        experienced_count = sum(
            1
            for member in self.crew
            if member.years_experience >= EXPERIENCED_YEARS
        )
        return experienced_count / len(self.crew)


def display_mission(mission: SpaceMission) -> None:
    """Print a formatted summary of a mission and its crew."""
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"- {member.name} ({member.rank.value}) - {member.specialization}"
        )


def main() -> None:
    """Run the Exercise 2 demonstration."""
    separator = "=" * 42
    print("Space Mission Crew Validation")
    print(separator)
    print("Valid mission created:")
    valid_crew = [
        CrewMember(
            member_id="CRW001",
            name="Sarah Connor",
            rank="commander",
            age=42,
            specialization="Mission Command",
            years_experience=18,
        ),
        CrewMember(
            member_id="CRW002",
            name="John Smith",
            rank="lieutenant",
            age=29,
            specialization="Navigation",
            years_experience=7,
        ),
        CrewMember(
            member_id="CRW003",
            name="Alice Johnson",
            rank="officer",
            age=34,
            specialization="Engineering",
            years_experience=9,
        ),
    ]
    valid_mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date="2024-11-15T08:00:00",
        duration_days=900,
        crew=valid_crew,
        budget_millions=2500.0,
    )
    display_mission(valid_mission)
    print(separator)
    print("Expected validation error:")
    leaderless_crew = [
        CrewMember(
            member_id="CRW010",
            name="Mark Watney",
            rank="officer",
            age=31,
            specialization="Botany",
            years_experience=6,
        ),
    ]
    try:
        SpaceMission(
            mission_id="M2024_BASE",
            mission_name="Deep Space Outpost",
            destination="Moon",
            launch_date="2024-12-01T08:00:00",
            duration_days=180,
            crew=leaderless_crew,
            budget_millions=500.0,
        )
    except ValidationError as error:
        for issue in error.errors():
            print(issue["msg"])
    print()


if __name__ == "__main__":
    main()
