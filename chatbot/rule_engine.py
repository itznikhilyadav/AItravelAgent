def get_rule_based_response(message: str) -> str:
    msg = (message or "").lower()

    if "flight" in msg or "book" in msg and "flight" in msg:
        return "Flight booking: here are some flight options and next steps."

    if "hotel" in msg or "stay" in msg or "accommodation" in msg:
        return "Hotel search: here are some hotel options and what to consider."

    return "Travel assistance: tell me what you need (flights, hotels, food, itinerary)."

