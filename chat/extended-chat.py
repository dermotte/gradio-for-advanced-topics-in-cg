"""
# Simple Gradio-Based Chatbot with an OpenAI-compatible API endpoint

This file implements a simple chatbot web app using Gradio and an OpenAI-compatible API endpoint. 
It allows users to interact with an AI model (via a chat interface), sending messages and receiving 
responses. The chatbot uses a specified system prompt and adjustable temperature for response 
creativity. The code connects to a remote model endpoint and streams responses back to the user.
"""

import gradio as gr
from openai import OpenAI

api_key = "local"

client = OpenAI(
    base_url="http://localhost:1234/v1/",
    api_key=api_key,
)

"""
Chat function. 
Input parameters message and history come from the Gradio component.
System prompt and temparature have been added in the interface section.
"""
def predict(message, history, system_prompt, temperature):
    history.append({"role": "user", "content": message})
    stream = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt}] + history, 
        model="liquid/lfm2-1.2b", 
        stream=True,
        temperature=temperature,
    )
    chunks = []
    for chunk in stream:
        chunks.append(chunk.choices[0].delta.content or "")
        yield "".join(chunks)


demo = gr.ChatInterface(
    predict, # function
    type="messages",
    additional_inputs=[ 
        gr.Textbox("You are helpful AI.", 
                   label="System Prompt"),
        gr.Slider(label="Temperature", minimum=0, 
                  maximum=1, value=0.7, step=0.05),
    ],
    save_history=True, # local history saving
    title="GSE Chatbot",
    theme=gr.themes.Ocean(),
)

demo.launch()