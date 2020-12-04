# ear-training

Various musical ear training apps. Uses pygame.midi to drive a MIDI device. I set up the IAC MIDI driver roughly according to [these instructions](https://sites.google.com/site/mfalab/mac-stuff/how-to-use-the-iac-driver) and then connected that to [Addictive Keys](https://www.xlnaudio.com/products/addictive_keys) to get a nice piano sound. (I assume one could wire it up to any synth or DAW.)

The actual training programs are:

- `progressions.py` -- recognize chord progressions.
- `chord_types.py` -- recognize types of chords.
- `solfege.py` -- recognize the notes of a scale by their solefège names.
