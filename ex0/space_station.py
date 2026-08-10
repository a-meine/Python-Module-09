"""Exercise 0: Space Station Data.

Learn basic Pydantic model creation with BaseModel and Field validation
by modelling the vital telemetry reported by galactic space stations.

https://pydantic.dev/docs/validation/latest/concepts/models/

https://pydantic.dev/docs/validation/latest/concepts/fields/

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    """Validated telemetry record reported by a space station."""

    station_id: str = Field(
        min_length=3,
        max_length=10,
        description="Station identifier, 3 to 10 characters",
    )
    name: str = Field(
        min_length=1,
        max_length=50,
        description="Official station name, 1 to 50 characters",
    )
    crew_size: int = Field(
        ge=1, le=20, description="Number of crew members aboard"
    )
    power_level: float = Field(
        ge=0.0, le=100.0, description="Power output as a percentage"
    )
    oxygen_level: float = Field(
        ge=0.0, le=100.0, description="Oxygen levels as a percentage"
    )
    last_maintenance: datetime = Field(
        description="Date and time of the last maintenance"
    )
    is_operational: bool = Field(
        default=True, description="Operational status, defaults to True"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional maintenance notes, max 200 characters",
    )


def display_station(station: SpaceStation) -> None:
    """Print a formatted summary of a single space station."""
    status = "Operational" if station.is_operational else "Non-operational"
    print(f"ID: {station.station_id}")
    print(f"Name: {station.name}")
    print(f"Crew: {station.crew_size} people")
    print(f"Power: {station.power_level}%")
    print(f"Oxygen: {station.oxygen_level}%")
    print(f"Last maintenance: {station.last_maintenance:%Y-%m-%d %H:%M}")
    print(f"Status: {status}")
    if station.notes:
        print(f"Notes: {station.notes}")


def main() -> None:
    """Run the demonstration."""
    separator = "=" * 40
    print("Space Station Data Validation")
    print(separator)
    print("Valid station created:")
    valid_station = SpaceStation(
        station_id="ISS001",
        name="International Space Station",
        crew_size=6,
        power_level=85.5,
        oxygen_level=92.3,
        last_maintenance="2024-06-15T10:30:00",
        notes="Scheduled hull inspection completed.",
    )
    display_station(valid_station)
    print(separator)
    print("Expected validation error:")
    try:
        SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=30,
            power_level=100,
            oxygen_level="sdf",
            last_maintenance="2024-06-15T10:30:00",
        )
    except ValidationError as error:
        for issue in error.errors():
            print(issue["msg"])
    print()


if __name__ == "__main__":
    main()
