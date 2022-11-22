

from __future__ import division

import copy
import json
import re
from collections import defaultdict

# not sure if I need to set season to something like pbp2011df
SEASON = '2011'


# setting up counters equal to zero
def player_stats():
    return {
        'before': {
            'fg': 0,
            'fga': 0
        },
        'after': {
            'fg': 0,
            'fga': 0
        },
        'other': {
            'fg': 0,
            'fga': 0
        },
        'num_with_block': 0
    }

#adding to counters for each player
def merge_dicts(x,y):
    for k in y.keys():
        x[k]['before']['fg'] += y[k]['before']['fg']
        x[k]['before']['fga'] += y[k]['before']['fga']
        x[k]['after']['fg'] += y[k]['after']['fg']
        x[k]['after']['fga'] += y[k]['after']['fga']
        x[k]['other']['fg'] += y[k]['other']['fg']
        x[k]['other']['fga'] += y[k]['other']['fga']
        x[k]['num_with_block'] += y[k]['num_with_block']


#adding counters for all players?
def update_total(total, y):
    for k in y.keys():
        total['before']['fg'] += y[k]['before']['fg']
        total['before']['fga'] += y[k]['before']['fga']
        total['after']['fg'] += y[k]['after']['fg']
        total['after']['fga'] += y[k]['after']['fga']
        total['other']['fg'] += y[k]['other']['fg']
        total['other']['fga'] += y[k]['other']['fga']
        total['num_with_block'] += y[k]['num_with_block']

def find_max_min(stats, cutoff):
    max_player = ''
    max_val = -100
    min_player = ''
    min_val = 100
    for k in stats.keys():
        if stats[k]['before']['fga'] > cutoff and stats[k]['after']['fga'] > cutoff:
            diff = stats[k]['before']['fg'] / stats[k]['before']['fga'] - stats[k]['after']['fg'] / stats[k]['after']['fga']
            if diff > max_val:
                    max_val = diff
                    max_player = k
            if diff < min_val:
                    min_val = diff
                    min_player = k
        #       print "\n"
        #       print_header(k)
        #       print_summary(stats[k])
    return [max_player, min_player]

def print_header(txt):
    print (txt)
    print (''.join(['-' for i in txt]))

def print_summary(stats):
    print ("Before Block: %d%% (%d FGA)" % (100 * stats['before']['fg'] / stats['before']['fga'], stats['before']['fga']))
    print ("After Block: %d%% (%d FGA)" % (100 * stats['after']['fg'] / stats['after']['fga'], stats['after']['fga']))
    print ("Never Blocked in Game: %d%% (%d FGA)" % (100 * stats['other']['fg'] / stats['other']['fga'], stats['other']['fga']))
    print ("Overall: %d%% (%d FGA)" % (100 * (stats['before']['fg'] + stats['after']['fg'] + stats['other']['fg']) / (stats['before']['fga'] + stats['after']['fga'] + stats['other']['fga']), stats['before']['fga'] + stats['after']['fga'] + stats['other']['fga']))

f = open('pbp%sdf.txt' % SEASON)

num_games = 0
game_id = ''
stats = defaultdict(player_stats)
stats_total = player_stats()
stats_temp = defaultdict(player_stats)

for line in f:
    row = line.split('\t')

    if row[0] != game_id:
        #           print 'NEW GAME', len(stats), len(stats_temp)
        merge_dicts(stats, stats_temp)
        update_total(stats_total, stats_temp)

        game_id = row[0]
        stats_temp = defaultdict(player_stats)
        num_games += 1
#this would be where error is
    if 'two point' in row[2] or 'jumper' in row[2] or 'three point' in row[2]:
        name = re.findall('(^.*?\s.*?[\w+]+)', row[2])[0]

        participants_0_athlete_id = '%s' % (name)

    if 'blocks ' in row[2]
        nameb = re.findall('(^?:\S+\s{3}(\S+ \S+)', row[2])[0]

        participants_1_athlete_id = '%s' % (nameb)


# FIX THIS, FIND REGEX FOR 3rd and 4th WORDS AND THEN SUB THAT In LINE 110
        if 'blocks ' in row[2] and stats_temp[participants_0_athlete_id]['num_with_block'] == 0:
            stats_temp[participants_0_athlete_id]['before'] = copy.deepcopy(stats_temp[participants_0_athlete_id]['other'])
            stats_temp[participants_0_athlete_id]['other'] = dict(fg=0, fga=0)
            stats_temp[participants_0_athlete_id]['num_with_block'] = 1
            # print 'BLOCKED JUMPER: ', participants_0_athlete_id
        elif ' makes' in row[2]:
            if stats_temp[participants_0_athlete_id]['num_with_block']:
                stats_temp[participants_0_athlete_id]['after']['fg'] += 1
                stats_temp[participants_0_athlete_id]['after']['fga'] += 1
            else:
                stats_temp[participants_0_athlete_id]['other']['fg'] += 1
                stats_temp[participants_0_athlete_id]['other']['fga'] += 1

        elif ' misses' in row[2]:
            if stats_temp[participants_0_athlete_id]['num_with_block']:
                stats_temp[participants_0_athlete_id]['after']['fga'] += 1
            else:
                stats_temp[participants_0_athlete_id]['other']['fga'] += 1


        else:
            print ('WTF IS THIS', row[2])

print_header("League-Wide FG% on jump shots before/after a blocked jumper")
print_summary(stats_total)

cutoff = 25
out = []
for k in stats.keys():
    if stats[k]['before']['fga'] > cutoff and stats[k]['after']['fga'] > cutoff:
        out.append({
            'name': k,
            'fgp_before': stats[k]['before']['fg'] / stats[k]['before']['fga'],
            'fgp_after': stats[k]['after']['fg'] / stats[k]['after']['fga'],
            'fgp_overall': (stats[k]['before']['fg'] + stats[k]['after']['fg'] + stats[k]['other']['fg']) / (stats[k]['before']['fga'] + stats[k]['after']['fga'] + stats[k]['other']['fga']),
            'fga_before': stats[k]['before']['fga'],
            'fga_after': stats[k]['after']['fga'],
            'fga_overall': stats[k]['before']['fga'] + stats[k]['after']['fga'] + stats[k]['other']['fga']
        })

with open("output.json", "w") as f:
    f.write(json.dumps(out, sort_keys=True, indent=4))