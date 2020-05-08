# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 11:00:34 2020

@author: Sam
"""
from utilities import synonyms, synonyms_r
synonyms.update(synonyms_r)

from mingus.containers import Track, Bar
from mingus.containers.composition import Composition
from mingus.midi import midi_file_out, midi_file_in
import mingus.core.chords as chords
chord_to_shorthand = {v:k for k,v in chords.chord_shorthand_meaning.items()}

import json
from itertools import combinations
from datetime import datetime
import numpy as np

#%%
from tinydb import TinyDB, Query # https://tinydb.readthedocs.io/en/latest/getting-started.html
db = TinyDB(r'C:\Users\Sam\Documents\Sidewinder\local files\jazz-licks-db.json') # set-up / connection
#db.insert({'name': 'test', 'passage': None, 'tags':'251'})
#db_size = len(db.all())

#%% misc
def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

#%% db functions
def find_all_matches(db, entry):
    q = [(Query()[t[0]]==t[1]) for t in [(key,value) for key, value in entry.items()]]
    
    qq = q[0]
    for i, subq in enumerate(q):
        if i>0:
            qq = qq & q[i] # combine the full query with &'s
    
    return [x.doc_id for x in db.search(qq)]

def load_entry(db, entry):
    '''
    TO-DO: Returns the entry as an object 
    '''
    #process and potentially do some mingus instantiation, then JazzLick() -  should use jsonpickle for convenience
    return JazzLick(entry) # placeholder for Class instantiation - defn depends on use reqs e.g. auto-convert between scale degree formats

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
            chord_notes = event[2]
            chord_notes = [note.name for note in chord_notes]

            possible_chord_names = respell_and_determine(chord_notes)
            most_likely_chord_names = [poss[0] for poss in possible_chord_names]
            best_or_none = lambda x: None if x==[] else x[0]
            most_likely_chord = best_or_none(most_likely_chord_names)
            
            # get shorthand as mingus doesn't have a chord-from-fullname function
            if most_likely_chord is not None:
                ch = [most_likely_chord.split(' ')[0]] + [' '.join(most_likely_chord.split(' ')[1:])]
                sh = ch[0] + chord_to_shorthand[f' {ch[1]}']
            else:
                sh = None
            results.append([i, j, most_likely_chord, sh])
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

def respell_and_determine(chord):
    named_chords = [chords.determine(chord)]
    if len(named_chords[0]) == 0:
        named_chords = []
    
    candidates = list(set(chord) & set(list(synonyms.keys()) + list(synonyms.values())))
    for i in range(0, len(candidates)):
        combs = combinations(candidates, i+1)
        for comb in combs:
            respelling = chord.copy()
            for to_syn in comb:
                respelling[respelling.index(to_syn)] = synonyms[to_syn]
                if chords.determine(respelling) != []:
                    named_chords.append(chords.determine(respelling))
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
    for i, dur in enumerate(durations2):
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
            - if source is type Composition, chords are [bar_idx, event_idx, chordname, shorthand] cf get_chords_from_track()
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

    def tag(self, note):            
        if type(note) == list:
            self.tags += note
        else:
            self.tags.append(note)
        
    def to_midi(self, fp=''):
        if type(self.source) == Composition:
            midi_file_out.write_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\midi_out.mid', 
                                            self.source, repeat=0, verbose=True)
        elif type(self.passage) == Track:
            midi_file_out.write_Track(r'C:\Users\Sam\Documents\Sidewinder\local files\midi_out.mid', 
                                            self.passage, repeat=0, verbose=True)
    
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



#%% random utility functions for manipulating bars etc, not the nicest code and may be more suitable in Sidewinder core

def Bars_from_list(listb=[[0.0, 8.0, None],[0.125, 8.0, ['C-5']]]):
    listb = [notev[0] if len(notev) == 1 else notev for notev in listb]    
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
    
#%% lick ingestion workflow
    
def split_track_chords(chords, split_points):
    return [chords[int(i-1):int(j-1)] for i, j in zip([1]+split_points, split_points+[99999])]

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

#%% examples - here for dev purposes
    
if __name__ == 'main':
    print('If you are seeing this then LickLibrary is running in main!')
    # Load midi generated by Lilypond (Frescobaldi)
    y_comp, y_bpm = midi_file_in.MIDI_to_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\jiminpark\20 Licks in Jazz 251.mid') # generated via Lilypond (Frescobaldi)
    #midi_file_out.write_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\std_midi_out.mid', 
    #                                y_comp, repeat=0, verbose=True)
    #analyse_composition(y_comp)
    
    split_points = [5, 9, 13, 17, 21, 25, 29, 33, 36.5, 40.5, 45, 49, 53] # bar numbers 
    shared_tags = ['251','major','jiminpark']
    individual_tags = [[] for i in range(9)] + 2*[['pickup']] + [[] for i in range(3)]
    
    licks = licks_from_track(y_comp.tracks[2], get_chords_from_track(y_comp.tracks[1]), split_points,
                             shared_tags, individual_tags)
       
    
    #%%
    y_Obj = JazzLick(source=y_comp, chords=get_chords_from_track(y_comp.tracks[1]), tags=['251', 'major', 'jiminpark'])
    #y_Obj.to_midi()
    #y_Obj.store(db)
    #y_Obj.tag(['4 bars','quaver lines'])
    
    # ---------------------->> NOW ALSO CREATE SOME CODE TO IMPORT THE JIMINPARK 251 INDIVIDUAL MIDIS TO DB
    
#   NEXT -==========================================
    # 1) given slice markers, separate different licks
    # overlaying on progressions
    # 2) scale degree analysis e.g. generate more licks and find patterns


#%% Obsolete code (for reference)
    
#def split_track_at_barnum(track, barnum=1.5, too_long=False): # e.g. halfway through first bar
#    # might also want a version in terms of beats (deals with other meters - see bar.meter)
#    if float(np.floor(barnum)) == float(barnum):
#        return track[int(barnum-1):], track[:int(barnum-1)]
#    else:
#        split_bar = track[int(np.floor(barnum))-1]
#        if type(split_bar) == list:
#            split_bar = Bars_from_list(split_bar)[0]
#            
#        try:
#            while split_bar == []:
#                print('Warning, empty list encountered, should probably filter track in a different fn e.g. temporal_...')
#                track.bars.pop(int(np.floor(barnum))-1)
#                split_bar = track[int(np.floor(barnum))-1]
#                if type(split_bar) == list:
#                    split_bar = Bars_from_list(split_bar)[0]
#        except AttributeError: # split_bar != []
#            pass
#            
#        dur_target = (barnum-int(np.floor(barnum)))*split_bar.meter[0] * (1/split_bar.meter[1])                
#        pos = split_bar[0][0] # start position of first note or rest
#        for i, notev in enumerate(split_bar):
#            # deal with conjoined rests e.g. splitting [[0.0, 0.888, []]] into [[[0.0, 8.0, []]], [[0.0, 1.0, []]]]
#            if 1/notev[1]>=dur_target-pos and (notev[2]==[] or type(notev[2]) == type(None)):
#                print('splitting rest:', notev) 
#                restev = Bar()
#                try:
#                    restev.place_rest(1/(dur_target-pos))
#                except ZeroDivisionError: # dur_target-pos=0 => no rest added (like an infinitely subdivided rest)
#                    pass
#                restev_rem = Bar()
#                try:
#                    restev_rem.place_rest(1/(1/notev[1] - (dur_target-pos)))
#                except ZeroDivisionError:
#                    pass
##                print(barnum, dur_target, pos, notev)
#                
#                if not too_long:
#                    print('split into {} + {}'.format(restev, restev_rem))
#                    split_bar = [restev] + [restev_rem]
#                else:
#                    print('split into {} + {}'.format(restev_rem, restev))
#                    split_bar = [restev_rem] + [restev]
#                
#                L, R = split_bar[:i+1], split_bar[i+1:]
#            
#            elif pos + 1/notev[1] > dur_target: # if the split would cut a note in half, round down our split point to just before
#                L, R = split_bar[:i], split_bar[i:]
#                break
#            
#            pos += 1/notev[1]
#        
#        try:
#            out = track.bars[:int(np.floor(barnum)-1)]+[L], [R]+track.bars[int(np.floor(barnum)):]
#        except UnboundLocalError:
#            out = track.bars[:int(np.floor(barnum)-1)], track.bars[int(np.floor(barnum)):] # if we didn't ever fill the bar
#        
#        return out
#
#def push_or_pull_next_bar(i, track):
#    
#    bar = track[i]
#    if type(bar) == list:
#        bar = Bars_from_list(bar)[0]
#    next_bar = track[i+1]
#    bar_length = sum([1/notev[1] for notev in bar]) * bar.meter[0]*(1/bar.meter[1])
##    print('bar {} of length {}'.format(i, bar_length))
#   
#    while bar_length < 1:
#        print(f'bar {i} too short ({bar_length})', bar)
##        print(len(bar))
##        print('next bar', next_bar)
#        # pull back from the start of the next bar until our length is 1
#        rem = 1 - bar_length
#        back_of_track, next_bar_rem = split_track_at_barnum(track, i+2 + rem)
##        next_bar_shaved = next_bar_shaved[0] # the remaining bit we need to fill our bar
##        next_bar_rem = next_bar_rem[0] # what's left in the next bar
##        next_bar = next_bar_rem
##        next_notev = next_bar_shaved[0]
#        
#        try:
#            while next_bar_rem[0] == []:
#                next_bar_rem = next_bar_rem[1:]
#        except AttributeError: # comparison with empty list will fail if we are actually bars here
#            pass
#        next_notev = next_bar_rem[0][0]
#        
#        try:
#            bar.place_notes(next_notev[2], next_notev[1])
#        except IndexError:
#            bar.place_notes(None, next_notev[1])
#        bar_length += 1/next_notev[1] * bar.meter[0]*(1/bar.meter[1])
##        next_bar = next_bar[1:]
#        
#        track = Track_from_list(back_of_track + Bars_from_list(next_bar) + track[i+2:]) # inplace editing while iterating, uh-oh
#            
#    while bar_length > 1:
#        print(f'bar {i} too long ({bar_length})', bar)
#        # push forward into the start of the next bar until our length is 1
#        rem = bar_length - 1
#        back_of_track, excess = split_track_at_barnum(track, i+1 + rem, too_long=True)
#        # excess is the front half of the track, where excess[0] is [[[0.0, 8.0, None]]] and needs upserting into excess[1]
#        # back_of_track is the back half of the track including the split rest bar
#        
#        try:
#            while excess[0] == []:
#                excess = excess[1:]
#        except AttributeError: # comparison with empty list will fail if we are actually bars here
#            pass
#        last_notev = excess[0][0]
#        if type(last_notev[0]) == float:
#            last_notev = excess[0]
#
#        try:
#            if len(excess[1][0])<3:
#                excess[1] = [ev[0] for ev in excess[1]]
#        except IndexError: # no subsequent events
#            pass
#        
#        next_bar = [last_notev] + [[ev[0]+1/last_notev[0][1], ev[1], ev[2]] for ev in excess[1]] # insert and shift everything up
#        
##        next_bar = track[i+1]
##        try:
##            next_bar.place_notes(last_notev[2][0], last_notev[1])
##        except IndexError:
##            next_bar.place_notes(None, last_notev[1])
##        next_bar.notes = [last_notev] + next_bar.notes
#        bar_length += (-1)*1/last_notev[0][1] * bar.meter[0]*(1/bar.meter[1])
##        print('nb', next_bar)
#        track = Track_from_list(back_of_track + Bars_from_list(next_bar) + track[i+2:]) # inplace editing while iterating, uh-oh
#        
#    return track
#
#def temporal_realign_bars(track):
#    'MIDI_to_Composition can return bars with length longer than a full bar (given as duration < 1.0)'
#    'e.g. | - | r8 ... | -> [[0.0, 1/1.25, []]]'
#    'but we want to be able to navigate bars like [[0.0, 1.0, []]], [[0.0, 8.0, []], ...]'
#    'If we iterate over bars then we can periodically push extra bar content '
#    for i, bar in enumerate(track):
#        track = push_or_pull_next_bar(i, track) # should probably not be editing in place, and should maybe just store the left-hand tail as we iterate through the track
#
#    return track
        