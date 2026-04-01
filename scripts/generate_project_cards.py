#!/usr/bin/env python3
"""Generate SVG project showcase cards for GitHub profile README.

Each card is a visual representation of the project architecture,
rendered as an SVG with a dark theme matching the profile aesthetic.
"""

import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "projects")

# Card dimensions
W = 580
H = 320
R = 16  # corner radius

# Color palette
BG = "#0D1117"
BG2 = "#161B22"
BG3 = "#1C2333"
BORDER = "#30363D"
ACCENT = "#58A6FF"
ACCENT2 = "#3FB950"
ACCENT3 = "#D2A8FF"
ACCENT4 = "#F78166"
ACCENT5 = "#FF7B72"
TEXT = "#E6EDF3"
TEXT_DIM = "#8B949E"
TEXT_MID = "#C9D1D9"


def card_shell(title, subtitle, tag, tag_color, inner, icon_svg):
    """Wrap inner content in a styled card shell."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{BG}"/>
      <stop offset="100%" stop-color="{BG2}"/>
    </linearGradient>
    <linearGradient id="accent-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{tag_color}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{tag_color}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{tag_color}" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
    <!-- Background -->
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect x="0" y="0" width="{W}" height="1" fill="url(#accent-line)"/>

    <!-- Header -->
    <g transform="translate(24, 28)">
      {icon_svg}
      <text x="32" y="4" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="18" font-weight="700" fill="{TEXT}">{title}</text>
      <text x="32" y="22" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="11" fill="{TEXT_DIM}">{subtitle}</text>
    </g>

    <!-- Tag -->
    <rect x="{W - 100}" y="18" width="80" height="22" rx="11" fill="{tag_color}" opacity="0.15"/>
    <text x="{W - 60}" y="33" text-anchor="middle" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="10" font-weight="600" fill="{tag_color}">{tag}</text>

    <!-- Divider -->
    <line x1="24" y1="58" x2="{W - 24}" y2="58" stroke="{BORDER}" stroke-width="1"/>

    <!-- Content -->
    <g transform="translate(0, 68)">
{inner}
    </g>
  </g>

  <!-- Border -->
  <rect width="{W}" height="{H}" rx="{R}" fill="none" stroke="{BORDER}" stroke-width="1"/>
</svg>"""


def icon_bot():
    return f'<circle cx="10" cy="10" r="10" fill="{ACCENT}" opacity="0.15"/><circle cx="10" cy="10" r="5" fill="{ACCENT}"/>'


def icon_network():
    return (
        f'<circle cx="10" cy="10" r="10" fill="{ACCENT3}" opacity="0.15"/>'
        f'<circle cx="7" cy="7" r="2" fill="{ACCENT3}"/>'
        f'<circle cx="13" cy="13" r="2" fill="{ACCENT3}"/>'
        f'<circle cx="13" cy="7" r="2" fill="{ACCENT3}"/>'
        f'<line x1="7" y1="7" x2="13" y2="13" stroke="{ACCENT3}" stroke-width="1"/>'
        f'<line x1="7" y1="7" x2="13" y2="7" stroke="{ACCENT3}" stroke-width="1"/>'
    )


def icon_shield():
    return (
        f'<circle cx="10" cy="10" r="10" fill="{ACCENT2}" opacity="0.15"/>'
        f'<path d="M10 3 L16 6 L16 12 Q16 17 10 19 Q4 17 4 12 L4 6 Z" fill="none" stroke="{ACCENT2}" stroke-width="1.5"/>'
    )


def icon_graph():
    return (
        f'<circle cx="10" cy="10" r="10" fill="{ACCENT4}" opacity="0.15"/>'
        f'<polyline points="4,16 8,10 12,13 16,5" fill="none" stroke="{ACCENT4}" stroke-width="1.5"/>'
    )


