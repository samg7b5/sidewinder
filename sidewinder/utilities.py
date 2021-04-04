# -*- coding: utf-8 -*-
"""
Created on Fri May  8 10:11:04 2020

Holds utility-style functions that are used across different mid-level Sidewinder components

@author: Sam
"""
from mingus.containers import Note, Track, Bar
from mingus.core.mt_exceptions import NoteFormatError
import mingus.core.progressions as progressions
from mingus.core import intervals, notes
import mingus.core.scales as scales
import mingus.core.chords as chords
from mingus.core.chords import from_shorthand, chord_note_and_family, diatonic_thirteenth
from mingus.midi import midi_file_out

from datetime import datetime
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


#%% Charts / Progressions / Chords
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

def get_diatonic_upper_chord_extension(chord, extension, key=None, mode='major'):
    '''
    params:
        - chord is a (parsed) shorthand symbol e.g. 'Dm7'
        - extension is an integer representing the target extension (e.g. 3 to give the 3rd (major or minor))
    '''

    root, chord_type = chord_note_and_family(chord)

    extension_index = {1:0, 3:1, 5:2, 7:3, 9:4, 2:4, 11:5, 4:5, 13:6, 6:6}


    # we consider the thirteenth chords which arise from diatonic chord extensions only,
    # we then check if our chord is a subchord of any of these diatonic thirteenths;
    # if it is, then we assume that it plays the role of the chord (roman numeral) which is most likely to generate that thirteenth.
    # e.g. if we find a G13 then we assume it comes from G7 (V7 in C)

        # More details:
        # if key is not specified, then default to the most conventional extensions for a given chord type (https://en.wikipedia.org/wiki/Extended_chord#Chord_structure 
        # Note: Would this be different in a different mode/tonality (e.g. extend me a IV chord while playing a locrian tune...)? Should probably factor this in... (TO-DO)

            # M7 -> M13 (M7, 9, #11*, 13) *by convention
            # m7 -> m13 (m7, 9, 11, 13)
            # 7 -> 13 (7, 9, 11, 13)
            # m7b5 -> m7b5b9b13 (7, b9, 11, b13) (e.g. B D F A -> B D F A C E G)

        # if key is specified then we can work out the degree of our chord (e.g. an FM7 in C is a IV chord) and be more clever with extensions

            # IM7 -> M13#11
            # IIm7 -> m13 (e.g. DFACEGB) - note that this has a major 13th (https://music.stackexchange.com/questions/16932/why-does-a-cm13-chord-use-a-instead-of-a)
            # IIIm7 -> m13b9
            # IVM7 -> M13#11
            # V7 -> 13
            # VIm7 -> m7b13 (e.g. ACEGBDF)
            # VIIm7b5 -> m7b5b9b13
    def assume_key(root, chord_type, mode):

        if mode == 'harmonic_minor':
            if chord_type in ['7b9']:
                # assume V (C7b9 implies F harmonic minor, i.e. 7b9 is phyrgian dominant (V mode of HM)) TODO: refactor?
                return notes.int_to_note(notes.note_to_int(root) - 7) 
        
        if chord_type in ['M7','M9','M13','M6']:
            return root
        elif chord_type in ['m7','m9','m11','m13']:
            # assume II, e.g. Dm7 -> return C
            return notes.int_to_note(notes.note_to_int(root) - 2)
        elif chord_type in ['m7b9', 'm11b9', 'm13b9']:
            # assume III
            return notes.int_to_note(notes.note_to_int(root) - 4)
        elif '#11' in chord_type:
            # assume IV
            return notes.int_to_note(notes.note_to_int(root) - 5)
        elif chord_type in ['7', '9', '11', '13']:
            # assume V
            return notes.int_to_note(notes.note_to_int(root) - 7)
        elif chord_type in ['m7b13']:
            # assume VI
            return notes.int_to_note(notes.note_to_int(root) - 9)
        elif ('b5' in chord_type) or ('dim' in chord_type):
            # assume VII
            return notes.int_to_note(notes.note_to_int(root) - 11)
        else:
            #print(f'\nWarning: utilities.assume_key() does not know how to handle chord_type {chord_type}')
            pass

    if key is None:
        key = assume_key(root, chord_type, mode)

        # TODO: handle modes / alterations (also see above)
        # assume_key() is assuming major tonality (more precisely, diatonic_thirteen() is assuming major tonality and assume_key() provides accordingly)
        if key is None: # if assume_key didn't work e.g. for a 7b9 which does not arise on any 7th chord built from the major scale
            if chord_type == '7b9':
                diatonic_extended_chord = chords.dominant_flat_ninth(root) + chords.major_triad(intervals.minor_second(root))[1:]# 1 3 5 b7 b9 11 b13
            return diatonic_extended_chord[extension_index[extension]]
    
    try:
        diatonic_extended_chord = diatonic_thirteenth(root, key)
    except NoteFormatError:
        try:
            diatonic_extended_chord = diatonic_thirteenth(root, synonyms[key])
        except KeyError:
            try:
                diatonic_extended_chord = diatonic_thirteenth(root, synonyms_r[key])
            except:
                print(f'Problem fetching diatonic_thirteenth({root},{key})')

    return diatonic_extended_chord[extension_index[extension]]

#%% Tracks / MIDI

def notes_durations_to_track(_notes, durations=None):
    '''
    params:
    - _notes: list of list of Notes [['G','B','D','F'], ['C','E','G','B']]
    - durations: Durations should be a list of integers e.g. [2,2,1] will give | chord 1 chord 2 | chord 3 |

    TO-DO: 
        - mingus durations are limited to =< 1 bar; we want to be able to parse a duration of '0.5' (because in mingus '4'=crotchet i.e. num subdivs) to refer to 2 bars (just use 1/d)
    
    '''
    if durations is None:
        durations = [1]*len(_notes)

    t = Track()
    for i, _note in enumerate(_notes):
        b = Bar()
        b.place_notes(_note, durations[i]) 
        t.add_bar(b)
    return t

def track_to_midi(t, name='midi_out\\untitled', save=True, timestamp=True):
    '''
    Saves a mingus Track t to a midi file {name}.mid (automatically adds a timestamp)
    Returns name of the created file
    '''
    if timestamp:
        name += datetime.now().strftime('%Y%m%d%H%M%S')

    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
        return name

    return None

     