import json
from trafilatura import fetch_url, extract, metadata
from dotenv import load_dotenv, find_dotenv
#import newspaper
import asyncio
import logging
from program_page_handler import get_program_branches
from asyncio import Semaphore
import os
from program_url_detector import detect_prorgams
from program_page_handler import get_program_branches
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
from get_degree import get_names_and_degree





seed_urls = os.getenv("seed_urls")
gpt_selected_seed_urls = os.getenv("gpt_selected_seed_urls")
program_urls = os.getenv("program_urls")
gpt_selected_program_urls = os.getenv("gpt_selected_program_urls")
final_output_path = os.getenv("final_output_path")
i = int(os.getenv('start_index'))
end = int(os.getenv('end_index'))
batch_size = int(os.getenv('batch_size'))
program_name_storage = os.getenv('program_name_storage')


load_dotenv()
api_key1 = os.getenv("openaikey1")
api_key = api_key1

logger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception),
       before=before_log(logger, logging.DEBUG), 
       after=after_log(logger, logging.DEBUG))
async def call_chatgpt_async(session, links: list):
    '''
    This function calls gpt to select program related urls
    '''
    prompt = f"""
            '''{links}'''
            Given the list of url strings, select the url strings that you think are related to a specific master study program. Such strings should indicate
            a specific field of study or academic majors. Notice that sometimes major names are in abbreviation,remember to take the abbreviation into consideration.

            I will give you some examples:
            You should select these kind of urls:
            1) given url "https://graduateprograms.brown.edu/graduate-program/computational-biology-phd", you should include this url because you can tell from the
            string that this url is related to computational-biology;
            2) given "https://graduateprograms.brown.edu/graduate-program/political-science-phd", select it because it indicates field of study in political science;
            3) given "https://graduateprograms.brown.edu/graduate-program/music-and-multimedia-composition-phd", select it becuase it indicates major in music and multimedia composition;
            4) given 'https://grad.ucla.edu/programs/david-geffen-school-of-medicine/human-genetics-department/' select it because although it is a deparment level information, it relates to the 
               human genetic fields of study. 
            
            You should not choose following kind of urls:
            1) given url "https://graduateprograms.brown.edu/home", you should not select this one because no specific majors/field of study is indicated by this url;
            2) given "https://graduateprograms.brown.edu/home", do not select it because there is no major-specific information in the string;

            Follow the examples when make the decision, the key is to find whether you can tell a field of study or abbreviation of it in the url. If yes, include it
            even it is a department level urls.
            Return the selected urls in a JSON output, with PROPERTY named 'selected' and the list of selected urls as
            value. Try to make the decision fast and accurate, and I want the results to be comprehensive.
            """
    payload = {
        'model': "gpt-4-0125-preview",
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
        return json.loads(response['choices'][0]['message']['content'])['selected']
    except:
        print("Request failed.")


async def call_chatgpt_bulk(url_sets):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        idx = len(url_sets[0])//4
        task1 = [tg.create_task(call_chatgpt_async(session, url[:idx])) for url in url_sets]
        task2 = [tg.create_task(call_chatgpt_async(session, url[idx:2*idx])) for url in url_sets]
        task3 = [tg.create_task(call_chatgpt_async(session, url[2*idx:3*idx])) for url in url_sets]
        task4 = [tg.create_task(call_chatgpt_async(session, url[3*idx:])) for url in url_sets]
        response1 = await asyncio.gather(*task1)
        response2 = await asyncio.gather(*task2)
        response3 = await asyncio.gather(*task3)
        response4 = await asyncio.gather(*task4)
        response = response1[0]+response2[0]+response3[0]+response4[0]
    return response



async def fetch_all_links(page):
    '''
    This function fecthes all the links on the input webpage
    '''
    await page.wait_for_load_state('networkidle')
    links = await page.evaluate('''() => {
        // Select all anchor tags in the body
        const anchorElements = document.body.querySelectorAll('a');
        // Map each anchor element to its href attribute
        const allLinks = Array.from(anchorElements).map(a => a.href);
        // Return the array of links
        return allLinks;
    }''')
    return links

async def fetch_with_playwright(url):
    '''
    This function use playwright to open the webpage and extract the link on the pages
    '''
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            links = await fetch_all_links(page)
            await browser.close()
            return links
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None  # Return None or some error indicator assert the error


async def get_urls(url):
    '''
    By using GPT, the function fecthes the program list url webpage and filter out the program related urls
    '''
    links = await fetch_with_playwright(url)
    gpt_links = await call_chatgpt_bulk([links])
    return gpt_links

    
async def main():
    res = {}
    with open("names.json","w") as file:
        json.dump(res,file)
    with open("0330 program list.json", 'r') as file:
        data = json.load(file)
    for sc in data.keys():
        print(sc)
        res[sc] = {}
        entry_links = data[sc]
        for l in entry_links:
            q = await get_urls(l)
            d = await get_names_and_degree(q)
            res[sc][l] = d
            with open("names.json","w") as file:
                json.dump(res,file,indent=4)
asyncio.run(main())