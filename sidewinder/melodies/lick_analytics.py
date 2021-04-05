# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:03:27 2020

Temporary structure for functions to process and analyse licks (melodic lines)

@author: Sam
"""
from utilities import synonyms

import mingus.core.scales as scales



chromatic_scale_degrees = [['1'],
                           ['b9','b2'], 
                           ['9','2'], 
                           ['b3','#9'], 
                           ['3'], 
                           ['4','11'], 
                           ['#11','#4','b5'],
                           ['5'],
                           ['b6','#5','b13'],
                           ['6','13'],
                           ['b7'],
                           ['7']]
                           
def note_to_scale_degree(note, key, scale, label_nondiatonic=True, chromatic_options=False): # note as str for simplicity e.g. note.name
    # get scale
    scale = get_scale(scale)
    
    # double accidental correction 
    try: 
        note = malformed_double_accidentals[note] # these examples wouldn't work in the chr(ord()) code below
    except KeyError:
        pass 
    if '##' in note:
            note = chr(ord(note[0])+1)
    if 'bb' in note:
            note = chr(ord(note[0])-1)
    
    try:
        scale_idx = scale_notes.index(note)
    except ValueError:
        try: 
            scale_idx = scale_notes.index(synonyms[note])
        except (KeyError, ValueError):
            if label_nondiatonic:
                return (False, note_to_scale_degree(note, key, 'chromatic', chromatic_options=chromatic_options)) # not in scale
            else:
                return False
    
    if scale == 'chromatic':
        if chromatic_options:
            return chromatic_scale_degrees[scale_idx]
        else:
            return chromatic_scale_degrees[scale_idx][0]
        
    else:
        return scale_idx + 1 # e.g. output of 7 means this is the 7th (major or minor) diatonic to the given scale 
    
def scale_as_degrees(scale, **kwargs):
    '''returns the chromatic description of a scale, e.g. mixolydian as 1 2(9) 3 4 5 6 b7'''
    scale = scale.lower()
    try:
        scale_length = scale_lengths[scale]
    except KeyError:
        scale_length = 7
    scale_notes = list(scale_gens[scale]('C').generate(scale_length))
    return [note_to_scale_degree(note, 'C', 'chromatic', **kwargs) for note in scale_notes]

def track_to_degrees(track, key, scale, **kwargs):
    notes = [notev[2] for notev in track.get_notes()] # gives a list of NoteContainers
    note_names = [[note.name for note in nc] for nc in notes] # since each nc could contain multiple Note()'s
    return [[note_to_scale_degree(x, key, scale, **kwargs) for x in nc] for nc in note_names]

