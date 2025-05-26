import os
import tempfile
import uuid
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import pdfplumber
import requests
import whisper
import wikipedia
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.schema.messages import HumanMessage
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import AzureChatOpenAI


@tool
def search_pdf(pdf_url: str) -> str:
    """
    Download a PDF from the given URL and extract its text content.

    Args:
        pdf_url (str): The URL of the PDF file to download.

    Returns:
        str: The extracted text content from the PDF.
    """
    print("..[search pdf] ", pdf_url)

    response = requests.get(pdf_url)
    response.raise_for_status()

    all_text = ""
    with pdfplumber.open(BytesIO(response.content)) as pdf:
        for page in pdf.pages:
            all_text += page.extract_text() or ""

    print(all_text)
    return all_text.strip() if all_text else "No text found in the PDF."


@tool
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for a given query, retrieve the corresponding page's HTML content,
    clean it by removing unnecessary elements (such as styles, scripts, references, infoboxes, etc.),
    and return a simplified HTML string containing only the main content.

    Args:
        query (str): The search query for the Wikipedia page.

    Returns:
        str: Cleaned HTML string of the Wikipedia page's main content, or an empty string if not found.
    """

    page = wikipedia.page(query)
    print("..[wikipedia search] ", page.title)
    html = page.html()

    soup = BeautifulSoup(html, "html.parser")
    content_div = soup.find("div", class_="mw-parser-output")

    if not content_div:
        return ""

    to_decompose = []
    for tag in content_div.find_all():
        tag_classes = tag.get("class", [])
        if (
            tag.name in ["style", "script", "sup"]
            or any(cls in ["infobox", "navbox", "reference"] for cls in tag_classes)
        ):
            to_decompose.append(tag)

    for tag in to_decompose:
        tag.decompose()

    allowed_tags = {"ul", "li", "table", "tr", "td", "th"}
    to_unwrap = [tag for tag in content_div.find_all() if tag.name not in allowed_tags]

    for tag in to_unwrap:
        tag.unwrap()

    return str(content_div)


def _scrape(url: str) -> str:
    """Scrapes string and links from HTML page at the given URL, removing scripts and styles."""

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Failed to retrieve the page: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Extract only external links (absolute URLs with http/https)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http://") or href.startswith("https://"):
            link_text = a.get_text(strip=True)
            links.append(f"{link_text} ({href})" if link_text else href)

    links_str = "\n".join(links)
    return (
        f"URL: {url}"
        f"\n\nTEXT: {text}"
        f"\n\nLINKS:\n{links_str if links else 'No links found.'}"
    )


@tool
def search_and_scrape(query: str) -> str:
    """Search the web and scrape information from the top page."""

    print("..[search and scrape] ", query)

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=1)
        results = list(results)

    if not results:
        return "No search results found."

    url = results[0]["href"]
    print(".. scraping url: ", url)

    # Check if the URL points to a PDF file
    if url.lower().endswith(".pdf"):
        return f"Top result is a PDF file: {url}. Not scraping. Use a PDF tool instead."

    return _scrape(url)


@tool
def quick_web_search(query: str) -> str:
    """Search the internet and return summarised information or scraped text.
    Does not return HTML, page links or images, only text.

    Arguments:
        query: str - The search query to be executed.
    """
    print("..[quick web search] ", query)
    return DuckDuckGoSearchRun().run(query)


import subprocess


@tool
def execute_python_code(local_file_path: str):
    """This function executes Python code in the attachment and returns the output of the code.
    Only use this tool when you have a Python code file to execute and file extension is .py.
    Do not use this tool on images, audio files, or any other file types (eg. pdf, docx, etc.).

    Arguments:
        local_file_path: str - The file path to the Python code to be executed.
    """
    print("..[exec python] ", local_file_path)


    result = subprocess.run(["python", local_file_path], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else result.stderr



@tool
def download_file_from_url(url: str, filename: Optional[str] = None) -> str:
    """
    Download a file from a URL and save it to a temporary location.
    Do not download image files, use the vision_model tool instead.
    Do not download webpages, use the search_and_scrape tool instead.

    Args:
        url: The URL to download from
        filename: Optional filename, will generate one based on URL if not provided

    Returns:
        Path to the downloaded file
    """
    try:
        # Parse URL to get filename if not provided
        print("..[download file] ", url)
        if not filename:
            path = urlparse(url).path
            filename = os.path.basename(path)
            if not filename:
                filename = f"downloaded_{uuid.uuid4().hex[:8]}"

        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"File downloaded to {filepath}. You can now process this file."
    except Exception as e:
        return f"Error downloading file: {str(e)}"


@tool
def vision_model(image_url: str, question: str):
    """
    Use a Vision Model to answer a question about an image.

    Always use this tool to ask questions about a set of images you have been provided.
    This function uses an image-to-text AI model.
    Ensure your prompt is specific enough to retrieve the exact information you are looking for.

    The image_url must be a public URL that the model can access, not a local file path like /var/tmp/filename.jpg.
    This is because model used (azure gpt-4o) only supports public URLs for images, not local files.

    Args:
        image_url: The public URL of the image to analyze. Type: str
        question: The question to ask about the images.  Type: str
    """

    print("..[vision model] ", question, image_url)

    content = [
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": image_url, "detail": "auto"}}
    ]
    try:
        deployment = os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME")
        llm = AzureChatOpenAI(deployment_name=deployment, temperature=0)
        response = llm.invoke([HumanMessage(content=content)])
    except Exception as e:
        return f"Error processing image: {str(e)}"

    return response.content


@tool
def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribes an audio file.  Use when you need to process audio data.
    DO NOT use this tool for YouTube video; use the youtube_transcribe tool to process audio data from YouTube.
    Use this tool when you have an audio file in .mp3, .wav, .aac, .ogg, .flac, .m4a, .alac or .wma

    Args:
        audio_file_path: Filepath to the audio file (str)
    """
    model_size: str = "small"
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file_path)
    print(result["text"])
    return result["text"]



TOOLS = [
    quick_web_search,
    search_and_scrape,
    search_wikipedia,
    execute_python_code,
    download_file_from_url,
    vision_model,
    transcribe_audio,
    search_pdf
]
