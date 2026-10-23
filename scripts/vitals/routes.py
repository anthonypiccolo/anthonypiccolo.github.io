"""Turn a GPS track into an anonymous outline for the running page.

The output is an SVG path in a 100×100 box: the shape of the run, scaled and
centred, with no coordinates, scale or orientation-to-the-world that would
place it on a map. The first and last TRIM_M metres are dropped as well, so
the outline doesn't draw a line to the front door.
"""

import math
from collections.abc import Sequence

TRIM_M = 250
SIZE = 100
PADDING = 4
TOLERANCE = 0.35  # simplification tolerance, in output units

Point = tuple[float, float]


def decode_polyline(encoded: str, precision: int = 5) -> list[Point]:
    """Decode a Google encoded polyline into (lat, lon) pairs."""
    coords: list[Point] = []
    index = lat = lon = 0
    factor = 10**precision
    while index < len(encoded):
        deltas = []
        for _ in range(2):
            shift = result = 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            deltas.append(~(result >> 1) if result & 1 else result >> 1)
        lat += deltas[0]
        lon += deltas[1]
        coords.append((lat / factor, lon / factor))
    return coords


def _metres(a: Point, b: Point) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def _trim(points: Sequence[Point], metres: float) -> list[Point]:
    def first_beyond(seq: Sequence[Point]) -> int:
        travelled = 0.0
        for i in range(1, len(seq)):
            travelled += _metres(seq[i - 1], seq[i])
            if travelled >= metres:
                return i
        return len(seq)

    start = first_beyond(points)
    end = len(points) - first_beyond(points[::-1])
    return list(points[start:end + 1])


def _simplify(points: list[Point], tolerance: float) -> list[Point]:
    """Ramer–Douglas–Peucker, iterative."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        lo, hi = stack.pop()
        (x1, y1), (x2, y2) = points[lo], points[hi]
        length = math.hypot(x2 - x1, y2 - y1) or 1e-9
        best, best_i = 0.0, -1
        for i in range(lo + 1, hi):
            x0, y0 = points[i]
            d = abs((x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)) / length
            if d > best:
                best, best_i = d, i
        if best > tolerance:
            keep[best_i] = True
            stack += [(lo, best_i), (best_i, hi)]
    return [p for p, k in zip(points, keep) if k]


def outline(points: Sequence[Point]) -> str | None:
    """SVG path data for a (lat, lon) track, or None if there's nothing to draw."""
    points = [p for p in points if p[0] is not None and p[1] is not None]
    total = sum(_metres(points[i - 1], points[i]) for i in range(1, len(points)))
    # Short tracks keep at least their middle 60%.
    points = _trim(points, min(TRIM_M, total * 0.2))
    if len(points) < 2:
        return None

    mid_lat = math.radians(sum(lat for lat, _ in points) / len(points))
    xy = [(lon * math.cos(mid_lat), -lat) for lat, lon in points]
    xs, ys = [x for x, _ in xy], [y for _, y in xy]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    scale = (SIZE - 2 * PADDING) / span
    off_x = (SIZE - (max(xs) - min(xs)) * scale) / 2
    off_y = (SIZE - (max(ys) - min(ys)) * scale) / 2
    scaled = [((x - min(xs)) * scale + off_x, (y - min(ys)) * scale + off_y) for x, y in xy]

    simple = _simplify(scaled, TOLERANCE)
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in simple)
