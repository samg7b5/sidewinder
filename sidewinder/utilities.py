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
synonyms.update({v:k for k,v in synonyms.items()})

malformed_double_accidentals = {'B##':'C#',
                                'E##':'F#',
                                'Cbb':'Bb',
                                'Fbb':'Eb'}

def move_b_above_a_with_modularity(a,b,mod): # return min{x: x==b modulo 'mod' & x>a}
        b = np.mod(b, mod)
        while b < a:
            b+=mod
        return b

def cycle_of_fifths(start='C', repeats=0):
    preferred_accidentals = {'C#':'Db',
                             'G#':'Ab',
                             'D#':'Eb',
                             'A#':'Bb'}
    out = []
    repeat_counter = 0
    next_note = start
    while repeat_counter <= repeats:
        out.append(next_note)
        next_note = notes.reduce_accidentals(intervals.perfect_fifth(next_note))
        if str(next_note) == start:
            repeat_counter += 1 
    return [preferred_accidentals[note] if note in preferred_accidentals.keys() else note for note in out]

#%% Charts / Progressions / Chords
def parse_symbol(symbol):
    '''
        Notes:
        - Not sure mingus is consistent with lower-case numerals as minor or not (this is configures to expect - or m (or min I guess))
        - mingus progressions.to_chords() uses classical approach V7 = diatonic 7th, hence the 'dom' replacements

    '''
    return symbol.replace(' ','').replace('-','m').replace('maj','M').replace('Maj','M').replace('i','I').replace('v','V').replace('I7','Idom7').replace('V7','Vdom7').replace('dom7b9','7b9').replace('mIn','min').replace('dIm','dim')   

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
        if isinstance(numerals, str):
            raise TypeError('Did you mean utilities.parse_progression(numerals)?')
        try:
            chord_notes = [progressions.to_chords(chord, key=key)[0] for chord in numerals] # chords as individual Notes like [['C','E','G','B'],...]
        except NoteFormatError:
            chord_notes = [progressions.to_chords(chord, key=synonyms[key])[0] for chord in numerals]
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
    try:
        scale = scales.Chromatic(key)
    except NoteFormatError:
        scale = scales.Chromatic(synonyms[key])
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
                print(f'No synonym for {chord[0]}')
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

