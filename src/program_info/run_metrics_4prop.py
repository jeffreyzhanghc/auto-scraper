import json
import re
import subprocess
import concurrent.futures
from trafilatura import fetch_url, extract, metadata
from dotenv import load_dotenv, find_dotenv
#import newspaper
import asyncio
from asyncio import Semaphore
import os
#import modules
from .google2 import get_program_info
from .originalText import batch_compress
#import pacakge for downloading models
import nltk
from gensim.models import KeyedVectors
from nltk.tokenize import sent_tokenize
import numpy as np
import gensim.downloader as api
load_dotenv()

seed_urls = os.getenv("seed_urls")
gpt_selected_seed_urls = os.getenv("gpt_selected_seed_urls")
program_urls = os.getenv("program_urls")
gpt_selected_program_urls = os.getenv("gpt_selected_program_urls")
final_output_path = os.getenv("final_output_path")
i = int(os.getenv('start_index'))
end = int(os.getenv('end_index'))
batch_size = int(os.getenv('batch_size'))
program_name_storage = os.getenv('program_name_storage')


async def get_metrics4(input_file):
    with open(input_file, 'r') as file:
        data = json.load(file)
    schools = list(data.keys())
    for sc in schools:
        #print(sc)
        names = data[sc]
        metrics = await get_program_info(sc,names)    
        current_program_names = list(metrics.keys())
        processed_metrics = await asyncio.wait_for(batch_compress(metrics,current_program_names),timeout=6000)
        q = {}
        for k in range(len(current_program_names)):
            metrics[current_program_names[k]] = processed_metrics[k]
        q[sc] = metrics
        #print(len(list(metrics.keys())))
        with open(f"../knowledge_files/{sc}-metrics4.json","w") as file:
            q = json.dump(q,file,indent=4)
        print("get metrics for "+sc)





