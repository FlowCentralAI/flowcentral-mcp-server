"""Celeste's system prompt builder.

Assembles the final system prompt from the base prompt template
plus bot-specific interaction context.
"""

from datetime import datetime
from typing import List


def build_interaction_context(
    caller: str,
    prior_interaction_count: int,
    last_interaction_at: str,
    first_name: str = "",
) -> str:
    """Build a bot-specific interaction note."""
    if not caller:
        return ""

    display_name = first_name or caller

    hour = datetime.now().hour
    late_night = hour >= 22 or hour < 5
    morning = 5 <= hour < 11

    if prior_interaction_count <= 0:
        if late_night:
            interaction_note = f"This is your first time meeting {display_name}. It's late — offer something warm or a nightcap. Keep the tone quiet and welcoming."
        elif morning:
            interaction_note = f"This is your first time meeting {display_name}. Morning arrival — offer coffee or tea. Make them feel expected, even if they weren't."
        else:
            interaction_note = f"This is your first time meeting {display_name}. Welcome them graciously and ask what they'd like to drink."
    elif prior_interaction_count == 1:
        interaction_note = f"You've met {display_name} once before. Welcome them back — you're still learning their preferences but you remember the face."
    elif prior_interaction_count <= 5:
        interaction_note = f"You've served {display_name} {prior_interaction_count} times now. You're getting to know their preferences. Offer their usual or suggest something new."
    else:
        interaction_note = f"{display_name} is a regular — {prior_interaction_count} visits. You know exactly what they like. Have their drink ready before they ask."

    if last_interaction_at and prior_interaction_count > 0:
        try:
            elapsed = datetime.now() - datetime.fromisoformat(last_interaction_at)
            days = elapsed.days
            hours = elapsed.seconds // 3600
            if days > 30:
                interaction_note += f" It has been about {days // 30} month(s) since their last visit — acknowledge it's been a while. Perhaps their tastes have changed."
            elif days > 0:
                interaction_note += f" It has been about {days} day(s) since their last visit."
            elif hours > 0:
                interaction_note += f" Their last visit was about {hours} hour(s) ago — perhaps a refill or something different."
            else:
                interaction_note += " They were just here moments ago. Probably coming back for seconds."
        except (ValueError, TypeError):
            pass

    return interaction_note


def build_system_prompt(
    base_prompt: str,
    caller: str = "",
    prior_interaction_count: int = 0,
    last_interaction_at: str = "",
    first_name: str = ""
) -> str:
    parts: List[str] = [base_prompt]
    parts.append(f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    interaction_note = build_interaction_context(
        caller,
        prior_interaction_count,
        last_interaction_at,
        first_name,
    )
    if interaction_note:
        parts.append(interaction_note)

    return "\n\n".join(parts)
