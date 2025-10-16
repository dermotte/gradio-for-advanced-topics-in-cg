import glob
import os
import requests  # type: ignore
import markdownify  # type: ignore
import chromadb  # type: ignore
import re

# URL to grab data from:
geralt_wiki_links = """https://witcher.fandom.com/wiki/Geralt_of_Rivia
https://witcher.fandom.com/wiki/Ciri
https://witcher.fandom.com/wiki/Yennefer_of_Vengerberg
https://witcher.fandom.com/wiki/Triss_Merigold
https://witcher.fandom.com/wiki/Kaer_Morhen
https://witcher.fandom.com/wiki/Emhyr_var_Emreis
https://witcher.fandom.com/wiki/Dandelion
https://witcher.fandom.com/wiki/Keira_Metz
https://witcher.fandom.com/wiki/Zoltan_Chivay
https://witcher.fandom.com/wiki/Vesemir""".splitlines()


def download_data() -> str:
    # Download the HTML content from a URL and convert to markdown
    directory_path = "./data/"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    for url in geralt_wiki_links:
        print(f"Downloading {url}...")
        response = requests.get(url)
        html_content = response.text
        markdown_content = markdownify.markdownify(html_content, strip=["a", "img"], heading_style="ATX")
        # start with the first headline & remove gallery and footer ..
        match = re.search(r"^# .+", markdown_content, re.MULTILINE).start()
        markdown_content = markdown_content[match:] 
        markdown_content = markdown_content[:markdown_content.find("## Gallery")] 
        filename = directory_path + url.split("/")[-1] + ".md"
        print(f"Writing to {filename}...")
        with open(filename, "w", encoding="utf-8") as text_file:
            text_file.write(markdown_content)

def index_data():
    for filename in glob.glob(os.path.join("./data/", "*.md")):
      print(f"Indexing {filename}...")
      with open(filename, "r", encoding="utf-8") as text_file:
          markdown_content = text_file.read()
      # paragraphs = split_markdown_paragraphs(markdown_content)
      paragraphs = split_markdown_by_header(markdown_content)
      # print(f"Found {len(paragraphs)} paragraphs.")
      chroma_client = chromadb.PersistentClient(path="./chromadb-data-geralt")
      collection = chroma_client.get_or_create_collection(name="character")
      collection.upsert(
          documents=paragraphs,
          metadatas=[{"source": filename}] * len(paragraphs),
          ids=[f"{filename}-{i}" for i in range(len(paragraphs))],
      )

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

download_data() # make a directory data and downloads the URLs there.
index_data()