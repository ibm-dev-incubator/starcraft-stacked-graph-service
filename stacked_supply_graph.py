import hashlib
import json

import sc2reader
from sc2reader.engine.plugins import ContextLoader, GameHeartNormalizer

# hand built
# duplicated in sc2scan.py
army_units = ['Nuke',  # I guess
              'Marine',
              'Marauder',
              'Reaper',
              'Ghost',
              'BattleHellion',
              'Hellion',
              'Hellbat',
              'WidowMine',
              'SiegeTank',
              'Cyclone',
              'Thor',
              'Viking',
              'VikingFighter',
              'VikingAssault',
              'Medivac',
              'Liberator',
              'Raven',
              'Banshee',
              'Battlecruiser',
              'Nuke',  # I guess
              'Zealot',
              'Stalker',
              'Sentry',
              'Adept',
              'HighTemplar',
              'DarkTemplar',
              'Immortal',
              'Disruptor',
              'Colossus',
              'Archon',
              'Observer',
              'WarpPrism',
              'Phoenix',
              'VoidRay',
              'Oracle',
              'Tempest',
              'Carrier',
              'Zergling',
              'Roach',
              'Ravager',
              'Hydralisk',
              'SwarmHost',
              'Infestor',
              'Ultralisk',
              'Mutalisk',
              'Corruptor',
              'Viper',
              'Baneling',
              'BroodLord',
              'Overseer', ]


def frame_to_time(frame):
    # note for future python3 work
    game_seconds = int(frame / 16)

    minutes = int(game_seconds / 60)
    seconds = game_seconds - (60 * minutes)
    return '{0}:{1:02d}'.format(minutes, seconds)

def alive_at_this_time(unit, time):
    if unit.died_at is None:
        unit.died_at = replay.frames
    if time >= unit.started_at and time <= unit.died_at:
        return True
    else:
        return False


replay = sc2reader.load_replay(
    'thereplay.SC2Replay',
    engine=sc2reader.engine.GameEngine(plugins=[
        ContextLoader(),
        GameHeartNormalizer(),
    ])
)

unit_supplies = {}
for unit_type in army_units:
    unit_supplies[unit_type] = []

# All done in frames
times = []
game_end = replay.frames
game_start = 0

for current_frame in range(game_start, game_end, 160):
    times.append(current_frame)
    supply_per_unit = {}
    for unit_type in army_units:
        supply_per_unit[unit_type] = 0
    # Scan all units owned by player
    for unit in replay.players[1].units:
        if unit.name not in army_units:
            continue
        if alive_at_this_time(unit, current_frame):
            supply_per_unit[unit.name] += unit.supply
    for unit_name, supply in supply_per_unit.items():
        unit_supplies[unit_name].append(supply)

to_pop = []
for key, value in unit_supplies.items():
    if sum(value) == 0:
        to_pop.append(key)


for key in to_pop:
    unit_supplies.pop(key, None)

print(json.dumps(unit_supplies))

