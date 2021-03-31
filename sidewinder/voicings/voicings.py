import numpy as np
import mingus.core.notes as notes
from mingus.containers import Note
import mingus.core.chords as chords

from sidewinder.utilities import move_b_above_a_with_modularity
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
    if voicing_type == 'shell':
        voiced_semitones = None
    elif voicing_type == 'rootless':
        voiced_semitones = rootless_voice(chord, **kwargs)

    # TO-DO: add_bass_note_to_slash_chord()

    if not semitones:
        return [Note().from_int(semi) for semi in voiced_semitones] # list of mingus Notes
    else:
        return voiced_semitones # list of semitones

#%% Individual voicings

def default_voice(chord:str):
    '''
    Expects a shorthand string like 'CM7' and will return with the natural voicing of ascending extensions as Notes
    '''
    note_names = chords.from_shorthand(chord) # shorthand -> unpitched note strings ['C', 'E', 'G', 'B']
    voiced_semitones = rebuild_chord_upwards([int(Note(note)) for note in note_names])
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

def rootless_voice(chord:str, key=None, type=None):
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


    chords_ = [chords.chord_note_and_family(chord) for chord in progression] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]

    # specify recipes for the different chord types in terms of diatonic scale degrees (e.g. 3 in m7 is a minor 3rd)

    recipes_A = {'M7': [3,5,7,9],
               '7': [7,9,3,13],
               'm7': [3,5,7,9]}

    recipes_B = {'M7': [6,9,3,5],
               '7': [3,13,7,9],
               'm7': [7,9,3,5]}
    
    if type == 'B':
        recipes = recipes_B
    else:
        recipes = recipes_A

    # apply recipes
    
    # if no recipe specified, default voice (return this as a None flag and handle it in the parent function)






    
    key_offset = {'M7':0,
                  '7': int(Note('G')) - int(Note('C')),
                  'm7': int(Note('D')) - int(Note('C'))            
                  }
    majors = ['maj7', 'M']
    minors = ['min7', 'm', '-', '-7', 'm9']
    doms = ['dom7', 'dom', '9']
    for synonym in majors:
        key_offset[synonym] = key_offset['M7']
    for synonym in minors:
        key_offset[synonym] = key_offset['m7']
    for synonym in doms:
        key_offset[synonym] = key_offset['7']
    majors = majors + ['M7']
    minors = minors + ['m7']
    doms = doms + ['7']
    
    voiced_chords = []
    slash_chord = False
    for i, chord in enumerate(chords_):
        chord_root = chord[0]
        chord_type = chord[1]

        

        
        try:
            rel_major = Note().from_int(int(Note(chord_root)) - key_offset[chord_type]).name 
        except KeyError:
            print(f'No rootless voicing provided for {chord_type}')
            rel_major = '' # manually voice exotic chords e.g. 7b9 for now
        
        if '#' in rel_major:
            rel_major = synonyms[rel_major]
        
        # TO-DO nb. this section might refactor to enable writing of lines ito scale degrees
        voiced_chord = None # reset to avoid appending the same voiced_chord (which would hide errors if chords are skipped)
        if type=='A':
            if chord_type in majors + minors:
                voiced_chord = [intervals.interval(rel_major, chord_root, 2), intervals.interval(rel_major, chord_root, 4), 
                                intervals.interval(rel_major, chord_root, 6), intervals.interval(rel_major, chord_root, 8)] # 3rd, 5th, 7th, 9th
            elif chord_type in doms:
                voiced_chord = [intervals.interval(rel_major, chord_root, 6), intervals.interval(rel_major, chord_root, 8),
                                intervals.interval(rel_major, chord_root, 2), intervals.interval(rel_major, chord_root, 12)] # 7th, 9th, 3rd, 13th
        elif type=='B':
            if chord_type in majors:
                voiced_chord = [intervals.interval(rel_major, chord_root, 5), intervals.interval(rel_major, chord_root, 8), 
                                intervals.interval(rel_major, chord_root, 2), intervals.interval(rel_major, chord_root, 4)] # 6th, 9th, 3rd, 5th
            elif chord_type in minors:
                voiced_chord = [intervals.interval(rel_major, chord_root, 6), intervals.interval(rel_major, chord_root, 8), 
                                intervals.interval(rel_major, chord_root, 2), intervals.interval(rel_major, chord_root, 4)] # 7th, 9th, 3rd, 5th
            elif chord_type in doms:
                voiced_chord = [intervals.interval(rel_major, chord_root, 2), intervals.interval(rel_major, chord_root, 12),
                                intervals.interval(rel_major, chord_root, 6), intervals.interval(rel_major, chord_root, 8)] # 3rd, 13th, 7th, 9th
        
        if chord_type in ['7b9', 'minMaj7', 'm6', 'M6', '7#5', 'o']:
            voiced_chord = chords.from_shorthand(chord_root + chord_type)
            if i>0:
                voiced_chord = smooth_next_chord(voiced_chords[i-1],voiced_chord)
                voiced_chord = [Note().from_int(int(note)) for note in voiced_chord]
            
        if slash_chord:
            voiced_chord = [int(Note(bass_note, octave=3))] + voiced_chord
            slash_chord = False
        
        voiced_chords.append(rebuild_chord_upwards([Note(note) for note in voiced_chord])) # to preserve the order we just made
    
    voiced_chords = [[Note().from_int(int(note)) for note in chord] for chord in voiced_chords]
    return voiced_chords 