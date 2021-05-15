import sidewinder
from mingus.containers import Track
from mingus.core.chords import from_shorthand
from sidewinder.utilities import track_to_midi
from sidewinder import detect_numeral_pattern
from tinydb import TinyDB
from sidewinder.lick_library import load_entry, find_by_chords_durations
from sidewinder.lick_library import Track_from_list

def flatten(myList):
    if type(myList[0]) == list:
        return flatten([element for sublist in myList for element in sublist])
    else:
        return myList

def main():
    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
        IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
        v-7, I7b9, IVM7, IVM7,\
        bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
        IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 
                1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
                1, 1, 1, 1, 
                1, 2, 2, 2, 2, 2, 2, 
                1, 2, 2, 1, 2, 2, 2, 2, 1, 1, 1, 1]

    mistyChart = sidewinder.Chart(progression=misty_numerals, key='F')
    mistyChart.set_durations(durations=misty_durs)

    twofiveone = ['IIm7','V7','IM7']
    two_five_ones = detect_numeral_pattern(mistyChart.get_numeral_representation(), pattern=twofiveone, transposing='True', original_key=mistyChart.key)
    print(two_five_ones)

    tfo_durs = [[mistyChart.durations[tf['start_index']], mistyChart.durations[tf['start_index']+1], mistyChart.durations[tf['start_index']+2]] for tf in two_five_ones['hits']]

    # from random import choices
    # # asc = [1,2,3,4,5,4,3,1]
    # asc = [1,2,4,'b7','b9']
    # p = choices(asc, weights=[1,2,2,2,1], k=32)
    # print(p)
    # melody = get_scale_patterns('chromatic', p=p, keys=['F'], pattern_as_chromatic=True) 
    # print(melody['F'][0])

    # add a selection of melody to a selection of bars in the Composition

    arps = [[from_shorthand(chord)[i] for i in (0,1,2,3,2,1,0,1)] for chord in mistyChart.progressionShorthandList]
    notes_ = []
    note_durations = []
    for arp, chord_dur in zip(arps, mistyChart.durations):
        if chord_dur == 1:
            note_durations += [8 for _ in range(8)]
            notes_ += [arp[i] for i in range(8)]
        elif chord_dur == 2:
            note_durations += [8 for _ in range(4)]
            notes_ += [arp[i] for i in range(4)]
    assert len(notes_) == len(note_durations)

    t = Track()
    for i, _ in enumerate(note_durations):
        t.add_notes(notes_[i], note_durations[i])

    # use the db to add/overlay a 251 lick in the right place
    start_index = two_five_ones['hits'][0]['start_index'] # refers to index in chord progression (not bar)
    key = two_five_ones['hits'][0]['key']
    durs = tfo_durs[0] # [1,1,1]

    # chords_ = mistyChart.progressionShorthandList[start_index:start_index+len(twofiveone)]
    ### now search db for a 251 in F w/ duratons 1,1,1 then place at start_index
    db = TinyDB(r'C:\Users\Sam\Documents\Sidewinder\local files\jazz-licks-db-260720-new.json') # set-up / connection
    # candidate_licks = find_partial_matches(db, {'tags':'251'}) # gives db id's (doc_id) # searching should be better, done on actual chord metadata
    candidate_licks = find_by_chords_durations(db, chords=['Gm7','C7','FM7'], durations=[1,1,1])

    # candidate_licks = [load_entry(db, doc_id) for doc_id in candidate_licks] # instantiate from db
    lick251 = load_entry(db, candidate_licks[0])

    # for doc_id in candidate_licks[-15:]:
    #     print(db.get(doc_id=doc_id))
    # print(candidate_licks[0].chords)
    # candidate_licks[0].to_midi()

    notes_ = [nc[2] for bar in lick251.passage for nc in bar]
    notes_ = [nc[0] if bool(nc) else None for nc in notes_]
    durations_ = [nc[1] for bar in lick251.passage for nc in bar]

    # [start of Misty ... 251 lick notes_,durations_ ... rest of Misty] 
    start_bar = 8 # could compute using start_index and misty_durs
    t2 = Track_from_list(t[:start_bar-1])
    for n, d in zip(notes_, durations_):
        t2.add_notes(n, d)
    for bar in Track_from_list(t[start_bar-1+4:]): # known that the lick is 4 bars, could probably compute from lick251.passage
        t2 + bar

    track_to_midi(t2, name='midi_out\\test251_lick_add')

    # voiced_chords = voice_chords(mistyChart.progressionShorthandList)
    # track_to_midi(notes_durations_to_track(voiced_chords, mistyChart.durations), timestamp=False)

if __name__ == '__main__':
    main()