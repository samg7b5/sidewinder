# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:03:27 2020

Temporary structure for functions to process and analyse licks (melodic lines)

@author: Sam
"""
from Sidewinder import synonyms, synonyms_r
synonyms.update(synonyms_r)

malformed_double_accidentals = {'B##':'C#',
                                'E##':'F#',
                                'Cbb':'Bb',
                                'Fbb':'Eb'}

import mingus.core.scales as scales

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
             'natural minor':scales.NaturalMinor, # same as minor/Aeolian
             'harmonic minor':scales.HarmonicMinor,
             'melodic minor':scales.MelodicMinor,
             'octatonic':scales.Octatonic, # WH diminished
             'minor neapolitan':scales.MinorNeapolitan, # this is the only scale that I'm not familiar with :)
             'diminished':scales.Octatonic,
             'whole-half diminished':scales.Octatonic,
             'half-whole diminished':scales.HalfWholeDiminished,
             'locrian nat6': scales.LocrianNat6,
             'ionian #5': scales.IonianSharp5,
             'ionian augmented': scales.IonianSharp5,
             'dorian #4': scales.DorianSharp4,
             'phrygian dominant': scales.PhrygianDominant,
             'lydian #2': scales.LydianSharp2,
             'altered dominant bb7': scales.AlteredDominantbb7,
             'superlocrian bb7': scales.AlteredDominantbb7,
             'dorian b2': scales.Dorianb2,
             'phrygian nat6': scales.Dorianb2,
             'lydian #5': scales.LydianSharp5,
             'lydian augmented': scales.LydianSharp5,
             'lydian dominant': scales.LydianDominant,
             'mixolydian b6': scales.Mixolydianb6,
             'locrian nat2': scales.LocrianNat2,
             'superlocrian': scales.AlteredDominant,
             'altered': scales.AlteredDominant,
             'altered dominant': scales.AlteredDominant,
             'pentatonic': scales.Pentatonic,
             'minor pentatonic': scales.MinorPentatonic,
             'major bebop':scales.MajorBebop,
             'dorian bebop':scales.DorianBebop,
             'alt dorian bebop':scales.DorianBebopAlt, # "alternative" (not "altered")
             'mixolydian bebop':scales.MixolydianBebop,
             'dominant bebop':scales.MixolydianBebop,
             'melodic minor bebop':scales.MelodicMinorBebop,
             'harmonic minor bebop':scales.HarmonicMinorBebop,
             'super-ultra-hyper-mega-meta-lydian': scales.SuperUltraHyperMegaMetaLydian, # no generate() method
             'super-ultra-hyper-mega-meta-mixolydian': scales.SuperUltraHyperMegaMetaMixolydian # no generate() method
             }   

# if different to the standard 7 note (plus octave) scale
scale_lengths= {'octatonic':8,
                'diminished':8,
                'whole-half diminished':8,
                'half-whole diminished':8,
                'whole tone':6,
                'pentatonic':5,
                'minor pentatonic':5,
                'blues': 6,
                'chromatic':12,
                'major bebop':8,
                'dorian bebop':8,
                'alt dorian bebop':8, 
                'mixolydian bebop':8,
                'dominant bebop':8,
                'melodic minor bebop':8,
                'harmonic minor bebop':8
                }

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
    scale = scale.lower() # input sanitisation 
    try:
        scale_length = scale_lengths[scale]
    except KeyError:
        scale_length = 7
    scale_notes = list(scale_gens[scale](key).generate(scale_length))
    
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

