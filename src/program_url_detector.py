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

universities = [
    "Massachusetts Institute of Technology (MIT)",
    "Stanford University",
    "Harvard University",
    "California Institute of Technology (Caltech)",
    "University of Chicago",
    "Princeton University",
    "Cornell University",
    "Yale University",
    "Columbia University",
    "University of Pennsylvania",
    "University of Michigan",
    "Johns Hopkins University",
    "Northwestern University",
    "University of California, Berkeley",
    "University of California, Los Angeles (UCLA)",
    "Duke University",
    "University of California, San Diego",
    "Brown University",
    "University of Wisconsin-Madison",
    "New York University (NYU)",
    "University of Texas at Austin",
    "Carnegie Mellon University",
    "University of Washington",
    "University of Illinois at Urbana-Champaign",
    "University of California, San Francisco",
    "University of Southern California",
    "Purdue University",
    "University of Maryland, College Park",
    "University of Minnesota",
    "University of North Carolina, Chapel Hill",
    "Boston University",
    "Pennsylvania State University",
    "Ohio State University",
    "University of California, Davis",
    "University of California, Santa Barbara",
    "University of California, Irvine",
    "University of Florida",
    "Rice University",
    "Michigan State University",
    "Indiana University Bloomington",
    "University of Virginia",
    "University of Colorado Boulder",
    "Rutgers University-New Brunswick",
    "Texas A&M University",
    "Georgia Institute of Technology",
    "University of Pittsburgh",
    "Washington University in St. Louis",
    "University of Rochester",
    "Vanderbilt University",
    "University of Notre Dame",
    "University of Miami",
    "University of Arizona",
    "University of Massachusetts Amherst",
    "University of Connecticut",
    "Dartmouth College",
    "Emory University",
    "University of Georgia",
    "University of California, Riverside",
    "University of Iowa",
    "Virginia Tech",
    "Georgetown University",
    "University of Colorado, Denver",
    "University of Illinois, Chicago",
    "University of Oregon",
    "Case Western Reserve University",
    "University of Tennessee, Knoxville",
    "University of Hawaii at Manoa",
    "University of Kansas",
"University of Utah",
"Tulane University",
"George Washington University",
"University of South Florida",
"University at Buffalo SUNY",
"University of Nebraska-Lincoln",
"University of Cincinnati",
"University of Delaware",
"University of Texas Dallas",
"University of South Carolina",
"University of Kentucky",
"University of Alabama",
"University of Missouri",
"University of Oklahoma",
"University of New Mexico",
"Oregon State University",
"University of Louisville",
"University of North Texas",
"Temple University",
"University of Arkansas",
"University of Mississippi",
"University of Nevada, Las Vegas",
"University of Vermont",
"University of Rhode Island",
"University of Idaho",
"University of North Carolina, Charlotte",
"University of North Carolina, Greensboro",
"University of Central Florida",
"Florida State University",
"Florida International University",
"San Diego State University",
"Colorado State University",
"Washington State University",
"Utah State University",
"New Mexico State University",
"Montana State University"
]

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
            likely the url entry for entering this schools' graduate program list. Think deliberately and accurately return results in JSON format, keep the 
            university name as the key and choose only ONE url for each university as the most proper entry point for finding school's graduate program lists

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

def google_program_url(path):
    dict = {}
    for university in universities:
        query = f"{university} Master Programs List"
        dict[university] =[]
        for j in search(query,num_results = 1):
            print(j)
            dict[university].append(j)
    with open(path, 'w', encoding='utf-8') as f:
            json.dump(dict, f, ensure_ascii=False, indent=4)

def _main_(inpath = "/Users/mac/Desktop/auto-scraper/knowledge_files/grad_school_programs_url.json",outpath = "/Users/mac/Desktop/auto-scraper/knowledge_files/gpt_selected_programs_url.json"):
    google_program_url("/Users/mac/Desktop/auto-scraper/knowledge_files/grad_school_programs_url.json")
    with open(inpath, 'r') as file:
        data = json.load(file)
    json_results = []
    keys = list(data.keys())
    schools = [{key:data[key]} for key in keys]
    results = asyncio.run(call_chatgpt_bulk(schools))
    for res in results:
        json_results.append(json.loads(res))
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, ensure_ascii=False, indent=4)

    



#------- Run this function to run the script ---------
_main_()





