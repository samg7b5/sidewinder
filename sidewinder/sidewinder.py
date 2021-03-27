# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 21:11:45 2019

@author: Sam
"""
#from . import lick_library

from mingus.containers import Note
import mingus.core.progressions as progressions
from mingus.midi import midi_file_out
#from mingus.containers import Track, Bar
#from mingus.core import intervals
import mingus.core.scales as scales
import mingus.core.chords as chords

from datetime import datetime
#import numpy as np
#import random

import sidewinder.utilities as utilities

synonyms = {'C#':'Db',
            'D#':'Eb',
            'E':'Fb',
            'E#':'F',
            'F#':'Gb',
            'G#':'Ab',
            'A#':'Bb',
            'B':'Cb',
            'B#':'C'}
synonyms_r = {v:k for k,v in synonyms.items()}


#%% Chords
    
def chords_to_midi(progression=['Dm7', 'G7', 'CM7'], durations=None, voicing='smooth', name='..\\midi_out\\untitled', key='C', save=True, prog_type='shorthand', **kwargs):
    '''
    Generate and export a basic midi file for given chord progression.
    Progression can be as shorthand (e.g. Am7) or Roman numerals (e.g. VIm7)
    
    Durations should be a list of integers e.g. [2,2,1] will give | chord 1 chord 2 | chord 3 |
    
    TO-DO: 
        - mingus durations are limited to =< 1 bar; we want to be able to parse a duration of '0.5' (because in mingus '4'=crotchet i.e. num subdivs) to refer to 2 bars (just use 1/d)
    '''

    # Pre-processing and parsing
    if name == 'midi_out\\untitled':
        name += datetime.now().strftime('%Y%m%d%H%M%S')
    
    progression = utilities.parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]
        
    if progression[0][0] in ['I', 'V', 'i', 'v']:
        prog_type = 'numerals'
    
    # Apply voicings 
    if voicing == 'smooth':
        voiced_chords = utilities.smooth_voice_leading(progression, durations, prog_type)
    elif voicing == 'shell':
        voiced_chords = utilities.shell_voice(progression, durations, prog_type, **kwargs)
    elif voicing == 'rootless':
        voiced_chords = utilities.rootless_voice(progression, durations, prog_type, **kwargs)

    t = utilities.chords_to_track(voiced_chords, durations)

    # Export
    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
    return t

def chords_to_bassline_midi(progression=['Dm7','G7','CM7'], durations=None, walking=True, name='midi_out\\bassline', key='C', save=True):
    if name == 'midi_out\\bassline':
        name += datetime.now().strftime('%Y%m%d%H%M%S')
        
    progression = utilities.parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]
        
    if progression[0][0] in ['I', 'V', 'i', 'v']:
        progression = [progressions.to_chords(chord)[0] for chord in progression]
        progression = [chords.determine(chord, shorthand=True)[0] for chord in progression] # shorthand e.g. Dm7
        
    chords_ = [chords.chord_note_and_family(chord) for chord in progression] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]
    
    bassline = [Note(chord[0], octave=3) for chord in chords_]
    t = utilities.chords_to_track(bassline, durations)
    
    if walking:
        bassline, durations = utilities.create_walking_bassline(chords_, durations)
        t = utilities.chords_to_track(bassline, durations)
    
    # Export
    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
    return t



#%% Analysis
def detect_numeral_pattern(progression, pattern=['IIm7','V7','IM7'], transposing=True, original_key='C'):
    '''
    Input progression should be in numeral format
    Transposing option is to detect the pattern outside of the base key
    '''
    # parsing
    progression = utilities.parse_progression(progression)
    pattern = utilities.parse_progression(pattern)
    
    window_size = len(pattern)
    
    hits = []
    for i in range(0, len(progression)-window_size+1):
        passage = progression[i:i+window_size]
        if passage == pattern:
            hits.append(i)
            
    if transposing:
        transposed_hits = []
        for i in range(0, len(progression)-window_size+1):
            passage = progression[i:i+window_size]
 
            for key in ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']:
                transposed_passage = progressions.to_chords(passage, original_key)
                transposed_pattern = progressions.to_chords(pattern, key)
                
                if transposed_passage == transposed_pattern:
                    transposed_hits.append((i,[chord.replace('dom','') for chord in passage],key))
        hits = [hits, transposed_hits]
        
    return hits
        

def shorthand_to_numerals(progression='Cmaj7, G-7, C7, Fmaj7, Bb7', key='C'):
    progression = utilities.parse_progression(progression)
    
    def get_note(symbol):
        if symbol[1] == '#' or symbol[1] == 'b':
            return symbol[0:2]
        else:
            return symbol[0]
        
    proc_progression = [[get_note(chord), chord[len(get_note(chord)):]] for chord in progression]
    
    scale = scales.Chromatic(key)
    scale_list = []
    for i in range(0, len(scale)-1):
        x = scale.degree(i+1)
        if '##' in x:
            x = chr(ord(x[0])+1)
        
        scale_list.append(x)
    chromatic_numerals = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']
    
    numerals_progression = []
    for i, chord in enumerate(proc_progression):
        
        stem = chord[1]
        
        try:
            numeral = chromatic_numerals[scale_list.index(chord[0])]
        except ValueError:
            try:
                numeral = chromatic_numerals[scale_list.index(synonyms[chord[0]])]
            except KeyError:
                numeral = chromatic_numerals[scale_list.index(synonyms_r[chord[0]])]
            
        numerals_progression.append(numeral+stem)
    
    return numerals_progression


    
    
    
    