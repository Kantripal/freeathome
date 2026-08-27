"""Helpers for Free@Home Home Assistant events."""


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