def icon_scale():
    return (
        f'<circle cx="10" cy="10" r="10" fill="{ACCENT5}" opacity="0.15"/>'
        f'<line x1="10" y1="4" x2="10" y2="16" stroke="{ACCENT5}" stroke-width="1.5"/>'
        f'<line x1="4" y1="7" x2="16" y2="7" stroke="{ACCENT5}" stroke-width="1.5"/>'
        f'<circle cx="5" cy="10" r="2" fill="none" stroke="{ACCENT5}" stroke-width="1"/>'
        f'<circle cx="15" cy="10" r="2" fill="none" stroke="{ACCENT5}" stroke-width="1"/>'
    )


def icon_search():
    return (
        f'<circle cx="10" cy="10" r="10" fill="{ACCENT}" opacity="0.15"/>'
        f'<circle cx="9" cy="9" r="4" fill="none" stroke="{ACCENT}" stroke-width="1.5"/>'
        f'<line x1="12" y1="12" x2="16" y2="16" stroke="{ACCENT}" stroke-width="1.5"/>'
    )


def _box(x, y, w, h, label, color, sublabel=None):
    """Rounded box with label inside."""
    lines = [
        f'      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{color}" opacity="0.12" stroke="{color}" stroke-width="0.5" stroke-opacity="0.3"/>',
        f'      <text x="{x + w / 2}" y="{y + h / 2 + (0 if sublabel else 4)}" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-size="10" font-weight="600" fill="{color}">{label}</text>',
    ]
    if sublabel:
        lines.append(
            f'      <text x="{x + w / 2}" y="{y + h / 2 + 14}" text-anchor="middle" font-family="\'Segoe UI\',sans-serif" font-size="8" fill="{TEXT_DIM}">{sublabel}</text>'
        )
    return "\n".join(lines)


def _arrow(x1, y1, x2, y2, color=TEXT_DIM):
    """Simple line arrow."""
    return f'      <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1" stroke-dasharray="3,2" opacity="0.4"/>'


def _label(x, y, text, size=9, color=TEXT_DIM):
    return f'      <text x="{x}" y="{y}" font-family="\'Segoe UI\',sans-serif" font-size="{size}" fill="{color}">{text}</text>'


def _metric(x, y, value, label, color=ACCENT):
    """A metric badge."""
    return (
        f'      <text x="{x}" y="{y}" font-family="\'Segoe UI\',sans-serif" font-size="20" font-weight="700" fill="{color}">{value}</text>\n'
        f'      <text x="{x}" y="{y + 14}" font-family="\'Segoe UI\',sans-serif" font-size="9" fill="{TEXT_DIM}">{label}</text>'
    )


# ══════════════════════════════════════════════
# PROJECT CARDS — Abdellah Ennajari
# ══════════════════════════════════════════════

def card_pageindex():
    """PageIndex — Document Index for Vectorless, Reasoning-based RAG."""
    inner = "\n".join([
        _label(30, 12, "ARCHITECTURE VECTORLESS RAG", 9, TEXT_DIM),

        # Input
        _box(30, 22, 90, 36, "Documents", ACCENT2, "PDF / TXT / MD"),

        # Indexing step
        _arrow(120, 40, 150, 40, ACCENT2),
        _box(150, 22, 110, 36, "Page Indexer", ACCENT, "Chunking + Metadata"),

        # Reasoning engine
        _arrow(260, 40, 290, 40, ACCENT),
        _box(290, 22, 120, 36, "Reasoning Engine", ACCENT3, "LLM-based retrieval"),

        # Query handler
        _arrow(410, 40, 440, 40, ACCENT3),
        _box(440, 22, 110, 36, "Response", ACCENT4, "Contextual answer"),

        # Key innovation
        _label(30, 82, "INNOVATION CLEE", 9, TEXT_DIM),
        _box(30, 92, 175, 28, "Sans Base Vectorielle", ACCENT2, "Pas de FAISS / ChromaDB"),
        _box(215, 92, 165, 28, "Raisonnement LLM pur", ACCENT),
        _box(390, 92, 160, 28, "Index Page structuree", ACCENT3),

        # Tech stack
        _label(30, 142, "STACK", 9, TEXT_DIM),
        _box(30, 152, 100, 24, "Python", ACCENT),
        _box(140, 152, 100, 24, "LangChain", ACCENT3),
        _box(250, 152, 120, 24, "OpenAI / Gemini", ACCENT2),
        _box(380, 152, 170, 24, "Document Parsing", ACCENT4),

        # Metrics
        _metric(50, 218, "0", "Vecteurs requis", ACCENT2),
        _metric(170, 218, "LLM", "Raisonnement pur", ACCENT3),
        _metric(310, 218, "Multi", "Formats docs", ACCENT),
        _metric(430, 218, "RAG", "Sans index dense", ACCENT4),
    ])
    return card_shell(
        "PageIndex", "Document Index for Vectorless RAG", "NLP", ACCENT,
        inner, icon_search()
    )


