from trafilatura import fetch_url, extract
from playwright.async_api import async_playwright
import re
import os
import openai
from openai import OpenAI
import time
from dotenv import load_dotenv, find_dotenv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import collections
import aiohttp
import ssl
import asyncio
import certifi
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_log, 
    after_log
) 
import logging
import spacy
from spacy.lang.en import English



load_dotenv()
api_key1 = os.getenv("openaikey1")
api_key = api_key1


async def simple_fetch(url):
    '''
    Simple fetch using trafilatura library to get the url
    '''
    try:
        downloaded = fetch_url(url)
        text = extract(downloaded,include_links= True)
        return text

    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None  # Return None or some error indicator
    
async def compress_metric(raw_metrics,program_name):
    name_to_keywords = {"Deadline":['deadline', 'application due', 'due', 'date',"submitted by"], \
                        "GRERequirement":['GRE',"Graduate Record Examination", "test scores"],\
                        "TOFELRequirement":['TOFEL',"IELTS","English Proficiency"],\
                        "prerequisiteCourse":['course requirement',"'course requirements","courses like","courses in"],\
                        "essay/thesisRequirement":["statement","statement of purpose","purpose","personal history statement","essay"],\
                        "applicationFee":['payment','$',"credit card","fee"],\
                        "recommendations":["recommendation","letters of recommendation"],}
    q = raw_metrics[program_name]
    metric_name = list(q.keys())
    
    link_name_map = {}
    for name in metric_name:
        q[name]['originalText'] = []
        q[name]['compressedText'] = []
        if q[name]['link'] not in link_name_map:
            link = q[name]['link']
            link_name_map[link] = []
            link_name_map[link].append(name)
        else:
            link_name_map[link].append(name)
    for link,names in link_name_map.items():
        if 'admission' in link:
            names = metric_name
        text = await simple_fetch(link)
        if text == None:
            print("Trafilatura failed to fetch context: "+link)
            for name in names:
                q[name]['originalText'].append(None)
                q[name]['compressedText'].append(None)

            continue
        for name in names:
            q[name]['originalText'].append(text)
        nlp = English()
        nlp.add_pipe('sentencizer')

        doc = nlp(text)

        sentences = [sent.text.strip() for sent in doc.sents]

        for name in names:
            keywords = []
            keywords = name_to_keywords[name]
            relevant_sentences = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]
            q[name]['compressedText'].append(relevant_sentences)
    return q

async def batch_compress(raw_metrics,program_names):
    task = [asyncio.create_task(compress_metric(raw_metrics,program_name)) for program_name in program_names]
    responses = await asyncio.gather(*task)
    return responses

print(asyncio.run(simple_fetch("https://orc.mit.edu/academics/phd-operations-research")))






    
    
