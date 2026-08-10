"""Exercise 1: Alien Contact Logs.

Master custom validation using @model_validator(mode="after") to enforce
complex business rules on sensitive alien contact reports.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Supported kinds of alien contact reports."""

    radio = "radio"
    visual = "visual"
    physical = "physical"
    telepathic = "telepathic"


class AlienContact(BaseModel):
    """Validated report describing a single alien contact event."""

    contact_id: str = Field(
        min_length=5,
        max_length=15,
        description="Report identifier, 5 to 15 characters",
    )
    timestamp: datetime = Field(description="Moment the contact occurred")
    location: str = Field(
        min_length=3,
        max_length=100,
        description="Where the contact was reported, 3 to 100 characters",
    )
    contact_type: ContactType = Field(description="Kind of contact report")
    signal_strength: float = Field(
        ge=0.0, le=10.0, description="Signal strength on a 0-10 scale"
    )
    duration_minutes: int = Field(
        ge=1, le=1440, description="Contact duration in minutes, max 24h"
    )
    witness_count: int = Field(
        ge=1, le=100, description="Number of witnesses, 1 to 100"
    )
    message_received: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional decoded message, max 500 characters",
    )
    is_verified: bool = Field(
        default=False, description="Whether the report was verified"
    )

    @model_validator(mode="after")
    def enforce_contact_rules(self) -> "AlienContact":
        """Apply the observatory's business rules to the whole report."""
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')
        if self.contact_type == ContactType.physical and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")
        if (
            self.contact_type == ContactType.telepathic
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (> 7.0) should include received messages"
            )
        return self


def display_contact(contact: AlienContact) -> None:
    """Print a formatted summary of a single alien contact report."""
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    message = contact.message_received or "No message recorded"
    print(f"Message: '{message}'")


def main() -> None:
    """Run the Exercise 1 demonstration."""
    separator = "=" * 38
    print("Alien Contact Log Validation")
    print(separator)
    print("Valid contact report:")
    valid_contact = AlienContact.model_validate(
        {
            "contact_id": "AC_2024_001",
            "timestamp": "2024-03-12T21:05:00",
            "location": "Area 51, Nevada",
            "contact_type": "radio",
            "signal_strength": 8.5,
            "duration_minutes": 45,
            "witness_count": 5,
            "message_received": "Greetings from Zeta Reticuli",
        }
    )
    display_contact(valid_contact)
    print(separator)
    print("Expected validation error:")
    try:
        AlienContact.model_validate(
            {
                "contact_id": "AC_2024_002",
                "timestamp": "2024-03-12T22:00:00",
                "location": "Zeta Reticuli Grid",
                "contact_type": "telepathic",
                "signal_strength": 9.1,
                "duration_minutes": 12,
                "witness_count": 2,
            }
        )
    except ValidationError as error:
        for issue in error.errors():
            print(issue["msg"].removeprefix("Value error, "))
    print()


if __name__ == "__main__":
    main()
