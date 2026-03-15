"""
F1 reference data used to seed the database.

Countries, skills, teams, drivers, tracks, curated skill profiles,
circuit-type affinities, and driver-track multiplier overrides.
"""

# ---------------------------------------------------------------------------
# Countries  (name → ISO 3166-1 alpha-3)
# ---------------------------------------------------------------------------
COUNTRIES: dict[str, str] = {
    "Argentina": "ARG",
    "Australia": "AUS",
    "Austria": "AUT",
    "Azerbaijan": "AZE",
    "Bahrain": "BHR",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Canada": "CAN",
    "China": "CHN",
    "Denmark": "DNK",
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "Hungary": "HUN",
    "India": "IND",
    "Indonesia": "IDN",
    "Italy": "ITA",
    "Japan": "JPN",
    "Malaysia": "MYS",
    "Mexico": "MEX",
    "Monaco": "MCO",
    "Netherlands": "NLD",
    "New Zealand": "NZL",
    "Poland": "POL",
    "Portugal": "PRT",
    "Qatar": "QAT",
    "Russia": "RUS",
    "Saudi Arabia": "SAU",
    "Singapore": "SGP",
    "South Africa": "ZAF",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Thailand": "THA",
    "UAE": "ARE",
    "United Kingdom": "GBR",
    "United States": "USA",
    "Venezuela": "VEN",
}

# ---------------------------------------------------------------------------
# Skill definitions  (name, description)
# ---------------------------------------------------------------------------
SKILLS: list[tuple[str, str]] = [
    ("pace", "Raw single-lap speed"),
    ("racecraft", "Wheel-to-wheel racing ability"),
    ("awareness", "Spatial awareness and avoiding incidents"),
    ("experience", "Career experience and consistency"),
    ("wet_weather", "Performance in rain conditions"),
    ("tire_management", "Ability to preserve tires over stints"),
]

# ---------------------------------------------------------------------------
# Teams  (name → headquarters country)
# ---------------------------------------------------------------------------
TEAMS: dict[str, str] = {
    "Ferrari": "Italy",
    "Red Bull Racing": "Austria",
    "McLaren": "United Kingdom",
    "Mercedes": "Germany",
    "Aston Martin": "United Kingdom",
    "Alpine": "France",
    "Haas": "United States",
    "Williams": "United Kingdom",
    "Cadillac": "United States",
    "Audi": "Germany",
    "Racing Bulls": "Italy",
    "Brawn GP": "United Kingdom",
    "BMW Sauber": "Switzerland",
    "Lotus": "United Kingdom",
    "Toro Rosso": "Italy",
    "Alfa Romeo": "Switzerland",
    "AlphaTauri": "Italy",
    "Renault": "France",
    "Sauber": "Switzerland",
    "Manor Racing": "United Kingdom",
    "Manor Marussia": "United Kingdom",
}

