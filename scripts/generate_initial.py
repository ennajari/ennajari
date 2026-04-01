#!/usr/bin/env python3
"""Generate an initial banner without needing the weather API (uses defaults)."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from generate_banner import generate_svg, get_time_period
from datetime import datetime
from zoneinfo import ZoneInfo

# Fake weather data for initial generation
mock_weather = {
    "weather": [{"main": "Clear", "description": "clear sky"}],
    "main": {"temp": 38, "feels_like": 32},
}

now = datetime.now(ZoneInfo("America/New_York"))
svg = generate_svg(mock_weather, now)

out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "banner.svg")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    f.write(svg)

print(f"Generated initial banner for {get_time_period(now.hour)} ({now.strftime('%I:%M %p')} ET)")
