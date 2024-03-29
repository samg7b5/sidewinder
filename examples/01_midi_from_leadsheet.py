from sidewinder import Chart, detect_numeral_pattern
from sidewinder.voicings.voicings import voice_chords
from sidewinder.voicings.voice_leading import smooth_voice_leading
from sidewinder.melodies.basslines import create_walking_bassline
from sidewinder.utilities import notes_durations_to_track, track_to_midi
from mingus import *
from mingus.containers import Note

def main():
    # 1. Numerals -> midi
    misty = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
            IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
            v-7, I7b9, IVM7, IVM7,\
            bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
            IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, I6'

    misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
                1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
                1, 1, 1, 1, 
                1, 2, 2, 2, 2, 2, 2, 
                1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1]

    # load the variables into a Chart
    mistyChart = Chart(progression=misty, key='F')
    mistyChart.set_durations(durations=misty_durs)

    # voice the (auto-generated) shorthand chords, and export the (voiced chords, durations) as midi
    print(mistyChart.progressionShorthandList)
    voiced_chords = voice_chords(mistyChart.progressionShorthandList, voicing_type='rootless', type='A')
    track_to_midi(notes_durations_to_track(voiced_chords, mistyChart.durations), name='midi_out\\misty_rootlessA_example', timestamp=False)

    # generate a walking bassline and export as midi
    bassline_track = create_walking_bassline(mistyChart.progressionShorthandList, mistyChart.durations)
    track_to_midi(bassline_track, name='midi_out\\misty_wb_example', timestamp=False)

    # detect patterns e.g. all 2-5's
    two_fives = detect_numeral_pattern(mistyChart.get_numeral_representation(), pattern=['II-7','V7'], transposing='True', original_key=mistyChart.key)
    print(two_fives)


    # 2. Shorthand -> midi
    giant_steps = 'Abmaj7, B7, Emaj7, G7, Cmaj7, F#-7, B7, Emaj7, G7, Cmaj7, Eb7, Abmaj7, D-7, G7, Cmaj7, F#-7, B7, Emaj7, Bb-7, Eb7, Abmaj7, D-7, G7, Cmaj7, Bb-7, Eb7'
    bt2 = [2,2]
    giant_steps_durs = 2*bt2 + [1] + 3*bt2 + [1] + 4*(bt2 + [1]) + bt2

    gsChart = Chart(progression=giant_steps)
    gsChart.set_durations(durations=giant_steps_durs)

    print(gsChart.get_numeral_representation(key='Ab'))

    smooth_voiced_chords = smooth_voice_leading(voice_chords(gsChart.progressionShorthandList))
    track_to_midi(notes_durations_to_track(smooth_voiced_chords, gsChart.durations), name='midi_out\\giant-steps_smooth-voice-leading_example', timestamp=False)

if __name__ == '__main__':
    main()