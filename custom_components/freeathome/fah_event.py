"""Helpers for Free@Home Home Assistant events."""

DIMMING_STATUS_OPTIONS = [
    "pressed_up",
    "pressed_down",
    "held_up",
    "held_down",
]


def create_event_data(name, serialnumber, unique_id, event):
    """Build a freeathome_event payload from a decoded datapoint event."""
    event_data = {
        "name": name,
        "serialnumber": serialnumber,
        "unique_id": unique_id,
        "command": event["command"],
    }

    if "state" in event:
        event_data["state"] = event["state"]
    if "direction" in event:
        event_data["direction"] = event["direction"]

    return event_data


def dimming_status_from_event(event):
    """Return one of the four visible dimming actions for an event."""
    if event.get("command") == "pressed":
        if event.get("state") is True:
            return "pressed_up"
        if event.get("state") is False:
            return "pressed_down"

    if event.get("command") == "dim_start":
        if event.get("direction") == "up":
            return "held_up"
        if event.get("direction") == "down":
            return "held_down"

    return None