# ---------------------------------------------------------------------------
# Drivers  (id, name, number, gp_wins, team, peak_year, country)
# id is the serial primary key used in the DB
# ---------------------------------------------------------------------------
DRIVERS: list[tuple[int, str, int, int, str, int, str]] = [
    (1, "Lewis Hamilton", 44, 105, "Ferrari", 2026, "United Kingdom"),
    (2, "Michael Schumacher", 1, 91, "Ferrari", 2004, "Germany"),
    (3, "Max Verstappen", 1, 71, "Red Bull Racing", 2026, "Netherlands"),
    (4, "Sebastian Vettel", 5, 53, "Red Bull Racing", 2013, "Germany"),
    (5, "Alain Prost", 2, 51, "McLaren", 1989, "France"),
    (6, "Ayrton Senna", 12, 41, "McLaren", 1988, "Brazil"),
    (7, "Fernando Alonso", 14, 32, "Aston Martin", 2026, "Spain"),
    (8, "Nico Rosberg", 6, 23, "Mercedes", 2016, "Germany"),
    (9, "Kimi Räikkönen", 7, 21, "Ferrari", 2007, "Finland"),
    (10, "Jenson Button", 22, 15, "Brawn GP", 2009, "United Kingdom"),
    (11, "Lando Norris", 4, 11, "McLaren", 2026, "United Kingdom"),
    (12, "Felipe Massa", 19, 11, "Ferrari", 2008, "Brazil"),
    (13, "Valtteri Bottas", 77, 10, "Cadillac", 2026, "Finland"),
    (14, "Oscar Piastri", 81, 9, "McLaren", 2026, "Australia"),
    (15, "Daniel Ricciardo", 3, 8, "Red Bull Racing", 2014, "Australia"),
    (16, "Charles Leclerc", 16, 8, "Ferrari", 2026, "Monaco"),
    (17, "Sergio Pérez", 11, 6, "Cadillac", 2026, "Mexico"),
    (18, "Carlos Sainz Jr.", 55, 3, "Williams", 2026, "Spain"),
    (19, "George Russell", 63, 2, "Mercedes", 2026, "United Kingdom"),
    (20, "Robert Kubica", 88, 1, "BMW Sauber", 2008, "Poland"),
    (21, "Pastor Maldonado", 13, 1, "Williams", 2012, "Venezuela"),
    (22, "Pierre Gasly", 10, 1, "Alpine", 2026, "France"),
    (23, "Esteban Ocon", 31, 1, "Haas", 2026, "France"),
    (24, "Romain Grosjean", 8, 0, "Lotus", 2013, "France"),
    (25, "Kevin Magnussen", 20, 0, "Haas", 2018, "Denmark"),
    (26, "Daniil Kvyat", 26, 0, "Toro Rosso", 2019, "Russia"),
    (27, "Lance Stroll", 18, 0, "Aston Martin", 2026, "Canada"),
    (28, "Alexander Albon", 23, 0, "Williams", 2026, "Thailand"),
    (29, "Nico Hülkenberg", 27, 0, "Audi", 2026, "Germany"),
    (30, "Yuki Tsunoda", 22, 0, "Red Bull Racing", 2026, "Japan"),
    (31, "Guanyu Zhou", 24, 0, "Alfa Romeo", 2022, "China"),
    (32, "Antonio Giovinazzi", 99, 0, "Alfa Romeo", 2019, "Italy"),
    (33, "Stoffel Vandoorne", 2, 0, "McLaren", 2017, "Belgium"),
    (34, "Marcus Ericsson", 9, 0, "Sauber", 2018, "Sweden"),
    (35, "Logan Sargeant", 2, 0, "Williams", 2023, "United States"),
    (36, "Mick Schumacher", 47, 0, "Haas", 2022, "Germany"),
    (37, "Nyck de Vries", 21, 0, "AlphaTauri", 2023, "Netherlands"),
    (38, "Nicholas Latifi", 6, 0, "Williams", 2021, "Canada"),
    (39, "Nikita Mazepin", 9, 0, "Haas", 2021, "Russia"),
    (40, "Brendon Hartley", 28, 0, "Toro Rosso", 2018, "New Zealand"),
    (41, "Sergey Sirotkin", 35, 0, "Williams", 2018, "Russia"),
    (42, "Felipe Nasr", 12, 0, "Sauber", 2015, "Brazil"),
    (43, "Jolyon Palmer", 30, 0, "Renault", 2017, "United Kingdom"),
    (44, "Esteban Gutiérrez", 21, 0, "Sauber", 2013, "Mexico"),
    (45, "Pascal Wehrlein", 94, 0, "Manor Racing", 2016, "Germany"),
    (46, "Rio Haryanto", 88, 0, "Manor Racing", 2016, "Indonesia"),
    (47, "Alexander Rossi", 53, 0, "Manor Marussia", 2015, "United States"),
    (48, "Will Stevens", 28, 0, "Manor Marussia", 2015, "United Kingdom"),
    (49, "Roberto Merhi", 98, 0, "Manor Marussia", 2015, "Spain"),
    (50, "Jack Aitken", 89, 0, "Williams", 2020, "United Kingdom"),
    (51, "Pietro Fittipaldi", 51, 0, "Haas", 2020, "Brazil"),
    (52, "Oliver Bearman", 87, 0, "Haas", 2026, "United Kingdom"),
    (53, "Franco Colapinto", 43, 0, "Alpine", 2026, "Argentina"),
    (54, "Liam Lawson", 30, 0, "Racing Bulls", 2026, "New Zealand"),
    (55, "Kimi Antonelli", 12, 0, "Mercedes", 2026, "Italy"),
    (56, "Jack Doohan", 7, 0, "Alpine", 2026, "Australia"),
    (57, "Gabriel Bortoleto", 5, 0, "Audi", 2026, "Brazil"),
    (58, "Isack Hadjar", 6, 0, "Red Bull Racing", 2026, "France"),
    (59, "Arvid Lindblad", 3, 0, "Racing Bulls", 2026, "United Kingdom"),
]

