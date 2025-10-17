# Gradio Examples for Advanced Topics in CG 

We are working with LLMs, and the examples in this repository show how to get started with Gradio.

## How to run the GAGA app? 

1. `uv sync`
2. For the GAGA, the RAG example, run `python rag/index-data.py` first. It will download a few files from the Witcher Fandom Wiki, convert them to markdown and index them in a local vector store.
3. Run specific examples with `uv run <file>` (e.g., `uv run chat/simple-chat.py` or `uv run rag/rag-chat.py`)

For the chat examples, you'll need to have an LM Studio server running with the model "liquid/lfm2-1.2b" at http://localhost:1234/v1/
