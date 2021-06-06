# -*- coding: utf-8 -*-
# Note: using `pip install -e .` as per https://docs.pytest.org/en/latest/explanation/goodpractices.html#goodpractices
# TO-DO: unittest -> pytest (?)

from math import exp
from sidewinder.utilities import reduce_to_seventh_chord, reduce_to_triad
import sidewinder
import unittest

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True

    def test_import_from_sidewinder_core(self):
        synonyms = None
        from sidewinder import synonyms
        assert synonyms is not None

class RepresentationConversions(unittest.TestCase):
    """Tests to drive work on refactor-core 28/03/21 (creating a Chart object to replicate monolithic examples of chords_to_midi(), chords_to_bassline_midi())
    Specifically conversion between the various representations of a Chart (numerals, shorthands)"""

    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
    v-7, I7b9, IVM7, IVM7,\
    bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_key = 'F'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
            1, 1, 1, 1, 
            1, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

    def test_numeral_and_key_to_shorthand_list(self):
        
        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        #print(mistyChart.__dict__)

        cond1 = (mistyChart.progressionShorthandList[0] == 'FM7')
        cond2 = (mistyChart.progressionShorthandList[1] == 'Cm7')
        assert (cond1 & cond2)
    
    def test_shorthand_string_to_shorthand_list(self):

        shorthand_string = 'FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, Am7, D7, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, Eb9, FM7, Cm7, F7b9, BbM7, BbM7, Cbm7, E7, G7, Am7, D7b9, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, FM6'
        mistyChart = sidewinder.Chart(progression=shorthand_string, key=self.misty_key)

        cond1 = (mistyChart.progressionShorthandList[0] == 'FM7')
        cond2 = (mistyChart.progressionShorthandList[1] == 'Cm7')
        assert (cond1 & cond2)

    def test_shorthand_string_to_shorthand_tuples_list(self):

        shorthand_string = 'FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, Am7, D7, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, Eb9, FM7, Cm7, F7b9, BbM7, BbM7, Cbm7, E7, G7, Am7, D7b9, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, FM6'
        mistyChart = sidewinder.Chart(progression=shorthand_string, key=self.misty_key)

        cond1a = (mistyChart.progressionShorthandTuplesList[0][0] == 'F')
        cond1b = (mistyChart.progressionShorthandTuplesList[0][1] == 'M7')
        cond2a = (mistyChart.progressionShorthandTuplesList[1][0] == 'C')
        cond2b = (mistyChart.progressionShorthandTuplesList[1][1] == 'm7')
        assert (cond1a & cond1b & cond2a & cond2b)

    def test_difficult_shorthand_string_to_parsed_shorthand_list(self):

        shorthand_string = 'Fmaj7, co7, Ebm7b5, '
        mistyChart = sidewinder.Chart(progression=shorthand_string, key=self.misty_key)

        cond1a = (mistyChart.progressionShorthandTuplesList[0][0] == 'F')
        cond1b = (mistyChart.progressionShorthandTuplesList[0][1] == 'M7')
        cond2a = (mistyChart.progressionShorthandTuplesList[1][0] == 'C')
        cond2b = (mistyChart.progressionShorthandTuplesList[1][1] == 'o7')
        cond3a = (mistyChart.progressionShorthandTuplesList[2][0] == 'Eb')
        cond3b = (mistyChart.progressionShorthandTuplesList[2][1] == 'm7b5')
        
        assert (cond1a & cond1b & cond2a & cond2b & cond3a & cond3b)

    def test_shorthand_list_and_given_key_to_numerals_list(self):

        shorthand_string = 'FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, Am7, D7, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, Eb9, FM7, Cm7, F7b9, BbM7, BbM7, Cbm7, E7, G7, Am7, D7b9, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, FM6'
        shorthand_list = shorthand_string.replace(' ','').split(',')
        test_key = self.misty_key

        mistyChart = sidewinder.Chart(progression=shorthand_list, key=test_key)
        numerals = mistyChart.get_numeral_representation(key=test_key)
        
        cond1 = (numerals[1] == 'Vm7')
        assert (cond1)

