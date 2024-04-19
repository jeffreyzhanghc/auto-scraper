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
from asyncio import Semaphore
import datetime
import os
from .gpt_program_content import get_prorgam_name
from .google_search import get_program_info
from .compress import batch_compress
from .get_degree import get_names_and_degree
import nltk
from gensim.models import KeyedVectors
from nltk.tokenize import sent_tokenize
import numpy as np
import gensim.downloader as api
load_dotenv()



async def get_metrics5(input_file):
    with open(input_file, 'r') as file:
        data = json.load(file)
    schools = list(data.keys())
    for sc in schools:
        names = data[sc]
        print("length of "+sc,len(names))
        metrics = await get_program_info(sc,names)   
        current_program_names = list(metrics.keys())
        processed_metrics = await asyncio.wait_for(batch_compress(metrics,current_program_names),timeout=6000)
        q = {}
        for k in range(len(current_program_names)):
            metrics[current_program_names[k]] = processed_metrics[k]
        q[sc] = metrics
        with open(f"../knowledge_files/{sc}-metrics5.json","w") as file:
            q = json.dump(q,file,indent=4)
        print("get metrics for "+sc)




