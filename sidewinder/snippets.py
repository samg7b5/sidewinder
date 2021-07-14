from sidewinder.utilities import parse_progression

## CHUNKS

# could generate/generalise these e.g. two_five_one is implicitly the II, V and I chords from the major scale
two_five = 'ii-7, V7'
two_five_one = two_five + ', IM7'
two_five_one_four = two_five_one + ', IVM7'
three_six_two_five_one = 'iii-7, vi-7, ' + two_five_one
minor_two_five = 'iim7b5, V7'
minor_two_five_one = minor_two_five + ', im/M7'
minor_two_five_one_m7 = minor_two_five + ', i-7'
twelve_bar_blues = 'I7, IV7, I7, V7, IV7, I7'
major_to_minor = 'IM7, i-7'
dominant_two_to_minor_two = 'II7, ii-7'
dominant_in_fourths = 'I7, IV7'
sixth_relation = 'IM7, VI7' # could sub VI7 -> #io7 which functions like a VI7b9 (e.g. AC#EG -> C#EGBb)
one_to_flat_two = 'IM7, bIIM7' # bII is from parallel Phrygian, or tritone sub of VMaj7/bvii-7 (functions as Neapolitan subdominant), see https://www.youtube.com/watch?v=yF49xvxaaBY
half_step_dominants_up = 'I7, bII7'
half_step_dominants_down = 'I7, VII7'
minor_third_dominant = 'IMaj7, bIII7'
tonic_to_half_dim_seven = 'IM7, VIIm7b5'


CHUNKS = {k:parse_progression(v) for k,v in 
    {
        "25": two_five,
        "251": two_five_one,
        "2514": two_five_one_four,
        "36251": three_six_two_five_one,
        "minor 251": minor_two_five_one,
        "minor 251m7": minor_two_five_one_m7,
        "12 bar blues": twelve_bar_blues,
        "major to minor": major_to_minor,
        "II7 to ii7": dominant_two_to_minor_two,
        "I7 to IV7": dominant_in_fourths,
        "tonic to six dominant": sixth_relation,
        "tonic to flat two": one_to_flat_two,
        "half step dominants up": half_step_dominants_up,
        "half step dominants down": half_step_dominants_down,
        "tonic to b3 dominant": minor_third_dominant,
        "tonic to VII half dim": tonic_to_half_dim_seven,
    }.items()
}

## SUBSITUTIONS
backdoor_two_five = {'ii-7, V7': 'iv-7, bVII7'}
shelton_berg_backdoor = {'#ivm7b5, VII7, IM9': '#ivm7b5, VII7, iii-7'}
tritone_sub = {'V7': 'bII7'}
tritone_1625 = {'I, VI7, ii-7, V7': 'I, bIII7, ii-7, bII7'} # descending root like in Oleo (Coltrane)

CHORD_SUBS = {
    "tritone": tritone_sub,
    "backdoor 25": backdoor_two_five,
}


## STANDARDS

misty = 'IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, iii-7, VI7, ii-7, V7, \
            IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, I6, bVII9, IM7, \
            v-7, I7b9, IVM7, IVM7,\
            bv-7, VII7, II7, iii-7, VI7b9, ii-7, V7, \
            IM7, v-7, I7, IVM7, iv-9, bVII7, IM7, vi-7, ii-7, V7, III7, VI7b9, iim7b5, V7, I6'

misty_durs = [1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 
            1, 1, 1, 1, 
            1, 2, 2, 2, 2, 2, 2, 
            1, 2, 2, 1, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 1]

# could be simplified
yardbird_suite = "A, D-, G7, A7, G7, F#7, B7, E7, C#-, F#7, F#7,\
                  A, D-, G7, A7, G7, F#7, B7, E7, A7#11, A, G#7alt, \
                  C#-, D#m7b5, G#7b9, C#-, F#7, B-, C#m7b5, F#7, B7, B7, Bb7, \
                  A, D-, G7, A7, G7, F#7, B7, E7, C#-, F#7, B-, E7, A, D-, G7" # in A

yardbird_suite_durs = [1, 2, 2, 2, 2, 1, 1, 1, 2, 2, 1, 
                       1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 
                       1, 2, 2, 1, 1, 1, 2, 2, 1, 2, 2, 
                       1, 2, 2, 2, 2, 1, 1, 0.5, 2, 2, 
                       1, 2, 2, 2, 2]



# other examples
sentimental = 'E-, EminMaj7, E-7, E-6, A-, AminMaj7, A-7, A-6, B7, E-, E7, A-7, Ab7, Gmaj7, F-7, Bb7, Ebmaj7, C-7, F-7, Bb7, Ebmaj7, C7, F7, Bb7, Ebmaj7, C-7, F-7, Bb7, A-7, D7, E-, EminMaj7, E-7, E-6, A-, AminMaj7, A-7, A-6, B7, E-, E7, A-7, D7b9, Gmaj7'
sentimental_durs = [2, 2, 2, 2, 2, 2, 2, 4, 4, 1, 1, 2, 2, 2, 4, 4] + 6*[2, 2] + [1, 1] + [2, 2, 2, 2, 2, 2, 2, 4, 4, 1, 1, 2, 2, 1]

somedaymyprince = 'Cmaj7, E7#5, Fmaj7, A7#5, D-7, A7#5, D7, G7, ' + 'E-7, D#o, D-7, G7, E-7, D#o, D-7, G7, ' + 'Cmaj7, E7#5, Fmaj7, A7#5, D-7, A7#5, D7, G7, ' + 'G-7, C7, F7, F#o, C/G, D-7/G, G7, C'
somedaymyprince_durs = 29*[1] + [2,2,1]

desafinado = 'Gmaj7, A7b5, A-7, D7, B-7b5, E7b9, A-7, B7b9, E7, E7b9, A7b9, Abmaj7, D7b9, Gmaj7, A7b5, A-7, D7, B-7b5, E7b9, A-7, C-6, Gmaj7, C#-7b5, F#7#9, Bmaj7, Co7, C#-7, F#7, Bmaj7, Co7, C#-7, F#7, Bmaj7, G#-7, C#-7, F#-7, Dmaj7, D#o7, E-7, A7, A-7, F-6, A7, D7b9, Gmaj7, A7b5, A-7, D7, B-7b5, E7, A-7, C-6, Gmaj7, E-7, A7, C-7, F7, A7, A-7, D7, G6'
desafinado_durs = [1,1,2,2,2,2,2,2,2,2,1,2,2,1,1,2,2,2,2,2,2,2,4,4,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,1,2,2,2,4,4,1]

blueingreen = 'A-7, B7#9, E-7, Eb7b5, D-7, G7b9, Cmaj7, B7#9, E-7, F#7#5, B-7, E-7'
blueingreen_durs = [1,1,2,2,2,2,1,1,1,1,1,1]

robin = 'C#m9, C#m11b5, F#m7b5, C#m9, Gmaj7(#11), F#m7b5, ' +'C#m9, C#m11b5, F#m7b5, C#m9, Gmaj7(#11), F#m7b5, ' + 'B6, C7#5, C#13, C7#5, Bmaj9, Abmaj9, Bmaj9, C#m11b5, F#7, ' + 'C#m9, C#m11b5, F#m7b5'
robin_durs = [1,2,2]*4 + [1,1,1,1,1,1,1,2,2] + [1,2,2]