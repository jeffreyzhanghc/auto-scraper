from trafilatura import fetch_url, extract,bare_extraction,metadata
from playwright.async_api import async_playwright
import re
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import json
import aiohttp
import ssl
import asyncio
import certifi
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
) 
import logging
from spacy.lang.en import English
import html_text


load_dotenv()
serperkey = os.getenv("serperkey")
api_key1 = os.getenv("openaikey1")
api_key = api_key1

async def simple_fetch_with_playwright(url,semaphore):
    async with async_playwright() as p,semaphore:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=30000)  # Timeout after 10 seconds
        except:
            await asyncio.sleep(10)
            try:
                await page.goto(url, timeout=30000)  # Timeout after 10 seconds
            except:
                print("Timeout while loading the page using playwright: "+url)
                return None

        # Add logic here to wait for the elements you need to ensure they are loaded
        content = await page.content()  # Gets the full page HTML
        # Process the content as needed
        await browser.close()
        r = html_text.extract_text(content,guess_layout=True)
        res = r.replace("\n", ".")
        return res
    
llogger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception))
async def call_chatgpt_async(session, text: list):
    prompt = f"""
            '''{text}'''
            These list of sentences is fetched from graduate program website of a university, given these sentences, identify the degree offered by this prorgam
            accurately. Return the results in a JSON format. Return the results in format where key is the program name and values are lists that contains 
            degree offered by the program described in webpage. 
            
            There is only ONE program described in the given text, so results are expect to have one key and one list value containing degrees you identified.And remember,
            the given text describes specific field of study.

            There are four cases you should consider:
            1) program names can be found and degrees offered can be found, then key is the program name and value is list of degrees;
            2) program names can be found but degrees cannot be identified, then key is the program name and value is list containing one element "graduate program";
            3) the given texts is not considered to be related to specific field of study, and program names cannot be determined, then key is "not program info" and value is None;
            4) When the given text is None, in this case, just do the same as case 3) return key is "not program info" and value is None;

            Strict follow the 4 scenarios above and DO NOT hallucinate or fabricate any program names and degrees information!!!

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
        return json.loads(response['choices'][0]['message']['content'])
    except:
        print("GPT program Summrization: Request failed.")


async def summarize(texts):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        #task1 = [tg.create_task(call_chatgpt_async(session, url[:idx])) for url in url_sets]
        idx = len(texts)//2
        task1 = [tg.create_task(call_chatgpt_async(session, text)) for text in texts[:idx]]
        task2 = [tg.create_task(call_chatgpt_async(session, text)) for text in texts[idx:]]
        response1 = await asyncio.gather(*task1)
        response2 = await asyncio.gather(*task2)
    return response1+response2

async def normal_compress(sentences,keywords):
    relevant_sentences = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]
    return relevant_sentences

async def get_sentences(text):
    nlp = English()
    nlp.add_pipe('sentencizer')
    try:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
    except:
        print("receiving none text at get_Sentences step")
        sentences = []
    return sentences

async def parse(urls):
    semaphore = asyncio.Semaphore(10)
    async with asyncio.TaskGroup() as tg:
        task1 = [tg.create_task(simple_fetch_with_playwright(url,semaphore)) for url in urls]
        response1 = await asyncio.gather(*task1)
        sentences = response1
        task2 = [tg.create_task(get_sentences(sentence)) for sentence in sentences]
        response2 = await asyncio.gather(*task2)
        return response2

async def get_names_and_degree(urls):
    #only work when batch=1
    texts = []
    block = await parse(urls)
    texts.append(block)
    degree = await summarize(texts[0])
    with open("nametodegree.json",'w') as f:
        json.dump(degree,f,indent=4)
    program_names = []
    for element in degree:
        for name,deg in element.items():
            if name == "not program info":continue
            for d in deg:
                #filter certificate
                if 'certificat' in d.lower() or 'exchange' in d.lower() or 'online' in d.lower() or 'distance' in d.lower(): continue
                program_names.append(d+" in "+name)
    program_names_no_dup = list(set(program_names))
    with open("../knowledge_files/program_name_list.json",'w') as f:
        json.dump(program_names_no_dup,f,indent=4)
    return program_names_no_dup