class AddingDurationsToProgressions(unittest.TestCase):
    """Tests to drive work on refactor-core 28/03/21 (creating a Chart object to replicate monolithic examples of chords_to_midi(), chords_to_bassline_midi())
    Specifically overlaying durations to the Chart representations to create compositions e.g. voicings -> midi files"""

    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
    v-7, I7b9, IVM7, IVM7,\
    bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_key = 'F'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
            1, 1, 1, 1, 
            1, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

    def test_create_representation_of_chart_with_durations(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        mistyChart.set_durations(durations=self.misty_durs)
        assert self.misty_durs == mistyChart.durations

    def test_set_mismatched_length_durations_LONG(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        mistyChart.set_durations(durations=self.misty_durs*2)
        assert self.misty_durs == mistyChart.durations[:len(self.misty_durs)]

    def test_set_mismatched_length_durations_SHORT(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        mistyChart.set_durations(durations=self.misty_durs[:2])
        assert self.misty_durs[:2] == mistyChart.durations[:2]

class BasicVoicingMidiHandling(unittest.TestCase):
    """Tests to drive work on refactor-core 28/03/21 (creating a Chart object to replicate monolithic examples of chords_to_midi(), chords_to_bassline_midi())
    Specifically handling of basic 'vertical' (e.g. individual rootless) and 'horizontal' (== smooth voice leading, at this stage) voicing """

    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
    v-7, I7b9, IVM7, IVM7,\
    bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_key = 'C'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
            1, 1, 1, 1, 
            1, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

    def test_individual_chord_voicing_basic(self):
        
        from mingus.containers import Note
        from sidewinder.voicings.voicings import apply_individual_chord_voicing
        
        cond1 = (apply_individual_chord_voicing('Gm7')[3] == 'F-5') # default octave is 4 so it makes sense that we've extended to 5
        cond2 = (apply_individual_chord_voicing('Gm7', semitones=True)[3] == int(Note('F',5)))
        #        apply_individual_chord_voicing('shorthand':str, semitones:bool) returns a list of mingus Note()'s where semitone pitches are int(Note())'s
        
        assert (cond1 & cond2)
    
    def test_individual_chord_voicing_option_rootless(self):

        from mingus.containers import Note
        from sidewinder.voicings.voicings import apply_individual_chord_voicing
        
        # we would expect Gm7 to be voiced as (type B): 7,9,3,5 == F,A,Bb,D
        cond1 = (apply_individual_chord_voicing('Gm7', voicing_type='rootless', semitones=True, type='B')[0] == int(Note('F')))
        cond2 = (apply_individual_chord_voicing('Gm7', voicing_type='rootless', semitones=True, type='B')[1] == int(Note('A')))
        cond3 = (apply_individual_chord_voicing('Gm7', voicing_type='rootless', semitones=True, type='B')[2] == int(Note('Bb')))
        cond4 = (apply_individual_chord_voicing('Gm7', voicing_type='rootless', semitones=True, type='B')[3] == int(Note('D')))

        # we would expect D7 to be voiced as (type A): 7,9,3,13 == C,E,F#,B
        cond5 = (apply_individual_chord_voicing('D7', voicing_type='rootless', semitones=True)[0] == int(Note('C')))
        cond6 = (apply_individual_chord_voicing('D7', voicing_type='rootless', semitones=True)[1] == int(Note('E')))
        cond7 = (apply_individual_chord_voicing('D7', voicing_type='rootless', semitones=True)[2] == int(Note('F#')))
        cond8 = (apply_individual_chord_voicing('D7', voicing_type='rootless', semitones=True)[3] == int(Note('B')))
        
        assert (cond1 & cond2 & cond3 & cond4) & (cond5 & cond6 & cond7 & cond8)

    def test_basic_voiced_chord_midi_output(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        mistyChart.set_durations(durations=self.misty_durs)

        from sidewinder.utilities import notes_durations_to_track, track_to_midi
        from sidewinder.voicings.voicings import voice_chords

        # TO-DO: refactor the below into a Chart method?
        print('=== testing basic voiced chord midi out - please manually inspect the generated midi file: ===')
        voiced_chords = voice_chords(mistyChart.progressionShorthandList, voicing_type='rootless', type='A')
        assert track_to_midi(notes_durations_to_track(voiced_chords, mistyChart.durations), timestamp=False) is not None

    def test_smooth_voice_leading(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        mistyChart.set_durations(durations=self.misty_durs)

        from sidewinder.utilities import notes_durations_to_track, track_to_midi
        from sidewinder.voicings.voicings import voice_chords
        from sidewinder.voicings.voice_leading import smooth_voice_leading

        print('=== testing smooth voice leading - please manually inspect the generated midi file: ===')
        voiced_chords = voice_chords(mistyChart.progressionShorthandList, voicing_type='rootless', type='B')
        smooth_voiced_chords = smooth_voice_leading(voiced_chords)
        assert track_to_midi(notes_durations_to_track(smooth_voiced_chords, mistyChart.durations), name='midi_out\\smooth_voice_test_SVL', timestamp=False) is not None
        assert track_to_midi(notes_durations_to_track(voiced_chords, mistyChart.durations), name='midi_out\\smooth_voice_test_default', timestamp=False) is not None

    def test_generate_midi_from_shorthands_and_durations_in_3_4(self):
        print('test_generate_midi_from_shorthands_and_duration_in_3_4 not implemented!')
        assert True

    def test_generate_simple_bassline_midi(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        
        from sidewinder.utilities import notes_durations_to_track, track_to_midi
        from sidewinder.melodies.basslines import simple_bassline
        bassline_track = simple_bassline(mistyChart.progressionShorthandList, self.misty_durs)

        assert track_to_midi(bassline_track, name='midi_out\\bassline_test', timestamp=False) is not None

    def test_generate_walking_bassline_midi(self):

        mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        
        from sidewinder.utilities import notes_durations_to_track, track_to_midi
        from sidewinder.melodies.basslines import create_walking_bassline
        bassline_track = create_walking_bassline(mistyChart.progressionShorthandList, self.misty_durs)

        assert track_to_midi(bassline_track, name='midi_out\\walking_bassline_test', timestamp=False) is not None

class ScalePatternGeneration(unittest.TestCase):
    """02/04 
    - Shell voicing
    - 1351 chord exercises
    - pattern detection
    """

    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
    v-7, I7b9, IVM7, IVM7,\
    bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_key = 'C'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
            1, 1, 1, 1, 
            1, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

    def test_better_extension_from_chord_function(self):

        from sidewinder.utilities import get_diatonic_upper_chord_extension as f
        cond1 = (f('D7',3) == 'F#')
        cond2 = (f('D7',7) == 'C')
        cond2 = (f('D7',9) == 'E')
        cond3 = (f('CM6',6) == 'A')
        cond4 = (f('GM13',13) == 'E')
        cond5 = (f('C7b9',9) == 'Db')
        cond6 = (f('C7b9',13) == 'Ab') # f assumes a 7b9 is a harmonic minor V7 (e.g. C7b9 from F harmonic minor has Ab, Bb, Db)

        assert (cond1 & cond2 & cond3 & cond4 & cond5 & cond6)

    def test_generate_135arp_for_each_major_scale_ascending_chord_around_cycle_of_fifths(self):
        '''
        D  F#  A
          E  G  B
            F# A C#
              ...
        
        A  C#  E
          B  D  F#

        etc.
        '''

        from sidewinder.utilities import cycle_of_fifths
        from sidewinder.melodies.patterns import get_scale_patterns

        patterns = get_scale_patterns('Major', p=[1,3,5], keys=cycle_of_fifths(start='D'), name_only=True) # returns ascending scale patterns
        keys = [k for k,v in patterns.items()]
  
        cond1 = (patterns[keys[0]][0][0] == 'D')
        cond2 = (patterns[keys[0]][0][1] == 'F#')
        cond3 = (patterns[keys[0]][0][2] == 'A')
        cond4 = (patterns[keys[1]][1][0] == 'B')
        cond5 = (patterns[keys[2]][1][1] == 'A') # E -> F# -> A as m3
        cond6 = (patterns[keys[3]][2][2] == 'A#') # B -> D# -> A# as 5th

        assert (cond1 & cond2 & cond3 & cond4 & cond5 & cond6)

    def test_get_scale(self):

        from sidewinder.utilities import get_scale as g

        # print(g('major', 'E', ascending=False)[-1])
        # print(type(g('major', 'E', ascending=False)[-1]))
        conds = []
        conds += [
                    str(g('major', 'E', name_only=True)[0]) == 'E',
                    str(g('major', 'E', name_only=True)[1]) == 'F#',
                    str(g('major', 'E', name_only=True)[2]) == 'G#',
                    str(g('lydian', 'C', name_only=True)[3]) == 'F#',
                    str(g('Minor Pentatonic', 'C', name_only=True)[1]) == 'Eb',
                    str(g('Minor Pentatonic', 'C', name_only=True, ascending=False)[1]) == 'Bb',
                 ]

        for cond in conds:
            assert cond

    def test_get_scale_patterns(self):

        from sidewinder.melodies.patterns import get_scale_patterns as g
        from sidewinder.utilities import cycle_of_fifths
        from mingus.core.notes import reduce_accidentals

        asc = [1,3,5,7,4,11,8]
        target = ['C','E','G','B','F#','F#','C']
        result = g('lydian', p=asc, keys=cycle_of_fifths('C'))['C']

        conds = [ result[0][i].name == target[i] for i,_ in enumerate(target)
                ]

        target = ['D','F','G#','C','F#','F#','D']
        result = g('altered', p=asc, keys=['D'])['D']
        #print([reduce_accidentals(result[0][i].name) for i,_ in enumerate(target)])

        conds += [ reduce_accidentals(result[0][i].name) == target[i] for i,_ in enumerate(target)
                ]
        conds += [ result[0][4].octave == result[0][5].octave - 1]
        
        for cond in conds:
         #   print(cond)
            assert cond

    def test_get_diatonic_chords(self):

        from sidewinder.utilities import get_scale
        from sidewinder.melodies.patterns import get_scale_patterns
        from sidewinder.lick_library import respell_and_determine

        # note assert will fail if we use alternative shorthands like Maj7
        expected = {
            'phrygian': {1: 'Cm7', 2: 'DbM7', 3: 'Eb7', 4: 'Fm7', 5: 'Gm7b5', 6: 'AbM7', 7: 'Bbm7'},
            'major': {1: 'CM7', 2: 'Dm7', 3: 'Em7', 4: 'FM7', 5: 'G7', 6: 'Am7', 7: 'Bm7b5'},
        }
        
        # 1 3 5 7 on each scale degree
        for scale in list(expected.keys()):
            
            chord_degrees = [[i+j for i in (1,3,5,7)] for j, note in enumerate(get_scale(scale))]
            chord_notes = [get_scale_patterns(scale, p=chord_degrees[j]) for j, note in enumerate(get_scale(scale))]

            # then recognise as chord
            chords = [respell_and_determine(chord, shorthand=True) for chord in chord_notes[0]['C']]

            for k,v in expected[scale].items():
                assert chords[k-1][0][0] == v


    def test_note_to_scale_degree(self):

        from sidewinder.utilities import note_to_scale_degree as n

        conds = []
        conds += [
                n('C', 'C', 'major') == 1,
                n('G', 'C', 'major') == 5,
                n('Bb', 'C', 'mixolydian') == 7,
                n('F','G','Dorian') == 7,
                n('Db','C','chromatic') == 'b9',
                n('C#','C','chromatic') == 'b9',
        ]
        
        for cond in conds:
            #print(cond)
            assert cond
        
    def test_shell_voicing(self):

        conds = []
        conds += [
                
        ]
        
        for cond in conds:
            assert cond

class LicksOverChords(unittest.TestCase):
    """Compose a melodic line, using pre-defined licks and other methods, to accompany given chords"""

    misty_numerals = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
    v-7, I7b9, IVM7, IVM7,\
    bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
    IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_key = 'F'

    def test_import_frescobaldi_midi(self):

        test_files = []
        for file in test_files:
            # MIDI_to_Composition(file)
            # check known rhythms and pitches e.g. using a reference dict defined pre-loop
            ...

    def test_generate_and_save_midi_import_midi(self):
        ...


    def test_detect_all_251s(self):
        
        from sidewinder import detect_numeral_pattern
        
        # mistyChart = sidewinder.Chart(progression=self.misty_numerals, key=self.misty_key)
        shorthand_string = 'FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, Am7, D7, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, Eb9, FM7, Cm7, F7b9, BbM7, BbM7, Cbm7, E7, G7, Am7, D7b9, Gm7, C7, FM7, Cm7, F7, BbM7, Bbm9, Eb7, FM7, Dm7, Gm7, C7, FM6, FM6'
        mistyChart = sidewinder.Chart(progression=shorthand_string, key=self.misty_key) # in F
        numerals = mistyChart.get_numeral_representation(key=mistyChart.key)
        
        twofiveone = ['IIm7','V7','IM7']
        two_five_ones = detect_numeral_pattern(numerals, pattern=twofiveone, transposing='True', original_key=mistyChart.key)

        # original key results
        chords_ = [c.replace(' ','') for c in shorthand_string.split(',')]
        expect = [idx for idx, equal in enumerate([(i,j,k)==('Gm7','C7','FM7') for i,j,k in zip(chords_,chords_[1:],chords_[2:])]) if equal]
        found = [hit['start_index'] for hit in two_five_ones['hits']]
        assert expect == found
        
        # transposed results
        expect_transposed = [(1, 'Bb'), (15, 'Bb'), (39, 'Bb')]
        found_transposed = [(hit['start_index'], hit['key']) for hit in two_five_ones['transposed_hits']]
        assert expect_transposed == found_transposed

    def test_detect_all_CHUNKS(self):

        from sidewinder.snippets import CHUNKS, yardbird_suite
        from sidewinder.sidewinder import detect_numeral_pattern, Chart
        from random import choices
        
        choice = [list(CHUNKS.items())[i] for i in (0,0,2,1,1,3)]
        hits = {key: detect_numeral_pattern(
            Chart([ch for chunk in choice for ch in chunk[1]], 'A').get_numeral_representation(), 
            pattern=CHUNKS[key], 
            original_key='A'
            ) for key in [chunk[0] for chunk in choice]}
        # filter out empties
        hits = {chunk: hits[chunk] for chunk in list(hits.keys()) if any([len(hits[chunk][key])>0 for key in list(hits[chunk].keys())])}
        
        assert [hit['start_index'] for key in hits.keys() for hit in hits[key]['hits']] == [0, 2, 4, 8, 11, 16, 4, 4, 8, 11, 16, 14]


    def test_suggested_db_lick_has_correct_chords_and_durations(self):
        ... # see example 03


    def test_get_scale_choices_over_key_and_numeral_chord(self):
        # e.g. iii chord assume Phrygian e.g. Am7 in F - A Bb C D E F G . Also see get_diatonic_upper_extensions
        key, chord = ('F', 'iiim7') # should return ['A phrygian', ]
        ...

    def test_get_scale_choices_over_chord_shorthand(self):
        # less contextual info so make assumptions 
        ...

    def test_whether_numerals_sevenths_belong_to_a_mode(self):

        from sidewinder.snippets import CHUNKS
        from sidewinder.utilities import get_scale

        chords_ = CHUNKS["2514"] + CHUNKS["minor 251m7"] + ['I7']
        chart = sidewinder.Chart(progression=chords_, key=self.misty_key) # in F
        
        scale_types = ['major','harmonic minor','melodic minor']
        from sidewinder.harmony.changes import get_diatonic_chords # this is the key functionality added
        diatonic_seventh_chords = get_diatonic_chords(scale_types, (1,3,5,7))

        diatonic_chords = {scale: {} for scale in scale_types}
        for key in get_scale('chromatic'):
            transposed_chart = chart.get_numeral_representation(key=key.name)
            for scale in scale_types:
                diatonic_chords[scale][key.name] = [chord if chord in diatonic_seventh_chords[scale] else False for chord in transposed_chart]

        assert diatonic_chords['major']['F'] == ['IIm7', 'V7', 'IM7', 'IVM7', False, 'V7', False, False]
        assert diatonic_chords['harmonic minor']['F'] == [False, 'V7', False, False, 'IIm7b5', 'V7', False, False]
        ...



class AnalyseChordsAndExtensions(unittest.TestCase):
    """Know when to extend/alter chords given harmonic context"""

    from sidewinder.utilities import reduce_to_seventh_chord, reduce_to_triad

    def test_reduce_to_seventh_chord(self):

        cases = [
            ('CM13','CM7'),
            ('CM11','CM7'),
            ('CM7#11','CM7'),
            ('CM9','CM7'),
            ('G7alt','G7'),
            ('E7b9','E7')
        ]

        for test, expected in cases:
            assert reduce_to_seventh_chord(test) == expected # synonyms?

    def test_reduce_to_triad(self):
        '''
        Note: this is not equivalent to detecting tonality because e.g. G7 is more like CM than GM
        '''

        cases = [
            ('CM13','CM'),
            ('CM11','CM'),
            ('CM7#11','CM'),
            ('CM9','CM'),
            ('C6/9','CM'),
            ('Cadd9','CM'),
            ('C+9','CM'),
            ('G7alt','GM'),
            ('E7b9','EM'),
            ('Dm13','Dm'),
            ('Bbm7b9','Bbm'),
            ('Dm6', 'Dm')
        ]

        for test, expected in cases:
            print(test, expected, reduce_to_triad(test))
            assert reduce_to_triad(test) == expected # synonyms?

    def test_Chart_get_simplified_numeral_representation(self):

        from sidewinder import Chart
        from sidewinder.snippets import yardbird_suite
        
        ybird = Chart(yardbird_suite, 'A') # "A, D-, G7, A7, G7, F#7, B7, E7, C#-, F#7, F#7,\
                  # A, D-, G7, A7, G7, F#7, B7, E7, A7, A, G#7+9, \
                  # C#-, D#m7b5, G#7+9, C#-, F#7, B-, C#m7b5, F#7, B7, B7, Bb7, \
                  # A, D-, G7, A7, G7, F#7, B7, E7, C#-, F#7, B-, E7, A, D-, G7" # in A
        assert ybird.get_simplified_numeral_representation('triad') == ['IM', 'IVm', 'bVIIM', 'IM', 'bVIIM', 'VIM', 'IIM', 'VM', 'IIIm', 'VIM', 'VIM', 'IM', 'IVm', 'bVIIM', 'IM', 'bVIIM', 'VIM', 'IIM', 'VM', 'IM', 'IM', 'VIIM', 'IIIm', 'bVm', 'VIIM', 'IIIm', 'VIM', 'IIm', 'IIIm', 'VIM', 'IIM', 'IIM', 'bIIM', 'IM', 'IVm', 'bVIIM', 'IM', 'bVIIM', 'VIM', 'IIM', 'VM', 'IIIm', 'VIM', 'IIm', 'VM', 'IM', 'IVm', 'bVIIM']
        assert ybird.get_simplified_numeral_representation('seventh') == ['IM7', 'IVm7', 'bVII7', 'I7', 'bVII7', 'VI7', 'II7', 'V7', 'IIIm7', 'VI7', 'VI7', 'IM7', 'IVm7', 'bVII7', 'I7', 'bVII7', 'VI7', 'II7', 'V7', 'I7', 'IM7', 'VII7', 'IIIm7', 'bVm7', 'VII7', 'IIIm7', 'VI7', 'IIm7', 'IIIm7', 'VI7', 'II7', 'II7', 'bII7', 'IM7', 'IVm7', 'bVII7', 'I7', 'bVII7', 'VI7', 'II7', 'V7', 'IIIm7', 'VI7', 'IIm7', 'V7', 'IM7', 'IVm7', 'bVII7']


class ChordSubstitutions(unittest.TestCase):
    """"""


    def test_get_available_substitutions(self):

        from sidewinder import Chart
        from sidewinder.harmony.substitutions import get_available_chord_subs
        from sidewinder.snippets import CHUNKS, CHORD_SUBS, yardbird_suite

        
        ybird = Chart(yardbird_suite, 'A') 

        chosen_subs = [
            # get_available_chord_subs(CHORD_SUBS['backdoor 25'], ybird.get_numeral_representation(), ybird.key)[0],
            # get_available_chord_subs(CHORD_SUBS['backdoor 25'], ybird.get_numeral_representation(), ybird.key)[1],
            get_available_chord_subs(CHORD_SUBS['tritone'], ybird.get_numeral_representation(), ybird.key)[5],
        ]
        ...

if __name__ == '__main__':
    unittest.main()