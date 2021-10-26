import os
import os.path
import random
import pretty_midi
import io
import gc
import subprocess

import numpy as np
import streamlit as st

from scipy.io import wavfile
from aitextgen import aitextgen

@st.cache(hash_funcs={aitextgen: id}, allow_output_mutation=True)
def setup_ai():
    return aitextgen(model_folder=".")

if not os.path.isfile("pytorch_model.bin"):
    os.system("gdown --id 1LMYHKntH9b348BviVwEG_CENXPlDDQDO")

ai = setup_ai()
    
st.title("PianoGPT")
st.text("AI that generate piano music\nCreated by Annas")

form = st.form(key="submit-form")
title = form.text_input("Enter a title if not the AI will generate it randomly")

if title.strip() != "":
    title += "\n"

generate = form.form_submit_button("Generate")

if generate:
    random_number = random.randrange(0, 150_000)
    
    with st.spinner("Generating..."):
        while True:
            generated = ai.generate_one(prompt=f"X:{random_number}\nT:{title}",
                                        top_k=40,
                                        temperature=0.8,
                                        max_length=1024,
                                        eos_token_id=437).replace("\n<|end", "")
            with open("generated_music.abc", "w") as f:
                f.write(generated)

            if "Error" not in str(subprocess.getoutput("abc2midi generated_music.abc -o generated_music.mid")):
                break
        os.remove("generated_music.abc")

        # https://github.com/andfanilo/streamlit-midi-to-wav/blob/main/app.py
        midi_data = pretty_midi.PrettyMIDI("generated_music.mid")
        audio_data = midi_data.fluidsynth()
        audio_data = np.int16(
            audio_data / np.max(np.abs(audio_data)) * 32767 * 0.9
        )  # -- Normalize for 16 bit audio https://github.com/jkanner/streamlit-audio/blob/main/helper.py
        
        virtualfile = io.BytesIO()
        wavfile.write(virtualfile, 44100, audio_data)
        st.text(generated.split("T:")[1].split("\n")[0])
        st.audio(virtualfile)
        
        del virtualfile
        del audio_data
        del midi_data
        
        print(subprocess.getoutput("ls"))
        
        gc.collect()
