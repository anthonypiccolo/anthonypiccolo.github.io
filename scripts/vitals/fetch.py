"""Pull the latest numbers from Garmin Connect for the site.

    python scripts/vitals/fetch.py <data-dir>

<data-dir> holds tokens.enc and receives vitals.json (home page card) and
running.json (/running/). Run every ~15 minutes by .github/workflows/vitals.yml.
Refreshed session tokens are written back even if some of the data calls fail.
Only the fields listed here are published: route outlines are anonymised
shapes (see routes.py), never coordinates.
"""

import hashlib
import json
import logging
import sys
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Any

from garminconnect import Garmin

from routes import decode_polyline, outline
from vault import load_key, read_tokens, write_tokens

log = logging.getLogger("vitals")

RUN_TYPES = {"running", "treadmill_running", "trail_running", "track_running", "indoor_running"}
SERIES_BUCKET_MINUTES = 10
RECENT_RUNS = 8


def iso(ms: int | float | None) -> str | None:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, UTC).isoformat(timespec="seconds")


def heart_rate(garmin: Garmin, today: str, yesterday: str) -> dict[str, Any]:
    days = [garmin.get_heart_rates(yesterday), garmin.get_heart_rates(today)]
    samples = sorted(
        (ts, bpm)
        for day in days
        for ts, bpm in (day.get("heartRateValues") or [])
        if bpm is not None
    )
    cutoff = samples[-1][0] - 24 * 3600 * 1000 if samples else 0
    buckets: dict[int, list[int]] = {}
    for ts, bpm in samples:
        if ts >= cutoff:
            buckets.setdefault(ts // (SERIES_BUCKET_MINUTES * 60_000), []).append(bpm)
    series = [
        [key * SERIES_BUCKET_MINUTES * 60_000, round(mean(values))]
        for key, values in sorted(buckets.items())
    ]
    latest = samples[-1] if samples else (None, None)
    return {
        "latest": latest[1],
        "at": iso(latest[0]),
        "resting": days[1].get("restingHeartRate") or days[0].get("restingHeartRate"),
        "series": series,
    }


def summary(garmin: Garmin, today: str, yesterday: str) -> dict[str, Any]:
    # Until the watch syncs after midnight, today's summary is empty — show yesterday's.
    s = garmin.get_user_summary(today)
    if s.get("totalSteps") is None:
        s = garmin.get_user_summary(yesterday)
    stress = s.get("averageStressLevel")
    return {
        "isToday": s.get("calendarDate") == today,
        "bodyBattery": s.get("bodyBatteryMostRecentValue"),
        "stress": stress if stress is not None and stress >= 0 else None,
        "steps": s.get("totalSteps"),
        "stepGoal": s.get("dailyStepGoal"),
    }


def sleep(garmin: Garmin, today: str, yesterday: str) -> dict[str, Any]:
    for cdate in (today, yesterday):
        dto = garmin.get_sleep_data(cdate).get("dailySleepDTO") or {}
        if dto.get("sleepTimeSeconds"):
            score = ((dto.get("sleepScores") or {}).get("overall") or {}).get("value")
            return {"score": score, "seconds": dto["sleepTimeSeconds"]}
    return {"score": None, "seconds": None}


def last_sync(garmin: Garmin) -> str | None:
    ts = garmin.get_sync_timestamp()  # GMT, e.g. "2026-10-22T07:48:21.994"
    return datetime.fromisoformat(ts).replace(tzinfo=UTC).isoformat(timespec="seconds") if ts else None


def vo2max(garmin: Garmin, today: str) -> float | None:
    generic = (garmin.get_max_metrics_latest(today) or {}).get("generic") or {}
    return generic.get("vo2MaxPreciseValue") or generic.get("vo2MaxValue")


def running(garmin: Garmin, now: datetime) -> dict[str, Any]:
    runs = [
        a for a in garmin.get_activities(0, 40)
        if (a.get("activityType") or {}).get("typeKey") in RUN_TYPES
    ]
    week_start = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
    week_m = sum(a.get("distance") or 0 for a in runs if a["startTimeLocal"] >= week_start)
    last = runs[0] if runs else None
    return {
        "weekKm": round(week_m / 1000, 1),
        "lastRun": last and {
            "date": last["startTimeLocal"][:10],
            "distanceKm": round((last.get("distance") or 0) / 1000, 2),
            "durationSec": round(last.get("duration") or 0),
            "avgHr": round(last["averageHR"]) if last.get("averageHR") else None,
        },
    }


def _key(activity: dict[str, Any]) -> str:
    """Stable, non-reversible handle for an activity (used only for caching)."""
    return hashlib.sha256(str(activity["activityId"]).encode()).hexdigest()[:12]


def _route(garmin: Garmin, activity_id: int) -> str | None:
    details = garmin.get_activity_details(str(activity_id), maxchart=1, maxpoly=1500)
    track = (details.get("geoPolylineDTO") or {}).get("polyline") or []
    points = [(p.get("lat"), p.get("lon")) for p in track]
    if not points:
        encoded = (garmin.get_activity_polyline(activity_id) or {}).get("gPolyline")
        points = decode_polyline(encoded) if isinstance(encoded, str) else []
    return outline(points) if len(points) > 1 else None


def running_page(garmin: Garmin, now: datetime, previous: dict[str, Any] | None) -> dict[str, Any]:
    first_week = (now - timedelta(days=now.weekday(), weeks=51)).date()
    runs = garmin.get_activities_by_date(first_week.isoformat(), now.strftime("%Y-%m-%d"), "running")
    runs.sort(key=lambda a: a["startTimeLocal"], reverse=True)

    weeks: dict[date, float] = {first_week + timedelta(weeks=i): 0.0 for i in range(52)}
    year = {"year": now.year, "km": 0.0, "runs": 0, "longestKm": 0.0}
    for run in runs:
        day = date.fromisoformat(run["startTimeLocal"][:10])
        km = (run.get("distance") or 0) / 1000
        monday = day - timedelta(days=day.weekday())
        if monday in weeks:
            weeks[monday] += km
        if day.year == now.year:
            year["km"] += km
            year["runs"] += 1
            year["longestKm"] = max(year["longestKm"], km)

    cached_routes = {r["key"]: r.get("route") for r in (previous or {}).get("recent", [])}
    recent = []
    for run in runs[:RECENT_RUNS]:
        key = _key(run)
        if key not in cached_routes:
            try:
                cached_routes[key] = _route(garmin, run["activityId"])
            except Exception as e:
                log.warning("route for a run failed: %s", e)
                cached_routes[key] = None
        recent.append({
            "key": key,
            "date": run["startTimeLocal"][:10],
            "type": (run.get("activityType") or {}).get("typeKey"),
            "distanceKm": round((run.get("distance") or 0) / 1000, 2),
            "durationSec": round(run.get("duration") or 0),
            "avgHr": round(run["averageHR"]) if run.get("averageHR") else None,
            "elevationGainM": round(run["elevationGain"]) if run.get("elevationGain") else None,
            "route": cached_routes[key],
        })

    return {
        "updated": datetime.now(UTC).isoformat(timespec="seconds"),
        "asOf": now.strftime("%Y-%m-%d"),
        "year": {k: round(v, 1) if isinstance(v, float) else v for k, v in year.items()},
        "weeks": [[monday.isoformat(), round(km, 1)] for monday, km in weeks.items()],
        "recent": recent,
    }


def main(data_dir: Path) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    tokens_path = data_dir / "tokens.enc"
    out_path = data_dir / "vitals.json"
    running_path = data_dir / "running.json"
    key = load_key()
    garmin = Garmin()
    garmin.login(tokenstore=read_tokens(tokens_path, key))

    now = garmin.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    vitals: dict[str, Any] = {"updated": datetime.now(UTC).isoformat(timespec="seconds")}
    sections = {
        "heartRate": lambda: heart_rate(garmin, today, yesterday),
        "lastSync": lambda: last_sync(garmin),
        "day": lambda: summary(garmin, today, yesterday),
        "sleep": lambda: sleep(garmin, today, yesterday),
        "vo2max": lambda: vo2max(garmin, today),
        "running": lambda: running(garmin, now),
    }
    failures = 0
    try:
        for name, fetch in sections.items():
            try:
                vitals[name] = fetch()
            except Exception as e:  # one flaky endpoint shouldn't blank the whole card
                failures += 1
                log.warning("%s failed: %s", name, e)
                vitals[name] = None
        if failures < len(sections):
            out_path.write_text(json.dumps(vitals, separators=(",", ":")) + "\n")
            log.info("wrote %s (%d section(s) failed)", out_path, failures)

        # The running page only changes when there's a new run (or a new day for the
        # weekly chart), so skip the heavier calls otherwise.
        try:
            previous = json.loads(running_path.read_text()) if running_path.exists() else None
            newest = (garmin.get_activities(0, 1, "running") or [None])[0]
            previous_newest = ((previous or {}).get("recent") or [{}])[0].get("key")
            if (
                previous is None
                or previous.get("asOf") != today
                or (newest and _key(newest) != previous_newest)
            ):
                page = running_page(garmin, now, previous)
                running_path.write_text(json.dumps(page, separators=(",", ":")) + "\n")
                log.info("wrote %s", running_path)
        except Exception as e:
            log.warning("running page failed: %s", e)
    finally:
        # Tokens may have been refreshed (and the old refresh token revoked) — always persist.
        write_tokens(tokens_path, key, garmin.client.dumps())

    if failures == len(sections):
        log.error("every vitals section failed")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