# ---------------------------------------------------------------------------
# Tracks  (name, country, laps, circuit_type, description)
# circuit_type is one of: street, high_speed, technical, power, mixed
# ---------------------------------------------------------------------------
TRACKS: list[tuple[str, str, int, str, str]] = [
    (
        "Albert Park Circuit",
        "Australia",
        58,
        "technical",
        "A scenic lakeside circuit in Melbourne with a mix of fast sweeps and tight chicanes through parkland.",
    ),
    (
        "Shanghai International Circuit",
        "China",
        56,
        "power",
        "A Hermann Tilke design featuring the unique snail-shaped Turn 1-2-3 complex and one of F1's longest back straights.",
    ),
    (
        "Suzuka International Racing Course",
        "Japan",
        53,
        "technical",
        "A legendary figure-eight layout with the fearsome 130R corner and the demanding Esses section.",
    ),
    (
        "Bahrain International Circuit",
        "Bahrain",
        57,
        "power",
        "A desert circuit raced under floodlights, known for heavy braking zones and abrasive sand that punishes tires.",
    ),
    (
        "Jeddah Corniche Circuit",
        "Saudi Arabia",
        50,
        "street",
        "The fastest street circuit on the calendar, with blind high-speed corners threading along the Red Sea waterfront.",
    ),
    (
        "Miami International Autodrome",
        "United States",
        57,
        "street",
        "A semi-permanent circuit built around the Hard Rock Stadium with tight turns and a long DRS straight.",
    ),
    (
        "Autodromo Enzo e Dino Ferrari (Imola)",
        "Italy",
        63,
        "technical",
        "A classic old-school circuit running anti-clockwise through the hills of Emilia-Romagna with limited overtaking.",
    ),
    (
        "Circuit de Monaco",
        "Monaco",
        78,
        "street",
        "The crown jewel of F1 — ultra-narrow streets, the famous Tunnel, and the Swimming Pool chicane. Qualifying is everything.",
    ),
    (
        "Circuit de Barcelona-Catalunya",
        "Spain",
        66,
        "technical",
        "A benchmark testing venue with a high-speed final sector and heavy tire degradation throughout the race.",
    ),
    (
        "Circuit Gilles Villeneuve",
        "Canada",
        70,
        "mixed",
        "A semi-permanent circuit on an island in the St. Lawrence River, famous for the Wall of Champions at the final chicane.",
    ),
    (
        "Red Bull Ring",
        "Austria",
        71,
        "power",
        "A short, high-altitude circuit set in the Styrian mountains with dramatic elevation changes and three heavy braking zones.",
    ),
    (
        "Silverstone Circuit",
        "United Kingdom",
        52,
        "high_speed",
        "The home of British motorsport with legendary high-speed corners like Copse, Maggotts, and Becketts.",
    ),
    (
        "Circuit de Spa-Francorchamps",
        "Belgium",
        44,
        "high_speed",
        "A fearsome Ardennes forest circuit featuring Eau Rouge / Raidillon and unpredictable weather that changes corner to corner.",
    ),
    (
        "Hungaroring",
        "Hungary",
        70,
        "technical",
        "A tight, twisty circuit nicknamed 'Monaco without walls' — low-speed, high-downforce, and notoriously hard to overtake.",
    ),
    (
        "Circuit Zandvoort",
        "Netherlands",
        72,
        "technical",
        "A classic seaside circuit with banked final turns and a packed Dutch crowd creating an electric atmosphere.",
    ),
    (
        "Autodromo Nazionale di Monza",
        "Italy",
        53,
        "high_speed",
        "The Temple of Speed — long straights, minimal downforce, slipstream battles, and the Tifosi's passionate roar.",
    ),
    (
        "IFEMA Madrid",
        "Spain",
        66,
        "street",
        "A new semi-street circuit winding through the IFEMA exhibition grounds in the Spanish capital.",
    ),
    (
        "Baku City Circuit",
        "Azerbaijan",
        51,
        "street",
        "A dramatic street circuit mixing a medieval old town section with a 2.2 km flat-out blast along the Caspian Sea.",
    ),
    (
        "Marina Bay Street Circuit",
        "Singapore",
        62,
        "street",
        "F1's original night race — a grueling, bumpy street circuit under floodlights in tropical heat and humidity.",
    ),
    (
        "Circuit of the Americas (COTA)",
        "United States",
        56,
        "power",
        "A purpose-built circuit in Austin featuring an iconic uphill Turn 1 and sections inspired by great circuits worldwide.",
    ),
    (
        "Autódromo Hermanos Rodríguez",
        "Mexico",
        71,
        "mixed",
        "Sitting at 2,200m altitude where thin air robs engines and downforce, ending with the Foro Sol stadium section.",
    ),
    (
        "Autódromo José Carlos Pace (Interlagos)",
        "Brazil",
        71,
        "high_speed",
        "A short, anti-clockwise circuit with dramatic elevation changes and a history of producing legendary wet-weather races.",
    ),
    (
        "Las Vegas Strip Circuit",
        "United States",
        50,
        "street",
        "A glitzy night race down the famous Las Vegas Strip with a 1.9 km straight past iconic casino hotels.",
    ),
    (
        "Lusail International Circuit",
        "Qatar",
        57,
        "mixed",
        "A flowing, high-speed circuit in the desert with long corners that push sustained lateral G-forces on drivers.",
    ),
    (
        "Yas Marina Circuit",
        "UAE",
        58,
        "mixed",
        "The traditional season finale, raced at twilight, with its iconic hotel straddling the circuit and a fast final sector.",
    ),
    (
        "Buddh International Circuit",
        "India",
        60,
        "power",
        "A Tilke-designed circuit near Delhi with a sweeping Turn 1 entry and long straights rewarding raw power.",
    ),
    (
        "Nürburgring",
        "Germany",
        60,
        "technical",
        "The modern GP circuit adjacent to the legendary Nordschleife, known for changeable Eifel mountains weather.",
    ),
    (
        "Hockenheimring",
        "Germany",
        67,
        "high_speed",
        "Once an ultra-fast blast through the forest, now a shorter layout but still with a high-speed character and the Motodrom stadium.",
    ),
    (
        "Sepang International Circuit",
        "Malaysia",
        56,
        "power",
        "A Tilke masterpiece in tropical heat with wide run-offs, long straights, and dramatic monsoon downpours.",
    ),
    (
        "Kyalami Racing Circuit",
        "South Africa",
        72,
        "mixed",
        "A high-altitude circuit near Johannesburg with a rich F1 heritage and a mix of fast and technical sections.",
    ),
    (
        "Indianapolis Motor Speedway",
        "United States",
        73,
        "high_speed",
        "The Brickyard — F1 used the infield road course with the famous banked Turn 1 leading onto the main oval straight.",
    ),
    (
        "Circuit Paul Ricard",
        "France",
        53,
        "high_speed",
        "A test track turned GP venue with the distinctive blue-and-red run-off stripes and the high-speed Mistral straight.",
    ),
    (
        "Circuit de Nevers Magny-Cours",
        "France",
        70,
        "mixed",
        "A remote, technical circuit in central France with low-grip surfaces and a challenging mix of slow and medium-speed corners.",
    ),
    (
        "Watkins Glen International",
        "United States",
        59,
        "high_speed",
        "A classic American road course in upstate New York with flowing elevation changes and high-speed bends through the countryside.",
    ),
    (
        "Brands Hatch Circuit",
        "United Kingdom",
        75,
        "technical",
        "A short, undulating Kent circuit with the famous Paddock Hill Bend — a dramatic downhill plunge into the first corner.",
    ),
    (
        "Autódromo do Estoril",
        "Portugal",
        71,
        "mixed",
        "A classic Iberian circuit near the Atlantic coast known for strong winds and the high-speed Turn 1 right-hander.",
    ),
]

