"""
# Simple Gradio-Based Chatbot with an OpenAI-compatible API endpoint

This file implements a simple chatbot web app using Gradio and an OpenAI-compatible API endpoint.
It allows users to interact with an AI model (via a chat interface), sending messages and receiving
responses. The chatbot uses a specified system prompt and adjustable temperature for response
creativity. The code connects to a remote model endpoint and streams responses back to the user.

This implementation uses RAG (Retrieval-Augmented Generation) to provide context from the Witcher Fandom Wiki data to answer questions about Geralt of Rivia and other characters.
"""

import gradio as gr
from openai import OpenAI
import chromadb

# API configuration for local LLM endpoint
api_key = "local"

client = OpenAI(
    base_url="http://localhost:1234/v1/",
    api_key=api_key,
)


def search_data(query: str) -> list[str]:
    """
    Search for relevant documents in the ChromaDB vector store based on the query.
    
    Args:
        query (str): The search query to find relevant documents
        
    Returns:
        list[str]: List of document strings that match the query
    """
    # Connect to the ChromaDB persistent client
    chroma_client = chromadb.PersistentClient(path="./chromadb-data-geralt")
    # Get or create the character collection
    collection = chroma_client.get_or_create_collection(name="character")
    # Query for relevant documents
    results = collection.query(query_texts=[query], n_results=5)
    # Return the list of documents from the first query result
    return results["documents"][0]


"""
Chat function that handles user messages and generates responses using RAG.
Input parameters message and history come from the Gradio component.
System prompt and temperature have been added in the interface section.
"""


def predict(message, history, system_prompt, temperature):
    """
    Generate a response to a user message using RAG (Retrieval-Augmented Generation).
    
    This function:
    1. Searches for relevant context from the Witcher Fandom Wiki data
    2. Combines the user message with the retrieved context
    3. Sends the combined query to the LLM for response generation
    4. Streams the response back to the user
    
    Args:
        message (str): The user's message
        history (list): Chat history
        system_prompt (str): System prompt for the LLM
        temperature (float): Temperature setting for response creativity
        
    Yields:
        str: Chunks of the response as they are generated
    """
    # RAG part: find the context for the message
    user_context = ""
    for doc in search_data(message):
        user_context += doc + "\n\n"
    user_query = (
        "Please answer the following question: "
        + message
        + "\n\n You can use the following data as context: \n\n"
        + user_context
    )
    print(user_query)
    # LLM part: Let the LLM answer
    # history.append({"role": "user", "content": message})
    history.append({"role": "user", "content": user_query})
    stream = client.chat.completions.create(
        messages=[{"role": "system", "content": system_prompt}] + history,
        model="ibm/granite-4-h-tiny",
        stream=True,
        temperature=temperature,
    )
    chunks = []
    for chunk in stream:
        chunks.append(chunk.choices[0].delta.content or "")
        yield "".join(chunks)


demo = gr.ChatInterface(
    predict,  # function
    type="messages",
    additional_inputs=[
        gr.Textbox(
            "You are an expert on Geralt of Rivia, the witcher from the famous series. You answer questions based on the context provided. If the answer is not in the context, say 'I don't know'. Do not make up any information. You do not repeat information. You do not add any commentary. You only provide a factual answer to the question based on the data provided.",
            label="System Prompt",
        ),
        gr.Slider(label="Temperature", minimum=0, maximum=1, value=0.7, step=0.05),
    ],
    save_history=True,  # local history saving
    title="GAGA - Gradio App Geralt Answers",
    theme=gr.themes.Ocean(),
)

demo.launch()
