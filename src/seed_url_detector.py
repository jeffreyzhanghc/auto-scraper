import sys
#must be python 3.11 or above to use some of the library
print(sys.version)

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


load_dotenv()
api_key1 = os.getenv("openaikey1")
api_key = api_key1

logger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception),
       before=before_log(logger, logging.DEBUG), 
       after=after_log(logger, logging.DEBUG))
async def call_chatgpt_async(session, urls: str):
    prompt = f"""
            '''{urls}'''
            given the json information containing the school name as the key and three url as value, determine which url you think is most 
            likely the url entry for entering this schools' graduate admission homepage. By homepage I mean the seed url that I can start from 
            it to scrape the admission information following the seed url. Think deliberately and accurately return results in JSON format, keep the 
            university name as the key and choose only ONE url for each university as its graduate admission homepage 

            """
    payload = {
        'model': "gpt-4-1106-preview",
        'messages': [
            {"role": "user", "content": prompt}
        ],
        'response_format':{ "type": "json_object" }
    }
    try:
        async with session.post(
            url='https://api.openai.com/v1/chat/completions',
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            json=payload,
            ssl=ssl.create_default_context(cafile=certifi.where())
        ) as response:
            response = await response.json()
        if "error" in response:
            print(f"OpenAI request failed with error {response['error']}")
        return response['choices'][0]['message']['content']
    except:
        print("Request failed.")


async def call_chatgpt_bulk(url_sets):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(call_chatgpt_async(session, url)) for url in url_sets]
        responses = await asyncio.gather(*tasks)
    return responses



async def seed_url_detector(inpath,outpath):

    with open(inpath, 'r') as file:
        data = json.load(file)
    json_results = []
    keys = list(data.keys())
    schools = [{key:data[key]} for key in keys]
    results = await call_chatgpt_bulk(schools)
    for res in results:
        json_results.append(json.loads(res))
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, ensure_ascii=False, indent=4)

    




