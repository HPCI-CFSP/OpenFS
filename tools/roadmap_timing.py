"""Validate source-supported milestone windows in inclusive calendar quarters."""

from typing import Any


def quarter_ordinal(year: int, quarter: str) -> int:
    if type(year) is not int or year < 2020 or not isinstance(quarter, str) or quarter not in {"Q1", "Q2", "Q3", "Q4"}:
        raise ValueError("invalid roadmap year or quarter")
    return year * 4 + int(quarter[1]) - 1


def milestone_quarter_window(milestone: dict[str, Any]) -> tuple[int, int] | None:
    """A window expresses timing uncertainty, never event duration."""
    precision = milestone["timing_precision"]
    year, quarter = milestone["year"], milestone["quarter"]
    half = milestone.get("half")
    end_year, end_quarter = milestone.get("end_year"), milestone.get("end_quarter")
    if precision != "quarter-range" and (end_year is not None or end_quarter is not None):
        raise ValueError("range endpoints require quarter-range timing precision")
    if precision != "half-year" and half is not None:
        raise ValueError("unexpected half-year value")
    if precision == "undated":
        if year is not None or quarter is not None:
            raise ValueError("undated milestone has dated fields")
        return None
    if precision in {"quarter", "quarter-range"}:
        start = quarter_ordinal(year, quarter)
        end = quarter_ordinal(end_year, end_quarter) if precision == "quarter-range" else start
        if end < start:
            raise ValueError("reversed roadmap timing window")
        return start, end
    if quarter is not None:
        raise ValueError("quarter has inconsistent timing precision")
    if precision == "half-year":
        if not isinstance(half, str) or half not in {"H1", "H2"}:
            raise ValueError("half-year roadmap milestone requires H1 or H2")
        return (quarter_ordinal(year, "Q1"), quarter_ordinal(year, "Q2")) if half == "H1" else (
            quarter_ordinal(year, "Q3"), quarter_ordinal(year, "Q4"))
    if precision == "year":
        return quarter_ordinal(year, "Q1"), quarter_ordinal(year, "Q4")
    raise ValueError("invalid roadmap timing precision or half-year")
