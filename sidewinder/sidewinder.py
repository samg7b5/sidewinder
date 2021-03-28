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

import sidewinder.utilities as utilities # aim to remove this line
from sidewinder.utilities import parse_progression, numerals_list_to_shorthand_list, shorthand_list_to_numerals_list

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


class Chart():
    def __init__(self, progression='Dm7, G7, CM7', key='C'):
        '''
        progression can be a string or list, in either numeral (I7 etc) or shorthand (CM7 etc) form, and will get parsed into various formats and stored as object internals
        '''
        
        self.progressionNumeralsList = None
        self.progressionRawShorthandString = None
        self.progressionShorthandList = None
        self.progressionShorthandTuplesList = None
        
        self.key = key

        if progression is not None:
            if progression[0][0] in ['I', 'V', 'i', 'v']:
                self.progressionNumeralsList = utilities.parse_progression(progression)
                self.progressionShorthandList = numerals_list_to_shorthand_list(self.progressionNumeralsList, key=self.key) # ['Dm7', 'Gdom7', 'CM7']
            else: # if shorthand str or shorthand list
                if type(progression) == str:
                    self.progressionRawShorthandString = progression
                self.progressionShorthandList = utilities.parse_progression(progression) # ['Dm7', 'Gdom7', 'CM7']
            self.progressionShorthandTuplesList = [chords.chord_note_and_family(chord) for chord in self.progressionShorthandList] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]


#%% Chords
    
def chords_to_midi(progression=['Dm7', 'G7', 'CM7'], durations=None, voicing='smooth', name='..\\midi_out\\untitled', key='C', save=True, prog_type='shorthand', **kwargs):
    '''
    Generate and export a basic midi file for given chord progression.
    Progression can be as shorthand (e.g. Am7) or Roman numerals (e.g. VIm7)
    
    Durations should be a list of integers e.g. [2,2,1] will give | chord 1 chord 2 | chord 3 |
    
    TO-DO: 
        - mingus durations are limited to =< 1 bar; we want to be able to parse a duration of '0.5' (because in mingus '4'=crotchet i.e. num subdivs) to refer to 2 bars (just use 1/d)
    '''

    # TO-DO: factor out PROGRESSION HANDLING logic
    progression = utilities.parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]
        



        
        
    # TO-DO: factor out VOICINGS logic  
    if voicing == 'smooth':
        voiced_chords = utilities.smooth_voice_leading(progression, durations, prog_type)
    elif voicing == 'shell':
        voiced_chords = utilities.shell_voice(progression, durations, prog_type, **kwargs)
    elif voicing == 'rootless':
        voiced_chords = utilities.rootless_voice(progression, durations, prog_type, **kwargs)

    t = utilities.chords_to_track(voiced_chords, durations) # REFACTORING: where does this line go? potentially part as 'I want output X' logic within overall workflow (which would also include midi as an option)

    
    
    
    
    # MIDI logic
    if name == 'midi_out\\untitled':
        name += datetime.now().strftime('%Y%m%d%H%M%S')    

    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
    return t

def chords_to_bassline_midi(progression=['Dm7','G7','CM7'], durations=None, walking=True, name='midi_out\\bassline', key='C', save=True):
        
    # REFACTORING: take inspiration from chords_to_midi()
    
    # PROGRESSION logic
    progression = utilities.parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]

    # numeral_to_sh (-> PROGRESSION logic)    
    if progression[0][0] in ['I', 'V', 'i', 'v']:
        progression = [progressions.to_chords(chord)[0] for chord in progression]
        progression = [chords.determine(chord, shorthand=True)[0] for chord in progression] # shorthand e.g. Dm7
        
    
    # chord_tuple_list
    # REFACTORING: this looks different to progressions, is this separate chord logic? looks like a raw mingus import actually, so be clever in where this goes (maybe as part of the overall workflow logic)
    chords_ = [chords.chord_note_and_family(chord) for chord in progression] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]
    
    
    # REFACTORING: having a specific _bassline function seems like a quick hack - now we should generalise to horizontal composition (where voicings are vertical composition)
    # for chords_to_track refactoring, see function above (tease apart 'horizontal' (eg walking) and 'output' (eg track->midi) logic/choices)
    bassline = [Note(chord[0], octave=3) for chord in chords_]
    t = utilities.chords_to_track(bassline, durations)
    if walking:
        bassline, durations = utilities.create_walking_bassline(chords_, durations)
        t = utilities.chords_to_track(bassline, durations)
    
    # MIDI logic
    if name == 'midi_out\\bassline':
        name += datetime.now().strftime('%Y%m%d%H%M%S')
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
    # REFACTORING: PROGRESSION logic
    progression = utilities.parse_progression(progression)
    pattern = utilities.parse_progression(pattern)
    
    
    
    
    # REFACTORING: looks like we can keep the rest of the code as a detect_numeral_pattern Progression method 
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
        
    
    
 

    
    
    
    