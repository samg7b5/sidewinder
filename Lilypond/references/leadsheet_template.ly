\version "2.20.0"

  
melody = \relative c'' { % sets reference starting pitch where ' denotes 8va
     \key c \major
     \time 4/4
     r8 c16 b bes8 a g f d dis
     e g d? des c bes_"enclosure" g gis
     a1
   }

lead = \chordmode {
 { g1:m7 c:7 f:maj7
   }
}

\score {
 <<
  \new ChordNames \lead
  \new Staff \melody
 >>
 \layout { } % enable to also typeset if midi=true
 \midi { } % enable for midi - saves to AppData/Local/Temp/frescobaldi-xx
}
