# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 11:00:34 2020

@author: Sam
"""
from Sidewinder import synonyms, synonyms_r
synonyms.update(synonyms_r)

from mingus.containers.composition import Composition
from mingus.midi import midi_file_out, midi_file_in
import mingus.core.chords as chords
chord_to_shorthand = {v:k for k,v in chords.chord_shorthand_meaning.items()}

import json
from itertools import combinations
from datetime import datetime

#%%
from tinydb import TinyDB, Query # https://tinydb.readthedocs.io/en/latest/getting-started.html
db = TinyDB(r'C:\Users\Sam\Documents\Sidewinder\local files\jazz-licks-db.json')
#db.insert({'name': 'test', 'passage': None, 'tags':'251'})
db_size = len(db.all())

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
    Returns the entry as an object 
    '''
    #process and potentially do some mingus instantiation, then JazzLick()
    return entry_instantiated_as_lick_object(entry) # placeholder for Class instantiation - defn depends on use reqs e.g. auto-convert between scale degree formats

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

    def tag(self, note):            
        if type(note) == list:
            self.tags += note
        else:
            self.tags.append(note)
        
    def to_midi(self, fp=''):
        midi_file_out.write_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\midi_out.mid', 
                                self.source, repeat=0, verbose=True)
    
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
        return json.dumps(out)
        
    def store(self, db):
        'Save the JazzLick (as JSON) to the db'
        db.insert(json.loads(self.to_json()))
    
#    def to_ly(self, fp=''):
        # No need for a function - run to_midi() then open in Lilypond via midi2ly (e.g. drag-and-drop into Frescobaldi)

#%% examples
# Load midi generated by Lilypond (Frescobaldi)
y_comp, y_bpm = midi_file_in.MIDI_to_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\jiminpark\20 Licks in Jazz 251.mid')
#analyse_composition(y_comp)
track = y_comp.tracks[1]
y_chords = get_chords_from_track(track)

y_Obj = JazzLick(source=y_comp, chords=y_chords, tags=['251', 'major', 'jiminpark'])
#y.to_midi()

#### NEXT -==========================================> 
    # x1) combine chords with lick passage, potentially by creating a lick Object to ensure everything meshes together regardless of format
    # 2) given slice markers, separate different licks
    # 3) store in db 
    # 4) scale degree analysis

#midi_file_out.write_Composition(r'C:\Users\Sam\Documents\Sidewinder\local files\std_midi_out.mid', 
#                                y_comp, repeat=0, verbose=True)
    