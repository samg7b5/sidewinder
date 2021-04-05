# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 19:38:09 2019

@author: Sam
"""
from sidewinder import Chart
from sidewinder.voicings.voicings import voice_chords
from sidewinder.voicings.voice_leading import smooth_voice_leading
from sidewinder.melodies.basslines import create_walking_bassline
from sidewinder.utilities import notes_durations_to_track, track_to_midi
from mingus import *
from mingus.containers import Note

#%% Playing with progressions and standards

# 1. Numerals -> midi
misty = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
         IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
         v-7, I7b9, IVM7, IVM7,\
         bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
         IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
              1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
              1, 1, 1, 1, 
              1, 2, 2, 2, 2, 2, 2, 
              1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

# load the variables into a Chart
mistyChart = Chart(progression=misty, key='F')
mistyChart.set_durations(durations=misty_durs)

# voice the (auto-generated) shorthand chords, and export the (voiced chords, durations) as midi
print(mistyChart.progressionShorthandList)
voiced_chords = voice_chords(mistyChart.progressionShorthandList, voicing_type='rootless', type='A')
track_to_midi(notes_durations_to_track(voiced_chords, mistyChart.durations), name='midi_out\\misty_rootlessA_example', timestamp=False)

# generate a walking bassline and export as midi
bassline_track = create_walking_bassline(mistyChart.progressionShorthandList, mistyChart.durations)
track_to_midi(bassline_track, name='midi_out\\misty_wb_example', timestamp=False)

# TO-DO: detect all 2-5's
#two_fives = sw.detect_numeral_pattern(misty, pattern=['II-7','V7'])


# 2. Shorthand -> midi
giant_steps = 'Abmaj7, B7, Emaj7, G7, Cmaj7, F#-7, B7, Emaj7, G7, Cmaj7, Eb7, Abmaj7, D-7, G7, Cmaj7, F#-7, B7, Emaj7, Bb-7, Eb7, Abmaj7, D-7, G7, Cmaj7, Bb-7, Eb7'
bt2 = [2,2]
giant_steps_durs = 2*bt2 + [1] + 3*bt2 + [1] + 4*(bt2 + [1]) + bt2

gsChart = Chart(progression=giant_steps)
gsChart.set_durations(durations=giant_steps_durs)

print(gsChart.get_numeral_representation(key='Ab'))

smooth_voiced_chords = smooth_voice_leading(voice_chords(gsChart.progressionShorthandList))
track_to_midi(notes_durations_to_track(smooth_voiced_chords, gsChart.durations), name='midi_out\\giant-steps_smooth-voice-leading_example', timestamp=False)

#%% Generating scale patterns for practice exercises

# 3. 10 Warmup Exercises Every Jazz Musician Should Know
#    inspired by Chad LB https://www.youtube.com/watch?v=hOQL9grV7Lw
# I realise this code doesn't look the nicest but most of it is just basic data-wrangling of the get_scale_patterns() output

from sidewinder.utilities import cycle_of_fifths, get_scale, note_to_scale_degree
from sidewinder.melodies.patterns import get_scale_patterns
from collections import OrderedDict


# 3.1 1234 shape
asc = [1,2,3,4,5,4,3,1]
desc = [1,2,3,4,3,2,1,6]
desc = [8,9,10,11,10,9,8,6] # actually want to jump down to the 6th, so we should re-write it like this

exercises = {}
exercises[0] = None
exercises[1] = get_scale_patterns('Major', p=asc, keys=cycle_of_fifths()) 
exercises[2] = get_scale_patterns('Major', p=desc, keys=cycle_of_fifths(), descending=True)


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
        # unchanged apart from the 8th note
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
        # unchanged apart from the 8th note
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
arp7 = [1,3,5,7,8,10,12,14,15,14,12,10,8,7,5,3,1] # TODO: does this work?
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
    print(f'{sd}: {note.name}, {chrom}') # this tells us what integer to use in get_scale_patterns, and also what chromatic interval it represents
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
print(f'Choices are {triad1_name} and {triad2_name}')

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
print(exercises[17])


# 3.10 triplet approach notes





  
        

# %%
