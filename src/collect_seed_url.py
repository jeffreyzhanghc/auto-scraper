from googlesearch import search
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_log, 
    after_log
) 
import json
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
dict = {}
async def google_search(university,dict):
    query = f"{university} Graduate Admission Homepage"
    dict[university] = []
    for j in search(query,num_results=1):
        dict[university].append(j)
async def main():
    tasks = [google_search(university,dict) for university in universities[0]]
    results = await asyncio.gather(*tasks)
    return results

def main(path):
    for university in universities:
        query = f"{university} Graduate Admission Homepage"
        dict[university] =[]
        for j in search(query,num_results = 1):
            print(j)
            dict[university].append(j)
    with open(path, 'w', encoding='utf-8') as f:
            json.dump(dict, f, ensure_ascii=False, indent=4)

main("/Users/mac/Desktop/auto-scraper/knowledge_files/grad_school_url.json")
