import json
import re
import subprocess
import concurrent.futures
from trafilatura import fetch_url, extract, metadata
from dotenv import load_dotenv, find_dotenv
#import newspaper
import asyncio
import time
import logging
from program_page_handler import get_program_branches
from asyncio import Semaphore
import datetime
import os
from collect_seed_url import collect_seed_url
from seed_url_detector import seed_url_detector
from program_url_detector import detect_prorgams
from gpt_program_content import get_prorgam_name
from google_search import get_program_info
from compress import batch_compress
import nltk
from gensim.models import KeyedVectors
from nltk.tokenize import sent_tokenize
import numpy as np
import gensim.downloader as api


seed_urls = os.getenv("seed_urls")
gpt_selected_seed_urls = os.getenv("gpt_selected_seed_urls")
program_urls = os.getenv("program_urls")
gpt_selected_program_urls = os.getenv("gpt_selected_program_urls")
final_output_path = os.getenv("final_output_path")
i = int(os.getenv('start_index'))
end = int(os.getenv('end_index'))
batch_size = int(os.getenv('batch_size'))
program_name_storage = os.getenv('program_name_storage')


async def simple_fetch(url):
    '''
    Simple fetch using trafilatura library to get the url
    '''
    try:

    
        downloaded = fetch_url(url)
        text = extract(downloaded,include_links= True)
        date = str(metadata.extract_metadata(downloaded).date)
        return (url,text,date)

    except Exception as e:
        return (url,None,None)  # Return None or some error indicator
    
async def main():
    await detect_prorgams(["MIT"],program_urls,gpt_selected_program_urls)
    program_branches,entry_pages = await asyncio.wait_for(get_program_branches(gpt_selected_program_urls),timeout=1000)
    #await asyncio.wait_for(get_prorgam_name(program_info,program_name_storage),timeout=1000)
    tasks = [simple_fetch(url) for url in program_branches[0]]
    program_info = await asyncio.wait_for(asyncio.gather(*tasks),timeout=1000)
    await asyncio.wait_for(get_prorgam_name(program_info,program_name_storage),timeout=1000)
asyncio.run(main())