import os
import os.path
import pretty_midi
import io
import subprocess
import time
import re

import numpy as np
import streamlit as st

from scipy.io import wavfile

@st.cache(allow_output_mutation=True)
def setup():
    os.system("gdown --id 1-I_kCu3a0L8XeMDHZL_ILxwIcAyuNoPX")
    os.system("tar -xf PianoGPT.tar.gz")


setup()

st.title("PianoGPT")
st.text("AI that generate piano music\nCreated by Annas")

form = st.form(key="submit-form")
title = "".join([chunk.title() for chunk in re.sub("\s+", " ", form.text_input("Enter a title or let the AI generate it randomly")).split(" ")])

generate = form.form_submit_button("Generate")

if generate:
    
    with st.spinner("Generating..."):
        while True:
            process = subprocess.Popen([f"cd PianoGPT && ./gpt2tc -m 117M -l 1024 -t 0.9 g T:{title}, The"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            result = b""
            
            for i in range(150):
              text = process.stdout.readline()
              result += text

              if b"<|endoftext|>" in result:
                process.terminate()
                break
              
              time.sleep(0.1)


            generated = "X:1\n" + result.decode("utf-8").split("<|endoftext|>")[0]

            with open("generated_music.abc", "w") as f:
                f.write(generated)

            if "Error" not in str(subprocess.getoutput("abc2midi generated_music.abc -o generated_music.mid")):
                try:
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
                except:
                    continue
                break
