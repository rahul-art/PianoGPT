import os
import random
import pretty_midi

import streamlit as st
from aitextgen import aitextgen

os.system("gdown --id 1LMYHKntH9b348BviVwEG_CENXPlDDQDO")
os.system("apt install abcmidi")

st.title("PianoGPT")

ai = aitextgen(model_folder=".")
random_number = random.randrange(0, 150_000)
title = st.text_input(label="Enter a title or the ai will randomly generate it")

with st.spinner("Generating..."):
    generated = ai.generate_one(prompt=f"X:{random_number}\nT:{title}",
                                top_k=40,
                                temperature=0.8,
                                max_length=1024,
                                eos_token_id=437).replace("\n<|end", "")
    with open("generated_music.abc", "w") as f:
        f.write(generated)

    os.system("abc2midi generated_music.abc -o generated_music.mid")
    os.remove("generated_music.abc")
    
    # https://github.com/andfanilo/streamlit-midi-to-wav/blob/main/app.py
    midi_data = pretty_midi.PrettyMIDI("generated_music.mid")
    audio_data = midi_data.fluidsynth()
    audio_data = np.int16(
        audio_data / np.max(np.abs(audio_data)) * 32767 * 0.9
    )  # -- Normalize for 16 bit audio https://github.com/jkanner/streamlit-audio/blob/main/helper.py

    virtualfile = io.BytesIO()
    wavfile.write(virtualfile, 44100, audio_data)

    st.audio(virtualfile)