import numpy as np
import mingus.core.notes as notes
from mingus.containers import Note
import mingus.core.chords as chords

from sidewinder.utilities import move_b_above_a_with_modularity, get_diatonic_upper_chord_extension
from sidewinder.voicings.voicing_utilities import rebuild_chord_upwards, add_bass_note_to_slash_chord


def apply_individual_chord_voicing(chord:str, voicing_type=None, semitones=False, **kwargs):
    '''
    Main handler for individual chord voicings.
    Expects a single chord shorthand e.g. 'C7'.
    Returns mingus Notes by default with option to return as semitone integers.
    '''
    voiced_semitones = None
    if voicing_type is None:
        voiced_semitones = default_voice(chord)
    elif voicing_type == 'root':
        voiced_semitones = root_only_voice(chord)
    if voicing_type == 'shell':
        voiced_semitones = None
    elif voicing_type == 'rootless':
        voiced_semitones = rootless_voice(chord, **kwargs)

    if voiced_semitones is None:
        print(f'voicing_type {voicing_type} returned None for chord {chord}')
        voiced_semitones = default_voice(chord)

    # TO-DO: add_bass_note_to_slash_chord() (e.g. C7/E -> put an E in the bass)
    
    if not semitones:
        return [Note().from_int(semi) for semi in voiced_semitones] # list of mingus Notes
    else:
        return voiced_semitones # list of semitones

def voice_chords(chords, voicing_type=None, semitones=False, **kwargs):
    '''
    For voicings multiple chords (each with the same voicing parameters)
    Expects a list of chord shorthands e.g. ['Dm7', 'G7']
    Returns mingus Notes by default with option to return as semitone integers.
    '''
    return [apply_individual_chord_voicing(chord, voicing_type=voicing_type, semitones=semitones, **kwargs) for chord in chords]


#%% Individual voicings

def default_voice(chord:str):
    '''
    Expects a shorthand string like 'CM7' and will return with the natural voicing of ascending extensions as semitones (integers)
    '''
    note_names = chords.from_shorthand(chord) # shorthand -> unpitched note strings ['C', 'E', 'G', 'B']
    voiced_semitones = rebuild_chord_upwards([int(Note(note)) for note in note_names])
    return voiced_semitones # ensure we voice from root upwards (in case e.g. everything defaulted to same octave)

def root_only_voice(chord:str):
    '''
    Expects a shorthand string like 'CM7' and will return with the root only (as semitone integer)
    '''
    note_names = chords.from_shorthand(chord) # shorthand -> unpitched note strings ['C', 'E', 'G', 'B']
    voiced_semitones = rebuild_chord_upwards([int(Note(note_names[0], octave=3))])
    return voiced_semitones # ensure we voice from root upwards (in case e.g. everything defaulted to same octave)
    

def shell_voice(progression, durations, prog_type='shorthand', roots=False, extensions=False):
    '''
    shell voice: play just the 3rd and 7th (as the most harmonic) (cf http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chords/shell-chords/)
    
    potentially also add extensions. extensions flag is to by default filter out any extensions above 7th, otherwise cf http://www.jamieholroydguitar.com/how-to-play-shell-voicings/
    '''
    chords_ = progression_to_chords(progression, prog_type)
        
    # save them if we're putting in the bass
    if roots:
        roots_ = [int(Note(chord[0], octave=3)) for chord in chords_] 
           
    chords_ = [[chord[1]]+chord[3:] for chord in chords_] # to create the shell voicing, let's first remove the root and 5th 
    base_chords_ = [chord[:2] for chord in chords_] # keep the first two notes (3rd and 7th)
    if extensions:
        extensions_ = [chord[2:] for chord in chords_] # keep any higher extensions
        
    # we now perform simple voice leading on the base_chords_ (and then stick the extensions_ on top)
    chords_ = base_chords_
    track = chords_to_track(chords_, durations)
    
    voiced_chords = []
    for i, event in enumerate(track):
        chord = event[0][2] # current chord, to align with previous (if i>0)
        if extensions:
            chord_extensions = extensions_[i]
        if i == 0:
            voiced_chords.append([int(note) for note in chord])
        if i>0:
            voiced_chords.append(smooth_next_chord(voiced_chords[i-1], chord))
            
        # add extensions for each chord
        if extensions and len(chord_extensions)>0:
            chord_extensions = rebuild_chord_upwards([Note(ext) for ext in chord_extensions]) # to preserve ordering
            ext_shift = move_b_above_a_with_modularity(max(voiced_chords[i]),chord_extensions[0],12) - chord_extensions[0] # move first extension above base chord
            chord_extensions = [ext + ext_shift for ext in chord_extensions]
            
            # TO-DO build in other shell voicing extension options, see:
            # http://jamieholroydguitar.com/wp-content/uploads/2012/07/Shell-extentions1.png
            # this effectively captures 3 and 4-note voicings (http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chord-voicings/three-note-voicings/), possibly by limiting the number or priority of extensions

            voiced_chords[i] = voiced_chords[i] + chord_extensions
            
        if roots:
            voiced_chords[i] = [roots_[i]] + voiced_chords[i]
            
    voiced_chords = [[Note().from_int(int(note)) for note in chord] for chord in voiced_chords]
    return voiced_chords

