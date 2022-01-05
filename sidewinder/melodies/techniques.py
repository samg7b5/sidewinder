from random import choices
from itertools import accumulate
from functools import lru_cache
from typing import List

from mingus import *
from mingus.containers import Note
from mingus.core.chords import from_shorthand

from sidewinder.utilities import get_scale, note_to_scale_degree, total_duration
from sidewinder.melodies.patterns import get_scale_patterns

def flatten(myList):
    if type(myList[0]) == list:
        return flatten([element for sublist in myList for element in sublist])
    else:
        return myList

# DIATONIC CHUNKS ("SHAPES")
# A diatonic chunk is a shape specified in terms of diatonic scale degrees (integers)
# which means that its sound depends upon the choice of scale
# It optionally has attributes:
#   i. Durations
#   ii. Applicable scale option(s) - NOTE potentially not required (can handle at the point of choosing a scale)
#       nb. ito constraint not style - e.g. can't directly play 12345678 on a pentatonic
#   (I was going to put "iii. Chord over which to utilise this chunk" but logically that is 
#   part of the policy management and not the policy itself - "I know this technique and 
#   I can choose where I want to apply it"; however a policy may contain global rules 
#   (e.g. "never play on chord X"))

DIATONIC_CHUNKS = {
    'triad': {
        'degrees': [1,3,5],
        'durations': None,
    },
    'arp7': {
        'degrees': [1,3,5,7],
        'durations': None,
    },
    'bird': { # usually on Maj7 # from Positively Progressing
        'degrees': [3,5,7,9,8],
        'durations': [8,8,8,8,4],
    },
}

def apply_diatonic_chunk(chunk_name: str, scale: str='major', key: str='C', durations=False, **kwargs):

    if durations:
        durs = DIATONIC_CHUNKS[chunk_name]['durations']
        assert len(durs) == len(DIATONIC_CHUNKS[chunk_name]['degrees']), "Check chunk definition"
    else:
        durs = None

    pattern = get_scale_patterns(scale, DIATONIC_CHUNKS[chunk_name]['degrees'], keys=[key], **kwargs)[key][0]
    return pattern, durs

# CHROMATIC CHUNKS ("SOUNDS/COLOURS")
# A chromatic chunk is a sound specified in terms of chromatic scale degrees (int/str)
# which means that its sound is independent upon choice of scale
# It optionally has attributes:
#   i. Durations
#   ii. Octave adjustments - unlike diatonic chunks where 1 < 8
#   (same iii. as diatonic chunks)

CHROMATIC_CHUNKS = {
    'minor_major': {
        'degrees': ['b7',2,4,6,'b13','b9',1,'b7'],
        'durations': None,
        'octaves': [0,0,0,0,0,0,0,-1],
    },
    'dexter': { # on a m7 # from Positively Progressing
        'degrees': ['7',1,'b3',5,'b7',9,11],
        'durations': None,
        'octaves': [-1,0,0,0,0,0,0],
    },
    'bird': { # usually on Maj7 # from Positively Progressing
        'degrees': [3,5,7,9,8],
        'durations': [8,8,8,8,4],
    },
}

def apply_chromatic_chunk(chunk_name: str, key: str='C', durations=False, **kwargs):

    if durations:
        durs = CHROMATIC_CHUNKS[chunk_name]['durations']
        assert len(durs) == len(CHROMATIC_CHUNKS[chunk_name]['degrees']), \
        "Check chunk definition"
    else:
        durs = None

    chunk = [str(x) for x in CHROMATIC_CHUNKS[chunk_name]['degrees']]

    # build a chromatic degree to integer conversion map:
    # note_to_scale_degree can return multiple chromatic_options for each scale degree,
    # so create a temp dict and then unpack its keys into individual chromatic options
    # and remember i+1 because degrees start from root = 1.
    chrom_to_pattern = {
        chrom: deg for chroms, deg in {
            tuple(
                note_to_scale_degree(note, 'C', 'chromatic', chromatic_options=True)
                ): i+1 for i, note in enumerate(get_scale('chromatic','C'))
                }.items() for chrom in chroms
                }

    pattern = get_scale_patterns(
        'chromatic', 
        p=[chrom_to_pattern[chrom] for chrom in chunk], 
        keys=[key], 
        **kwargs)[key][0]

    if CHROMATIC_CHUNKS[chunk_name]['octaves'] is None:
        octaves = [0] * len(chunk)
    else:
        octaves = CHROMATIC_CHUNKS[chunk_name]['octaves']
    
    pattern_correct_octaves = [
        Note().from_int(int(note) + adj*12)
        for (note, adj) in zip(pattern, octaves)
        ]

    return pattern_correct_octaves, durs

# NOTE it is possible to convert diatonic -> chromatic
# NOTE it is possible to convert some chromatic -> diatonic where an appropriate scale exists
# NOTE this logic is related to db (see lick_library) except here we fudge storage with dicts
# and focus more on the representation and application of chunks rather than db ops

# GENERATIVE CHUNKS
# A generative chunk is defined by its representation as Python logic i.e. it is
# given as a function and not a set of degrees.
# They (likely) take a starting note as input, plus any function-specific inputs
# Currently they output a None duration like the other cf types

