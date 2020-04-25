# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 21:11:45 2019

@author: Sam
"""
from mingus.containers import Note
import mingus.core.progressions as progressions
from mingus.midi import midi_file_out, midi_file_in
from mingus.containers import Track, Bar
from mingus.core import intervals
import mingus.core.scales as scales
import mingus.core.chords as chords

from datetime import datetime
import numpy as np
import random

#%% Misc.
def move_b_above_a_with_modularity(a,b,mod): # return min{x: x==b modulo 'mod' & x>a}
        b = np.mod(b, mod)
        while b < a:
            b+=mod
        return b
    
synonyms = {'C#':'Db',
            'D#':'Eb',
            'F#':'Gb',
            'G#':'Ab',
            'A#':'Bb',
            'B#':'C',
            'E#':'F'}
synonyms_r = {v:k for k,v in synonyms.items()}

#%% Chords
def minimal_chord_distance(source_chord, target_chord):
    source_chord = [int(note) for note in source_chord]
    target_chord = [int(note) for note in target_chord]
    distance = 0
    for target_note in target_chord:
        distance += min([abs(target_note - source_note) for source_note in source_chord])
    return distance

def rebuild_chord_upwards(chord): 
    chord = [int(Note(note)) for note in chord] # Note() to int
    a = chord[0]
    for i, b in enumerate(chord[1:]):
        b = move_b_above_a_with_modularity(a,b,12)
        chord[i+1] = b
        a = b
    return chord

def rebuild_chord_inwards(chord):
    '''
    Expects a list of Note strings
    '''
    chord = [int(Note(note)) for note in chord] # Note() to int
    a = chord[0]
    for i, b in enumerate(chord[1:]):
        b = np.floor(a/12)*12 + np.mod(b, 12)
        chord[i+1] = b
        a = b
    return chord

def chords_to_track(chords, durations):
    t = Track()
    for i, chord in enumerate(chords):
        b = Bar()
        b.place_notes(chord, durations[i]) # default octave is ['C','E','G']->['C-4','E-4','G-4'] (this is the first instance of voicing)
        t.add_bar(b)
    return t

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

#%% Voices
def generate_chord_inversions(chord): # works on semitones
    inversions = [[chord[p - q] for p in range(len(chord))] for q in range(len(chord))]
    for i, chord in enumerate(inversions):
        inversions[i] = rebuild_chord_upwards(chord)
    return inversions

def generate_close_chords(chord):
    '''
    Works on lists (individual elements could be int or str)
    '''
    inversions = [[chord[p - q] for p in range(len(chord))] for q in range(len(chord))]
    for i, chord in enumerate(inversions):
        inversions[i] = rebuild_chord_inwards(chord)
    return inversions

def smooth_next_chord(voiceA, chordB):
    '''
    voiceA is a list of ints
    chordB is a list of Notes e.g. [Note('C-4'), ...] 
    '''
    inversions = generate_close_chords(chordB)
    distances = [minimal_chord_distance(voiceA, inversion) for inversion in inversions]
    voiceB = inversions[np.argmin(distances)]
    return voiceB

def smooth_voice_leading(progression, durations, prog_type='shorthand'):
    
    chords_ = progression_to_chords(progression, prog_type)
    # here, chords_ is a list of lists [['C', 'E', 'G', 'B'],...] (which will default to octave as C-4 etc in chords_to_track)
    
    track = chords_to_track(chords_, durations)
    
    voiced_chords = []
    for i, event in enumerate(track):
        chord = event[0][2] # current chord, to align with previous (if i>0); as voiced str ['C-4', 'E-4', 'G-4']
        if i == 0:
            voiced_chords.append([int(note) for note in chord]) # converted into ints
        if i>0:
            voiced_chords.append(smooth_next_chord(voiced_chords[i-1], chord))
    
    voiced_chords = [[Note().from_int(int(note)) for note in chord] for chord in voiced_chords]
    return voiced_chords

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

def rootless_voice(progression, durations, prog_type='shorthand', type='A'):
    '''
    http://www.thejazzpianosite.com/jazz-piano-lessons/jazz-chord-voicings/rootless-voicings/
    
    Note:
        - this is a badly written function, in particular the handling of modes to get the correct scale degrees is inelegant and
        not very reproducible/extensible
        - it also doesn't handle other chord types very well
    
    '''
    # chords_ = progression_to_chords(progression, prog_type) # using a different approach below
    
    if prog_type == 'numerals': # e.g. IIm7
        progression = [progressions.to_chords(chord)[0] for chord in progression]
        progression = [chords.determine(chord, shorthand=True)[0] for chord in progression] # shorthand e.g. Dm7
        
    chords_ = [chords.chord_note_and_family(chord) for chord in progression] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]
#    print(chords_)
    
    # simple version: assume M7 = major, m7 = dorian, 7 = mixolydian
    # which equates to parallel major key-centres of 0, -2 (e.g. Dm7 in C), -7 (e.g. G7 in C) semitones resp.
    # but in future (TO-DO) might want to allow alterations by putting in different keys e.g. a dom7 chord that's not mixolydian
    
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

        
        if '/' in chord_type:
            print('TO-DO: handle slash chords at a more macro level, e.g. have a function which adds bass note to any slash chord voicing')
            slash_chord = True
            bass_note = ''.join(chord_type.split('/')[1:])
            chord_type = chord_type.split('/')[0]
        if chord_type == '':
            chord_type = 'M'
        
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


#%% Progressions 
def parse_symbol(symbol):
    '''
        Notes:
        - Not sure mingus is consistent with lower-case numerals as minor or not (this is configures to expect - or m (or min I guess))
        - mingus progressions.to_chords() uses classical approach V7 = diatonic 7th, hence the 'dom' replacements

    '''
    return symbol.replace(' ','').replace('-','m').replace('maj','M').replace('i','I').replace('v','V').replace('I7','Idom7').replace('V7','Vdom7').replace('dom7b9','7b9').replace('mIn','min')   

def parse_progression(progression):
    '''
    Convert from a progression string to a list as mingus would expect
        '''    
    if type(progression) == str:    
        return parse_symbol(progression).split(',') 
    else:
        return [parse_symbol(chord) for chord in progression]
    
def chords_to_midi(progression=['Dm7', 'G7', 'CM7'], durations=None, voicing='smooth', name='midi_out\\untitled', key='C', save=True, prog_type='shorthand', **kwargs):
    '''
    Generate and export a basic midi file for given chord progression.
    Progression can be as shorthand (e.g. Am7) or Roman numerals (e.g. VIm7)
    
    Durations should be a list of integers e.g. [2,2,1] will give | chord 1 chord 2 | chord 3 |
    
    TO-DO: 
        - mingus durations are limited to =< 1 bar; we want to be able to parse a duration of '0.5' (because in mingus '4'=crotchet i.e. num subdivs) to refer to 2 bars (just use 1/d)
    '''

    # Pre-processing and parsing
    if name == 'midi_out\\untitled':
        name += datetime.now().strftime('%Y%m%d%H%M%S')
    
    progression = parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]
        
    if progression[0][0] in ['I', 'V', 'i', 'v']:
        prog_type = 'numerals'
    
    # Apply voicings 
    if voicing == 'smooth':
        voiced_chords = smooth_voice_leading(progression, durations, prog_type)
    elif voicing == 'shell':
        voiced_chords = shell_voice(progression, durations, prog_type, **kwargs)
    elif voicing == 'rootless':
        voiced_chords = rootless_voice(progression, durations, prog_type, **kwargs)

    t = chords_to_track(voiced_chords, durations)

    # Export
    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
    return t

def chords_to_bassline_midi(progression=['Dm7','G7','CM7'], durations=None, walking=True, name='midi_out\\bassline', key='C', save=True):
    if name == 'midi_out\\bassline':
        name += datetime.now().strftime('%Y%m%d%H%M%S')
        
    progression = parse_progression(progression)
    
    if durations is not None and not len(durations) == len(progression):
        print('Warning - length mismatch')
    if durations is None:
        durations = len(progression)*[1]
        
    if progression[0][0] in ['I', 'V', 'i', 'v']:
        progression = [progressions.to_chords(chord)[0] for chord in progression]
        progression = [chords.determine(chord, shorthand=True)[0] for chord in progression] # shorthand e.g. Dm7
        
    chords_ = [chords.chord_note_and_family(chord) for chord in progression] # [('D', 'm7'), ('G', '7'), ('C', 'M7')]
    
    bassline = [Note(chord[0], octave=3) for chord in chords_]
    t = chords_to_track(bassline, durations)
    
    if walking:
        bassline, durations = create_walking_bassline(chords_, durations)
        t = chords_to_track(bassline, durations)
    
    # Export
    if save:
        midi_file_out.write_Track(f'{name}.mid', t)
        print(f'Saved: {name}.mid')
    return t

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
                

#%% Analysis
def detect_numeral_pattern(progression, pattern=['IIm7','V7','IM7'], transposing=True, original_key='C'):
    '''
    Input progression should be in numeral format
    Transposing option is to detect the pattern outside of the base key
    '''
    # parsing
    progression = parse_progression(progression)
    pattern = parse_progression(pattern)
    
    window_size = len(pattern)
    
    hits = []
    for i in range(0, len(progression)-window_size+1):
        passage = progression[i:i+window_size]
        if passage == pattern:
            hits.append(i)
            
    if transposing:
        transposed_hits = []
        for i in range(0, len(progression)-window_size+1):
            passage = progression[i:i+window_size]
 
            for key in ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']:
                transposed_passage = progressions.to_chords(passage, original_key)
                transposed_pattern = progressions.to_chords(pattern, key)
                
                if transposed_passage == transposed_pattern:
                    transposed_hits.append((i,[chord.replace('dom','') for chord in passage],key))
        hits = [hits, transposed_hits]
        
    return hits
        

def shorthand_to_numerals(progression='Cmaj7, G-7, C7, Fmaj7, Bb7', key='C'):
    progression = parse_progression(progression)
    
    def get_note(symbol):
        if symbol[1] == '#' or symbol[1] == 'b':
            return symbol[0:2]
        else:
            return symbol[0]
        
    proc_progression = [[get_note(chord), chord[len(get_note(chord)):]] for chord in progression]
    
#    scale = scales.ionian(key) # default to major
#    if mode == 'minor':
#        scale = scales.aeolian(key)
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


    
    
    
    