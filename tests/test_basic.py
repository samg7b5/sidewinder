# -*- coding: utf-8 -*-
# Note: using `pip install -e .` as per https://docs.pytest.org/en/latest/explanation/goodpractices.html#goodpractices

#from .context import sidewinder
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


class CoreExamplesRefactoring(unittest.TestCase):
    """Tests to drive work on refactor-core 28/03/21 (creating a Chart objective to replicate monolithic examples of chords_to_midi(), chords_to_bassline_midi())"""

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

        # most likely using the sidewinder.detect_numeral_pattern() function which should be refactored similarly with utilities.progression_to_chords() / Chart.numerals_list_to_shorthand_list()

        assert False

    def test_create_representation_of_chart_with_durations(self):

        assert True

    def test_generate_midi_from_shorthands_and_durations_in_4_4(self):

        assert True

    def test_generate_midi_from_shorthands_and_durations_in_3_4(self):

        assert True

    def test_generate_midi_with_choice_of_voicing(self):

        assert True

    def test_generate_walking_bassline_midi(self):

        assert True


if __name__ == '__main__':
    unittest.main()