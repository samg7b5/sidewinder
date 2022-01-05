import numpy as np
from mingus.containers import Note
import mingus.core.chords as chords
from sidewinder.utilities import notes_durations_to_track
from sidewinder.voicings.voicing_utilities import *

def smooth_next_chord(voiceA, chordB):
    '''
    voiceA is a list of ints
    chordB is a list of Notes e.g. [Note('C-4'), ...] 
    '''
    inversions = generate_close_chords(chordB)
    distances = [minimal_chord_distance(voiceA, inversion) for inversion in inversions]
    voiceB = inversions[np.argmin(distances)] if len(distances) > 0 else inversions
    return voiceB

def smooth_voice_leading(_chords):
    '''
    _chords is a list of lists of Notes [['C', 'E', 'G', 'B'],...] 
    This function will permute the notes of _chords[n+1] to make it follow smoothly from _chords[n] 
    '''
    
    track = notes_durations_to_track(_chords)
    
    voiced_chords = []
    for i, event in enumerate(track):
        chord = event[0][2] # current chord, to align with previous (if i>0); as voiced str ['C-4', 'E-4', 'G-4']
        if i == 0:
            voiced_chords.append([int(note) for note in chord]) # converted into ints
        if i>0:
            prev_idx = i-1
            prev_chord = voiced_chords[prev_idx]
            while len(prev_chord) == 0:
                prev_idx -= 1
                try:
                    prev_chord = voiced_chords[prev_idx] # keep searching backwards for last non-rest
                    if prev_idx < 0:
                        raise IndexError
                except IndexError:
                    pass
            voiced_chords.append(smooth_next_chord(prev_chord, chord))
    
    voiced_chords = [[Note().from_int(int(note)) for note in chord] for chord in voiced_chords]
    return voiced_chords
