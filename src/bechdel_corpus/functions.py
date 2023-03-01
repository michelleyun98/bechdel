#Import statements
import nltk
from nltk import pos_tag
from nltk import word_tokenize
from nltk import ne_chunk
from nltk.corpus import names
import urllib
import pathlib
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import json
import os
import urllib.request as request
from urllib.error import HTTPError
import chapterize

## Constants
DIRNAME = 'files'
QO = '“'
QC = '”'

## Scraping ##


def get_id_by_title(title):
    formatted_title = title.replace(" ", "+")
    url = f"https://www.gutenberg.org/ebooks/search/?query={formatted_title}&submit_search=Search"        
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    book_link = soup.find("li", { "class" : "booklink" })
    book_link = book_link.find('a', href=True)['href']
    book_id = book_link.split("/")[-1]
    return book_id

def get_text_by_id(book_id, filename):
    url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'
    out_file = filename
    count = 0
    while count <5:
        try:
            urllib.request.urlretrieve(url, out_file)
            break
        except HTTPError:
            print(f"ID#{book_id} did not work.\nTrying alternate URL")
            url = f'https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt'
            out_file = filename
            count +=1

def add_texts_from_file(filename):
    files = Path(dirname)
    files.mkdir(parents = True, exist_ok = True)
    
    with open(filename) as f:
        titles = f.read().splitlines()
    
    links_list = list()
    for title in titles:
        filename = dirname + '/' + title.replace(" ", "_") + ".txt"

        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            print(f"{title} file already exists")
        else:
            print(f"{title} file does not already exist. Getting from Project Gutenberg")        
            book_id = get_id_by_title(title)
            get_text_by_id(book_id, filename)
            print(f"{title} added successfully")
        time.sleep(1) #Sleep for one second, so that we don't slam the website.
        
def get_book_titles(filename):

    with open(filename) as f:
        titles = f.read().splitlines()
    return [title.replace(" ", "_") for title in titles]

## Annotation

def read_chapter(path, chapternumber):
    '''function that reads in a chapter at the specified path and returns a text variable corresponding to 
    the chapter'''
    #Create an empty string for the text
    text = ''
    #Open the chapter at the given path (since we are chapterizing from command line)
    with open(path + chapternumber + '.txt', 'rt') as file_in:
        #Add each line to the text string
        for line in file_in:
            #Skip illustrations
            if 'Illustration' not in line:
                text = text + line
    return text

def get_dialogues(chapter, open_quote, close_quote):
    '''function that processes the text file of a given chapter to return a list of all the dialogues in it'''
    #Initializing list for the dialogues

    dialogue_list = list()
    #Splitting the chapter text into paragraphs
    for para in chapter.split("\n\n"):
        #If an open and closed quote exist in a paragraph, append it to the dialogue list
        if open_quote and close_quote in para:
            dialogue_list.append(para)
    return dialogue_list

def get_proper_nouns(dialogue_list):
    '''function that returns all the proper noun labels in a dialogue list'''
    #List to keep a track of the current dialogue chain
    current_chain = list()
    #Initializing list of all noun labels
    all_nnps = list()

    for dialogue in dialogue_list:
        #Tokenizing and part of speech tagging the dialogue
        tagged_dialogue = pos_tag(word_tokenize(dialogue))
        for word, pos in tagged_dialogue:
            #If the word has a proper noun tag, append it to the current chain
            if pos == "NNP":
                current_chain.append(word)
            else:
                #For any other tag, check if the current chain is not empty
                if current_chain:
                    #Add the list of proper nouns to the final list
                    all_nnps.append(current_chain)
                    #Reinitialize current chain
                    current_chain = list()
    return all_nnps

def get_female_labels(all_nnps):
    '''function that returns all the female labels from a list of proper noun labels'''
    #Creating a list of all female names from the names corpus in nltk
    female_names = [name for name in names.words('female.txt')]
    #Creating a title list 
    female_titles = ['Mrs.', 'Ms.', 'Miss', 'Lady']
    #Initializing list of female labels
    female_nnps = list()
    for noun in all_nnps:
        #If the title exists in the noun labels, append it to the female labels list
        if any(title in noun for title in female_titles):
            female_nnps.append(noun)
        #Or if the name exists in the names corpus, append it to the female labels list
        elif any(name in female_names for name in noun):
            female_nnps.append(noun)
    return female_nnps