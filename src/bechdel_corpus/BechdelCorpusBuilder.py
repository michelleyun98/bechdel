# BUILDER
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
import re


FORMATTED_DIR = "data_formatted"
already_loaded_file = "books_processed.txt"

class BechdelCorpus:
    def __init__(self, books_filename, formatted_dir = FORMATTED_DIR):
        
        print("BEGIN BUILD\n")
        
        # INITIALIZE CLASS VARIABLES
        self.formatted_dir = formatted_dir
        self.current_id = 1000
        
        
        # CONVERT INPUT FILE TO LIST OF TITLE, AUTHOR TUPLES
        self.books_list = self.get_books_from_file(books_filename)
        
        # ADD BOOKS TO CORPUS (WILL NOT ADD BOOKS THAT ALREADY EXIST IN THE CORPUS)
        self.process_books_from_list(already_loaded_file)
        
        print("BUILD COMPLETE")

    def get_books_from_file(self, books_filename):
        with open(books_filename) as f:
            books = f.read().splitlines()
        
        books_list = list()
        for line in books:
            split_line = line.split("|")
            title = split_line[0]
            author = None            
            # IF AUTHOR SPECIFIED, ADD TO TUPLE
            if len(split_line) > 1:
                title = split_line[0].strip()
                author = split_line[-1].strip()        
           
            books_list.append((title, author))
        return books_list        
        
        
    def get_url_from_title(self, formatted_title):        
        url = f"https://standardebooks.org/ebooks?query={formatted_title}&sort=newest&view=grid&per-page=12" 
        soup = BeautifulSoup(urlopen(url), 'html.parser')   
        results = len(soup.find_all("div", { "class" : "thumbnail-container" }))
        if results != 1:
            print(f"{title} is ambiguous, please specify author")
            return
        book_link = soup.find("div", { "class" : "thumbnail-container" }) 
        book_link = book_link.find('a', href=True)['href']
        url = "https://standardebooks.org/" + book_link + "/text/single-page"    
        return url

    def get_url_from_title_and_author(self, formatted_title, formatted_author):    
        url = f"https://standardebooks.org//ebooks/{formatted_author}/{formatted_title}/text/single-page"    
        return url
      
    def process_books_from_list(self, already_loaded_file):
        for book in self.books_list:
            formatted_title = book[0].lower().replace(" ", "-")
            formatted_author = ""
            if book[1] != None:
                formatted_author = book[1].lower().replace(" ", "-")
                book_id = formatted_title + "_" + formatted_author
            else:
                book_id = formatted_title
            # CHECK IF THE FILE IS ALREADY LOADED
            with open(already_loaded_file) as f:
                already_loaded_books = f.read().splitlines()
            if book_id in already_loaded_books:
                print(f"{book_id} folder already exists.\n")
            else:       
                print(f"Adding {book[0]} to corpus")

                if formatted_author == "": # If author is not specified
                    url = self.get_url_from_title(formatted_title)          
                else: # Author is specified
                    url = self.get_url_from_title_and_author(formatted_title, formatted_author)
                author = url.split("/")[5].replace("-", " ").title()
                title = book[0]
                self.create_annotated_chapters_from_url(url, book_id, title, author)
                # ADD TO LIST OF ADDED BOOKS
                with open(already_loaded_file, "a") as f:
                    f.write(f"{book_id}\n")

                print(f"\t{book[0]} successfully added to corpus\n\n")
                time.sleep(1)
            
    def create_annotated_chapters_from_url(self, url, book_id, title, author):
        soup = BeautifulSoup(urlopen(url), 'html.parser')    
        chapters = soup.findAll("section", { "epub:type" : "chapter bodymatter z3998:fiction" })
        if len(chapters) == 0:
            chapters = soup.findAll("section", { "epub:type" : "chapter" })
        
        # FORMAT AND ANNOTATE CHAPTERS
        for chapter in chapters:
            chapter_number = chapter.get('id').split("-")[-1]
            chapter_text = chapter.getText()  
            chapter_id = book_id + "_" + chapter_number
            dialogue_list = self.get_dialogues(chapter_text)
            inner_text, outer_text = self.get_inner_outer_text(dialogue_list)
            male_mentions = self.get_dialogue_counts(inner_text, "male")
            male_speakers = self.get_dialogue_counts(outer_text, "male")
            female_speakers = self.get_dialogue_counts(outer_text, "female")
            passes_bechdel = False
            if male_mentions == 0 and male_speakers==0 and female_speakers>=2:
                passes_bechdel = True
                print(chapter_id)
            with open(FORMATTED_DIR + "/" + chapter_id + ".txt", "w+") as f:
                f.write(f"<bechdel>{passes_bechdel}</bechdel>/n<id>{chapter_id}</id>\n<title>{title}</title>\n<author>{author}</author>\n<text>{chapter_text}</text><male_mentions>{male_mentions}</male_mentions>\n<male_speakers>{male_speakers}</male_speakers>\n<female_speakers>{female_speakers}</female_speakers>\n\n")
        
    def get_dialogues(self, chapter, open_quote = '“', close_quote = '”'):
        '''function that processes the text file of a given chapter to return a list of all the dialogues in it'''
        #Initializing list for the dialogues
        dialogue_list = list()
        #Splitting the chapter text into paragraphs
        for para in chapter.split("\n\n"):
            #If an open and closed quote exist in a paragraph, append it to the dialogue list
            if open_quote and close_quote in para:
                dialogue_list.append(para)
        return dialogue_list
    
    def get_inner_outer_text(self, dialogue_list):
        '''function that returns the text inside and outside a dialogue for a given list of dialogues'''
        inner_text = list()
        outer_text = list()

        for dialogue in dialogue_list:
            dialogue = " ".join(word_tokenize(dialogue))
            quoted = re.compile('“[^”]*”')
            unquoted = re.compile('”.*[“.]')
            for value in quoted.findall(dialogue):
                inner_text.append(value)
            for value in unquoted.findall(dialogue):
                outer_text.append(value)

        return inner_text, outer_text

    
    def get_proper_nouns(self, text):
        '''function that returns all the proper noun and pronoun labels in a dialogue list'''
        #List to keep a track of the current dialogue chain
        current_chain = list()
        #Initializing list of all proper noun labels
        all_nps = list()

        for dialogue in text:
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
                        all_nps.append(current_chain)
                        #Reinitialize current chain
                        current_chain = list()
        return all_nps
    
    def get_gendered_labels(self, all_nps, gender):
        '''function that returns all the gendered labels from a list of proper noun and pronoun labels'''
        #If entered gender is female, use female names, titles
        if gender == "female":
            gn_names = [name for name in names.words('female.txt')]
            titles = ['Mrs.', 'Ms.', 'Miss', 'Lady']

        #If entered gender is male, use male names, titles 
        if gender == "male":
            gn_names = [name for name in names.words('male.txt')]
            titles = ['Mr.', 'Sir']

        #List of all gendered labels
        gender_nps = list() 
        for noun in all_nps:
            if any(title in noun for title in titles):
                gender_nps.append(noun)
            elif any(name in gn_names for name in noun):
                gender_nps.append(noun)
        return gender_nps
    
    def get_dialogue_counts(self, text, gender):
        '''function that returns the count of gendered label in the text'''
        #Get all nouns and pronouns in given text
        all_nps = self.get_proper_nouns(text)
        #Get all gendered nouns and pronouns in given text
        gendered_nps = self.get_gendered_labels(all_nps, gender)
        #Get the count and return it
        count = len(gendered_nps)
        return count
    

