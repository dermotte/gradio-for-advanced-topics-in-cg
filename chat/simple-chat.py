import gradio as gr

# Don't forget to run LM Studio for an inference endpoint 
gr.load_chat("http://localhost:1234/v1/", 
             model="liquid/lfm2-1.2b", 
             token="***").launch()