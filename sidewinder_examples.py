# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 19:38:09 2019

@author: Sam
"""
import sidewinder as sw

#%% General

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

# create a midi of the chords
t = sw.chords_to_midi(misty, misty_durs, name='midi_out\\misty_shellrootless', key='Eb', voicing='rootless', type='A') # includes voicing kwargs
# detect all 2-5's
two_fives = sw.detect_numeral_pattern(misty, pattern=['II-7','V7'])

tb = sw.chords_to_bassline_midi(misty, misty_durs, name='midi_out\\misty_bass', key='Eb') # includes voicing kwargs
    

# 2. Shorthand -> midi
giant_steps = 'Abmaj7, B7, Emaj7, G7, Cmaj7, F#-7, B7, Emaj7, G7, Cmaj7, Eb7, Abmaj7, D-7, G7, Cmaj7, F#-7, B7, Emaj7, Bb-7, Eb7, Abmaj7, D-7, G7, Cmaj7, Bb-7, Eb7'
bt2 = [2,2]
giant_steps_durs = 2*bt2 + [1] + 3*bt2 + [1] + 4*(bt2 + [1]) + bt2

t = sw.chords_to_midi(giant_steps, giant_steps_durs, voicing='shell', name='midi_out\\giant_stepssh') # no need to specify a key
tb = sw.chords_to_bassline_midi(giant_steps, giant_steps_durs, name='midi_out\\giantsteps_bass', walking=True, key='Eb') # includes voicing kwargs


# Combining 1 & 2:
# input chord symbols (e.g. from Real Book) and perform roman numeral analysis:
gs_numerals = sw.shorthand_to_numerals(giant_steps, key='A')
two_fives = sw.detect_numeral_pattern(gs_numerals, pattern=['II-7','V7'])


#%%
import sidewinder as sw

sentimental = 'E-, EminMaj7, E-7, E-6, A-, AminMaj7, A-7, A-6, B7, E-, E7, A-7, Ab7, Gmaj7, F-7, Bb7, Ebmaj7, C-7, F-7, Bb7, Ebmaj7, C7, F7, Bb7, Ebmaj7, C-7, F-7, Bb7, A-7, D7, E-, EminMaj7, E-7, E-6, A-, AminMaj7, A-7, A-6, B7, E-, E7, A-7, D7b9, Gmaj7'
sentimental_durs = [2, 2, 2, 2, 2, 2, 2, 4, 4, 1, 1, 2, 2, 2, 4, 4] + 6*[2, 2] + [1, 1] + [2, 2, 2, 2, 2, 2, 2, 4, 4, 1, 1, 2, 2, 1]

t = sw.chords_to_midi(sentimental, sentimental_durs, name='midi_out\\sentimentalr', voicing='rootless') # no need to specify a key
tb = sw.chords_to_bassline_midi(sentimental, sentimental_durs, name='midi_out\\sentimental_bass', walking=True)

#%%
import sidewinder as sw

somedaymyprince = 'Cmaj7, E7#5, Fmaj7, A7#5, D-7, A7#5, D7, G7, ' + 'E-7, D#o, D-7, G7, E-7, D#o, D-7, G7, ' + 'Cmaj7, E7#5, Fmaj7, A7#5, D-7, A7#5, D7, G7, ' + 'G-7, C7, F7, F#o, C/G, D-7/G, G7, C'
somedaymyprince_durs = 29*[1] + [2,2,1]

t = sw.chords_to_midi(somedaymyprince, somedaymyprince_durs, name='midi_out\\prince_rsmth', voicing='rootless') # no need to specify a key
tb = sw.chords_to_bassline_midi(somedaymyprince, somedaymyprince_durs, name='midi_out\\prince_bass')

#%%
import sidewinder as sw

desafinado = 'Gmaj7, A7b5, A-7, D7, B-7b5, E7b9, A-7, B7b9, E7, E7b9, A7b9, Abmaj7, D7b9, Gmaj7, A7b5, A-7, D7, B-7b5, E7b9, A-7, C-6, Gmaj7, C#-7b5, F#7#9, Bmaj7, Co7, C#-7, F#7, Bmaj7, Co7, C#-7, F#7, Bmaj7, G#-7, C#-7, F#-7, Dmaj7, D#o7, E-7, A7, A-7, F-6, A7, D7b9, Gmaj7, A7b5, A-7, D7, B-7b5, E7, A-7, C-6, Gmaj7, E-7, A7, C-7, F7, A7, A-7, D7, G6'
desafinado_durs = [1,1,2,2,2,2,2,2,2,2,1,2,2,1,1,2,2,2,2,2,2,2,4,4,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1,2,2,2,4,4,1]

t = sw.chords_to_midi(desafinado, desafinado_durs, name='midi_out\\desafinado_s', voicing='smooth') # no need to specify a key
tb = sw.chords_to_bassline_midi(desafinado, desafinado_durs, name='midi_out\\desafinado_bass')

#%%
import sidewinder as sw

blueingreen = 'A-7, B7#9, E-7, Eb7b5, D-7, G7b9, Cmaj7, B7#9, E-7, F#7#5, B-7, E-7'
blueingreen_durs = [1,1,2,2,2,2,1,1,1,1,1,1]

t = sw.chords_to_midi(blueingreen, blueingreen_durs, name='midi_out\\blueingreen_sh', voicing='shell', roots=True) # no need to specify a key
tb = sw.chords_to_bassline_midi(blueingreen, blueingreen_durs, name='midi_out\\blueingreen_bass', walking=True)

#%% 

import sidewinder as sw

robin = 'C#m9, C#m11b5, F#m7b5, C#m9, Gmaj7(#11), F#m7b5, ' +'C#m9, C#m11b5, F#m7b5, C#m9, Gmaj7(#11), F#m7b5, ' + 'B6, C7#5, C#13, C7#5, Bmaj9, Abmaj9, Bmaj9, C#m11b5, F#7, ' + 'C#m9, C#m11b5, F#m7b5'
robin_durs = [1,2,2]*4 + [1,1,1,1,1,1,1,2,2] + [1,2,2]

t = sw.chords_to_midi(robin, robin_durs, name='midi_out\\robinsh', voicing='shell', roots=True) # no need to specify a key
tb = sw.chords_to_bassline_midi(robin, robin_durs, name='midi_out\\robin_bass')

