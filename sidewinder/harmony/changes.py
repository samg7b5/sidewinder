from mingus.core import notes, intervals

from sidewinder import Chart
from sidewinder.utilities import get_scale
from sidewinder.melodies.patterns import get_scale_patterns
from sidewinder.lick_library import respell_and_determine
from sidewinder.utilities import numerals_list_to_shorthand_list
from sidewinder.snippets import CHUNKS

############# Analysis

def get_diatonic_chords(scales, shape=(1,3,5)):
    '''
    Play a chord shape starting on each scale degree
    Return the resultant chords as numerals

    scales: str ('major') or [str] (['major', 'harmonic minor', ...])

    Outputs numerals e.g. {'major': ['IM7', 'IIm7', 'IIIm7', 'IVM7', 'V7', 'VIm7', 'VIIm7b5']}
    '''
    
    out = {}
    for scale in scales: 
        chord_degrees = [[i+j for i in shape] for j, note in enumerate(get_scale(scale))]
        chord_notes = [get_scale_patterns(scale, p=chord_degrees[j]) for j, note in enumerate(get_scale(scale))]
        # then recognise as chord
        chords = [respell_and_determine(chord, shorthand=True)[0][0] for chord in chord_notes[0]['C']] # TODO determine extended chords not as slash(|)/polychords
        numerals_list = Chart(chords).get_numeral_representation() # TODO numeral representation of slash/polychords doesn't convert the bottom from note to numeral
        out[scale] = numerals_list
    return out

############ Generation

# ii-7 V7 IM7 IVM7
start_key = 'Bb'
# c1 = numerals_list_to_shorthand_list(numerals=CHUNKS["251"] + ['IVM7'], key=start_key)

# # minor 251 in key a minor third below
# c2 = numerals_list_to_shorthand_list(numerals=CHUNKS["minor 251m7"] + ['I7'], 
#         key=intervals.from_shorthand(start_key,'b3',False)) # False for downwards interval

# autumn = Chart((c1+c2)*4, start_key) 

kc1 = start_key # Bb
kc2 = intervals.from_shorthand(start_key,'b3',False) # False for downwards interval (G)
kc3 = intervals.from_shorthand(start_key,'4') # Eb
key_centres = ([kc1]*4 + [kc2]*4) + ([kc1]*4 + [kc2]*4) + ([kc2]*4 + [kc1]*4) + [kc2]*4 + [kc3]*2 + [kc2]*4
chord_symbols = CHUNKS["2514"] + CHUNKS["minor 251m7"] + ['I7'] + \
    CHUNKS["2514"] + CHUNKS["minor 251m7"] + ['i-7'] + \
    CHUNKS["minor 251m7"] + ['i-7'] + CHUNKS["251"] + ['IM7'] + \
    CHUNKS["minor 251m7"] + ['IV7'] + \
    CHUNKS["25"] + \
    CHUNKS["minor 251m7"] + ['i-7']

# alternative input WIP:
# allowing duration of 0.5 will replace e.g. ((251, IM7), 1 1 1 1) -> (251, 1 1 0.5)
leadsheet = '''kc1: 2514
kc2: minor 251m7, I7
kc1: 2514
kc2: minor 251m7, i-7
kc2: minor 251m7, i-7
kc1: 251, IM7
kc2: minor 251m7, IV7
kc3: 25
kc2: minor 251m7, i-7'''
# _key_centres = ...
## generate the code to define key_centres:
print('['+']*1 + ['.join([line.split(': ')[0] for line in leadsheet.split('\n')])+']*1')
## change *1 to *number of chords in line
# _chord_symbols = ...
## generate the code to define chord_symbols:
print(' + '.join(["CHUNKS"+str([el]) if el in CHUNKS.keys() else str([el]) for sl in [line.split(': ')[1].split(', ') for line in leadsheet.split('\n')] for el in sl]))

# build numerals list from numeral chord symbols and related key centres
new_kc_idx = [i for i, _ in enumerate(key_centres) if key_centres[i] != key_centres[max(0,i-1)]]
chart = []
for start, end in zip([0]+new_kc_idx, new_kc_idx+[len(chord_symbols)+1]):
    chart += numerals_list_to_shorthand_list(numerals=chord_symbols[start:end], key=key_centres[start])

autumn = Chart(chart, start_key) 
autumn.set_durations([1]*14+[1,1] + [1]*2+[1,1] + [1]*2+[1,1] + [1,1,2,2,2,2] + [1]*2+[1,1]) # TODO allow a duration of 0.5 = 2 bars
