import random

from mingus.containers import Note
from mingus.core.chords import from_shorthand, chord_note_and_family
from sidewinder.utilities import notes_durations_to_track
from sidewinder.voicings.voicings import voice_chords
from sidewinder.voicings.voicing_utilities import rebuild_chord_upwards

def simple_bassline(_chords, durations=None):
    '''
    params:
      - _chords as a list of shorthand chord symbols
      - durations as list of integers (for each chord)

    returns a Track playing the root of each chord, for each respective duration
    '''
    if durations is None:
        durations = [1]*len(_chords)

    bassline = voice_chords(_chords, voicing_type='root')
    bassline = notes_durations_to_track(bassline, durations)
    return bassline

def create_walking_bassline(_chords, durations=None):
    '''
    Will assume 4/4 and create patterns like http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chord-voicings/walking-bass-lines/
    
    params:
      - _chords as a list of shorthand symbols
      - durations as list of integers (for each chord)
    '''
    chords_ = [chord_note_and_family(c) for c in _chords]

    if durations is None:
        durations = [1]*len(chords_)
    
    variants = ['pedal', 'arp7', 'arp', 'diat', 'chrom', 'dblchrm']
    variant_weights = [.5,5,5,2,.5,.3]
    styles = random.choices(population=variants, weights=variant_weights, k=len(chords_))
    
    bassline = []
    new_durations = []
    for i, chord in enumerate(chords_):
        new_dur = [4,4,4,4] # by default a full bar becomes 4 crotchets (TO-DO: add more variation)
        
        chord = rebuild_chord_upwards([Note(n) for n in from_shorthand(chords_[i][0]+chords_[i][1])]) # ints
        style = styles[i]
        if style == 'pedal':
            basspattern = [chord[0]]*4
        elif style == 'arp7':
            basspattern = [chord[0], chord[1], chord[2], chord[-1]] # get last in case triad (won't have a seventh)
        elif style == 'arp':
            basspattern = [chord[0], chord[1], chord[2], chord[1]] # root, 3rd, 5th, 3rd 
        elif style == 'diat':
            if chords_[i][1] == 'M7' or chords_[i][1] == 'Maj7':
                basspattern = [chord[0], chord[1], chord[2], chord[1]] # root, 3rd, 5th, 3rd
            else:
                basspattern = [chord[0], chord[0]+2, chord[1], chord[2]] # TO-DO chords from other modes will need adjustment e.g. b9
        elif style == 'chrom':
            if 'minMaj' in chords_[i][1]:
                basspattern = [chord[0], chord[1], chord[2], chord[3]] # root, 3rd, 5th, 7th
            elif 'm' in chords_[i][1]:
                basspattern = [chord[0], chord[1], chord[2]-1, chord[1]+1] # root, minor 3, flat 5, b11 (leading tone for V/II-7)
            elif 'M' in chords_[i][1]:
                basspattern = [chord[0], chord[0]+1, chord[0]+2, chord[2]] # root, b9, 2, 5th
            elif chords_[i][1] in ['7','7b9']:
                basspattern = [chord[0], chord[1], chord[2], chord[0]+1] # root, 3rd, 5th, b9
            elif chords_[i][1] in ['9']:
                basspattern = [chord[0],chord[1],chord[0]+2,chord[3]-12] # root, 3rd, 9th, down to b7
            else:
                print(f'No chromatic basspattern given for chord type {chords_[i][1]}')
        elif style == 'dblchrm':
            if chords_[i][1] == 'M7' or chords_[i][1] == 'Maj7':
                basspattern = [chord[0], chord[2], chord[2]+2, chord[0]+1] # root, 5th, 6th, b9
            else:
                basspattern = [chord[0], chord[0], chord[2]-1, chord[2]-1] # root, root, b5, b5
                       
        # TO-DO: need to drop octaves where we end up going to high...
                
        if durations[i] == 2:
            basspattern = [basspattern[0], basspattern[3]]
            new_dur = [4,4]
        if durations[i] == 4:
            basspattern = [basspattern[0]]
            new_dur = [4]
        
        bassline.append(basspattern) # as list of sublists of ints (one sublist per bar)
        new_durations += new_dur
        
    amount_of_extra_leading_tones = 0.25
    for i, chord in enumerate(chords_):
        roll = random.random()
        if roll < amount_of_extra_leading_tones and i < len(chords_)-1:
            next_root = bassline[i+1][0]
            bassline[i][-1] = next_root - 1
            
    bassline = notes_durations_to_track([Note().from_int(int(n)-12) for b in bassline for n in b], new_durations) # - 12 to bring down to octave 3
    return bassline

