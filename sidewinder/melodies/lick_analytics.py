# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:03:27 2020

Temporary structure for functions to process and analyse licks (melodic lines)

@author: Sam
"""
from sidewinder.utilities import synonyms, note_to_scale_degree
import mingus.core.scales as scales


def track_to_degrees(track, key, scale, **kwargs):
    notes = [notev[2] for notev in track.get_notes()] # gives a list of NoteContainers
    note_names = [[note.name for note in nc] for nc in notes] # since each nc could contain multiple Note()'s
    return [[note_to_scale_degree(x, key, scale, **kwargs) for x in nc] for nc in note_names]