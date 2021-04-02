# -*- coding: utf-8 -*-
# Note: using `pip install -e .` as per https://docs.pytest.org/en/latest/explanation/goodpractices.html#goodpractices
# TO-DO: unittest -> pytest (?)

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

class BasicVoicingHandling(unittest.TestCase):
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

    def test_generate_1351_exercise_for_given_scale(self):

        assert True

    def test_detect_all_251s(self):

        assert True

    def test_shell_voicing(self):

        assert True


if __name__ == '__main__':
    unittest.main()