# ---------------------------------------------------------------------------
# Curated skill profiles for the top 20 drivers
# Values: (pace, racecraft, awareness, experience, wet_weather, tire_management)
# ---------------------------------------------------------------------------
DRIVER_SKILL_OVERRIDES: dict[str, tuple[int, int, int, int, int, int]] = {
    "Lewis Hamilton": (96, 95, 92, 99, 97, 95),
    "Michael Schumacher": (95, 97, 85, 98, 90, 88),
    "Max Verstappen": (98, 96, 82, 85, 96, 84),
    "Sebastian Vettel": (90, 88, 90, 95, 80, 85),
    "Alain Prost": (88, 92, 97, 96, 82, 93),
    "Ayrton Senna": (97, 95, 78, 90, 99, 80),
    "Fernando Alonso": (89, 95, 93, 99, 88, 96),
    "Nico Rosberg": (87, 82, 88, 85, 78, 86),
    "Kimi Räikkönen": (90, 85, 80, 92, 83, 88),
    "Jenson Button": (82, 84, 90, 88, 95, 92),
    "Lando Norris": (92, 88, 82, 72, 85, 80),
    "Felipe Massa": (84, 80, 76, 85, 72, 78),
    "Valtteri Bottas": (85, 72, 84, 82, 75, 80),
    "Oscar Piastri": (90, 86, 84, 65, 80, 82),
    "Daniel Ricciardo": (86, 92, 85, 80, 82, 78),
    "Charles Leclerc": (93, 85, 75, 72, 82, 74),
    "Sergio Pérez": (78, 82, 80, 82, 76, 90),
    "Carlos Sainz Jr.": (86, 84, 86, 76, 80, 84),
    "George Russell": (90, 82, 84, 70, 82, 80),
    "Robert Kubica": (85, 83, 78, 72, 80, 76),
}