def rootless_voice(chord:str, key=None, type=None, mode='major'):
    '''

    - 3rds and 7ths define chord quality
    - drop the roots; we might drop 5ths too as they're not particularly interesting


    http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chord-voicings/rootless-voicings/

    "Because you are playing 4 notes all within the span of a single octave, these voicings can be a little bit muddy if played too low. 
    As such, try adhere to the ‘rule of thumb’: the top note of a rootless chord voicing (played with your thumb) should be 
    between middle C and the C an octave above middle C on the piano. That is, try stick to the middle register with this chord voicing.
    
    
    Type A Rootless Voicings
    Chord	7th Chord in C	Rootless Chord	Notes	    Degrees	    Note on Bottom
    ii	    Dm7	            Dm9	            F A C E	    3 5 7 9	    3rd
    V	    G7	            13	            F A B E	    7 9 3 13	7th
    I	    CMaj7	        CMaj9	        E G B D	    3 5 7 9	    3rd

    Type B Rootless Voicings
    Chord	7th Chord in C	Rootless Chord	Notes	    Degrees	    Note on Bottom
    ii	    Dm7	            Dm9	            C E F A	    7 9 3 5	    7th
    V	    G7	            G13	            B E F A	    3 13 7 9    3rd
    I	    CMaj7	        C69	            A D E G	    6 9 3 5	    7th

    params:
    - key (e.g. 'C') is used to determine flavours of extensions. 
        For example, a Dm7 in C (ii7) would extend to a Dm13 (with a G natural), while an Am7 in C (vi7) would extend to an Am11b13 (G natural)
        If key is None then we can still make assumptions about alterations because (for example) if we get a 13 we know it is from a dom7 and is a natural 13
    - use type == 'A' or 'B', or if None then use randomness? Or pick one.
    
    
    '''

    # specify recipes for the different chord types in terms of diatonic scale degrees (e.g. 3 in m7 is a minor 3rd)
    recipes_A = {'M7': [3,5,7,9],
                'M6': [3,6,7,9],
               '7': [7,9,3,13],
               'm7': [3,5,7,9]}

    recipes_B = {'M7': [6,9,3,5],
               '7': [3,13,7,9],
               'm7': [7,9,3,5]}
    recipes_B['M6'] = recipes_B['M7']
    
    if type == 'B':
        recipes = recipes_B
    else:
        recipes = recipes_A

    # extrapolate recipes to other chord types
    for ct in ['m9','m11','m13']:
        recipes[ct] = recipes['m7']
    for ct in ['M9','M13']:
        recipes[ct] = recipes['M7']
    for ct in ['9','11','13','7b9']:
        recipes[ct] = recipes['7']

    # apply recipes
    voiced_chord = []
    root, chord_type = chords.chord_note_and_family(chord) # 'D', 'm7'
    try:
        recipe = recipes[chord_type]
    except KeyError:
        print(f'No rootless voicing recipe specified for chord: {chord}')    
        return None # acts as flag to parent function        
    for extension in recipe:
        voiced_chord.append(get_diatonic_upper_chord_extension(chord, extension, key=key, mode=mode))
    # TO-DO: fix octaves (if needed?)
    return [int(Note(note)) for note in voiced_chord]

