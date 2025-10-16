"""
# Simple Gradio-Based Chatbot with an OpenAI-compatible API endpoint

This file implements a simple chatbot web app using Gradio and an OpenAI-compatible API endpoint. 
It allows users to interact with an AI model (via a chat interface), sending messages and receiving 
responses. The chatbot uses a specified system prompt and adjustable temperature for response 
creativity. The code connects to a remote model endpoint and streams responses back to the user.
"""

import gradio as gr
from openai import OpenAI
import chromadb

api_key = "local"

client = OpenAI(
    base_url="http://localhost:1234/v1/",
    api_key=api_key,
)

def search_data(query: str) -> list[str]:
    chroma_client = chromadb.PersistentClient(path="./chromadb-data-geralt")
    collection = chroma_client.get_or_create_collection(name="character")
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    # print(results)
    return results['documents'][0]  # Return the list of documents from the first query result

"""
Chat function. 
Input parameters message and history come from the Gradio component.
System prompt and temparature have been added in the interface section.
"""
def predict(message, history, system_prompt, temperature):
    # RAG part: find the context for the message
    user_context = ""
    for doc in search_data(message):
        user_context += doc + "\n\n"
    user_query = "Please answer the following question: " + \
        message + "\n\n You can use the following data as context: \n\n" + user_context
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
    predict, # function
    type="messages",
    additional_inputs=[ 
        gr.Textbox("You are an expert on Geralt of Rivia, the witcher from the famous series. You answer questions based on the context provided. If the answer is not in the context, say 'I don't know'. Do not make up any information. You do not repeat information. You do not add any commentary. You only provide a factual answer to the question based on the data provided.", 
                   label="System Prompt"),
        gr.Slider(label="Temperature", minimum=0, 
                  maximum=1, value=0.7, step=0.05),
    ],
    save_history=True, # local history saving
    title="GAGA - Gradio App Geralt Answers",
    theme=gr.themes.Ocean(),
)

demo.launch()