# ---------------------------------------------------------------------------
# Per-circuit-type affinity for every driver  (fallback when no track override)
# Circuit types: street, high_speed, technical, power, mixed
# Multiplier range: 0.5 – 2.0   (1.0 = neutral)
# ---------------------------------------------------------------------------
DRIVER_CIRCUIT_TYPE_AFFINITY: dict[str, dict[str, float]] = {
    # ── Champions & legends (1-10) ────────────────────────────────────────
    "Lewis Hamilton": {"street": 1.50, "high_speed": 1.75, "technical": 1.65, "power": 1.55, "mixed": 1.60},
    "Michael Schumacher": {"street": 1.35, "high_speed": 1.70, "technical": 1.60, "power": 1.65, "mixed": 1.60},
    "Max Verstappen": {"street": 1.40, "high_speed": 1.70, "technical": 1.65, "power": 1.70, "mixed": 1.60},
    "Sebastian Vettel": {"street": 1.35, "high_speed": 1.55, "technical": 1.50, "power": 1.60, "mixed": 1.50},
    "Alain Prost": {"street": 1.40, "high_speed": 1.50, "technical": 1.55, "power": 1.45, "mixed": 1.55},
    "Ayrton Senna": {"street": 1.80, "high_speed": 1.60, "technical": 1.55, "power": 1.45, "mixed": 1.50},
    "Fernando Alonso": {"street": 1.45, "high_speed": 1.50, "technical": 1.55, "power": 1.45, "mixed": 1.50},
    "Nico Rosberg": {"street": 1.40, "high_speed": 1.35, "technical": 1.30, "power": 1.30, "mixed": 1.30},
    "Kimi Räikkönen": {"street": 1.15, "high_speed": 1.55, "technical": 1.40, "power": 1.45, "mixed": 1.40},
    "Jenson Button": {"street": 1.25, "high_speed": 1.40, "technical": 1.35, "power": 1.30, "mixed": 1.40},
    # ── Race winners / strong current drivers (11-20) ─────────────────────
    "Lando Norris": {"street": 1.20, "high_speed": 1.40, "technical": 1.35, "power": 1.35, "mixed": 1.30},
    "Felipe Massa": {"street": 1.15, "high_speed": 1.30, "technical": 1.25, "power": 1.35, "mixed": 1.25},
    "Valtteri Bottas": {"street": 1.10, "high_speed": 1.30, "technical": 1.20, "power": 1.35, "mixed": 1.25},
    "Oscar Piastri": {"street": 1.20, "high_speed": 1.30, "technical": 1.30, "power": 1.30, "mixed": 1.25},
    "Daniel Ricciardo": {"street": 1.40, "high_speed": 1.30, "technical": 1.30, "power": 1.25, "mixed": 1.30},
    "Charles Leclerc": {"street": 1.45, "high_speed": 1.35, "technical": 1.30, "power": 1.35, "mixed": 1.30},
    "Sergio Pérez": {"street": 1.45, "high_speed": 1.20, "technical": 1.20, "power": 1.25, "mixed": 1.30},
    "Carlos Sainz Jr.": {"street": 1.25, "high_speed": 1.30, "technical": 1.30, "power": 1.30, "mixed": 1.30},
    "George Russell": {"street": 1.20, "high_speed": 1.35, "technical": 1.25, "power": 1.30, "mixed": 1.25},
    "Robert Kubica": {"street": 1.15, "high_speed": 1.30, "technical": 1.25, "power": 1.30, "mixed": 1.25},
    # ── Solid midfield / single-win drivers (21-30) ───────────────────────
    "Pastor Maldonado": {"street": 0.95, "high_speed": 1.10, "technical": 1.00, "power": 1.05, "mixed": 1.00},
    "Pierre Gasly": {"street": 1.15, "high_speed": 1.20, "technical": 1.15, "power": 1.15, "mixed": 1.15},
    "Esteban Ocon": {"street": 1.10, "high_speed": 1.15, "technical": 1.10, "power": 1.10, "mixed": 1.10},
    "Romain Grosjean": {"street": 1.00, "high_speed": 1.15, "technical": 1.10, "power": 1.10, "mixed": 1.05},
    "Kevin Magnussen": {"street": 1.05, "high_speed": 1.10, "technical": 1.05, "power": 1.10, "mixed": 1.05},
    "Daniil Kvyat": {"street": 0.95, "high_speed": 1.05, "technical": 1.00, "power": 1.05, "mixed": 1.00},
    "Lance Stroll": {"street": 1.15, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 1.00},
    "Alexander Albon": {"street": 1.05, "high_speed": 1.10, "technical": 1.05, "power": 1.05, "mixed": 1.10},
    "Nico Hülkenberg": {"street": 1.00, "high_speed": 1.15, "technical": 1.10, "power": 1.10, "mixed": 1.10},
    "Yuki Tsunoda": {"street": 1.05, "high_speed": 1.10, "technical": 1.05, "power": 1.10, "mixed": 1.05},
    # ── Lower tier (31-45) ────────────────────────────────────────────────
    "Guanyu Zhou": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
    "Antonio Giovinazzi": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 0.95, "mixed": 0.95},
    "Stoffel Vandoorne": {"street": 1.00, "high_speed": 1.00, "technical": 1.00, "power": 0.95, "mixed": 0.95},
    "Marcus Ericsson": {"street": 0.90, "high_speed": 0.95, "technical": 0.90, "power": 0.95, "mixed": 0.90},
    "Logan Sargeant": {"street": 0.85, "high_speed": 0.90, "technical": 0.85, "power": 0.90, "mixed": 0.85},
    "Mick Schumacher": {"street": 0.90, "high_speed": 0.95, "technical": 0.90, "power": 0.95, "mixed": 0.90},
    "Nyck de Vries": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 0.95, "mixed": 0.95},
    "Nicholas Latifi": {"street": 0.85, "high_speed": 0.85, "technical": 0.85, "power": 0.85, "mixed": 0.85},
    "Nikita Mazepin": {"street": 0.75, "high_speed": 0.80, "technical": 0.75, "power": 0.80, "mixed": 0.75},
    "Brendon Hartley": {"street": 0.90, "high_speed": 1.00, "technical": 0.95, "power": 0.95, "mixed": 0.95},
    "Sergey Sirotkin": {"street": 0.85, "high_speed": 0.90, "technical": 0.85, "power": 0.90, "mixed": 0.85},
    "Felipe Nasr": {"street": 0.90, "high_speed": 0.90, "technical": 0.85, "power": 0.90, "mixed": 0.85},
    "Jolyon Palmer": {"street": 0.85, "high_speed": 0.85, "technical": 0.80, "power": 0.85, "mixed": 0.80},
    "Esteban Gutiérrez": {"street": 0.85, "high_speed": 0.90, "technical": 0.85, "power": 0.90, "mixed": 0.85},
    "Pascal Wehrlein": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 0.95, "mixed": 0.95},
    # ── Very limited / rookies (46-59) ────────────────────────────────────
    "Rio Haryanto": {"street": 0.80, "high_speed": 0.85, "technical": 0.80, "power": 0.85, "mixed": 0.80},
    "Alexander Rossi": {"street": 0.90, "high_speed": 0.90, "technical": 0.85, "power": 0.90, "mixed": 0.85},
    "Will Stevens": {"street": 0.80, "high_speed": 0.85, "technical": 0.80, "power": 0.85, "mixed": 0.80},
    "Roberto Merhi": {"street": 0.80, "high_speed": 0.85, "technical": 0.80, "power": 0.85, "mixed": 0.80},
    "Jack Aitken": {"street": 0.85, "high_speed": 0.90, "technical": 0.85, "power": 0.85, "mixed": 0.85},
    "Pietro Fittipaldi": {"street": 0.85, "high_speed": 0.85, "technical": 0.85, "power": 0.85, "mixed": 0.85},
    "Oliver Bearman": {"street": 1.00, "high_speed": 1.05, "technical": 1.00, "power": 1.00, "mixed": 1.00},
    "Franco Colapinto": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
    "Liam Lawson": {"street": 1.00, "high_speed": 1.05, "technical": 1.00, "power": 1.05, "mixed": 1.00},
    "Kimi Antonelli": {"street": 1.05, "high_speed": 1.10, "technical": 1.05, "power": 1.05, "mixed": 1.05},
    "Jack Doohan": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
    "Gabriel Bortoleto": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
    "Isack Hadjar": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
    "Arvid Lindblad": {"street": 0.95, "high_speed": 1.00, "technical": 0.95, "power": 1.00, "mixed": 0.95},
}

