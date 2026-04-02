#!/usr/bin/env python3
"""Generate a dynamic Casablanca skyline SVG based on current weather and time.

Features a multi-layered 3D skyline with recognizable Casablanca landmarks,
atmospheric perspective, and dynamic weather/lighting.
"""

import os
import random
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

WIDTH = 1200
HEIGHT = 300
TIMEZONE = "Africa/Casablanca"
LAT = 33.5731
LON = -7.5898
WATER_Y = 255  # where the horizon starts

# WMO weather codes → (main category, description)
WMO_CODES = {
    0: ("Clear", "clear sky"),
    1: ("Clear", "mainly clear"),
    2: ("Clouds", "partly cloudy"),
    3: ("Clouds", "overcast"),
    45: ("Fog", "fog"),
    48: ("Fog", "depositing rime fog"),
    51: ("Drizzle", "light drizzle"),
    53: ("Drizzle", "moderate drizzle"),
    55: ("Drizzle", "dense drizzle"),
    56: ("Drizzle", "freezing drizzle"),
    57: ("Drizzle", "dense freezing drizzle"),
    61: ("Rain", "slight rain"),
    63: ("Rain", "moderate rain"),
    65: ("Rain", "heavy rain"),
    66: ("Rain", "freezing rain"),
    67: ("Rain", "heavy freezing rain"),
    71: ("Snow", "slight snow"),
    73: ("Snow", "moderate snow"),
    75: ("Snow", "heavy snow"),
    77: ("Snow", "snow grains"),
    80: ("Rain", "slight rain showers"),
    81: ("Rain", "moderate rain showers"),
    82: ("Rain", "violent rain showers"),
    85: ("Snow", "slight snow showers"),
    86: ("Snow", "heavy snow showers"),
    95: ("Thunderstorm", "thunderstorm"),
    96: ("Thunderstorm", "thunderstorm with slight hail"),
    99: ("Thunderstorm", "thunderstorm with heavy hail"),
}


