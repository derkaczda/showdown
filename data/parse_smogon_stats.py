import ntpath
from datetime import datetime
from dateutil import relativedelta

import requests

from showdown.engine.helpers import spreads_are_alike
from showdown.engine.helpers import normalize_name

OTHER_STRING = "other"
MOVES_STRING = "moves"
ITEM_STRING = "items"
SPREADS_STRING = "spreads"
ABILITY_STRING = "abilities"


def get_smogon_stats_file_name(game_mode, month_delta=1):
    """
    Gets the smogon stats url based on the game mode
    Uses the previous-month's statistics
    """

    # blitz comes and goes - use the non-blitz version
    if game_mode.endswith('blitz'):
        game_mode = game_mode[:-5]

    # always use the `-0` file - the higher ladder is for noobs
    smogon_url = "https://www.smogon.com/stats/{}-{}/chaos/{}-0.json"

    previous_month = datetime.now() - relativedelta.relativedelta(months=month_delta)
    year = previous_month.year

    # TODO: chnage that back 
    # somehow the month switch did not work
    #month = "{:02d}".format(previous_month.month)
    month = "04"

    return smogon_url.format(year, month, game_mode)


def get_pokemon_information(smogon_stats_url, pkmn_names=None):
    r = requests.get(smogon_stats_url)
    if r.status_code == 404:
        r = requests.get(get_smogon_stats_file_name(ntpath.basename(smogon_stats_url.replace('-0.txt', '')), month_delta=2))

    infos = r.json()['data']
    final_infos = {}
    for pkmn_name, pkmn_information in infos.items():
        normalized_name = normalize_name(pkmn_name)

        # if `pkmn_names` is provided, only find data on pkmn in that list
        if pkmn_names and normalized_name not in pkmn_names:
            continue

        spreads = []
        items = []
        moves = []
        abilities = []
        total_count = pkmn_information['Raw count']
        final_infos[normalized_name] = {}

        for spread, count in sorted(pkmn_information['Spreads'].items(), key=lambda x: x[1], reverse=True):
            percentage = round(100 * count / total_count, 2)
            if percentage > 0:
                nature, evs = [normalize_name(i) for i in spread.split(":")]
                evs = evs.replace("/", ",")
                for sp in spreads:
                    if spreads_are_alike(sp, (nature, evs)):
                        sp[2] += percentage
                        break
                else:
                    spreads.append([nature, evs, percentage])

        for item, count in pkmn_information['Items'].items():
            if count > 0:
                items.append((item, round(100*count / total_count, 2)))

        for move, count in pkmn_information['Moves'].items():
            if count > 0 and move and move.lower() != "nothing":
                moves.append((move, round(100*count / total_count, 2)))

        for ability, count in pkmn_information['Abilities'].items():
            if count > 0:
                abilities.append(
                    (ability, round(100 * count / total_count, 2))
                )

        final_infos[normalized_name][SPREADS_STRING] = sorted(spreads, key=lambda x: x[2], reverse=True)
        final_infos[normalized_name][ITEM_STRING] = sorted(items, key=lambda x: x[1], reverse=True)
        final_infos[normalized_name][MOVES_STRING] = sorted(moves, key=lambda x: x[1], reverse=True)
        final_infos[normalized_name][ABILITY_STRING] = sorted(abilities, key=lambda x: x[1], reverse=True)

    return final_infos