def card_eniad_rag():
    """Chatbot RAG ENIAD — Assistant Academique Production."""
    inner = "\n".join([
        _label(30, 12, "PIPELINE RAG ACADEMIQUE", 9, TEXT_DIM),

        # Query flow
        _box(30, 22, 100, 36, "Etudiant", ACCENT, "Question libre"),
        _arrow(130, 40, 160, 40, ACCENT),

        _box(160, 22, 115, 36, "RAG Pipeline", ACCENT3, "Recherche semantique"),
        _arrow(275, 40, 305, 40, ACCENT3),

        _box(305, 22, 110, 36, "LLM Gemini", ACCENT2, "Generation reponse"),
        _arrow(415, 40, 445, 40, ACCENT2),

        _box(445, 22, 105, 36, "Reponse", ACCENT4, "Contextualisee"),

        # Knowledge base
        _label(30, 82, "BASE DE CONNAISSANCES ENIAD", 9, TEXT_DIM),
        _box(30, 92, 160, 28, "Documents Academiques", ACCENT2),
        _box(200, 92, 160, 28, "Reglement Interieur", ACCENT),
        _box(370, 92, 180, 28, "FAQ Etudiants", ACCENT3),

        # Tech stack
        _label(30, 142, "STACK TECHNIQUE", 9, TEXT_DIM),
        _box(30, 152, 110, 24, "LangChain", ACCENT3),
        _box(150, 152, 90, 24, "FAISS", ACCENT),
        _box(250, 152, 110, 24, "Gemini API", ACCENT2),
        _box(370, 152, 80, 24, "FastAPI", ACCENT4),
        _box(460, 152, 90, 24, "Docker", ACCENT5),

        # Metrics
        _metric(50, 218, "500+", "Requetes/jour", ACCENT2),
        _metric(170, 218, "91%", "Precision", ACCENT),
        _metric(310, 218, "-70%", "Charge admin", ACCENT3),
        _metric(430, 218, "Multi", "Tours conv.", ACCENT4),
    ])
    return card_shell(
        "Chatbot RAG ENIAD", "Assistant Academique Production-Grade", "RAG", ACCENT3,
        inner, icon_bot()
    )


def card_article_generator():
    """Generateur d'Articles Intelligent — Data Flywheel Multi-Agents."""
    inner = "\n".join([
        _label(30, 12, "PIPELINE MULTI-AGENTS (CREWAI)", 9, TEXT_DIM),

        # Agent hierarchy
        _box(200, 20, 160, 30, "Orchestrateur", ACCENT3, "Planification taches"),

        # Arrows down to agents
        _arrow(240, 50, 80, 76, ACCENT3),
        _arrow(270, 50, 200, 76, ACCENT3),
        _arrow(300, 50, 340, 76, ACCENT3),
        _arrow(330, 50, 470, 76, ACCENT3),

        # Worker agents
        _box(30, 76, 110, 30, "Chercheur", ACCENT, "Web search + RAG"),
        _box(150, 76, 110, 30, "Redacteur", ACCENT2, "Generation article"),
        _box(280, 76, 110, 30, "Editeur", ACCENT4, "Qualite + style"),
        _box(410, 76, 130, 30, "Optimiseur", ACCENT5, "SEO + lisibilite"),

        # Data flywheel
        _label(30, 128, "DATA FLYWHEEL AUTO-AMELIORANT", 9, TEXT_DIM),
        _box(30, 138, 155, 28, "Feedback Loop", ACCENT2, "Evaluation qualite"),
        _arrow(185, 152, 215, 152, ACCENT2),
        _box(215, 138, 145, 28, "Fine-tuning continu", ACCENT3),
        _arrow(360, 152, 390, 152, ACCENT3),
        _box(390, 138, 160, 28, "+40% pertinence", ACCENT, "vs baseline"),

        # Metrics
        _metric(50, 218, "4", "Agents IA", ACCENT3),
        _metric(170, 218, "+40%", "Pertinence", ACCENT2),
        _metric(310, 218, "Auto", "Data Flywheel", ACCENT),
        _metric(430, 218, "Prod", "Ready", ACCENT4),
    ])
    return card_shell(
        "Article Generator", "Data Flywheel Multi-Agents", "MULTI-AGENT", ACCENT3,
        inner, icon_network()
    )


