import numpy as np
from mingus.containers import Note
import mingus.core.chords as chords

def smooth_next_chord(voiceA, chordB):
    '''
    voiceA is a list of ints
    chordB is a list of Notes e.g. [Note('C-4'), ...] 
    '''
    inversions = generate_close_chords(chordB)
    distances = [minimal_chord_distance(voiceA, inversion) for inversion in inversions]
    voiceB = inversions[np.argmin(distances)]
    return voiceB

def smooth_voice_leading(progression, durations, prog_type='shorthand'):
    
    chords_ = progression_to_chords(progression, prog_type)
    # here, chords_ is a list of lists [['C', 'E', 'G', 'B'],...] (which will default to octave as C-4 etc in chords_to_track)
    
    track = chords_to_track(chords_, durations)
    
    voiced_chords = []
    for i, event in enumerate(track):
        chord = event[0][2] # current chord, to align with previous (if i>0); as voiced str ['C-4', 'E-4', 'G-4']
        if i == 0:
            voiced_chords.append([int(note) for note in chord]) # converted into ints
        if i>0:
            voiced_chords.append(smooth_next_chord(voiced_chords[i-1], chord))
    
    voiced_chords = [[Note().from_int(int(note)) for note in chord] for chord in voiced_chords]
    return voiced_chords
