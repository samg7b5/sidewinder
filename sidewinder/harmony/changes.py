from mingus.core import notes, intervals

from sidewinder import Chart
from sidewinder.utilities import get_scale
from sidewinder.melodies.patterns import get_scale_patterns
from sidewinder.lick_library import respell_and_determine
from sidewinder.utilities import numerals_list_to_shorthand_list
from sidewinder.snippets import CHUNKS

############# Analysis

def get_diatonic_chords(scales, shape=(1,3,5)):
    '''
    Play a chord shape starting on each scale degree
    Return the resultant chords as numerals

    scales: str ('major') or [str] (['major', 'harmonic minor', ...])

    Outputs numerals e.g. {'major': ['IM7', 'IIm7', 'IIIm7', 'IVM7', 'V7', 'VIm7', 'VIIm7b5']}
    '''
    
    out = {}
    for scale in scales: 
        chord_degrees = [[i+j for i in shape] for j, note in enumerate(get_scale(scale))]
        chord_notes = [get_scale_patterns(scale, p=chord_degrees[j]) for j, note in enumerate(get_scale(scale))]
        # then recognise as chord
        chords = [respell_and_determine(chord, shorthand=True)[0][0] for chord in chord_notes[0]['C']] # TODO determine extended chords not as slash(|)/polychords
        numerals_list = Chart(chords).get_numeral_representation() # TODO numeral representation of slash/polychords doesn't convert the bottom from note to numeral
        out[scale] = numerals_list
    return out