def card_webscraping_crew():
    """WebScraping Agent Automation Crew — Automatisation CrewAI."""
    inner = "\n".join([
        _label(30, 12, "PIPELINE WEBSCRAPING AUTOMATISE", 9, TEXT_DIM),

        # Input
        _box(30, 22, 110, 36, "URLs Cibles", ACCENT, "Config YAML"),
        _arrow(140, 40, 170, 40, ACCENT),

        # Scraper agent
        _box(170, 22, 120, 36, "Scraper Agent", ACCENT2, "BeautifulSoup + Sel."),
        _arrow(290, 40, 320, 40, ACCENT2),

        # Processing
        _box(320, 22, 115, 36, "Data Processor", ACCENT3, "Nettoyage + struct."),
        _arrow(435, 40, 465, 40, ACCENT3),

        _box(465, 22, 90, 36, "Output", ACCENT4, "JSON / CSV"),

        # Capabilities
        _label(30, 82, "CAPACITES", 9, TEXT_DIM),
        _box(30, 92, 155, 28, "Multi-sites parallele", ACCENT2),
        _box(195, 92, 145, 28, "Anti-detection", ACCENT),
        _box(350, 92, 200, 28, "Orchestration CrewAI", ACCENT3),

        # Tech stack
        _label(30, 142, "STACK", 9, TEXT_DIM),
        _box(30, 152, 90, 24, "CrewAI", ACCENT3),
        _box(130, 152, 120, 24, "BeautifulSoup", ACCENT),
        _box(260, 152, 110, 24, "Selenium", ACCENT2),
        _box(380, 152, 80, 24, "Python", ACCENT4),
        _box(470, 152, 80, 24, "Pandas", ACCENT5),

        # Metrics
        _metric(50, 218, "Multi", "Sites en //", ACCENT2),
        _metric(170, 218, "Auto", "Orchestration", ACCENT3),
        _metric(310, 218, "Struct.", "Donnees prop.", ACCENT),
        _metric(430, 218, "YAML", "Config simple", ACCENT4),
    ])
    return card_shell(
        "WebScraping Crew", "Automatisation Agents CrewAI", "AUTOMATION", ACCENT2,
        inner, icon_shield()
    )