# ---------------------------------------------------------------------------
# Specific driver-track overrides based on historical race results (FastF1/Ergast)
# Only listed for tracks where a driver has a notable record.
# Takes priority over DRIVER_CIRCUIT_TYPE_AFFINITY.
# ---------------------------------------------------------------------------
DRIVER_TRACK_OVERRIDES: dict[str, dict[str, float]] = {
    "Lewis Hamilton": {
        "Silverstone Circuit": 1.95,                          # 8 wins — most successful driver ever at Silverstone
        "Hungaroring": 1.90,                                  # 8 wins — most successful at Hungary
        "Circuit Gilles Villeneuve": 1.80,                    # 7 wins
        "Circuit de Barcelona-Catalunya": 1.75,               # 6 wins
        "Shanghai International Circuit": 1.70,               # 6 wins
        "Circuit of the Americas (COTA)": 1.70,               # 6 wins
        "Bahrain International Circuit": 1.60,                # 5 wins
        "Autodromo Nazionale di Monza": 1.60,                 # 5 wins
        "Yas Marina Circuit": 1.60,                           # 5 wins
        "Circuit de Spa-Francorchamps": 1.65,                 # 4 wins
        "Marina Bay Street Circuit": 1.55,                    # 4 wins
        "Autódromo José Carlos Pace (Interlagos)": 1.55,      # 3 wins + iconic 2021 comeback
        "Circuit de Monaco": 1.50,                            # 3 wins
        "Suzuka International Racing Course": 1.50,           # 1 win, consistently fast
        "Albert Park Circuit": 1.55,                          # 2 wins
        "Jeddah Corniche Circuit": 1.45,                      # 1 win
        "Red Bull Ring": 1.35,                                # not his strongest
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.45,
        "Sepang International Circuit": 1.55,                 # 3 wins
        "Nürburgring": 1.55,                                 # 2 wins
        "Hockenheimring": 1.40,
    },
    "Michael Schumacher": {
        "Circuit de Spa-Francorchamps": 1.90,                 # 6 wins — the Spa master
        "Circuit Gilles Villeneuve": 1.80,                    # 7 wins
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.80,        # 7 San Marino GP wins
        "Circuit de Barcelona-Catalunya": 1.75,               # 6 wins
        "Suzuka International Racing Course": 1.75,           # 6 wins
        "Circuit de Nevers Magny-Cours": 1.80,                # 8 French GP wins
        "Autodromo Nazionale di Monza": 1.65,                 # 5 wins
        "Circuit de Monaco": 1.60,                            # 5 wins
        "Nürburgring": 1.65,                                 # multiple wins, German hero
        "Hockenheimring": 1.60,                               # 4 wins
        "Hungaroring": 1.60,                                  # 4 wins
        "Albert Park Circuit": 1.60,                          # 4 wins
        "Sepang International Circuit": 1.65,                 # 3 wins
        "Shanghai International Circuit": 1.50,               # 3 wins
        "Silverstone Circuit": 1.45,                          # 3 wins
        "Autódromo José Carlos Pace (Interlagos)": 1.50,      # 3 wins
        "Indianapolis Motor Speedway": 1.55,                  # 5 US GP wins
        "Red Bull Ring": 1.50,                                # A1-Ring wins
    },
    "Max Verstappen": {
        "Circuit Zandvoort": 1.90,                            # home track, 3 consecutive wins
        "Circuit de Spa-Francorchamps": 1.85,                 # born in Belgium, multiple wins
        "Red Bull Ring": 1.80,                                # team home, 5 wins
        "Autódromo Hermanos Rodríguez": 1.75,                 # 4 wins
        "Suzuka International Racing Course": 1.70,           # multiple wins, clinched title
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.65,        # 2 wins
        "Circuit of the Americas (COTA)": 1.60,               # 2 wins
        "Autódromo José Carlos Pace (Interlagos)": 1.60,      # multiple wins
        "Yas Marina Circuit": 1.60,                           # 2 wins (2021 title)
        "Bahrain International Circuit": 1.60,                # multiple wins
        "Jeddah Corniche Circuit": 1.55,                      # 2 wins
        "Miami International Autodrome": 1.55,                # 2 wins
        "Circuit de Barcelona-Catalunya": 1.55,               # 2 wins
        "Lusail International Circuit": 1.55,                 # 2 wins
        "Autodromo Nazionale di Monza": 1.50,                 # 2 wins
        "Hungaroring": 1.50,                                  # 2 wins
        "Marina Bay Street Circuit": 1.50,                    # 2 wins
        "Las Vegas Strip Circuit": 1.50,                      # 1 win
        "Shanghai International Circuit": 1.50,               # 1 win
        "Silverstone Circuit": 1.45,                          # competitive but not dominant
        "Circuit de Monaco": 1.35,                            # 1 win, tricky for him historically
        "Albert Park Circuit": 1.45,
    },
    "Sebastian Vettel": {
        "Buddh International Circuit": 1.90,                  # 3 wins in 3 races — perfect record
        "Marina Bay Street Circuit": 1.85,                    # 5 wins — the Singapore king
        "Suzuka International Racing Course": 1.70,           # 4 wins, clinched 2 titles
        "Bahrain International Circuit": 1.65,                # 4 wins
        "Yas Marina Circuit": 1.65,                           # 3 wins
        "Circuit Gilles Villeneuve": 1.60,                    # 3 wins
        "Autodromo Nazionale di Monza": 1.55,                 # 3 wins
        "Sepang International Circuit": 1.60,                 # 3 wins
        "Shanghai International Circuit": 1.50,               # 2 wins
        "Albert Park Circuit": 1.50,                          # 2 wins
        "Red Bull Ring": 1.50,                                # 1 win
        "Hungaroring": 1.45,                                  # 1 win
        "Circuit de Spa-Francorchamps": 1.45,                 # 1 win
        "Circuit de Barcelona-Catalunya": 1.40,               # 1 win
        "Silverstone Circuit": 1.35,                          # 1 win
        "Circuit de Monaco": 1.35,                            # 1 win
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.40,
        "Autódromo José Carlos Pace (Interlagos)": 1.45,      # 1 win
    },
    "Alain Prost": {
        "Circuit Paul Ricard": 1.80,                          # French GP specialist
        "Circuit de Nevers Magny-Cours": 1.75,                # home race
        "Autódromo José Carlos Pace (Interlagos)": 1.75,      # 6 Brazilian GP wins
        "Silverstone Circuit": 1.65,                          # 5 wins
        "Circuit de Monaco": 1.60,                            # 4 wins
        "Kyalami Racing Circuit": 1.65,                       # 3 wins
        "Hockenheimring": 1.55,                               # 3 wins
        "Nürburgring": 1.55,                                  # multiple German GP wins
        "Circuit de Spa-Francorchamps": 1.55,                 # 2 wins
        "Brands Hatch Circuit": 1.60,                         # strong British GP record
        "Autódromo do Estoril": 1.55,                         # 2 wins
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.50,        # multiple San Marino wins
        "Suzuka International Racing Course": 1.50,           # title battles
        "Albert Park Circuit": 1.50,                          # Adelaide wins
        "Autodromo Nazionale di Monza": 1.45,
    },
    "Ayrton Senna": {
        "Circuit de Monaco": 1.95,                            # 6 wins — THE Monaco master
        "Autódromo José Carlos Pace (Interlagos)": 1.85,      # 2 wins, home hero
        "Autódromo do Estoril": 1.70,                         # first ever F1 win (1985)
        "Circuit de Spa-Francorchamps": 1.70,                 # incredible wet-weather drives
        "Suzuka International Racing Course": 1.70,           # epic title battles
        "Autodromo Enzo e Dino Ferrari (Imola)": 1.65,        # 3 San Marino wins
        "Hungaroring": 1.60,                                  # 3 wins
        "Brands Hatch Circuit": 1.60,                         # strong in debut season
        "Albert Park Circuit": 1.55,                          # Adelaide wins
        "Silverstone Circuit": 1.55,                          # 1 win
        "Autodromo Nazionale di Monza": 1.50,                 # 1 win
        "Hockenheimring": 1.50,
        "Nürburgring": 1.50,
        "Circuit Gilles Villeneuve": 1.50,                    # 1 win
        "Kyalami Racing Circuit": 1.50,
    },
    "Fernando Alonso": {
        "Hungaroring": 1.75,                                  # 4 wins
        "Circuit de Barcelona-Catalunya": 1.70,               # 2 wins, home specialist
        "Marina Bay Street Circuit": 1.65,                    # 2 wins
        "Sepang International Circuit": 1.60,                 # 2 wins
        "Nürburgring": 1.55,                                  # 2 wins
        "Silverstone Circuit": 1.55,                          # 2 wins
        "Circuit Gilles Villeneuve": 1.55,                    # 2 wins
        "Bahrain International Circuit": 1.55,                # 2 wins
        "Shanghai International Circuit": 1.50,               # 2 wins
        "Circuit de Monaco": 1.45,                            # 2 wins
        "Hockenheimring": 1.45,                               # 1 win
        "Autodromo Nazionale di Monza": 1.50,                 # 1 win
        "Circuit de Spa-Francorchamps": 1.45,                 # 1 win
        "Suzuka International Racing Course": 1.50,           # 1 win
        "Autódromo José Carlos Pace (Interlagos)": 1.45,      # 1 win
    },
    "Nico Rosberg": {
        "Circuit de Monaco": 1.70,                            # 3 wins, grew up in Monaco
        "Yas Marina Circuit": 1.55,                           # 2 wins, clinched 2016 title
        "Baku City Circuit": 1.50,                            # 1 win
        "Circuit de Spa-Francorchamps": 1.45,                 # 1 win
        "Hockenheimring": 1.45,                               # 1 win, German heritage
        "Suzuka International Racing Course": 1.40,           # 1 win
        "Bahrain International Circuit": 1.40,                # 1 win
        "Shanghai International Circuit": 1.40,               # 1 win
        "Marina Bay Street Circuit": 1.45,                    # 1 win
        "Red Bull Ring": 1.35,                                # 1 win
        "Circuit de Barcelona-Catalunya": 1.40,               # 1 win
        "Silverstone Circuit": 1.40,                          # 1 win
        "Albert Park Circuit": 1.40,                          # 1 win
        "Autodromo Nazionale di Monza": 1.35,
    },
    "Kimi Räikkönen": {
        "Circuit de Spa-Francorchamps": 1.80,                 # 4 wins — his best track
        "Sepang International Circuit": 1.60,                 # 3 wins
        "Albert Park Circuit": 1.60,                          # 2 wins
        "Autodromo Nazionale di Monza": 1.55,                 # 1 win, 2007 title clincher
        "Circuit of the Americas (COTA)": 1.55,               # 1 win at age 38
        "Silverstone Circuit": 1.50,                          # 1 win
        "Autódromo José Carlos Pace (Interlagos)": 1.50,      # 1 win
        "Suzuka International Racing Course": 1.50,           # 1 win
        "Bahrain International Circuit": 1.45,                # 1 win
        "Circuit Gilles Villeneuve": 1.45,                    # 1 win
        "Hockenheimring": 1.45,                               # 1 win
        "Nürburgring": 1.45,
        "Hungaroring": 1.40,
        "Circuit de Monaco": 1.25,                            # never won, not his style
    },
    "Jenson Button": {
        "Albert Park Circuit": 1.60,                          # 3 wins
        "Circuit Gilles Villeneuve": 1.55,                    # 2 wins, great in wet
        "Hungaroring": 1.55,                                  # 2 wins
        "Autódromo José Carlos Pace (Interlagos)": 1.55,      # 2 wins
        "Circuit de Spa-Francorchamps": 1.55,                 # 1 win, changeable weather suits him
        "Suzuka International Racing Course": 1.50,           # 1 win, 2009 title
        "Shanghai International Circuit": 1.50,               # 1 win
        "Silverstone Circuit": 1.45,                          # 1 win
        "Sepang International Circuit": 1.45,                 # 1 win
        "Bahrain International Circuit": 1.40,                # 1 win
        "Circuit de Monaco": 1.35,
        "Autodromo Nazionale di Monza": 1.30,
    },
    "Lando Norris": {
        "Miami International Autodrome": 1.55,                # first F1 win
        "Circuit Zandvoort": 1.50,                            # 1 win
        "Marina Bay Street Circuit": 1.50,                    # 1 win
        "Hungaroring": 1.45,                                  # 1 win
        "Yas Marina Circuit": 1.40,                           # 1 win
        "Silverstone Circuit": 1.40,                          # strong home results
        "Suzuka International Racing Course": 1.35,
        "Circuit de Spa-Francorchamps": 1.35,
        "Autodromo Nazionale di Monza": 1.35,
    },
    "Felipe Massa": {
        "Autódromo José Carlos Pace (Interlagos)": 1.60,      # home hero, nearly won 2008 title there
        "Bahrain International Circuit": 1.55,                # 2 wins
        "Sepang International Circuit": 1.45,                 # 2 wins
        "Autodromo Nazionale di Monza": 1.40,
        "Hungaroring": 1.35,
        "Shanghai International Circuit": 1.35,
    },
    "Valtteri Bottas": {
        "Red Bull Ring": 1.45,                                # 2 wins
        "Circuit of the Americas (COTA)": 1.40,               # 2 wins
        "Albert Park Circuit": 1.40,                          # 1 win
        "Suzuka International Racing Course": 1.40,           # 1 win
        "Yas Marina Circuit": 1.35,                           # 1 win
        "Bahrain International Circuit": 1.35,
        "Circuit de Spa-Francorchamps": 1.35,
        "Silverstone Circuit": 1.30,
        "Autodromo Nazionale di Monza": 1.30,
    },
    "Oscar Piastri": {
        "Hungaroring": 1.45,                                  # 1 win
        "Albert Park Circuit": 1.40,                          # home race
        "Autodromo Nazionale di Monza": 1.35,
        "Bahrain International Circuit": 1.35,
    },
    "Daniel Ricciardo": {
        "Circuit de Monaco": 1.60,                            # 1 win, incredible 2018
        "Baku City Circuit": 1.55,                            # 2 wins
        "Shanghai International Circuit": 1.50,               # 1 win
        "Sepang International Circuit": 1.50,                 # 1 win
        "Autodromo Nazionale di Monza": 1.50,                 # 1 win with McLaren
        "Hungaroring": 1.45,                                  # 1 win
        "Circuit de Spa-Francorchamps": 1.45,                 # 1 win
        "Circuit Gilles Villeneuve": 1.45,                    # 1 win
        "Albert Park Circuit": 1.40,                          # home race
    },
    "Charles Leclerc": {
        "Circuit de Monaco": 1.55,                            # 1 win, home
        "Bahrain International Circuit": 1.55,                # 2 wins
        "Circuit de Spa-Francorchamps": 1.50,                 # 1 win + emotional 2019
        "Autodromo Nazionale di Monza": 1.50,                 # 1 win, tifosi
        "Red Bull Ring": 1.45,                                # 1 win
        "Albert Park Circuit": 1.45,                          # 1 win
        "Marina Bay Street Circuit": 1.45,                    # 1 win
        "Circuit de Barcelona-Catalunya": 1.40,
        "Silverstone Circuit": 1.40,
    },
    "Sergio Pérez": {
        "Baku City Circuit": 1.65,                            # 2 wins — "King of Baku"
        "Marina Bay Street Circuit": 1.60,                    # 2 wins
        "Jeddah Corniche Circuit": 1.55,                      # 1 win
        "Circuit de Monaco": 1.55,                            # 1 win
        "Autódromo Hermanos Rodríguez": 1.55,                 # home race, strong results
        "Bahrain International Circuit": 1.50,                # 1 win
    },
    "Carlos Sainz Jr.": {
        "Marina Bay Street Circuit": 1.50,                    # 1 win
        "Silverstone Circuit": 1.50,                          # 1 win
        "Albert Park Circuit": 1.50,                          # 1 win
        "Autodromo Nazionale di Monza": 1.40,
        "Circuit de Barcelona-Catalunya": 1.40,               # home race
        "Circuit de Monaco": 1.35,
    },
    "George Russell": {
        "Autódromo José Carlos Pace (Interlagos)": 1.45,      # 1 win
        "Red Bull Ring": 1.40,                                # 1 win
        "Las Vegas Strip Circuit": 1.40,                      # 1 win
        "Silverstone Circuit": 1.40,                          # home, strong results
        "Yas Marina Circuit": 1.35,
    },
    "Robert Kubica": {
        "Circuit Gilles Villeneuve": 1.50,                    # only F1 win
        "Circuit de Spa-Francorchamps": 1.35,
    },
    "Pastor Maldonado": {
        "Circuit de Barcelona-Catalunya": 1.40,               # only F1 win
    },
    "Pierre Gasly": {
        "Autodromo Nazionale di Monza": 1.50,                 # 1 win — emotional AlphaTauri victory
    },
    "Esteban Ocon": {
        "Hungaroring": 1.45,                                  # 1 win
    },
    "Lance Stroll": {
        "Baku City Circuit": 1.30,                            # podium as a teenager
        "Circuit Gilles Villeneuve": 1.20,                    # home race
    },
    "Nico Hülkenberg": {
        "Autódromo José Carlos Pace (Interlagos)": 1.30,      # incredible qualifying, pole in 2010
    },
}
