# === Grid Settings ===
GRID_MIN_SIZE = 20  # Minimum grid size (e.g., 20x20)
MAX_SIMULATION_STEPS = 1000  # Optional simulation step cap

# === Treasure ===
TREASURE_DECAY_PERCENT = 0.001  # 0.1% value loss per step
TREASURE_MIN_VALUE = 0.0        # When value reaches this, treasure is removed

# === Treasure Hunters ===
HUNTER_STAMINA_LOSS_PER_MOVE = 0.02     # 2% stamina lost per movement
HUNTER_CRITICAL_STAMINA = 0.06          # Below 6% → go rest
HUNTER_REST_GAIN = 0.01                 # 1% per simulation step in hideout
HUNTER_COLLAPSE_STEPS = 3               # Collapses after 3 steps at 0 stamina
RECRUIT_PROBABILITY = 0.20              # 20% chance to recruit new hunter

# === Knights ===
KNIGHT_RADIUS = 3
KNIGHT_ENERGY_LOSS_PER_CHASE = 0.20     # 20% energy per chase
KNIGHT_REST_THRESHOLD = 0.20            # ≤ 20% → go rest
KNIGHT_REST_GAIN = 0.10                 # 10% energy regained per rest step

# === Hideouts ===
HIDEOUT_CAPACITY = 5                    # Max hunters per hideout
