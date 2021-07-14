import mingus.core.scales as scales
# NOTE: do not import from other scripts in sidewinder.melodies
from sidewinder.utilities import get_scale
from collections import OrderedDict

# TODO should probably refactor the below along with utilities.get_upper_diatonic_extensions()
def scale_pattern(scale, p=[1,3,5,7], offset=0):
    '''
    e.g. [1,3,5] returns [scale[0], scale[2], scale[4]] (1 => root, etc.)
    '''
    return [scale[(idx+offset-1) % len(scale)] for idx in p]

def get_scale_patterns(chosen_scale='Ionian', p=[1,3,5,7], keys=['C'], descending=False, name_only=False, pattern_as_chromatic=False, **kwargs):
    ''' 
        Returns notes indexed by p in the chosen_scale and keys.
        Descending: bool - reverse p
        name_only: bool - return Note.name
        pattern_as_chromatic - expect input as "chromatic degrees" e.g. 'b3' rather than '3' in a minor scale
    '''
    # TODO replace this dict approach with note_to_chromatic_degree(generate_scale()) - function may have different name
    chromatic_to_index = {
        'chromatic': [  ['1'],
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
                        ['7'],
                        ],
        'pentatonic':[
            ['1'],
            ['9','2'], 
            ['3'],
            ['5'],
            ['6','13'],
        ],
        'minor pentatonic':[
            ['1'],
            ['b3','#9'], 
            ['4','11'],
            ['5'],
            ['b7'],
        ]
        }

    if pattern_as_chromatic:
        try:
            old_p = p
            p = []
            for idx in old_p:
                p += [i+1 for i, degree_options in enumerate(chromatic_to_index[chosen_scale]) if str(idx) in degree_options]
        except KeyError:
            print(f'Please use chosen_scale in: {list(chromatic_to_index.keys())}')
    
    patterns = OrderedDict()
    scale_length = len(get_scale(chosen_scale))
    for _, key in enumerate(keys):
        scale = get_scale(chosen_scale, key, length=100, name_only=name_only) # length is for correctly numbering patterns which go too high
        patterns[key] = []
        if descending:
            for j, starting_note in enumerate(scale[:scale_length]):
                patterns[key].append(scale_pattern(scale, p, offset=scale_length-j))
        else:
            for j, starting_note in enumerate(scale[:scale_length]):
                patterns[key].append(scale_pattern(scale, p, offset=j))
    return patterns