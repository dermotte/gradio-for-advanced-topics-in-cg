# Gradio Examples for Advanced Topics in CG 

We are working with LLMs, and the examples in this repository show how to get started with Gradio.

## How to run? 

1. `git clone https://github.com/dermotte/gradio-for-advanced-topics-in-cg.git`
2. `cd gradio-app-tts-simple`
3. `uv sync`
4. `uv run <file>`

For the RAG example, make sure you run `index-data.py` first. It will download a few files from the Witcher Fandom Wiki, convert them to markdown and index them in a local vector store.