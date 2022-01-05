import numpy as np
from mingus.containers import Note
import mingus.core.chords as chords

from sidewinder.utilities import move_b_above_a_with_modularity

def minimal_chord_distance(source_chord, target_chord):
    source_chord = [int(note) for note in source_chord]
    target_chord = [int(note) for note in target_chord]
    distance = 0
    if len(source_chord) == 0: # no constraints when following a rest
        return distance
    for target_note in target_chord:
        distance += min([abs(target_note - source_note) for source_note in source_chord])
    return distance

def rebuild_chord_upwards(chord): 
    chord = [int(Note(note)) for note in chord] # Note() to int
    a = chord[0]
    for i, b in enumerate(chord[1:]):
        b = move_b_above_a_with_modularity(a,b,12)
        chord[i+1] = b
        a = b
    return chord

def rebuild_chord_inwards(chord):
    '''
    Expects a list of Note strings
    '''
    chord = [int(Note(note)) for note in chord] # Note() to int
    a = chord[0]
    for i, b in enumerate(chord[1:]):
        b = np.floor(a/12)*12 + np.mod(b, 12)
        chord[i+1] = b
        a = b
    return chord
 
def generate_chord_inversions(chord): # works on semitones
    inversions = [[chord[p - q] for p in range(len(chord))] for q in range(len(chord))]
    for i, chord in enumerate(inversions):
        inversions[i] = rebuild_chord_upwards(chord)
    return inversions

def generate_close_chords(chord):
    '''
    Works on lists (individual elements could be int or str)
    '''
    inversions = [[chord[p - q] for p in range(len(chord))] for q in range(len(chord))]
    for i, chord in enumerate(inversions):
        inversions[i] = rebuild_chord_inwards(chord)
    return inversions

def add_bass_note_to_slash_chord(chord):
    # e.g. C7/E should have E in the bass (when various voicings are applied)
    chord_root = chord[0]
    chord_type = chord[1]
    if '/' in chord_type:
        print('TO-DO: handle slash chords at a more macro level, e.g. have a function which adds bass note to any slash chord voicing')
        slash_chord = True
        bass_note = ''.join(chord_type.split('/')[1:])
    return None
