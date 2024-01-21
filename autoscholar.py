from tqdm import tqdm
import random
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Lock
import pickle
import openai
import random

from asyncio import run_coroutine_threadsafe
import threading
from firebase_admin.firestore import Query
from firebase_admin import auth, messaging
from datetime import datetime, timedelta
from pdf2image import convert_from_path
import arxiv
import fitz
from tempfile import NamedTemporaryFile
import base64
import os
import json
from pathlib import Path
from urllib.parse import urlparse

import time
import requests
from firebase_admin import credentials, firestore, initialize_app
from google.cloud import storage
from quart import Quart, g, jsonify, request, Response, abort, stream_with_context
from quart_cors import cors
from azure.storage.blob import BlobServiceClient, BlobClient, BlobProperties, ContentSettings



import tempfile
import yaml
from openai import OpenAI
from quart import current_app
import re

from langchain.llms.anthropic import Anthropic
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
# from langchain.chat_models import ChatOpenAI
# from langchain.tools import YouTubeSearchTool
from langchain.utilities import BingSearchAPIWrapper
from langchain.agents import AgentType, initialize_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import spookyai

from langchain.tools.render import format_tool_to_openai_function
# from langchain_experimental.agents.agent_toolkits import create_python_agent
# from langchain_experimental.tools import PythonREPLTool
from langchain.tools import BaseTool, StructuredTool, Tool, tool

from langchain.chat_models import AzureChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


from dotenv import load_dotenv


load_dotenv()
 
with open("config/config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        
apiKey = config["apiKey"]
agentID = config["agentID"]
agentName = config["agentName"]
agentImage = config["agentImage"]
arxivQuery = config["arxivQuery"]

# # stuff for chat
azure_gpt35_model = AzureChatOpenAI(
    azure_endpoint="<YOUR_AZURE_ENDPOINT>",
    openai_api_version="2020-10-10",
    deployment_name="<YOUR_AZURE_DEPLOYMENT_NAME>",
    openai_api_key="<YOUR_OPENAI_API_KEY>",
    openai_api_type="azure",
)


# Replace with your Azure Storage account connection string
connection_string = "<YOUR_AZURE_STORAGE_CONNECTION_STRING>"

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Construct the default API client.
arxivClient = arxiv.Client()


try:
    spookyai.api_key = apiKey
    spookyai.agent_id = agentID
    spookyai.agent_name = agentName
    spookyai.agent_image = agentImage

    # Search for the most recent article matching the keyword "quantum."
    search = arxiv.Search(
        # query="ti:cognitive AND ti:architecture",
        query=arxivQuery,
        max_results=10,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    # Get the results
    results = list(arxivClient.results(search))

    # Check if there's at least one result
    if results:
        # Retrieve information about the first paper
        first_paper = results[2]
        print("Title:", first_paper.title)

        # Download pdf to a temporary file
        with NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            first_paper.download_pdf(dirpath=".", filename=pdf_file.name)
            print("PDF downloaded")

            # Open the downloaded PDF
            with fitz.open(pdf_file.name) as doc:
                page = doc.load_page(0)
                pix = page.get_pixmap()

                # Save the cropped image to a temporary file
                with NamedTemporaryFile(suffix=".png", delete=False) as img_file:
                    img_file_name = img_file.name
                    pix.save(img_file_name)

        # Get Azure Storage Blob credentials
        container_name = "research-papers"
        
        blob_name = first_paper.entry_id.split("/")[-1].replace(".", "_") + ".png"

        # Upload the image to Azure Storage Blob
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=blob_name
        )
        
        try:
            with open(img_file_name, "rb") as img_data:
                blob_client.upload_blob(img_data)
                
        except Exception as e:
            print(e)

        # Get the link to the uploaded image
        blob_url = blob_client.url
        print("Blob URL:", blob_url)

        try:
            answer = azure_gpt35_model.predict(
                "Read the following research paper and make think about its implications. Draft a twitter post about it. Start it with 'Researchers just...'\n\n\n Paper: "
                + first_paper.title + first_paper.summary)
            print(answer)

            # Notify human with the paper title and blob URL
            spookyai.notify_human(message=answer, metadata=blob_url + "\n" + first_paper.pdf_url)
            
        except Exception as e:
            print(e)
            spookyai.notify_human(message=first_paper.title, metadata=blob_url + "\n" + first_paper.pdf_url)
        
    else:
        print("No results found.")
except Exception as e:
    print(e)