"""
Single source of truth for all application constants, reference data,
and configuration values.
"""

import re

# ---------------------------------------------------------------------------
# App-level constants
# ---------------------------------------------------------------------------
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{2,20}$")
NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 20

ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

DEFAULT_DB_URL = "postgresql+asyncpg://localhost:5432/f1mcp"

POINTS_PER_ROUND_WIN = 2
POINTS_PER_ROUND_DRAW = 1
POINTS_GAME_WIN_BONUS = 5
POINTS_GAME_LOSS_PENALTY = 5

CARDS_PER_PLAYER = 5
ROUNDS_PER_GAME = 5

TRACK_MULTIPLIER_MIN = 0.5
TRACK_MULTIPLIER_MAX = 2.0
TRACK_MULTIPLIER_DEFAULT = 1.0

SKILL_VALUE_MIN = 0
SKILL_VALUE_MAX = 100

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
