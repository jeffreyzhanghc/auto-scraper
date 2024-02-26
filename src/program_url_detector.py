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
from googlesearch import search


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
            Given the json information containing the school name as the key and three urls as value, help me determine whcih url is the webpage that contains
            list of program of studies of that university.

            For example, for Cornell University the google search results are:
            "https://gradschool.cornell.edu/admissions/degrees-fields/cugradfos/",
            "https://gradschool.cornell.edu/admissions/degrees-fields/graduate-school-degrees/",
            "https://gradschool.cornell.edu/admissions/degrees-fields/"
            the desired outcome for this "https://gradschool.cornell.edu/admissions/degrees-fields/cugradfos/" because this page contains the full list of the programs

            
            Think deliberately and accurately return results in JSON format, which contains each university name as property and the corresponding chosen
            url for program entry page as the value. Use dictionary to store the properties, DO NOT use list bracket AT ALL.
            Example output:
            {{"Cornell University:"https://gradschool.cornell.edu/admissions/degrees-fields/cugradfos/",
            "Yale University:"https://gsas.yale.edu/programs-of-study"}}
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
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(call_chatgpt_async(session, url)) for url in url_sets]
        responses = await asyncio.gather(*tasks)
    return responses


def google_program_url(path,universities):
    dict = {}
    for university in universities:
        query = f"{university} Graduate Programs List"
        dict[university] =[]
        for j in search(query,num_results = 1):
            print("Collecting Program List page URL for" + str(university)+": "+str(j))
            dict[university].append(j)
    with open(path, 'w', encoding='utf-8') as f:
            json.dump(dict, f, ensure_ascii=False, indent=4)

async def detect_prorgams(universities,inpath,outpath):
    google_program_url(inpath,universities)
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

    