## see example 02 e.g. chromatic approach (3.2)
def approach_with_chromatic_note(target=Note('D'), start=Note('C')):
    # returns the semitone between before and after if possible
    # e.g. C,D -> C# ; 
    # steps above if there is already a leading tone
    # B,C -> C# ; C#,C -> B
    # otherwise returns semitone below
    # B,D -> C# ;
    # also returns start note and target on either side
    if abs(int(start) - int(target)) == 2:
        return [start, Note().from_int(int((int(start)+int(target))/2)), target], None
    elif abs(int(start) - int(target)) == 1:
        return [start, Note().from_int(int(start) + 2*(int(target) - int(start))), target], None
    else:
        return [start, Note().from_int(int(target) - 1), target], None

def replace_with_chromatic_enclosure(start=Note()):
    start = int(start)
    return [Note().from_int(start + 1), Note().from_int(start - 1), Note().from_int(start)], None

def random_walk(start=Note(), length=8, scale='chromatic', key='C'):
    jumps = choices(range(1,6), weights=[1/n for n in range(1,6)], k=length-1)
    directions = choices((1,-1), k=length-1)
    start_idx = int(start)
    shape_idx = [
        start_idx, 
        *[start_idx + jump for jump in accumulate([jump*direction for jump, direction in zip(jumps, directions)])]
        ]

    # now index the shape from the scale, adding octave adjustments where needed
    # note that scale could be any given list of notes (eg. as degrees or chromatic)
    scale = get_scale(scale, key)
    shape_from_scale = [scale[idx % len(scale)] for idx in shape_idx]
    octave_adjustments = [idx//len(scale) for idx in shape_idx]
    pattern_correct_octaves = [
        Note().from_int(int(note) + adj*12)
        for (note, adj) in zip(shape_from_scale, octave_adjustments)
        ]
    
    return pattern_correct_octaves, None

def random_arpeggiator(chord, k=8, **kwargs):
    return choices(from_shorthand(chord), k=k), None

GENERATIVE_CHUNKS = {
    'chromatic_approach': {
        'function': approach_with_chromatic_note,
    },
    'chromatic_enclosure': {
        'function': replace_with_chromatic_enclosure,
    },
    'random_walk': {
        'function': random_walk,
        'stochastic_dv': True,
    },
    'arpeggiator': {
        'function': random_arpeggiator,
        'stochastic_dv': True,
    }
}

def apply_cf(cf: str, **kwargs) -> List[Note]:
    if cf in DIATONIC_CHUNKS.keys():
        chunk = apply_diatonic_chunk(cf, **kwargs)
    elif cf in CHROMATIC_CHUNKS.keys():
        chunk = apply_chromatic_chunk(cf, **kwargs)
    elif cf in GENERATIVE_CHUNKS.keys():
        chunk = GENERATIVE_CHUNKS[cf]['function'](**kwargs)
    else:
        raise KeyError(f"Chunk func {cf} not found")
    return chunk

@lru_cache(None) # TODO update Python and this to @cache or other
def get_dv(cf: str) -> int:
    '''
    Returns pitch distance (#semi) between first and last notes of a chunk func, cf.
    '''
    if cf in GENERATIVE_CHUNKS.keys():
        try:
            if GENERATIVE_CHUNKS[cf]['stochastic_dv']:
                return 999 # we can't give a reliable dv for stochastic cf
        except KeyError:
            pass
    chunk = apply_cf(cf)[0]
    return int(chunk[-1]) - int(chunk[0])

@lru_cache(None) # TODO update Python and this to @cache or other
def get_dh(cf: str) -> int:
    '''
    Returns total duration (4.0=qn) between first and last notes of a chunk func, cf.
    Return None if duration is not fixed (i.e. can be flexible for user).
    '''
    if cf in DIATONIC_CHUNKS.keys():
        if DIATONIC_CHUNKS[cf]['durations'] is None:
            return None
        else:
            return total_duration(DIATONIC_CHUNKS[cf]['durations'])
    elif cf in CHROMATIC_CHUNKS.keys():
        if CHROMATIC_CHUNKS[cf]['durations'] is None:
            return None
        else:
            return total_duration(CHROMATIC_CHUNKS[cf]['durations'])
    elif cf in GENERATIVE_CHUNKS.keys():
        # chunk = GENERATIVE_CHUNKS[cf]['function']()
        return None # none of these have fixed duration
    raise KeyError(f"Chunk func {cf} not found")

def check_cf_dh(dh, cfs, greedy=True):
    hits = []
    for cf in cfs:
        cf_dh = get_dh(cf)
        # print(f'{cf} dh: {cf_dh}')
        if cf_dh == dh or cf_dh is None:
            if greedy:
                return cf
            else:
                hits.append(cf)
        else:
            pass
    if len(hits) == 0:
        return None
    else:
        return hits

# TODO refactor...
def check_cf_dv_dh(dv, dh, cfs, greedy=True):
    hits = []
    for cf in cfs:
        cf_dv = get_dv(cf)
        # print(f'{cf} dv: {cf_dv}')
        if cf_dv == dv or cf_dv is None:
            matching_dh = check_cf_dh(dh, [cf], greedy=greedy)
            if matching_dh:
                if greedy: # returns str
                    return matching_dh
                else: # returns list
                    hits.append(matching_dh)
            else:
                pass
        else:
            pass
    if len(hits) == 0:
        return None
    else:
        return hits