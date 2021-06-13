# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 19:38:09 2019

@author: Sam
"""
from collections import OrderedDict
from sidewinder.melodies.patterns import get_scale_patterns
from sidewinder.utilities import notes_durations_to_track, track_to_midi, cycle_of_fifths, get_scale, note_to_scale_degree
from mingus import *
from mingus.containers import Note

def flatten(myList):
    if type(myList[0]) == list:
        return flatten([element for sublist in myList for element in sublist])
    else:
        return myList

# 3) Generating scale patterns based on 10 Warmup Exercises Every Jazz Musician Should Know
#    inspired by Chad LB https://www.youtube.com/watch?v=hOQL9grV7Lw
#    This example generates midi files for 17 different scale patterns.

# 3.1 1234 shape

# Start by specifying a pattern in terms of "diatonic scale degrees" e.g. 3 over a minor scale will give you a flat 3
asc = [1,2,3,4,5,4,3,1]
desc = [1,2,3,4,3,2,1,6]
desc = [8,9,10,11,10,9,8,6] # in this example we actually want to jump down to the 6th from the 1, so we should re-write up the octave like this

# I'm going to save the results into a dictionary since I'm going to be making more
exercises = {}
exercises[0] = None
exercises[1] = get_scale_patterns('Major', p=asc, keys=cycle_of_fifths()) 
exercises[2] = get_scale_patterns('Major', p=desc, keys=cycle_of_fifths(), descending=True)

# get_scale_patterns() returns us an OrderedDict so this code is just navigating that structure
for i in [1,2]:
    _notes = []
    for key in list(exercises[i].keys()):
        _notes += flatten(exercises[i][key])
    track_to_midi(notes_durations_to_track(_notes, [8]*len(_notes)), name=f'midi_out\\ChadLB_Warmups_{i}', timestamp=False) # save it to midi (I'm putting everything as 8th notes)


# Let's do some more... Most of the following code is navigating the OrderedDicts and making ad hoc tweaks to patterns

# 3.2 1234 with chromatic approach
## replace the 8th note of each group with a leading tone
## e.g. C D E F G F E C, D E F G A G F D, E F G ...
## ==>  C D E F G F E _D#_, D E F G A G F _Eb_, E F G ...
## using the rule: if n[i-1] - n[i+1] is a tone, then n[i] is the semitone in between, otherwise n[i-1] - n[i+1] is a semitone and n[i] is the semitone below n[i+1]

def replace_with_chromatic_note(before, after):
    if abs(int(before) - int(after)) == 2:
        return Note().from_int(int((int(before)+int(after))/2))
    else:
        return Note().from_int(int(before) + 2*(int(after) - int(before)))

prev_ex = 1
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    prev_exercise_flattened = [note for start_position in exercises[prev_ex][key] for note in start_position]
    for i, n in enumerate(prev_exercise_flattened):
        # unchanged apart from the 8th note (the `else`)
        if ((i+1) % 8 != 0):
            new_exercise[key].append(n)
        else:
            try:
                new_exercise[key].append(replace_with_chromatic_note(prev_exercise_flattened[i-1], prev_exercise_flattened[i+1]))
            except IndexError:
                new_exercise[key].append(replace_with_chromatic_note(prev_exercise_flattened[i-1], Note().from_int(int(prev_exercise_flattened[0]) + 12)))
exercises[3] = new_exercise.copy()

prev_ex = 2
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    prev_exercise_flattened = [note for start_position in exercises[prev_ex][key] for note in start_position]
    for i, n in enumerate(prev_exercise_flattened):
        # unchanged apart from the 8th note (the `else`)
        if ((i+1) % 8 != 0):
            new_exercise[key].append(n)
        else:
            try:
                new_exercise[key].append(replace_with_chromatic_note(prev_exercise_flattened[i-1], prev_exercise_flattened[i+1]))
            except IndexError:
                new_exercise[key].append(replace_with_chromatic_note(prev_exercise_flattened[i-1], Note().from_int(int(prev_exercise_flattened[0]) - 12)))
exercises[4] = new_exercise.copy()
    

# 3.3  1235 shape
asc = [1,2,3,5,4,3,2,1]
desc = asc

exercises[5] = get_scale_patterns('Major', p=asc, keys=cycle_of_fifths()) 
exercises[6] = get_scale_patterns('Major', p=desc, keys=cycle_of_fifths(), descending=True)


# 3.4 1235 with enclosure
def replace_with_chromatic_enclosure(start):
    start = int(start)
    return [Note().from_int(start), Note().from_int(start - 1), Note().from_int(start - 2), Note().from_int(start - 4)]

## ascending
prev_ex = 5
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    for start_position_chunk in exercises[prev_ex][key]:
        for i, n in enumerate(start_position_chunk):
            # unchanged apart from the 5th note of every 8
            if ((i+4) % 8 != 0):
                new_exercise[key].append(n)
            else:
                new_exercise[key] += replace_with_chromatic_enclosure(start_position_chunk[i])
                break
    # the pattern can give something like 'E-4', 'F-4', 'G-4', 'B-4', 'A-4', 'G#-4', 'G-4', 'F-4', 'F-4', 'G-4', 'A-4', 'C-5', ... so let's ensure we have leading tones
    for i in range(len(new_exercise[key])-1):
        if new_exercise[key][i] == new_exercise[key][i+1]:
            new_exercise[key][i] = Note().from_int(int(new_exercise[key][i]) - 1)
exercises[7] = new_exercise.copy()

## descending
desc2 = [1,2,3,1,2]
exercises[8] = get_scale_patterns('Major', p=desc2, keys=cycle_of_fifths(), descending=True)
prev_ex = 8
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    for start_position_chunk in exercises[prev_ex][key]:
        for i, n in enumerate(start_position_chunk):
            # unchanged apart from the 5th note of every 8
            if ((i+4) % 8 != 0):
                new_exercise[key].append(n)
            else:
                new_exercise[key] += replace_with_chromatic_enclosure(start_position_chunk[i])
                break
    for i in range(len(new_exercise[key])-1):
        if new_exercise[key][i] == new_exercise[key][i+1]:
            new_exercise[key][i] = Note().from_int(int(new_exercise[key][i]) - 1)
exercises[9] = new_exercise.copy()


# 3.5 arpeggiate up/down scale
arp7 = [1,3,5,7,8,7,5,3,1]
arp7 = [1,3,5,7,8,10,12,14,15,14,12,10,8,7,5,3,1] # extend up octaves with +7s
exercises[10] = get_scale_patterns('Major', p=arp7, keys=cycle_of_fifths()) 
exercises[11] = get_scale_patterns('Major', p=arp7, keys=cycle_of_fifths(), descending=True)


# 3.6 add a chromatic approach note to every note in the previous exercise (!)
prev_ex = 10
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    for note_chunk in exercises[prev_ex][key]:
        for note in note_chunk:
            new_exercise[key] += [Note().from_int(int(note)-1), note] # add a leading tone (from below) to every note
exercises[12] = new_exercise.copy()
    
prev_ex = 11
new_exercise = OrderedDict()
keys = list(exercises[prev_ex].keys())
for key in keys:
    new_exercise[key] = []
    for note_chunk in exercises[prev_ex][key]:
        for note in note_chunk:
            new_exercise[key] += [Note().from_int(int(note)-1), note] # add a leading tone (from below) to every note
exercises[13] = new_exercise.copy()


# 3.7 pentatonics
scale_choice = 'minor pentatonic'
keys = cycle_of_fifths()
p = ['1', 'b3', '4', '5', 'b7', '5', '4', '1'] # example where I know what I want in chromatic interval format
p2 = ['1','b7','5','4','b3','4','5','1']

scale = get_scale(scale_choice)
for note in scale:
    sd = note_to_scale_degree(note, 'C', scale_choice)
    chrom = note_to_scale_degree(note, 'C', 'chromatic')
    # print(f'{sd}: {note.name}, {chrom}') # this tells us what integer to use in get_scale_patterns, and also what chromatic interval it represents
chrom_to_pattern = {note_to_scale_degree(note, 'C', 'chromatic'): note_to_scale_degree(note, 'C', scale_choice) for note in scale}
exercises[14] = get_scale_patterns(scale_choice, p=[chrom_to_pattern[c] for c in p], keys=keys)
exercises[15] = get_scale_patterns(scale_choice, p=[chrom_to_pattern[c] for c in p2], keys=keys, descending=True)

# make octave fix ('1' is really an '8')
for key in list(exercises[15].keys()):
    for note_chunk in exercises[15][key]:
        note_chunk[0] = Note().from_int(int(note_chunk[0]) + 12) # can't just edit Note.octave as the ref is shared across the scale and key
        note_chunk[-1] = Note().from_int(int(note_chunk[-1]) + 12)


# 3.8 triad pairs (hexatonics)
key = 'D'
scale_choice = 'major'
triad_pair = [1,2] # 1 = I chord, 2 = II chord, etc.

triad_notes = [[1+i,3+i,5+i] for i in range(7)]
# restrict to a 7 note scale by getting note patterns which extend to higher octaves, then mapping back to scale degrees
# equivalently could calculate using [((n-1)%7)+1 for t in triad_notes for n in t]
triad_notes_norm = [note_to_scale_degree(note, 'C', scale_choice) for note in get_scale_patterns(scale_choice, [n for t in triad_notes for n in t])['C'][0]]
triad_notes_norm = [[t[0],t[1],t[2]] for t in [triad_notes_norm[3*i:3*i+3] for i in range(7)]] # unpack to same nested format

from mingus.core.chords import determine
triad1 = get_scale_patterns(scale_choice, p=triad_notes_norm[triad_pair[0]-1], keys=[key])[key][0]
triad2 = get_scale_patterns(scale_choice, p=triad_notes_norm[triad_pair[1]-1], keys=[key])[key][0]
triad1_name = determine([n.name for n in triad1])[0]
triad2_name = determine([n.name for n in triad2])[0]
# print(f'Choices are {triad1_name} and {triad2_name}')

# TODO: generate some triad pair patterns


# 3.9 chromatic cells
scale_choice = 'chromatic'
keys = ['C']#cycle_of_fifths()
p = ['1', '7', 'b7', '7'] 

scale = get_scale(scale_choice, key='C')
chrom_to_pattern = {note_to_scale_degree(note, 'C', 'chromatic'): i for i, note in enumerate(scale)}
exercises[17] = get_scale_patterns(scale_choice, p=[chrom_to_pattern[note]+1 for note in p], keys=keys)

# make octave fix ('1' is really an '8')
for key in list(exercises[17].keys()):
    for note_chunk in exercises[17][key]:
        note_chunk[0] = Note().from_int(int(note_chunk[0]) + 12) # can't just edit Note.octave as the ref is shared across the scale and key


# 3.10 triplet approach notes
scale_choice = 'major'
keys = ['C','G']

def replace_with_triplet_approach(start,end):
    start = int(start)
    end = int(end)
    if abs(end-start) == 3:
        return [Note().from_int(start), Note().from_int(start - 1), Note().from_int(start - 2)]
    else:
        return [Note().from_int(start), Note().from_int(start - 2), Note().from_int(start - 3)]

## ascending
p = [1,2,3,4,4,4]
first_pass = get_scale_patterns(scale_choice, p, keys=keys)
new_exercise = OrderedDict()
for key in list(first_pass.keys()):
    new_exercise[key] = []
    for j, start_position_chunk in enumerate(first_pass[key]):
        for i, n in enumerate(start_position_chunk):
            # unchanged apart from the 4th note of every 6
            if ((i+3) % 6 != 0):
                new_exercise[key].append(n)
            else:
                try:
                    target = first_pass[key][j+1][0]
                except IndexError:
                    target = int(first_pass[key][0][0])+12
                new_exercise[key] += replace_with_triplet_approach(n, target)
                break
exercises[18] = new_exercise.copy()

## descending
p = [1,2,3,2,2,2]
first_pass = get_scale_patterns(scale_choice, p, keys=keys, descending=True)
new_exercise = OrderedDict()
for key in list(first_pass.keys()):
    new_exercise[key] = []
    for j, start_position_chunk in enumerate(first_pass[key]):
        for i, n in enumerate(start_position_chunk):
            # unchanged apart from the 4th note of every 6
            if ((i+3) % 6 != 0):
                new_exercise[key].append(n)
            else:
                try:
                    target = first_pass[key][j+1][0]
                except IndexError:
                    target = int(first_pass[key][0][0])+12
                new_exercise[key] += replace_with_triplet_approach(n, target)
                break
exercises[19] = new_exercise.copy()


# Now let's export our exercises as midi
to_save = list(set(range(20)) - set([0,1,2,8,16]))
saving = True

if saving:
    for i in to_save:
        exercise = exercises[i] # OrderedDict
        _notes = []
        for key in list(exercise.keys()):
            _notes += flatten(exercise[key])
        track_to_midi(notes_durations_to_track(_notes, [8]*len(_notes)), name=f'midi_out\\ChadLB_Warmups_{i}', timestamp=False)