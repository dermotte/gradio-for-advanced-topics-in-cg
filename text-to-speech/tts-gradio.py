import gradio as gr
from pathlib import Path
import requests

speech_file_path = Path(__file__).parent / "speech.wav"
tts_base_URL = "http://localhost:4123/"

def generate_response(
    text_in, slider_exaggeration, slider_cfg_weight, slider_temperature, text_speaker
):
    response = requests.post(
        tts_base_URL + "v1/audio/speech",
        json={
            "input": text_in,
            "exaggeration": slider_exaggeration,
            "cfg_weight": slider_cfg_weight,
            "temperature": slider_temperature,
            "voice":text_speaker
        },
    )

    with open(speech_file_path, "wb") as f:
        f.write(response.content)

    return speech_file_path


with gr.Blocks() as ttsblock:
    gr.HTML(
        """
        <h1 style='text-align: center;'> Text-to-Speech with Chatterbox 📢 </h1>
        <h3 style='text-align: center;'> Install Chatterbox TTS on a Server and change IP </h3>
        <p style='text-align: center;'> Powered by <a href="https://github.com/travisvn/chatterbox-tts-api"> Chatterbox-TTS</a>
        """
    )
    with gr.Group():
        with gr.Row():
            audio_out = gr.Audio(label="Spoken Answer", streaming=True, autoplay=True)
        with gr.Row():
            text_in = gr.TextArea(label="TTS", max_length=3000, submit_btn=True)
        # with gr.Row():
        # btn = gr.Button("Submit")
        with gr.Accordion("Parameters", open=False):
            with gr.Row():
                slider_exaggeration = gr.Slider(
                    0.25,
                    2.0,
                    0.5,
                    step=0.05,
                    label="Exaggeration",
                    info="Balanced is 0.5, below is more serious, above more dramatic.",
                )
            with gr.Row():
                slider_cfg_weight = gr.Slider(
                    0.2,
                    0.8,
                    0.5,
                    step=0.05,
                    label="CFG Weight",
                    info="Balanced is 0.5, below is faster, above slower.",
                )
            with gr.Row():
                slider_temperature = gr.Slider(
                    0.05,
                    5.0,
                    0.8,
                    step=0.05,
                    label="Temperature",
                    info="Balanced is 0.8, below is more consistent, above is more creative.",
                )
            with gr.Row():
                text_speaker = gr.Textbox("jessica", label = "Speaker")

    text_in.submit(
        generate_response,
        [text_in, slider_exaggeration, slider_cfg_weight, slider_temperature, text_speaker],
        audio_out,
    )

ttsblock.launch()