def card_mini_llm():
    """Mini LLM — Experimentation Fine-tuning & Architecture LLM."""
    inner = "\n".join([
        _label(30, 12, "PIPELINE FINE-TUNING LLM", 9, TEXT_DIM),

        # Fine-tuning flow
        _box(30, 22, 100, 36, "Dataset", ACCENT2, "Paires Q/R"),
        _arrow(130, 40, 160, 40, ACCENT2),

        _box(160, 22, 120, 36, "Fine-tuning", ACCENT, "LoRA / DPO / PEFT"),
        _arrow(280, 40, 310, 40, ACCENT),

        _box(310, 22, 110, 36, "Evaluation", ACCENT3, "BLEU / ROUGE / Human"),
        _arrow(420, 40, 450, 40, ACCENT3),

        _box(450, 22, 100, 36, "Deploiement", ACCENT4, "HuggingFace Hub"),

        # Techniques
        _label(30, 82, "TECHNIQUES IMPLEMENTEES", 9, TEXT_DIM),
        _box(30, 92, 130, 28, "LoRA / PEFT", ACCENT, "Param. efficaces"),
        _box(170, 92, 120, 28, "DPO Alignment", ACCENT3, "Preference optim."),
        _box(300, 92, 120, 28, "Quantization", ACCENT2, "4-bit / 8-bit"),
        _box(430, 92, 120, 28, "Inference opt.", ACCENT4, "vLLM / Triton"),

        # Tech stack
        _label(30, 142, "STACK", 9, TEXT_DIM),
        _box(30, 152, 110, 24, "PyTorch", ACCENT),
        _box(150, 152, 130, 24, "HuggingFace", ACCENT2),
        _box(290, 152, 80, 24, "PEFT", ACCENT3),
        _box(380, 152, 80, 24, "TRL", ACCENT4),
        _box(470, 152, 80, 24, "MLflow", ACCENT5),

        # Metrics
        _metric(50, 218, "LoRA", "Fine-tuning", ACCENT),
        _metric(170, 218, "DPO", "Alignment", ACCENT3),
        _metric(310, 218, "4-bit", "Quantization", ACCENT2),
        _metric(430, 218, "Exp.", "MLflow track", ACCENT4),
    ])
    return card_shell(
        "Mini LLM", "Fine-tuning & Architecture LLM", "LLM", ACCENT,
        inner, icon_graph()
    )


def card_opencv_course():
    """OpenCV Course — Computer Vision avec Python."""
    inner = "\n".join([
        _label(30, 12, "PIPELINE COMPUTER VISION", 9, TEXT_DIM),

        # CV pipeline
        _box(30, 22, 100, 36, "Image Input", ACCENT2, "Webcam / Fichier"),
        _arrow(130, 40, 160, 40, ACCENT2),

        _box(160, 22, 120, 36, "Pre-traitement", ACCENT, "Resize + Normalize"),
        _arrow(280, 40, 310, 40, ACCENT),

        _box(310, 22, 110, 36, "Detection", ACCENT3, "YOLO / CNN / HOG"),
        _arrow(420, 40, 450, 40, ACCENT3),

        _box(450, 22, 100, 36, "Visualisation", ACCENT4, "Annotations + UI"),

        # Topics covered
        _label(30, 82, "SUJETS COUVERTS", 9, TEXT_DIM),
        _box(30, 92, 130, 28, "Detection objets", ACCENT2),
        _box(170, 92, 120, 28, "Segmentation", ACCENT),
        _box(300, 92, 115, 28, "Tracking temps reel", ACCENT3),
        _box(425, 92, 125, 28, "OCR + texte", ACCENT4),

        # Tech stack
        _label(30, 142, "STACK", 9, TEXT_DIM),
        _box(30, 152, 100, 24, "OpenCV", ACCENT),
        _box(140, 152, 100, 24, "Python", ACCENT2),
        _box(250, 152, 100, 24, "TensorFlow", ACCENT3),
        _box(360, 152, 80, 24, "YOLO", ACCENT4),
        _box(450, 152, 100, 24, "Mediapipe", ACCENT5),

        # Metrics
        _metric(50, 218, "10+", "Projets CV", ACCENT2),
        _metric(170, 218, "95%+", "Precision", ACCENT),
        _metric(310, 218, "RT", "Temps reel", ACCENT3),
        _metric(430, 218, "Open", "Source", ACCENT4),
    ])
    return card_shell(
        "OpenCV Course", "Computer Vision avec Python", "CV", ACCENT2,
        inner, icon_scale()
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    cards = {
        "aegis": card_pageindex,
        "partnerships-os": card_eniad_rag,
        "sentinel": card_article_generator,
        "lattice": card_webscraping_crew,
        "evita": card_mini_llm,
        "spectra": card_opencv_course,
    }

    for name, fn in cards.items():
        svg = fn()
        path = os.path.join(OUT_DIR, f"{name}.svg")
        with open(path, "w") as f:
            f.write(svg)
        print(f"Generated {path}")


if __name__ == "__main__":
    main()
