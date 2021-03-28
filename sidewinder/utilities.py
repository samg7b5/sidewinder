# -*- coding: utf-8 -*-
"""
Created on Fri May  8 10:11:04 2020

Holds utility-style functions that are used across different mid-level Sidewinder components

@author: Sam
"""
from mingus.containers import Note
import mingus.core.progressions as progressions
#from mingus.midi import midi_file_out
from mingus.containers import Track, Bar
from mingus.core import intervals
import mingus.core.scales as scales
import mingus.core.chords as chords

#from datetime import datetime
import numpy as np
import random

from typing import List

#%% misc 
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

def move_b_above_a_with_modularity(a,b,mod): # return min{x: x==b modulo 'mod' & x>a}
        b = np.mod(b, mod)
        while b < a:
            b+=mod
        return b


#%% Charts / Progressions
def parse_symbol(symbol):
    '''
        Notes:
        - Not sure mingus is consistent with lower-case numerals as minor or not (this is configures to expect - or m (or min I guess))
        - mingus progressions.to_chords() uses classical approach V7 = diatonic 7th, hence the 'dom' replacements

    '''
    return symbol.replace(' ','').replace('-','m').replace('maj','M').replace('i','I').replace('v','V').replace('I7','Idom7').replace('V7','Vdom7').replace('dom7b9','7b9').replace('mIn','min')   

def parse_progression(progression) -> List[str]:
    '''
    Code (e.g. mingus) will expect progressions as lists of shorthand chord strings.
    Sometimes a progression might be entered as a single string of comma-delimited shorthand chord symbols.
    This parsing function should be considered a general-purpose input sanitiser for shorthand progression strings.
    '''    
    if type(progression) == str:    
        return parse_symbol(progression).rstrip(' ').rstrip(',').split(',') 
    else:
        return [parse_symbol(chord) for chord in progression]

def numerals_list_to_shorthand_list(numerals, key='C'): 
        '''
        Convert numerals (e.g. ['IIm7', 'V7', 'IM7']) to shorthand (e.g. ['Dm7', 'Gdom7', 'CM7']) with optional choice of key (default is C)
        '''
        chord_notes = [progressions.to_chords(chord, key=key)[0] for chord in numerals] # chords as individual Notes like [['C','E','G','B'],...]
        return [chords.determine(chord, shorthand=True)[0] for chord in chord_notes] # shorthand e.g. ['CM7',...]

def shorthand_list_to_numerals_list(progression=['Cmaj7', 'G-7', 'C7', 'Fmaj7', 'Bb7'], key='C'):
    '''
    progression is a shorthand list or a raw shorthand string (either work since we use parse_progression() to be safe)
    returns chords as a list of numerals
    '''
    progression = parse_progression(progression)
    
    def get_note(symbol):
        if symbol[1] == '#' or symbol[1] == 'b':
            return symbol[0:2]
        else:
            return symbol[0]
        
    proc_progression = [[get_note(chord), chord[len(get_note(chord)):]] for chord in progression] # splits a shorthand (e.g. 'C#M7' -> ['C#','M7'])
    
    # the numeral is the note's index in the chromatic scale of this key
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

def progression_to_chords(progression, prog_type='shorthand'):
    '''
    progression is list of symbols -> chords_ is a list of unvoiced str e.g. as numerals ['I7', 'V7', 'II'] 
    and output is unvoiced chord strings -> [['C', 'E', 'G', 'Bb'], ...]
    
    NOTE: for numerals input, lower-case should not be used to imply minor (specify using '-', 'm', 'min')
    '''
    progression = parse_progression(progression) # to prevent mingus' diatonic parsing doing something like I7->Cmaj7
    if prog_type == 'shorthand': # e.g. Am7
        chords_ = [chords.from_shorthand(chord) for chord in progression]
    elif prog_type == 'numerals': # e.g. IIm7
        chords_ = [progressions.to_chords(chord)[0] for chord in progression]
    return chords_ #a list of lists [['C', 'E', 'G', 'B'],...]

#%% Chords


def chords_to_track(chords, durations):
    t = Track()
    for i, chord in enumerate(chords):
        b = Bar()
        b.place_notes(chord, durations[i]) # default octave is ['C','E','G']->['C-4','E-4','G-4'] (this is the first instance of voicing)
        t.add_bar(b)
    return t



#%% Generative
        
def create_walking_bassline(chords_, durations):
    '''
    Will assume 4/4 and create patterns like http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chord-voicings/walking-bass-lines/
    
    chords_ in the form [chords.chord_note_and_family(chord) for chord in prog] e.g. [('D', 'm7'), ('G', '7'), ('C', 'M7')]
    '''
    variants = ['pedal', 'arp7', 'arp', 'diat', 'chrom', 'dblchrm']
    variant_weights = [0.5,5,5,2,1,0.5]
    styles = random.choices(population=variants, weights=variant_weights, k=len(chords_))
    
    bassline = []
    new_durations = []
    for i, chord in enumerate(chords_):
        new_dur = [4,4,4,4] # by default a full bar becomes 4 crotchets
        
        chord = rebuild_chord_upwards([Note(n) for n in chords.from_shorthand(chords_[i][0]+chords_[i][1])]) # ints
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
            elif chords_[i][1] == '7':
                basspattern = [chord[0], chord[1], chord[2], chord[0]+1] # root, 3rd, 5th, b9
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
            
    return [Note().from_int(int(n)) for b in bassline for n in b], new_durations
                