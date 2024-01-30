
from collect_seed_url import collect_seed_url
from seed_url_detector import seed_url_detector
from program_url_detector import detect_prorgams
from scrawl import scrawl
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

#load variables
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

seed_urls = os.getenv("seed_urls")
gpt_selected_seed_urls = os.getenv("gpt_selected_seed_urls")
program_urls = os.getenv("program_urls")
gpt_selected_program_urls = os.getenv("gpt_selected_program_urls")
final_output_path = os.getenv("final_output_path")
i = int(os.getenv('start_index'))
batch_size = int(os.getenv('batch_size'))
#call functions
collect_seed_url(seed_urls,universities)
seed_url_detector(seed_urls,gpt_selected_seed_urls)
detect_prorgams(universities,program_urls,gpt_selected_program_urls)
asyncio.run(scrawl(gpt_selected_seed_urls,program_urls,final_output_path,i,batch_size))


