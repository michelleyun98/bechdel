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
import re
import csv


FORMATTED_DIR = "data_formatted"
already_loaded_file = "books_processed.txt"
corpus_csv_fn = "corpus.csv"

class BechdelCorpus:
    def __init__(self, books_filename, home_dir, formatted_dir = FORMATTED_DIR):
        
        print("BEGIN BUILD\n")
        
        # INITIALIZE CLASS VARIABLES
        self.formatted_dir = formatted_dir
        self.current_id = 1000    
        
        
        # CONVERT INPUT FILE TO LIST OF TITLE, AUTHOR TUPLES
        self.books_list = self.get_books_from_file(books_filename)
        
        # ADD BOOKS TO CORPUS (WILL NOT ADD BOOKS THAT ALREADY EXIST IN THE CORPUS)
        self.process_books_from_list(already_loaded_file)
        
        print("BUILD COMPLETE")
        
        print("WRITING TO FILE")
        self.write_corpus()
        
        print("To access corpus contents, use BechdelCorpusObject.read_corpus()")
        

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
            # self.get_proper_nouns(dialogue_list)

            inner_characters = self.get_characters_in_text(title.lower().replace(" ", "-"), inner_text)
            outer_characters = self.get_characters_in_text(title.lower().replace(" ", "-"), outer_text)
            
            male_mentions = {x for x in inner_characters if x[1] == "Male"}
            male_speakers = {x for x in outer_characters if x[1] == "Male"}
            female_mentions = {x for x in inner_characters if x[1] == "Female"}
            female_speakers = {x for x in outer_characters if x[1] == "Female"}
            
            passes_bechdel = False
            if len(male_mentions) == 0 and len(male_speakers)==0 and len(female_speakers)>=2:
                passes_bechdel = True
                print("\n", chapter_id)
                print(inner_characters, outer_characters)
            with open(FORMATTED_DIR + "/" + chapter_id + ".txt", "w+") as f:
                f.write(f"<bechdel>{passes_bechdel}</bechdel>\n<id>{chapter_id}</id>\n<title>{title}</title>\n<author>{author}</author>\n<text>{chapter_text}</text><male_mentions>{male_mentions}</male_mentions>\n<male_speakers>{male_speakers}</male_speakers>\n<female_speakers>{female_speakers}</female_speakers>\n\n")
        
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
        '''function that returns all the proper noun and pronoun labels in list of texts'''
        #List to keep a track of the current dialogue chain
        current_chain = list()
        #Initializing list of all proper noun labels
        all_nps = list()
        all_pronouns = list()

        for dialogue in text:
            #Tokenizing and part of speech tagging the dialogue
            tagged_dialogue = pos_tag(word_tokenize(dialogue.replace("-", ".")))
            for word, pos in tagged_dialogue:
                # If the word has a proper noun tag, append it to the current chain
                if pos == "NNP":
                    current_chain.append(word)
                else:
                    # For any other tag, check if the current chain is not empty
                    if current_chain:
                        for i in range(len(current_chain)):
                            if "\u2060" in current_chain[i]:
                                current_chain[i] = current_chain[i].replace("\u2060", " ")
                        #Add the list of proper nouns to the final list
                        all_nps.append(current_chain)
                        #Reinitialize current chain
                        current_chain = list()
                    if pos == "PRP":
                        all_pronouns.append((word, all_nps))
                        
        with open(f"/Users/jata/Documents/Bookdel/bechdel/src/bechdel_corpus/characterList.txt", 'a') as f:
            for np in all_nps:

                f.write(' '.join(np) + "\n")
        return all_nps, all_pronouns
        
    def handle_unknown(self, text, unknown_np):
        current_chain = list()
        female_titles = {'Miss', 'Lady', 'lady', 'sister', 'aunt'}
        male_specifications = {'uncle'}
        gender = "Male"
        for dialogue in text:
            tagged_dialogue = pos_tag(word_tokenize(dialogue.replace("-", ".")))
            for i, (word, pos) in enumerate(tagged_dialogue):            
                if pos == "NNP":
                    current_chain.append(word)
                else:
                    if current_chain:
                        if current_chain == unknown_np:
                            # print("YA", unknown_np, tagged_dialogue[i-5:i])
                            if len(male_specifications & set(x[0] for x in tagged_dialogue[i-5:i]))==0:
                                
                                if len(female_titles & set(x[0] for x in tagged_dialogue[i-3:i]))>0:
                                    gender = "Female"
                            # print(gender)
                        current_chain = list()
                        
        return gender
    
    def handle_pronouns(self, gender, all_nps, characters_dict):
        
        ret_val = None
        if gender == "Male":
            ret_val = ("Ambiguous Male", "Male")
        elif gender == "Female":
            ret_val = ("Ambiguous Female", "Female")
        for current_np in all_nps[::-1]:
            
            if ' '.join(current_np) in characters_dict:
                if characters_dict[' '.join(current_np)][1] == gender:
                    ret_val = tuple(characters_dict[' '.join(current_np)])
                    break
        # print(ret_val)
        return ret_val
    
    def get_characters_in_text(self, title, text):
        characters_dict = dict()
        female_pronouns = ['she', 'She']
        male_pronouns = ['he', 'He']
        with open(f"characters/{title}-characters.txt") as f:
            characters_dict = json.load(f)
        all_nps, all_pronouns = self.get_proper_nouns(text)
        ret_set = set()
        for np in all_nps:           
            if ' '.join(np) in characters_dict:
                if characters_dict[' '.join(np)][1] == "Unknown":
                    characters_dict[' '.join(np)][1] = self.handle_unknown(text, np)

                ret_set.add(tuple(characters_dict[' '.join(np)]))
        for pp in all_pronouns:
            if pp[0] in female_pronouns:
                # print(pp[0])
                ret_set.add(self.handle_pronouns("Female", pp[1], characters_dict))
            elif pp[0] in male_pronouns:
                # print(pp[0])
                ret_set.add(self.handle_pronouns("Male", pp[1], characters_dict))
        return ret_set
        
      
    def get_rows_cols(self, regs, text, column_names):
    
        def rehelp(pattern, text, column_names):

            cols, rows = [], []
            for match in pattern.finditer(text):

                if match.group(1) in column_names:

                    cols.append(match.group(1))
                    rows.append(match.group(2))

            return cols, rows

        cols, rows = [], []
        for pattern in regs:
            col, row = rehelp(pattern, text, column_names)
            cols.extend(col)
            rows.extend(row)

        return zip(cols, rows)
      
    def write_corpus(self):    
    

        def_pattern = re.compile(r"<(.*)>(.*)<\/.*>")
        male_pattern = re.compile(r"<\/text><(.*)>([0-9])")
        text_pattern = re.compile(r"<(text)>\n*((\n.*)+)\n+<\/text>")

        regs = [text_pattern, def_pattern, male_pattern]

        column_names = ["title", "male_mentions", "author", "text",
                        "male_speakers", "female_speakers", "bechdel","id"]
        text_list = os.listdir(self.formatted_dir)

        with open(corpus_csv_fn, 'w', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=column_names)
            writer.writeheader()
        #Text_list is like the list of all the text files
            for text in text_list:
                if text.endswith('.txt'):
                    with open(self.formatted_dir + "/" + text) as d:
                        text = d.read()
                        row = {col:row for col, row in self.get_rows_cols(regs, text,column_names)}
                        writer.writerow(row)
                        d.close()
            outfile.close()
            
    def read_corpus(self, fields):
          
        with open(corpus_csv_fn, newline = '') as corp:
            reader = csv.DictReader(corp)
            
            for row in corp:
              yield line