def get_weather():
    """Fetch current weather from Open-Meteo (free, no API key needed)."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,apparent_temperature,weather_code"
        f"&temperature_unit=celsius"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()["current"]
    code = data["weather_code"]
    main, desc = WMO_CODES.get(code, ("Clear", "clear sky"))
    return {
        "weather": [{"main": main, "description": desc}],
        "main": {
            "temp": data["temperature_2m"],
            "feels_like": data["apparent_temperature"],
        },
    }


def get_time_period(hour):
    if hour < 5 or hour >= 21:
        return "night"
    elif hour < 7:
        return "dawn"
    elif hour < 10:
        return "morning"
    elif hour < 17:
        return "day"
    elif hour < 19:
        return "sunset"
    else:
        return "dusk"


def darken(hex_color, factor):
    r = int(int(hex_color[1:3], 16) * factor)
    g = int(int(hex_color[3:5], 16) * factor)
    b = int(int(hex_color[5:7], 16) * factor)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


def lighten(hex_color, factor):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}"


def sky_gradient(period, weather):
    palettes = {
        "night":   [("#050B18", 0), ("#0B1628", 40), ("#162447", 100)],
        "dawn":    [("#1a1a2e", 0), ("#c0392b", 35), ("#f39c12", 70), ("#ffecd2", 100)],
        "morning": [("#2980b9", 0), ("#5dade2", 50), ("#aed6f1", 100)],
        "day":     [("#1a6fc4", 0), ("#4fb4f7", 40), ("#87CEEB", 100)],
        "sunset":  [("#1a1a2e", 0), ("#c0392b", 30), ("#e67e22", 60), ("#fdebd0", 100)],
        "dusk":    [("#0f0c29", 0), ("#302b63", 50), ("#544a7d", 100)],
    }
    colors = palettes.get(period, palettes["day"])
    if weather in ("Rain", "Thunderstorm", "Drizzle"):
        colors = [(darken(c, 0.5), p) for c, p in colors]
    elif weather == "Clouds":
        colors = [(darken(c, 0.75), p) for c, p in colors]
    elif weather == "Snow":
        colors = [(darken(c, 0.7), p) for c, p in colors]
    return colors


def building_colors(period):
    """Return (base_dark, base_mid, base_light, glass, highlight) for buildings."""
    if period in ("night", "dusk"):
        return ("#0a0e17", "#111827", "#1a2234", "#0d1525", "#1e293b")
    elif period == "dawn":
        return ("#1a1520", "#251e2a", "#2f2535", "#1e1828", "#3d2f45")
    elif period == "sunset":
        return ("#1a1015", "#2a1820", "#35202a", "#201018", "#452838")
    elif period == "morning":
        return ("#1a2a3a", "#253545", "#304050", "#1e2e3e", "#3a4a5a")
    else:  # day
        return ("#1e2d3d", "#2a3a4a", "#354555", "#243444", "#405060")


def render_defs(period, weather_main, gradient_stops):
    """Render all SVG defs: gradients, filters, clip paths."""
    bc = building_colors(period)
    is_night = period in ("night", "dusk", "dawn")

    # Glass reflection color varies by time
    glass_highlight = "#4a6a8a" if not is_night else "#1a2a4a"
    glass_top = "#ffffff" if not is_night else "#3a5a7a"

    # Window glow color
    win_warm = "#ffd166" if is_night else "#ffffff"
    win_cool = "#58A6FF" if is_night else "#e0e8f0"

    return f"""  <defs>
    <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
{gradient_stops}
    </linearGradient>

    <!-- Building face gradients (3D lighting - light from right) -->
    <linearGradient id="bldgFront" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bc[2]}"/>
      <stop offset="100%" stop-color="{bc[0]}"/>
    </linearGradient>
    <linearGradient id="bldgLeft" x1="100%" y1="0%" x2="0%" y2="0%">
      <stop offset="0%" stop-color="{bc[1]}"/>
      <stop offset="100%" stop-color="{bc[0]}"/>
    </linearGradient>
    <linearGradient id="bldgRight" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{bc[1]}"/>
      <stop offset="100%" stop-color="{bc[2]}"/>
    </linearGradient>

    <!-- Glass curtain wall gradient -->
    <linearGradient id="glass" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{glass_top}" stop-opacity="0.08"/>
      <stop offset="40%" stop-color="{glass_highlight}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{glass_highlight}" stop-opacity="0.05"/>
    </linearGradient>

    <!-- Atmospheric haze for background layer -->
    <linearGradient id="haze" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="url(#sky)" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="url(#sky)" stop-opacity="0.2"/>
    </linearGradient>

    <!-- Water gradient -->
    <linearGradient id="water" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bc[0]}" stop-opacity="0.6"/>
      <stop offset="50%" stop-color="#0a1628" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#050b14" stop-opacity="0.95"/>
    </linearGradient>

    <!-- City glow (light pollution) -->
    <radialGradient id="cityGlow" cx="50%" cy="85%" r="60%">
      <stop offset="0%" stop-color="{'#58A6FF' if is_night else '#ffecd2'}" stop-opacity="{'0.15' if is_night else '0.08'}"/>
      <stop offset="100%" stop-color="{'#58A6FF' if is_night else '#ffecd2'}" stop-opacity="0"/>
    </radialGradient>

    <!-- Warm window glow -->
    <radialGradient id="winGlow">
      <stop offset="0%" stop-color="{win_warm}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{win_warm}" stop-opacity="0"/>
    </radialGradient>

    <!-- Gaussian blur for reflections -->
    <filter id="waterBlur">
      <feGaussianBlur stdDeviation="2 1"/>
    </filter>
    <filter id="glowSoft">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
    <filter id="glowStrong">
      <feGaussianBlur stdDeviation="6"/>
    </filter>

    <!-- Clip to banner area -->
    <clipPath id="bannerClip">
      <rect width="{WIDTH}" height="{HEIGHT}"/>
    </clipPath>

    <style>
      @keyframes twinkle1 {{ 0%,100% {{ opacity: 0.2; }} 50% {{ opacity: 1; }} }}
      @keyframes twinkle2 {{ 0%,100% {{ opacity: 0.5; }} 50% {{ opacity: 0.9; }} }}
      @keyframes twinkle3 {{ 0%,100% {{ opacity: 0.1; }} 50% {{ opacity: 0.8; }} }}
      @keyframes windowPulse {{ 0%,100% {{ opacity: 0.3; }} 50% {{ opacity: 0.9; }} }}
      @keyframes windowFlicker {{ 0%,45% {{ opacity: 0.8; }} 50% {{ opacity: 0.2; }} 55%,100% {{ opacity: 0.8; }} }}
      @keyframes cloudDrift {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(30px); }} }}
      @keyframes waterShimmer {{ 0%,100% {{ opacity: 0.3; }} 50% {{ opacity: 0.6; }} }}
      @keyframes fadeIn {{ 0% {{ opacity: 0; transform: translateY(5px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
      .s1 {{ animation: twinkle1 3s ease-in-out infinite; }}
      .s2 {{ animation: twinkle2 2.5s ease-in-out infinite 0.8s; }}
      .s3 {{ animation: twinkle3 4s ease-in-out infinite 1.5s; }}
      .s4 {{ animation: twinkle1 3.5s ease-in-out infinite 2s; }}
      .s5 {{ animation: twinkle2 2s ease-in-out infinite 0.3s; }}
      .wp {{ animation: windowPulse 4s ease-in-out infinite; }}
      .wf {{ animation: windowFlicker 8s ease-in-out infinite; }}
      .cloud1 {{ animation: cloudDrift 20s ease-in-out infinite alternate; }}
      .cloud2 {{ animation: cloudDrift 25s ease-in-out infinite alternate-reverse; }}
      .ws {{ animation: waterShimmer 3s ease-in-out infinite; }}
      .name-text {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 48px; font-weight: 700; fill: #FFFFFF;
        filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));
        animation: fadeIn 2s ease-out;
      }}
      .sub-text {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 12px; font-weight: 400; fill: #58A6FF;
        letter-spacing: 6px;
        filter: drop-shadow(0 1px 4px rgba(0,0,0,0.4));
        animation: fadeIn 3s ease-out;
      }}
      .weather-text {{
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        font-size: 10px; fill: #8B949E; letter-spacing: 1.5px;
        filter: drop-shadow(0 1px 2px rgba(0,0,0,0.5));
      }}
    </style>
  </defs>"""


def render_stars(period):
    if period not in ("night", "dusk", "dawn"):
        return ""
    random.seed(42)
    count = {"night": 40, "dusk": 20, "dawn": 12}[period]
    base_op = {"night": 0.8, "dusk": 0.5, "dawn": 0.3}[period]
    lines = []
    for i in range(count):
        x = random.randint(20, WIDTH - 20)
        y = random.randint(5, 140)
        r = round(random.uniform(0.4, 1.8), 1)
        cls = f"s{(i % 5) + 1}"
        lines.append(
            f'  <circle class="{cls}" cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{base_op}"/>'
        )
    return "\n".join(lines)


def render_clouds(weather):
    if weather != "Clouds":
        return ""
    return """  <g opacity="0.25" class="cloud1">
    <ellipse cx="160" cy="50" rx="60" ry="16" fill="#6B7585"/>
    <ellipse cx="200" cy="42" rx="45" ry="14" fill="#7B8595"/>
    <ellipse cx="130" cy="47" rx="35" ry="12" fill="#6B7585"/>
    <ellipse cx="175" cy="38" rx="30" ry="10" fill="#8B959E"/>
  </g>
  <g opacity="0.18" class="cloud2">
    <ellipse cx="780" cy="35" rx="55" ry="14" fill="#6B7585"/>
    <ellipse cx="815" cy="28" rx="40" ry="12" fill="#7B8595"/>
    <ellipse cx="755" cy="32" rx="30" ry="10" fill="#6B7585"/>
  </g>
  <g opacity="0.15" class="cloud1">
    <ellipse cx="1050" cy="55" rx="45" ry="12" fill="#6B7585"/>
    <ellipse cx="1080" cy="49" rx="32" ry="10" fill="#7B8595"/>
  </g>"""


def render_rain():
    random.seed(789)
    lines = []
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        length = random.randint(10, 25)
        delay = round(random.uniform(0, 1.5), 2)
        op = round(random.uniform(0.15, 0.4), 2)
        lines.append(
            f'  <line x1="{x}" y1="{y}" x2="{x - 3}" y2="{y + length}" '
            f'stroke="#58A6FF" stroke-width="0.8" opacity="{op}">'
            f'<animate attributeName="y1" from="-20" to="{HEIGHT}" dur="0.8s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y2" from="{-20 + length}" to="{HEIGHT + length}" dur="0.8s" begin="{delay}s" repeatCount="indefinite"/>'
            f'</line>'
        )
    return "\n".join(lines)


def render_snow():
    random.seed(101)
    lines = []
    for _ in range(35):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        r = round(random.uniform(0.8, 2.5), 1)
        delay = round(random.uniform(0, 3), 2)
        drift = random.randint(-20, 20)
        lines.append(
            f'  <circle cx="{x}" cy="{y}" r="{r}" fill="white" opacity="0.5">'
            f'<animate attributeName="cy" from="-10" to="{HEIGHT + 10}" dur="4s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x};{x + drift};{x}" dur="4s" begin="{delay}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    return "\n".join(lines)


def render_sun_moon(period):
    if period in ("day", "morning"):
        return (
            '  <circle cx="980" cy="55" r="28" fill="#f9d71c" opacity="0.9"/>\n'
            '  <circle cx="980" cy="55" r="40" fill="#f9d71c" opacity="0.1" filter="url(#glowStrong)"/>\n'
            '  <circle cx="980" cy="55" r="55" fill="#f9d71c" opacity="0.04" filter="url(#glowStrong)"/>'
        )
    elif period == "night":
        return (
            '  <circle cx="1000" cy="45" r="16" fill="#e8e8e8" opacity="0.85"/>\n'
            '  <circle cx="993" cy="40" r="14" fill="url(#sky)" opacity="0.8"/>\n'
            '  <circle cx="1000" cy="45" r="25" fill="#e8e8e8" opacity="0.05" filter="url(#glowSoft)"/>'
        )
    elif period in ("sunset", "dawn"):
        color = "#f5a623" if period == "dawn" else "#e74c3c"
        return (
            f'  <circle cx="600" cy="240" r="30" fill="{color}" opacity="0.7"/>\n'
            f'  <circle cx="600" cy="240" r="50" fill="{color}" opacity="0.15" filter="url(#glowStrong)"/>\n'
            f'  <circle cx="600" cy="240" r="80" fill="{color}" opacity="0.05" filter="url(#glowStrong)"/>'
        )
    return ""


# ---------------------------------------------------------------------------
# 3D SKYLINE — Three depth layers with Philly landmarks
# ---------------------------------------------------------------------------

def _building(x, w, top, base, fill, side_fill=None, side_w=4, details=""):
    """Render a building with front face, optional right side for 3D, and details."""
    h = base - top
    parts = [f'  <rect x="{x}" y="{top}" width="{w}" height="{h}" fill="{fill}"/>']
    # Right side face for 3D depth
    if side_fill:
        parts.append(
            f'  <polygon points="{x + w},{top} {x + w + side_w},{top - 3} '
            f'{x + w + side_w},{base - 3} {x + w},{base}" fill="{side_fill}" opacity="0.6"/>'
        )
    # Glass overlay
    parts.append(f'  <rect x="{x}" y="{top}" width="{w}" height="{h}" fill="url(#glass)"/>')
    if details:
        parts.append(details)
    return "\n".join(parts)


def _spire(cx, top, base, w=3):
    """Antenna/spire on top of a building."""
    return f'  <line x1="{cx}" y1="{top}" x2="{cx}" y2="{base}" stroke="#3a4a5a" stroke-width="{w}" stroke-linecap="round"/>'


def _floor_lines(x, w, top, base, spacing=8, color="#ffffff", opacity=0.03):
    """Horizontal floor separator lines for glass buildings."""
    lines = []
    y = top + spacing
    while y < base:
        lines.append(f'  <line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{color}" stroke-width="0.5" opacity="{opacity}"/>')
        y += spacing
    return "\n".join(lines)


def render_skyline_bg(period):
    """Background layer — distant buildings, hazier and lighter."""
    bc = building_colors(period)
    haze_color = lighten(bc[0], 0.15)
    parts = []

    bgs = [
        (20, 35, 215), (60, 28, 222), (95, 22, 228), (125, 30, 218),
        (165, 25, 225), (200, 32, 212), (240, 28, 220), (278, 35, 210),
        (320, 22, 230), (350, 30, 215), (390, 26, 225), (425, 35, 208),
        (465, 28, 218), (500, 32, 222), (540, 25, 228), (575, 30, 215),
        (610, 28, 220), (645, 35, 210), (685, 22, 232), (715, 30, 218),
        (750, 28, 225), (785, 35, 212), (825, 25, 228), (860, 30, 220),
        (900, 28, 225), (935, 35, 215), (975, 22, 230), (1010, 30, 218),
        (1045, 28, 222), (1080, 35, 215), (1120, 25, 228), (1155, 30, 222),
    ]

    for x, w, top in bgs:
        parts.append(f'  <rect x="{x}" y="{top}" width="{w}" height="{WATER_Y - top}" fill="{haze_color}" opacity="0.35"/>')

    return "\n".join(parts)


def render_skyline_mid(period):
    """Midground — medium buildings with some detail."""
    bc = building_colors(period)
    mid = bc[1]
    mid_side = darken(bc[1], 0.7)
    parts = []

    mids = [
        (10, 38, 200, 4), (55, 30, 210, 3), (95, 35, 195, 4),
        (140, 25, 208, 3), (180, 40, 190, 5), (230, 30, 205, 3),
        (275, 35, 198, 4), (320, 28, 212, 3),
        (700, 35, 195, 4), (745, 28, 208, 3), (785, 40, 188, 5),
        (835, 30, 205, 3), (880, 35, 198, 4), (925, 25, 215, 3),
        (960, 38, 200, 4), (1010, 30, 210, 3), (1050, 35, 195, 4),
        (1095, 28, 205, 3), (1130, 32, 200, 4), (1170, 28, 210, 3),
    ]

    for x, w, top, sw in mids:
        parts.append(_building(x, w, top, WATER_Y, mid, mid_side, sw))
        parts.append(_floor_lines(x, w, top, WATER_Y, spacing=10, opacity=0.04))

    return "\n".join(parts)


def render_skyline_fg(period):
    """Foreground — recognizable Marrakech landmarks with full 3D treatment.

    Landmarks (left to right):
    - Koutoubia Mosque (iconic minaret)
    - Bahia Palace
    - Medina walls (low, wide, historic)
    - One Liberty Place (spire, tallest)
    - Two Liberty Place (shorter companion)
    - City Hall (with William Penn statue)
    - Comcast Technology Center (tall, modern)
    - Comcast Center
    - BNY Mellon Center
    - Three Logan Square
    - Various fill buildings
    """
    bc = building_colors(period)
    front = bc[1]
    side = darken(bc[1], 0.65)
    light_front = bc[2]
    dark = bc[0]
    parts = []

    # --- Left side fill buildings ---
    parts.append(_building(0, 32, 218, WATER_Y, front, side, 3))
    parts.append(_building(38, 25, 225, WATER_Y, dark, None))
    parts.append(_building(70, 30, 212, WATER_Y, front, side, 3))

    # --- FMC Tower (distinctive curved/angled top) ---
    parts.append(_building(110, 32, 168, WATER_Y, light_front, side, 5))
    # Angled crown
    parts.append(f'  <polygon points="110,168 126,155 142,168" fill="{light_front}"/>')
    parts.append(f'  <polygon points="142,168 147,165 147,168" fill="{side}" opacity="0.6"/>')
    parts.append(_floor_lines(110, 32, 168, WATER_Y, spacing=7, opacity=0.06))

    # --- Cira Centre (angular glass) ---
    parts.append(_building(155, 36, 158, WATER_Y, front, side, 5))
    # Slanted top
    parts.append(f'  <polygon points="155,158 173,148 191,158" fill="{front}"/>')
    parts.append(f'  <polygon points="191,158 196,155 196,163" fill="{side}" opacity="0.5"/>')
    parts.append(_floor_lines(155, 36, 158, WATER_Y, spacing=6, opacity=0.07))

    # --- 30th Street Station (low, wide, classical) ---
    parts.append(_building(205, 70, 215, WATER_Y, light_front, side, 4))
    # Classical columns suggestion
    for cx in range(212, 270, 10):
        parts.append(f'  <rect x="{cx}" y="218" width="3" height="37" fill="{bc[2]}" opacity="0.15"/>')
    # Cornice
    parts.append(f'  <rect x="203" y="213" width="74" height="3" fill="{bc[2]}"/>')

    # --- Fill buildings before main cluster ---
    parts.append(_building(285, 25, 205, WATER_Y, dark, None))
    parts.append(_building(315, 28, 198, WATER_Y, front, side, 3))

    # ============================================================
    # MAIN CENTER CLUSTER — the signature Philly skyline
    # ============================================================

    # --- BNY Mellon Center ---
    parts.append(_building(355, 35, 165, WATER_Y, front, side, 5))
    parts.append(_floor_lines(355, 35, 165, WATER_Y, spacing=6, opacity=0.06))

    # --- Three Logan Square ---
    parts.append(_building(398, 30, 178, WATER_Y, light_front, side, 4))
    parts.append(_floor_lines(398, 30, 178, WATER_Y, spacing=7, opacity=0.05))

    # --- One Liberty Place (tallest, iconic spire) ---
    parts.append(_building(440, 42, 110, WATER_Y, light_front, side, 6))
    # Stepped crown
    parts.append(f'  <rect x="445" y="105" width="32" height="8" fill="{bc[2]}"/>')
    parts.append(f'  <rect x="450" y="98" width="22" height="10" fill="{bc[2]}"/>')
    parts.append(f'  <rect x="455" y="90" width="12" height="10" fill="{bc[2]}"/>')
    # Spire
    parts.append(_spire(461, 60, 90, 2))
    parts.append(_floor_lines(440, 42, 115, WATER_Y, spacing=5, opacity=0.07))
    # Glass highlight stripe
    parts.append(f'  <rect x="458" y="115" width="2" height="140" fill="#ffffff" opacity="0.04"/>')

    # --- Two Liberty Place (shorter companion) ---
    parts.append(_building(490, 36, 135, WATER_Y, front, side, 5))
    # Stepped crown
    parts.append(f'  <rect x="494" y="130" width="28" height="7" fill="{bc[1]}"/>')
    parts.append(f'  <rect x="498" y="124" width="20" height="8" fill="{bc[1]}"/>')
    parts.append(_spire(508, 105, 124, 2))
    parts.append(_floor_lines(490, 36, 140, WATER_Y, spacing=6, opacity=0.06))

    # --- City Hall (with Penn statue, lower but iconic) ---
    parts.append(_building(540, 55, 185, WATER_Y, bc[2], side, 5))
    # Tower
    parts.append(f'  <rect x="558" y="148" width="18" height="37" fill="{bc[2]}"/>')
    parts.append(f'  <rect x="560" y="145" width="14" height="5" fill="{bc[2]}"/>')
    # Clock face suggestion
    parts.append(f'  <circle cx="567" cy="158" r="4" fill="{bc[2]}" stroke="#3a4a5a" stroke-width="0.5" opacity="0.5"/>')
    # William Penn statue (tiny!)
    parts.append(f'  <rect x="565" y="137" width="4" height="8" fill="{bc[3]}"/>')
    parts.append(f'  <circle cx="567" cy="135" r="2" fill="{bc[3]}"/>')
    # Cornice details
    parts.append(f'  <rect x="538" y="183" width="59" height="3" fill="{bc[2]}" opacity="0.8"/>')

    # --- Comcast Technology Center (2nd tallest, modern glass) ---
    parts.append(_building(610, 38, 95, WATER_Y, light_front, side, 6))
    # Flat modern crown
    parts.append(f'  <rect x="608" y="92" width="42" height="5" fill="{bc[2]}"/>')
    parts.append(_spire(629, 75, 92, 2))
    parts.append(_floor_lines(610, 38, 97, WATER_Y, spacing=5, opacity=0.08))
    # Vertical glass mullion highlights
    parts.append(f'  <rect x="622" y="97" width="1" height="158" fill="#ffffff" opacity="0.03"/>')
    parts.append(f'  <rect x="636" y="97" width="1" height="158" fill="#ffffff" opacity="0.03"/>')

    # --- Comcast Center (tall, modern) ---
    parts.append(_building(658, 35, 125, WATER_Y, front, side, 5))
    parts.append(_floor_lines(658, 35, 125, WATER_Y, spacing=6, opacity=0.06))
    parts.append(f'  <rect x="656" y="122" width="39" height="4" fill="{bc[1]}"/>')

    # ============================================================

    # --- Right side fill buildings ---
    parts.append(_building(705, 30, 188, WATER_Y, dark, side, 3))
    parts.append(_building(742, 28, 195, WATER_Y, front, side, 3))
    parts.append(_building(778, 35, 182, WATER_Y, light_front, side, 4))
    parts.append(_floor_lines(778, 35, 182, WATER_Y, spacing=8, opacity=0.05))

    parts.append(_building(822, 25, 205, WATER_Y, front, None))
    parts.append(_building(855, 30, 198, WATER_Y, dark, side, 3))
    parts.append(_building(895, 28, 210, WATER_Y, front, side, 3))
    parts.append(_building(930, 35, 202, WATER_Y, light_front, side, 4))
    parts.append(_building(975, 25, 215, WATER_Y, dark, None))
    parts.append(_building(1008, 30, 208, WATER_Y, front, side, 3))
    parts.append(_building(1045, 28, 218, WATER_Y, dark, None))
    parts.append(_building(1080, 35, 212, WATER_Y, front, side, 3))
    parts.append(_building(1122, 25, 222, WATER_Y, dark, None))
    parts.append(_building(1155, 30, 218, WATER_Y, front, side, 3))

    return "\n".join(parts)


def render_windows(period):
    """Render lit windows across the skyline, clustered on major buildings."""
    is_night = period in ("night", "dusk", "dawn")
    warm = "#ffd166"
    cool = "#58A6FF"
    white = "#ffffff"
    random.seed(42)

    lines = []

    # Window configs: (building_x, building_w, building_top, building_bottom, cols, rows)
    buildings = [
        # FMC Tower
        (112, 28, 172, 250, 4, 10),
        # Cira Centre
        (158, 32, 162, 250, 5, 11),
        # BNY Mellon
        (358, 31, 170, 250, 4, 10),
        # Three Logan
        (400, 26, 182, 250, 3, 8),
        # One Liberty Place
        (443, 38, 118, 250, 5, 16),
        # Two Liberty Place
        (493, 32, 142, 250, 4, 13),
        # City Hall
        (543, 50, 190, 250, 6, 7),
        # Comcast Tech Center
        (613, 34, 100, 250, 5, 18),
        # Comcast Center
        (661, 31, 130, 250, 4, 14),
        # Right buildings
        (708, 26, 192, 250, 3, 7),
        (780, 31, 186, 250, 4, 8),
        (932, 31, 206, 250, 4, 5),
    ]

    for bx, bw, btop, bbot, cols, rows in buildings:
        margin_x = 3
        margin_y = 4
        usable_w = bw - 2 * margin_x
        usable_h = bbot - btop - 2 * margin_y
        col_sp = usable_w / max(cols, 1)
        row_sp = usable_h / max(rows, 1)
        win_w = max(2, col_sp * 0.5)
        win_h = max(1.5, row_sp * 0.4)

        for r in range(rows):
            for c in range(cols):
                # Skip some windows randomly (not all lit)
                if random.random() < (0.35 if is_night else 0.7):
                    continue
                wx = bx + margin_x + c * col_sp + (col_sp - win_w) / 2
                wy = btop + margin_y + r * row_sp + (row_sp - win_h) / 2

                if is_night:
                    color = warm if random.random() < 0.6 else cool
                    op = round(random.uniform(0.4, 0.9), 2)
                    cls = "wp" if random.random() < 0.3 else ("wf" if random.random() < 0.1 else "")
                else:
                    color = white
                    op = round(random.uniform(0.06, 0.2), 2)
                    cls = ""

                cls_attr = f' class="{cls}"' if cls else ""
                lines.append(
                    f'  <rect{cls_attr} x="{wx:.1f}" y="{wy:.1f}" width="{win_w:.1f}" '
                    f'height="{win_h:.1f}" rx="0.3" fill="{color}" opacity="{op}"/>'
                )

    return "\n".join(lines)


def render_water(period):
    """Render the Schuylkill River with reflections."""
    is_night = period in ("night", "dusk", "dawn")
    parts = []

    # Water base
    parts.append(f'  <rect x="0" y="{WATER_Y}" width="{WIDTH}" height="{HEIGHT - WATER_Y}" fill="url(#water)"/>')

    # Reflection of skyline (blurred, flipped, faded)
    parts.append(f'  <g filter="url(#waterBlur)" opacity="0.12" transform="translate(0,{2 * WATER_Y}) scale(1,-1)">')
    parts.append(f'    <rect x="350" y="95" width="350" height="160" fill="{"#1a2a4a" if is_night else "#2a3a4a"}"/>')
    parts.append(f'  </g>')

    # Water surface highlights / ripples
    random.seed(777)
    ripple_color = "#58A6FF" if is_night else "#8ab4d8"
    for _ in range(20):
        rx = random.randint(0, WIDTH)
        ry = random.randint(WATER_Y + 5, HEIGHT - 5)
        rw = random.randint(15, 60)
        op = round(random.uniform(0.03, 0.12), 2)
        cls = "ws" if random.random() < 0.4 else ""
        cls_attr = f' class="{cls}"' if cls else ""
        parts.append(
            f'  <line{cls_attr} x1="{rx}" y1="{ry}" x2="{rx + rw}" y2="{ry}" '
            f'stroke="{ripple_color}" stroke-width="0.5" opacity="{op}"/>'
        )

    # Light reflections on water from major buildings (vertical streaks)
    if is_night:
        for cx, op in [(461, 0.08), (508, 0.06), (629, 0.09), (567, 0.04), (675, 0.05)]:
            parts.append(
                f'  <rect x="{cx - 2}" y="{WATER_Y}" width="4" height="{HEIGHT - WATER_Y}" '
                f'fill="#ffd166" opacity="{op}" filter="url(#waterBlur)"/>'
            )

    return "\n".join(parts)


def render_atmosphere(period):
    """Atmospheric haze overlay for depth."""
    parts = []
    # Horizon haze band
    if period in ("day", "morning"):
        parts.append(
            f'  <rect x="0" y="180" width="{WIDTH}" height="75" '
            f'fill="#aed6f1" opacity="0.06"/>'
        )
    elif period in ("sunset", "dawn"):
        parts.append(
            f'  <rect x="0" y="180" width="{WIDTH}" height="75" '
            f'fill="#f39c12" opacity="0.05"/>'
        )

    # City glow (light pollution dome)
    parts.append(f'  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="url(#cityGlow)"/>')

    return "\n".join(parts)


def generate_svg(weather_data, now):
    hour = now.hour
    period = get_time_period(hour)
    weather_main = weather_data["weather"][0]["main"]
    weather_desc = weather_data["weather"][0]["description"]
    temp = round(weather_data["main"]["temp"])

    colors = sky_gradient(period, weather_main)
    gradient_stops = "\n".join(
        f'      <stop offset="{pct}%" stop-color="{c}"/>' for c, pct in colors
    )

    weather_fx = ""
    if weather_main in ("Rain", "Drizzle", "Thunderstorm"):
        weather_fx = render_rain()
    elif weather_main == "Snow":
        weather_fx = render_snow()

    clouds = render_clouds(weather_main)
    stars = render_stars(period)
    sun_moon = render_sun_moon(period)
    defs = render_defs(period, weather_main, gradient_stops)

    skyline_bg = render_skyline_bg(period)
    skyline_mid = render_skyline_mid(period)
    skyline_fg = render_skyline_fg(period)
    windows = render_windows(period)
    water = render_water(period)
    atmosphere = render_atmosphere(period)

    time_str = now.strftime("%I:%M %p").lstrip("0")
    degree = "\u00b0"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
{defs}

  <g clip-path="url(#bannerClip)">
  <!-- Sky -->
  <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#sky)"/>

  <!-- Celestial -->
{sun_moon}
{stars}
{clouds}

  <!-- Atmosphere -->
{atmosphere}

  <!-- Skyline layers (back to front) -->
{skyline_bg}
{skyline_mid}
{skyline_fg}

  <!-- Windows -->
{windows}

  <!-- Water -->
{water}

  <!-- Weather effects -->
{weather_fx}

  <!-- Text overlay -->
  <text class="name-text" x="600" y="108" text-anchor="middle">Abdellah Ennajari</text>
  <text class="sub-text" x="600" y="130" text-anchor="middle">CASABLANCA, MAROC</text>
  <text class="weather-text" x="1180" y="16" text-anchor="end">{temp}{degree}C  {weather_desc.title()}</text>
  <text class="weather-text" x="1180" y="30" text-anchor="end">{time_str} GMT+1</text>
  </g>
</svg>"""


def main():
    weather = get_weather()
    now = datetime.now(ZoneInfo(TIMEZONE))
    svg = generate_svg(weather, now)

    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "banner.svg")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Generated banner: {now.strftime('%Y-%m-%d %I:%M %p')} GMT+1")
    print(f"Weather: {weather['weather'][0]['description']}, {round(weather['main']['temp'])}C")
    print(f"Period: {get_time_period(now.hour)}")


if __name__ == "__main__":
    main()
