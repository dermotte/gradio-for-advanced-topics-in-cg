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

geralt_context = """Geralt of Rivia is a legendary witcher from Andrzej Sapkowski's fantasy series The Witcher. Born as the son of sorceress Visenna and warrior Korin around 1211, he was raised at Kaer Morhen in Kaedwen. Geralt survived the Trial of The Grasses, gaining superhuman abilities such as heightened senses, strength, speed, resilience, complete immunity to conventional poisons, extreme pain resistance, and a white coat of hair that gave him the nickname "White Wolf".

Geralt embarked on his journey as a monster slayer for hire. He met his fellow classmate Eskel early on and together they became close friends, likened to brothers. His first contract involved killing a bald man who had abducted a young girl. Geralt's career included numerous adventures across the continent where he slew creatures like manticores, giants, and vampires.

During the Trial of The Grasses, Geralt displayed unusual tolerance for mutagens, which led to further experimental mutations granting him greater abilities but turning his hair white. He trained with Vesemir, regarded as a father figure, and later studied at Oxenfurt Academy under Yennefer's guidance.

Geralt began traveling widely on his horse Roach, taking contracts across the continent, fighting monsters, and assisting allies in various regions including Vizima, Kaedwen, Temeria, and Rivia. His most notable actions include thwarting the attempted assassination of King Foltest’s daughter Adda (turned striga) by curing her condition and discovering the identity of the mysterious Salamandra group that targeted witchers.

In The Witcher 3: Wild Hunt, Geralt sets out to find Ciri, who has been kidnapped by forces including the Wild Hunt. Throughout his journey he confronts various challenges and enemies culminating in defeating the Wild Hunt leader Eredin Bréacc Glas who offers Geralt Yennefer's soul in exchange for her freedom.

Throughout The Witcher series, Geralt maintains alliances with characters like Dandelion, Eskel, Yennefer (initially), Triss Merigold, and later Vengerberg mentors Vesemir and Iola. He navigates complex political landscapes dealing with conflicts between factions such as Nilfgaardian Empire, Scoia'tael rebels, and various local rulers.

Geralt's legacy is marked by his adventures detailed in ballads by Dandelion which romanticize his exploits while historical accounts provide factual insights into significant moments from his life. Despite being a popular figure among fans, accurate chronology sometimes varies between sources due to creative liberties taken during adaptations.

His story encompasses themes of loyalty, sacrifice, moral ambiguity, and personal growth reflecting deep exploration within fantasy narratives set against richly detailed worlds imbued with mythology inspired by Slavic folklore intertwined with broader epic fantasy elements."""

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
            "You are an expert on Geralt of Rivia, the witcher from the famous series. You answer questions based on the context provided. If the answer is not in the context, say 'I don't know'. Do not make up any information. You do not repeat information. You do not add any commentary. You only provide a factual answer to the question based on the data provided. This is a general overview on Geralt of Rivia: \n" + geralt_context,
            label="System Prompt",
        ),
        gr.Slider(label="Temperature", minimum=0, maximum=1, value=0.7, step=0.05),
    ],
    save_history=True,  # local history saving
    title="GAGA - Gradio App Geralt Answers",
    theme=gr.themes.Ocean(),
)

demo.launch()
