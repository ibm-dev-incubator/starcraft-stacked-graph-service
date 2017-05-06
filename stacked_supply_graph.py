import hashlib
import json

import sc2reader
from sc2reader.engine.plugins import ContextLoader, GameHeartNormalizer

import numpy as NP
from matplotlib import pyplot as PLT
import matplotlib.patches as mpatches

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

print(json.dumps(unit_suplies))

units = sorted(list(unit_supplies.keys()))
y = NP.row_stack([ unit_supplies[i] for i in units ])
# this call to 'cumsum' (cumulative sum), passing in your y data, 
# is necessary to avoid having to manually order the datasets
x = times
y_stack = NP.cumsum(y, axis=0)   # a 3x10 array

fig = PLT.figure()
ax1 = fig.add_subplot(111)

patches = []

ax1.fill_between(x, 0, y_stack[0,:], facecolor="#CC6666", alpha=.7)
patches.append(mpatches.Patch(color="#CC6666", label=units[0], alpha=.7))

for index, key in enumerate(units[1:]):
    color = "#" +  hashlib.sha224(bytes(key, 'utf-8')).hexdigest()[:6]

    patches.append(mpatches.Patch(color=color, label=key, alpha=.7))
    ax1.fill_between(x, y_stack[index,:], y_stack[index+1,:], facecolor=color, alpha=.7)

PLT.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0., handles=patches)
PLT.show()

