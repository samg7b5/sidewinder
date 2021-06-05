from sidewinder import detect_numeral_pattern
from sidewinder.snippets import CHUNKS, CHORD_SUBS
from sidewinder.utilities import numerals_list_to_shorthand_list, parse_progression, shorthand_list_to_numerals_list

def get_available_chord_subs(sub, numerals, key='C'):
    out = []
    for arg in sub.keys(): # could also do in one go with arg = ', '.join(sub.keys())
        detections = detect_numeral_pattern(numerals, parse_progression(arg), original_key=key)
        for hit_type in list(detections.keys()): # flattens hits, transposed hits
            for hit in detections[hit_type]:
                new_chord = numerals_list_to_shorthand_list(parse_progression(sub[arg]), hit['key'])
                out.append((hit, new_chord))
    if len(out) == 0:
        print('No chord substitutions made')
    return out

def apply_chord_sub(given_sub, numerals, key='C'):
    '''
    given_sub: ({'start_index': int}, [chord shorthands])
    TODO apply to a set of shorthands not numerals (then no need to specify key)
    '''
    given_sub_as_numerals = shorthand_list_to_numerals_list(given_sub[1], key)
    return numerals[:given_sub[0]['start_index']] + given_sub_as_numerals + numerals[given_sub[0]['start_index']+len(given_sub[1]):]