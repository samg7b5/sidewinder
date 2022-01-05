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

from sidewinder.utilities import (
    parse_progression, 
    numerals_list_to_shorthand_list, 
    shorthand_list_to_numerals_list, 
    reduce_to_seventh_chord,
    reduce_to_triad,
    synonyms,
    )


class Chart():
    def __init__(self, progression=None, key=None):
        '''
        progression: string or list of strings, in either numeral (I7 etc) or shorthand (CM7 etc) form, and will get parsed into various formats and stored as object internals
        key: string (e.g. 'C')
        '''
        self.progressionNumeralsList = None
        self.progressionRawShorthandString = None
        self.progressionShorthandList = None
        self.progressionShorthandTuplesList = None
        self.key = key

        self.durations = None # will be set by self.set_durations()

        # initial parsing of progression which may arrive in various formats; populate internal representations as best as possible
        if progression is not None:
            if progression[0][0] in ['I', 'V', 'i', 'v'] or progression[0][:2].lower() in ['bi','bv']:
                self.progressionNumeralsList = parse_progression(progression)
                parse_key = self.key if self.key else 'C'
                self.progressionShorthandList = numerals_list_to_shorthand_list(self.progressionNumeralsList, key=parse_key) # ['Dm7', 'Gdom7', 'CM7']
            else: # if shorthand str or shorthand list
                if type(progression) == str:
                    self.progressionRawShorthandString = progression
                self.progressionShorthandList = parse_progression(progression) # ['Dm7', 'Gdom7', 'CM7']
            self.progressionShorthandTuplesList = [chords.chord_note_and_family(chord) for chord in self.progressionShorthandList] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]

    def __repr__(self):
        return ', '.join(self.get_numeral_representation())

    def get_numeral_representation(self, key=None):
        if key is None: 
            key = self.key # https://stackoverflow.com/questions/1802971/nameerror-name-self-is-not-defined
            if key is None:
                key = 'C'
        return shorthand_list_to_numerals_list(self.progressionShorthandList, key=key)

    def get_simplified_numeral_representation(self, type='triad'):
        reduce_func = {
            'triad': reduce_to_triad,
            'seventh': reduce_to_seventh_chord,
        }
        # this feels slightly circular..?
        return Chart([reduce_func[type](chord) for chord in self.progressionShorthandList], key=self.key).get_numeral_representation()

    def set_durations(self, durations=None):
        if durations is None:
            self.durations = len(self.progressionShorthandList)*[1]
        else:
            if len(durations) != len(self.progressionShorthandList):
                print(f'Warning: length mismatch with supplied duration, got {len(durations)} expected {len(self.progressionShorthandList)}')
            self.durations = durations


#%% Analysis
def detect_numeral_pattern(progression, pattern=['IIm7','V7','IM7'], transposing=True, original_key='C'):
    '''
    Input progression should be in numeral format
    pattern is the target chunk to find
    Transposing option is to detect the pattern outside of the original key
    '''
    progression = parse_progression(progression)
    pattern = parse_progression(pattern)
    window_size = len(pattern)

    if pattern == parse_progression(['IIm7','V7','IM7']):
        print('sidewinder.detect_numeral_pattern: did you also want to look for [IIm7,V7,IM6] ?')
    
    out = {
            'hits':[],
            'transposed_hits':[],
          }
    for i in range(0, len(progression)-window_size+1):
        passage = progression[i:i+window_size]
        if passage == pattern:
            out['hits'].append({'start_index':i,'chords':[chord.replace('dom','') for chord in passage],'key':original_key})
            
    if transposing:
        for i in range(0, len(progression)-window_size+1):
            passage = progression[i:i+window_size]
 
            for key in ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']:
                transposed_passage = progressions.to_chords(passage, original_key)
                transposed_pattern = progressions.to_chords(pattern, key)
                
                if transposed_passage == transposed_pattern and not key == original_key:
                    out['transposed_hits'].append({'start_index':i,'chords':[chord.replace('dom','') for chord in passage],'key':key})
        
    return out
        