def get_scale(scale_class_name, key='C', ascending=True, length=None, name_only=False, help=False):

    # optional return as chromatic degree description?

    NON_SCALE_CLASSES = ['TemporalNote', '__name__', '__builtins__', 'get_notes', 'RangeError', '_Scale', 'intervals', '__package__', 'keys', '__loader__', 'augment', '__spec__', 'diminish', 'BLUES_INTERVALS', 'determine', 'NoteFormatError', '__cached__', 'FormatError', 'reduce_accidentals', '__doc__', '__file__', 'cycle']
    NON_SCALE_CLASSES += ['Bachian', 'Diatonic']
    SCALE_TYPES = list(set(dir(scales)) - set(NON_SCALE_CLASSES))
    if help:
        print('scale_class_name should be one of: ', SCALE_TYPES)
        return None

    scale_class_name = scale_class_name.lower().replace(' ','').replace('-','')

    scale_synonyms = {'altered':'superlocrian',
                      'altereddominant':'superlocrian',
                      'majorpentatonic':'pentatonic',
                      'suhmmlydian':'superultrahypermegametalydian',
                      'suhmmmixolydian':'superultrahypermegametamixolydian',
                      }
    try:
        scale_class_name = scale_synonyms[scale_class_name]
    except KeyError:
        pass
        
    scale_gens= {'major': scales.Major,
             'minor': scales.NaturalMinor,
             'lydian': scales.Lydian,
             'ionian': scales.Ionian, # same as major
             'mixolydian':scales.Mixolydian,
             'dorian':scales.Dorian,
             'aeolian':scales.Aeolian,
             'phrygian':scales.Phrygian,
             'locrian':scales.Locrian,
             'whole tone': scales.WholeTone,
             'blues':scales.Blues,
             'chromatic':scales.Chromatic,
             'diatonic':scales.Diatonic, # same as major/ionian, different class definition (uses W/H steps)
             'naturalminor':scales.NaturalMinor, # same as minor/Aeolian
             'harmonicminor':scales.HarmonicMinor,
             'melodicminor':scales.MelodicMinor,
             'octatonic':scales.Octatonic, # WH diminished
             'minorneapolitan':scales.MinorNeapolitan,
             'diminished':scales.Octatonic,
             'wholehalfdiminished':scales.Octatonic,
             'halfwholediminished':scales.HalfWholeDiminished,
             'locriannat6': scales.LocrianNat6,
             'ionian#5': scales.IonianSharp5,
             'ionianaugmented': scales.IonianSharp5,
             'dorian#4': scales.DorianSharp4,
             'phrygiandominant': scales.PhrygianDominant,
             'lydian#2': scales.LydianSharp2,
             'altereddominantbb7': scales.AlteredDominantbb7,
             'superlocrianbb7': scales.AlteredDominantbb7,
             'dorianb2': scales.Dorianb2,
             'phrygiannat6': scales.Dorianb2,
             'lydian#5': scales.LydianSharp5,
             'lydianaugmented': scales.LydianSharp5,
             'lydiandominant': scales.LydianDominant,
             'mixolydianb6': scales.Mixolydianb6,
             'locriannat2': scales.LocrianNat2,
             'superlocrian': scales.AlteredDominant,
             'pentatonic': scales.Pentatonic,
             'minorpentatonic': scales.MinorPentatonic,
             'majorbebop':scales.MajorBebop,
             'dorianbebop':scales.DorianBebop,
             'altdorian bebop':scales.DorianBebopAlt, # "alternative" (not "altered")
             'mixolydianbebop':scales.MixolydianBebop,
             'dominantbebop':scales.MixolydianBebop,
             'melodicminor bebop':scales.MelodicMinorBebop,
             'harmonicminorbebop':scales.HarmonicMinorBebop,
             'superultrahypermegametalydian': scales.SuperUltraHyperMegaMetaLydian, 
             'superultrahypermegametamixolydian': scales.SuperUltraHyperMegaMetaMixolydian, 
             }   

    # if different to the standard 7 note (plus octave) scale
    scale_lengths= {'octatonic':8,
                    'diminished':8,
                    'wholehalfdiminished':8,
                    'halfwholediminished':8,
                    'wholetone':6,
                    'pentatonic':5,
                    'minorpentatonic':5,
                    'blues': 6,
                    'chromatic':12,
                    'majorbebop':8,
                    'dorianbebop':8,
                    'altdorianbebop':8, 
                    'mixolydianbebop':8,
                    'dominantbebop':8,
                    'melodicminorbebop':8,
                    'harmonicminorbebop':8
                    }
    if length is None:
        try:
            length = scale_lengths[scale_class_name]
        except KeyError:
            length = 7

    out = list(scale_gens[scale_class_name](key).generate(length, ascending=ascending))
    if name_only:
        out = [note.name for note in out]
    return out

def note_to_scale_degree(note, key, scale, label_nondiatonic=True, chromatic_options=False): # note as str for simplicity e.g. note.name
    
    if type(note) == Note:
        note = note.name

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

    scale_notes = get_scale(scale, key=key, name_only=True)
    
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
        # See also https://www.reddit.com/r/musictheory/comments/8becrf/when_to_apply_which_chord_extension/

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
        elif chord_type in ['7b9']: # TODO: refactor so that this is not an ad hoc exception (given 7b9 is covered below) but instea maybe automatically check all hminor modes etc
            pass
        else:
            print(f'\nWarning: utilities.assume_key() does not know how to handle chord_type {chord_type}')
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
            print(f'Problem fetching diatonic_thirteenth({root},{key})')

    return diatonic_extended_chord[extension_index[extension]]

#%% Tracks / MIDI

def track_to_degrees(track, key, scale, **kwargs):
    notes = [notev[2] for notev in track.get_notes()] # gives a list of NoteContainers
    note_names = [[note.name for note in nc] for nc in notes] # since each nc could contain multiple Note()'s
    return [[note_to_scale_degree(x, key, scale, **kwargs) for x in nc] for nc in note_names]


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

     