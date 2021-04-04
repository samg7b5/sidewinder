import mingus.core.scales as scales
from collections import OrderedDict

def get_scale(scale_class_name, key):

    # TODO see lick_analytics scale_gens

    return eval(f"scales.{scale_class_name}(\'{key}\')")  # alternatively see https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object

NON_SCALE_CLASSES = ['Bachian', 'Diatonic'] + ['TemporalNote', '__name__', '__builtins__', 'get_notes', 'RangeError', '_Scale', 'intervals', '__package__', 'keys', '__loader__', 'augment', '__spec__', 'diminish', 'BLUES_INTERVALS', 'determine', 'NoteFormatError', '__cached__', 'FormatError', 'reduce_accidentals', '__doc__', '__file__', 'cycle']
SCALE_TYPES = list(set(dir(scales)) - set(NON_SCALE_CLASSES))

# TODO should probably refactor the below along with utilities.get_upper_diatonic_extensions()
def scale_pattern(scale, p=[1,3,5,7], offset=0):
    '''
    e.g. [1,3,5] returns [scale[0], scale[2], scale[4]] (1 => root, etc.)
    '''
    return [scale[(idx+offset-1) % len(scale)] for idx in p]

def get_scale_patterns(chosen_scale='Ionian', p=[1,3,5,7], keys=['C'], descending=False):
    ''' note: will probably only work for the main modes and not alternative length / alternatively-spaced scales like pentatonics etc.
    '''
    patterns = OrderedDict()
    for i, key in enumerate(keys):
        scale = get_scale(chosen_scale, key).ascending()[:-1]
        patterns[key] = []
        if descending:
            for j, starting_note in enumerate(scale):
                patterns[key].append(scale_pattern(scale, p, offset=len(scale)-j))
        else:
            for j, starting_note in enumerate(scale):
                patterns[key].append(scale_pattern(scale, p, offset=j))
    return patterns