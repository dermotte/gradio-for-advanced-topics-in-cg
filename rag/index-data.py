import requests  # type: ignore
import markdownify  # type: ignore
import chromadb  # type: ignore

# URL to grab data from:
geralt_wiki = "https://witcher.fandom.com/wiki/Geralt_of_Rivia"

def download_data(url: str) -> str:
    # Download the HTML content from a URL
    response = requests.get(geralt_wiki)
    html_content = response.text
    markdown_content = markdownify.markdownify(html_content)
    print(markdown_content)  
    with open("out.md", "w", encoding="utf-8") as text_file:
        text_file.write(markdown_content)

def index_data() -> str:
    with open("out.md", "r", encoding="utf-8") as text_file:
        markdown_content = text_file.read()
    paragraphs = split_markdown_paragraphs(markdown_content)
    # print(f"Found {len(paragraphs)} paragraphs.")
    chroma_client = chromadb.PersistentClient(path="./chromadb-data-geralt")
    collection = chroma_client.create_collection(name="character")
    collection.upsert(
        documents=paragraphs,
        metadatas=[{"source": "geralt_wiki"}] * len(paragraphs),
        ids=[f"geralt-{i}" for i in range(len(paragraphs))],
    )

    return markdown_content

def split_markdown_paragraphs(text):
  """Splits a Markdown string into paragraphs based on blank lines."""
  lines = text.splitlines()
  paragraphs = []
  current_paragraph = ""

  for line in lines:
    if line.strip():  # Check if the line is not empty after removing whitespace
      current_paragraph += line + "\n"
    else:
      if current_paragraph: # Avoid adding empty paragraphs
        paragraphs.append(current_paragraph.strip())
        current_paragraph = ""

  # Add the last paragraph if it exists
  if current_paragraph:
    paragraphs.append(current_paragraph.strip())

  return paragraphs

def split_markdown_by_header(text):
    """Splits Markdown text into chunks based on headers."""
    lines = text.splitlines()
    chunks = []
    current_chunk = ""

    for line in lines:
        if line.startswith("#"):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())  # Add the last chunk

    return chunks

# download_data(geralt_wiki) # edit manually to remove junk
index_data()