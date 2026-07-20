import json
import os
import requests

from config import CITY, LAT, LNG, EXPERIENCE, MOVIE_KEYWORD

URL = "https://api3.pvrcinemas.com/api/v1/booking/content/mshowtimes"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "appversion": "1.0",
    "chain": "PVR",
    "city": CITY,
    "content-type": "application/json",
    "country": "INDIA",
    "origin": "https://www.pvrcinemas.com",
    "platform": "WEBSITE",
    "user-agent": "Mozilla/5.0",
}

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")


def _load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def _fetch(dated="NA"):
    payload = {
        "city": CITY,
        "lat": LAT,
        "lng": LNG,
        "dated": dated,
        "experience": EXPERIENCE,
    }
    r = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def _extract_sessions(data):
    """
    Pull out every show for movies matching MOVIE_KEYWORD, keyed by sessionId.
    Returns { sessionId: {theatre, screen, showDate, showTime, status} }
    """
    sessions = {}
    output = data.get("output", {})
    for entry in output.get("showTimeSessions", []):
        movie = entry.get("movie", {})
        film_name = movie.get("filmName", "") or movie.get("n", "")
        if MOVIE_KEYWORD.upper() not in film_name.upper():
            continue

        for cinema_session in entry.get("movieCinemaSessions", []):
            cinema = cinema_session.get("cinema", {})
            theatre_name = cinema.get("name", "Unknown theatre")

            for exp_session in cinema_session.get("experienceSessions", []):
                for show in exp_session.get("shows", []):
                    sid = str(show.get("sessionId"))
                    sessions[sid] = {
                        "theatre": theatre_name,
                        "screen": show.get("screenName", ""),
                        "showDate": show.get("showDate", ""),
                        "showTime": show.get("showTime", ""),
                        "status": show.get("statusTxt", ""),
                    }
    return sessions


def _format_summary(sessions):
    if not sessions:
        return f"🎬 No IMAX sessions found for '{MOVIE_KEYWORD}' right now."

    by_theatre = {}
    for s in sessions.values():
        by_theatre.setdefault(s["theatre"], []).append(s)

    lines = [f"🎬 THE ODYSSEY (IMAX) — {CITY} — status check"]
    for theatre, shows in by_theatre.items():
        lines.append(f"\n📍 {theatre}")
        shows.sort(key=lambda s: (s["showDate"], s["showTime"]))
        for s in shows:
            lines.append(f"   {s['showDate']} {s['showTime']} — {s['status']}")
    return "\n".join(lines)


def _format_diff(old_sessions, new_sessions):
    added = [sid for sid in new_sessions if sid not in old_sessions]
    removed = [sid for sid in old_sessions if sid not in new_sessions]
    changed = [
        sid for sid in new_sessions
        if sid in old_sessions and old_sessions[sid]["status"] != new_sessions[sid]["status"]
    ]

    if not added and not removed and not changed:
        return None

    lines = ["🔔 CHANGE DETECTED — THE ODYSSEY (IMAX)"]

    for sid in added:
        s = new_sessions[sid]
        lines.append(f"➕ NEW SHOW: {s['theatre']} — {s['showDate']} {s['showTime']} ({s['status']})")

    for sid in removed:
        s = old_sessions[sid]
        lines.append(f"➖ REMOVED: {s['theatre']} — {s['showDate']} {s['showTime']}")

    for sid in changed:
        old_s = old_sessions[sid]
        new_s = new_sessions[sid]
        lines.append(
            f"🔁 {new_s['theatre']} — {new_s['showDate']} {new_s['showTime']}: "
            f"{old_s['status']} → {new_s['status']}"
        )

    return "\n".join(lines)


def check():
    """
    Called every CHECK_INTERVAL seconds by main.py.
    Always returns a regular status message, plus a change alert (as a
    separate, distinctly-worded message) if anything changed since the
    last run.
    """
    messages = []

    data = _fetch()
    new_sessions = _extract_sessions(data)

    state = _load_state()
    old_sessions = state.get("sessions", {})

    diff_msg = _format_diff(old_sessions, new_sessions)
    if diff_msg:
        messages.append(diff_msg)

    messages.append(_format_summary(new_sessions))

    state["sessions"] = new_sessions
    _save_state(state)

    return messages
