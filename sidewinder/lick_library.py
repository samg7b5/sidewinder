# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 11:00:34 2020

@author: Sam
"""
from sidewinder.utilities import synonyms

from mingus.containers import Track, Bar
from mingus.containers.composition import Composition
from mingus.midi import midi_file_out, midi_file_in
import mingus.core.chords as chords
chord_to_shorthand = {v:k for k,v in chords.chord_shorthand_meaning.items()}

import json
from itertools import combinations
from datetime import datetime
import numpy as np

import ast
from tinydb import TinyDB, Query # https://tinydb.readthedocs.io/en/latest/getting-started.html

#%% misc
def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

#%% db functions
def find_exact_matches(db, entry):
    # searches db for items L where L.key == value for (key,value) in entry
    # e.g. entry = {'tags':'251'} will return items L where L.tags == ['251'] # note has to match entirely
    
    q = [(Query()[t[0]]==t[1]) for t in [(key,value) for key, value in entry.items()]]
    
    qq = q[0]
    for i, subq in enumerate(q):
        if i>0:
            qq = qq & q[i] # combine the full query with &'s
    
    return [x.doc_id for x in db.search(qq)]

def find_partial_matches(db, entry):
    # searches db for items L where value in L.key for (key,value) in entry
    # e.g. entry = {'tags':'251'} will return items L where '251' is an element of L.tags 
    
    out = []
    for key, value in entry.items():
        search_fn = lambda t: value in t
        out = out + [x.doc_id for x in db.search(Query()[key].test(search_fn))]
    
    return out


def find_by_chords_durations(db, chords=['Gm7', 'C7', 'FM7'], durations=[1,1,1]):
    
    search_fn = lambda t: all([c==t[i][3] for i, c in enumerate(chords)] + [float(d) == t[i][1] for i, d in enumerate(durations)])
    return [x.doc_id for x in db.search(Query()['chords'].test(search_fn))]
     

def load_entry(db, doc_id=0):
    '''
    Re-instantiates entry as a JazzLick object given TinyDB doc_id
    '''
    x = Track_from_list(ast.literal_eval(db.get(doc_id=doc_id)['passage'])[1])

    c = Composition()
    x.bars = Bars_from_list(x.bars)
    c.add_track(x)

    j = JazzLick(c, passage_track=0, chords=db.get(doc_id=doc_id)['chords'])
            
    return j

# TO-DO: do a search by stylistic tag e.g. modern, bebop etc.

#%% TO-DO: could probably move some of this into sidewinder core, and also some of the below into _examples
def analyse_composition(comp):
    print(f'Composition has {len(comp.tracks)} tracks')
    print(f'The first is usually the header (empty) track: {comp.tracks[0]}')
    for i, track in enumerate(comp.tracks):
        print(f'Track {i} is {len(track)} events long:')
        print(track[:2], '...', track[-2:])
    return True

def get_chords_from_track(track):
    results = []
    for i, bar in enumerate(track):
        for j, event in enumerate(bar):
            bar_position, chord_duration, chord_notes = event[0], event[1], event[2]
            chord_notes = [note.name for note in chord_notes]
            # NoneType error may arise from faulty MidiEditor quantisation - prefer Frescobaldi to edit midi programmatically'

            possible_chord_names = respell_and_determine(chord_notes)
            print(123,possible_chord_names)
            most_likely_chord_names = [poss[0] for poss in possible_chord_names]
            best_or_none = lambda x: None if x==[] else x[0]
            most_likely_chord = best_or_none(most_likely_chord_names)
            
            # get shorthand as mingus doesn't have a chord-from-fullname function TODO replace with kwarg in respell_and_determine
            if most_likely_chord is not None:
                ch = [most_likely_chord.split(' ')[0]] + [' '.join(most_likely_chord.split(' ')[1:])]
                sh = ch[0] + chord_to_shorthand[f' {ch[1]}']
            else:
                sh = None
            # results.append([i, j, most_likely_chord, sh])
            results.append([i, chord_duration, most_likely_chord, sh]) # return chord's duration instead of chord's index within bar, but might break track splitting..?
    return results

def get_all_chord_respellings(chord):
    respellings = [chord]
    
    candidates = list(set(chord) & set(list(synonyms.keys()) + list(synonyms.values())))
    for i in range(0, len(candidates)):
        combs = combinations(candidates, i+1)
        for comb in combs:
            respelling = chord.copy()
            for to_syn in comb:
                respelling[respelling.index(to_syn)] = synonyms[to_syn]
                respellings.append(respelling)
    return respellings

def respell_and_determine(chord, shorthand=False):
    try:
        named_chords = [chords.determine(chord, shorthand=shorthand)]
    except TypeError:
        chord = [note.name for note in chord]
        named_chords = [chords.determine(chord, shorthand=shorthand)]
    if len(named_chords[0]) == 0:
        named_chords = []
    
    candidates = list(set(chord) & set(list(synonyms.keys()) + list(synonyms.values())))
    for i in range(0, len(candidates)):
        combs = combinations(candidates, i+1)
        for comb in combs:
            respelling = chord.copy()
            for to_syn in comb:
                respelling[respelling.index(to_syn)] = synonyms[to_syn]
                if chords.determine(respelling, shorthand=shorthand) != []:
                    named_chords.append(chords.determine(respelling, shorthand=shorthand))
    return named_chords

def temporal_realign_track_bars(track, pickup=None, give_notes=False, give_durations=False, debug=False):
    '''Realign notes within bar lines (e.g. splitting rest events which cross barlines after reading in from midi)
    
    Warning: do not begin a bar with an acciacatura as current_pos will get out of sync (acciacatura implies rests and anticipation which gets confusing for timing)
    (at least in the case where the previous bar ends with a rest, not tested otherwise)'''
    notes = [notev[2] for notev in track.get_notes()]
    durations = [notev[1] for notev in track.get_notes()]
    
    # output will get out of alignment if we start mid-bar, let's workaround by padding with rests at start
    if pickup == 0: # input sanitising
        pickup = None
    if pickup is not None:
        notes = [[]] + notes
        durations = [1/pickup] + durations
    
    notes2 = []
    durations2 = []
    current_pos = 0 # maybe this should be set negative in the case of a pickup bar / upbeat ? e.g. determined by split pos
    for i, duration in enumerate(durations):
    
        # if a duration < 1.0 then we have a conjoined bar
        # e.g. a rest of duration 0.88888 is the same as 1.0 + 0.125 (i.e. whole plus quarter rest)
        # because 1/0.8888 = 1.125
        if duration < 1.0:
            ones = int(1//duration) # // gives integer part of div
            remainder = 1/duration - ones
            
            # check if we are at the end/start of a new bar
            if round(current_pos*2**10)/2**10 == current_pos//1 or round(current_pos*2**10)/2**10 == current_pos//1 + 1:  
                if debug:
                    print('splitting rest',i)
                new_durations = ones*[1.0] + [1/remainder]
            else: # if we are part way through a bar then the rem comes first
                new_durations = [1/remainder] + ones*[1.0] 
                
            notes2 += (ones+1)*[notes[i]]
            durations2 += new_durations
            current_pos += 1/durations[i]
            
        else:
            if debug:
                print(i, 'current_pos',current_pos, round(current_pos*2**10)/2**10, 1/durations[i], current_pos + 1/durations[i])
            notes2.append(notes[i])
            durations2.append(durations[i])
            current_pos += 1/durations[i]

    t = Track()
    if debug:
        t2 = Track()
        print(len(durations2), durations2)
        print(len(notes2), notes)
    for i, _ in enumerate(durations2):
        if debug:
            if not t2.add_notes(notes2[i], durations2[i]):
                print('')
                print(f'failed to add {notes2[i]}, {durations2[i]} to on index {i}')
                print(i, t2.bars[-3:])
                print('')
        t.add_notes(notes2[i], durations2[i])

    # outputs
    if give_notes and give_durations:
        return t, notes2, durations2
    elif give_notes:
        return t, notes2
    elif give_durations:
        return t, durations2
    else:
        return t

#%%
    
class JazzLick:
    '''
    parameters:
        source: data to instantiate the object (e.g. for conversions/analysis)
        chords: 
            - if source is type Composition, chords are generated by get_chords_from_track()
        passage:
            - if source is type Composition, passage is a Track containing main lick
            - Now: mostly data, used when writing final midi
            - TO-DO: get in a nice form for analysing rhythms, fragments, arpeggios etc.
        
    '''
    def __init__(self, source=None, chord_track=1, passage_track=2, chords=None, passage=None, tags=[], name=None):
        self.ID = int(datetime.now().strftime('%Y%m%d%H%M%S'))
        self.source = source
        self.chords = chords
        self.passage = passage
        self.name = name
        if type(tags) != list:
            tags = [tags]
        self.tags = tags
        
        # instantiate from source (e.g. comp and attach get_chord_from_Track)
        source_type = type(source)
        if source_type == Composition:
            
            # chords
            if chords is None:
                ch = get_chords_from_track(source.tracks[chord_track]) 
                sh = [c[3] for c in ch]
                print('Detected chords: ', sh[0:3], '...')
                self.chords = ch
            if chords is not None:
                print('Supplied chords overwrite auto-generated')
                self.chords = chords
                
            # passage
            print('Passage from composition added')
            self.passage = source.tracks[passage_track]
        
        elif source_type != type(None):
            print('unrecognised source type')

    def __repr__(self):
        return str((self.ID, self.passage))

    def tag(self, note):            
        if type(note) == list:
            self.tags += note
        else:
            self.tags.append(note)
        
    def to_midi(self, fp=''):
        if len(fp)>0:
            outf = r'C:\Users\Sam\Documents\Sidewinder\local files\\'+f'{fp}.mid'
        else:
            outf = r'C:\Users\Sam\Documents\Sidewinder\local files\midi_out.mid'

        if type(self.source) == Composition:
            midi_file_out.write_Composition(outf, self.source, repeat=0, verbose=True)
        elif type(self.passage) == Track:
            midi_file_out.write_Track(outf, self.passage, repeat=0, verbose=True)
    
    def to_json(self):
        out = dict()
        if is_jsonable(self.source):
            out['source'] = self.source
        if is_jsonable(self.chords):
            out['chords'] = self.chords
        if is_jsonable(str(self.passage)):
            out['passage'] = str(self.passage)
        if is_jsonable(self.tags):
            out['tags'] = self.tags
        if is_jsonable(self.name):
            out['name'] = self.name            
        return json.dumps(out) # 
        
    def store(self, db):
        'Save the JazzLick (as JSON) to the db'
        db.insert(json.loads(self.to_json())) # TO-DO: change this to jsonpickle so that we can reinstantiate class
    
#    def to_ly(self, fp=''):
        # No need for a function - run to_midi() then open in Lilypond via midi2ly (e.g. drag-and-drop into Frescobaldi)



#%% Logic for manipulation Bars and Tracks, generally where the object already exists and needs re-instantiating or slicing

def Bars_from_list(listb=[[0.0, 8.0, None],[0.125, 8.0, ['C-5']]]):
    '''
    Helps TinyDB de-serialisation (load)
    Input list of (representations of) bars of the form [[position,duration,[note(s)]] , ...]
    Places these note events into Bar objects and returns as a list of Bars
    '''
    #listb = [notev[0] if len(notev) == 1 else notev for notev in listb] # commented out as was repeating whole bars (notev = [whole bar note container nc])
    listb = [nc if type(notev[0])!=float else notev for notev in listb for nc in notev]
    b = Bar() # we're instantiating Bars so I'm not sure why the outputs are sometimes type [list]..., cf fix_track_bar()
    bars = [b]
    for notev in listb:
        if notev != []:
            if bars[-1].place_notes(notev[2], notev[1]):
                pass
            else:
                bars.append(Bar())
                bars[-1].place_notes(notev[2], notev[1])
    return bars
           
def Track_from_list(listt=[[[0.0, 8.0, None], [0.125, 16.0, ['C-6']]]]):
    t = Track()
    for bars in listt:
        t.add_bar(bars)
    return t

def fix_track_bar(bar):
    if type(bar) == list: # i.e. not Bar
        if bar == []:
            return []
        if len(bar[0]) > 1: # len=3 if list [[a, b, NoteContainer]] 
            b = Bar()
            b.place_notes(bar[0][2], bar[0][1])
            bar = b
        else: # if list like [Bar] or [Bar, Bar] (hopefully no [Bar]x3's)
            return bar
    return [bar]      

def split_track(track, split_points):
    track_splits = []
    boundaries = [[z[0],z[1]] for z in list(zip([1]+split_points, split_points+[99999]))]

    for pair in boundaries:
        track_piece = []

        if (pair[0]//1 != pair[0]) or (pair[1]//1 != pair[1]): # if a boundary start or end is a fraction
            if pair[0]//1 != pair[0]: # if we start mid-bar
                start_partialbar = split_bar(track[int(pair[0]//1-1)], pair[0] - pair[0]//1)[1]
                pair[0] = int(pair[0]//1 + 1)
                track_piece.append(start_partialbar) 
            if pair[1]//1 != pair[1]: # if we end mid-bar
                end_partialbar = split_bar(track[int(pair[1]//1-1)], pair[1] - pair[1]//1)[0]
                pair[1] = int(pair[1]//1)
                epb = True
            track_piece.append(track[pair[0]-1:pair[1]-1])
            if epb:
                track_piece.append(end_partialbar)
                epb = False
            #track_piece = [b for bar_list in track_piece for b in bar_list]
            track_piece = flatten(track_piece)
            track_splits.append(track_piece)
        else:
            track_splits.append(track[pair[0]-1:pair[1]-1])   
    
    out = []
    for i, lick in enumerate(track_splits):
        out_track = Track_from_list(lick)
        pickup = split_points[i-1]-split_points[i-1]//1
        if pickup == 0:
            pickup = None
        out_track = temporal_realign_track_bars(out_track, pickup=pickup) 
        out.append(out_track)
    
    return out 

def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt

def split_bar(bar, split_point):
    current_pos = 0
    bar_l = Bar()
    
    if 1/bar[0][1] > split_point: # if the first event crosses the split point (e.g. a conjoined rest)
        bar_l.place_notes(bar[0][2], 1/split_point)
        current_pos += split_point
        bar = [[bar[0][0], 1/(1/bar[0][1]-split_point), bar[0][2]]] + bar[1:] 
    
    while current_pos < split_point:
        bar_l.place_notes(bar[0][2], bar[0][1])
        current_pos += 1/bar[0][1]
        bar = bar[1:]
    bar_r = bar   
    bar_r = [fix_track_bar([b])[0] for b in bar_r]
    
    return bar_l, bar_r
    
#%% lick ingestion functions
    
def split_track_chords(chords, split_points):
    
    split_chords = [chords[int(i-1):int(j-1)] for i, j in zip([1]+split_points, split_points+[99999])] # note that this will round bars if split is fraction
    
    # instead of naively returning the split chords, we should relabel durations so that each split begins from bar pos 0
    # and appropriate counting of partial bars is retained (note that it is probably in the initial lick splitting where we never really distinguish between licks which begin with notes vs. rests (i.e. partial bars))
    out = []
    for split in split_chords:
        start_idx = split[0][0]
        reindexed_split = []
        for i, chord in enumerate(split):
            reindexed_chord = [chord[0]-start_idx] + chord[1:] # note that [i,j,chord name, chord symbol] comes from get_chords_from_track (j is in-bar event number but may need to refer to position in case we have different length chords)
            reindexed_split.append(reindexed_chord)
        out.append(reindexed_split)
    
    return out

def licks_from_track(track, chords, split_points, shared_tags=[''], individual_tags=None):
    if individual_tags == None:
        individual_tags = [[] for i in range(len(split_points)+1)]
      
    track = temporal_realign_track_bars(track) # fix conjoined bars from midi in: now bar i = track[i-1]
    track_splits = split_track(track, split_points)
#    for i, lick_track in enumerate(track_splits):
#        midi_file_out.write_Track(r'C:\Users\Sam\Documents\Sidewinder\local files\lick_'+str(i)+'.mid', lick_track)
    
    track_chords = split_track_chords(chords, split_points)
    
    licks = []
    for i, lick in enumerate(track_splits):
        y_Obj = JazzLick(passage=track_splits[i], chords=track_chords[i], tags=shared_tags+individual_tags[i])
        licks.append(y_Obj)
        
    return licks  
