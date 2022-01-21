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
st.text("AI that generate piano pieces\nCreated by Annas")
st.markdown(
    """[more info here](https://github.com/annasajkh/PianoGPT)"""
)

form = st.form(key="submit-form")
input_text = re.sub("\s+", " ", form.text_input("Enter a title or let the AI generate it randomly"))
temperature = form.number_input("Temperature (the higher the value the less repetitive it will be)", min_value=0.3, max_value=1.0, value=1.0, step=0.01)
top_k = form.number_input("Top k (the number of highest probability to be consider)", min_value=3, max_value=50257, value=40, step=1)
generate = form.form_submit_button("Generate")

title = "".join([chunk[0].upper() + chunk[1:] if len(chunk) >= 2  else chunk for chunk in input_text.split(" ")])

if title.strip() != "":
    title += "\n"


if generate:
    with st.spinner("Generating..."):
        while True:
            process = subprocess.Popen([f"cd PianoGPT && ./gpt2tc -m 117M -l 1024 -k {top_k} -t {temperature} g 'T:{title}'"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            result = b""
            
            for i in range(300):
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

                    st.text(generated.split("T:")[1].split("\n")[0].split(",")[0])
                    st.audio(virtualfile)
                except:
                    continue
                break
