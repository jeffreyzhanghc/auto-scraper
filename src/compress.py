from trafilatura import fetch_url, extract,bare_extraction,metadata
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
import html_text
import nltk
from gensim.models import KeyedVectors
from nltk.tokenize import sent_tokenize
import numpy as np
import gensim.downloader as api



load_dotenv()
api_key1 = os.getenv("openaikey1")
api_key = api_key1

#nltk.download('punkt')
#model = api.load('word2vec-google-news-300')
model_path = "word2vec-google-news-300.bin"
#model.save_word2vec_format(model_path, binary=True)

model = KeyedVectors.load_word2vec_format(model_path, binary=True)


# Function to vectorize a sentence based on the word vectors
def sentence_vector(sentence,model):
    words = nltk.word_tokenize(sentence)
    word_vectors = [model[word] for word in words if word in model]
    return np.mean(word_vectors, axis=0) if word_vectors else np.zeros(model.vector_size)

# Compute cosine similarity between keyword vectors and each sentence vector
def cosine_similarity(v1, v2):
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 > 0 and norm2 > 0:
        return np.dot(v1, v2) / (norm1 * norm2)
    else:
        return 0
    
async def normal_compress(sentences,keywords):
    relevant_sentences = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]
    return relevant_sentences
        


async def special_compress(sentences,keywords,threshold,model=model):
    # Vectorize keywords and sentences
    keyword_vectors = np.mean([sentence_vector(keyword,model) for keyword in keywords], axis=0)
    sentence_vectors = np.array([sentence_vector(sentence,model) for sentence in sentences])

    # Apply a threshold to determine if a sentence is related to the keywords
    related_sentences = []

    for sentence, vector in zip(sentences, sentence_vectors):
        sim = cosine_similarity(keyword_vectors, vector)
        if sim > threshold:
            related_sentences.append(sentence)
    return related_sentences


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
    
async def simple_fetch_with_playwright(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=10000)  # Timeout after 10 seconds
        except:
            print("Error: Timeout while loading the page using playwright: "+url)
            return await simple_fetch(url)
        # Add logic here to wait for the elements you need to ensure they are loaded
        content = await page.content()  # Gets the full page HTML
        # Process the content as needed
        await browser.close()
        r = html_text.extract_text(content,guess_layout=True)
        res = r.replace("\n", ".")
        return res

    
async def compress_metric(raw_metrics,program_name):
    
    name_to_keywords = {"Deadline":['deadline', 'application due','application deadline', 'due', 'date',"submit material","material submitted"], \
                        "GRERequirement":['GRE',"Graduate Record Examination","Graduate Record Examination", "test scores","GMAT"],\
                        "TOEFLRequirement":['toefl',"ielts","english proficiency"],\
                        "prerequisiteCourse":['course requirement',"introductory coursework","academic preparation","coursework preparation","following areas"],\
                        "recommendations":["recommendation","letters of recommendation"],}
    q = raw_metrics[program_name]
    metric_name = list(q.keys())
    
    link_name_map = {}
    for name in metric_name:
        q[name]['originalText'] = []
        q[name]['compressedText'] = []
        link = q[name]['link']
        if link not in link_name_map:
            link_name_map[link] = []
            link_name_map[link].append(name)
            continue
        else:
            link_name_map[link].append(name)
    for link,names in link_name_map.items():
        text = await  simple_fetch_with_playwright(link)
        if text == None:
            print("Fetched None context: "+link)
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
                keywords = name_to_keywords[name]        
                if name == "prerequisiteCourse":
                    relevant_sentences = await special_compress(sentences,keywords,0.63,model)
                elif name == "GRERequirement":
                    relevant_sentences = [sentence for sentence in sentences if any(keyword in sentence for keyword in keywords)]
                else:
                    relevant_sentences = await normal_compress(sentences,keywords)
                q[name]['compressedText'].append(relevant_sentences)
        



    return q

async def batch_compress(raw_metrics,program_names):
    task = [asyncio.create_task(compress_metric(raw_metrics,program_name)) for program_name in program_names]
    responses = await asyncio.gather(*task)
    return responses













    
    
