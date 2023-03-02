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

RAW_DIR = "/Users/jata/Documents/bechdel/bechdel/src/bechdel_corpus/data_raw"
FORMATTED_DIR = "/Users/jata/Documents/bechdel/bechdel/src/bechdel_corpus/data_formatted"

class BechdelCorpus:
    def __init__(self, titles='titles.txt',
                 raw_dir = RAW_DIR,
                 formatted_dir = FORMATTED_DIR):
        print("BEGIN INIT")
        # When we initialize the corpus
        self.raw_dir = raw_dir
        self.formatted_dir = formatted_dir
        self.current_id = 1000
        # print_me()
        # 1. load titles from txt file
        self.titles = self.get_book_titles(titles)

        # 2. Get texts of each of those titles
        self.add_texts_from_file(self.titles)
        
        # 3.1 Chapterize those texts +
        # 3.2 tag chapters into formatted txt files
        self.chapterize_by_directory() 
        
        # 4.1 Annotation
        # 4.2 Formatting
        print("FINISHED INIT")
    
    def get_id_by_title(self, title):
        '''
        Gets Gutenberg ID by title.
        Takes the first result, assuming it is the most relevant/popular.
        '''
        formatted_title = title.replace(" ", "+")
        url = f"https://www.gutenberg.org/ebooks/search/?query={formatted_title}&submit_search=Search"        
        soup = BeautifulSoup(urlopen(url), 'html.parser')
        book_link = soup.find("li", { "class" : "booklink" })
        book_link = book_link.find('a', href=True)['href']
        book_id = book_link.split("/")[-1]
        return book_id

    def get_text_by_id(self, book_id, filename):
        '''
        Gets text from Gutenberg site by ebook id
        (If the first ID does not work, tries alterate ID)
        '''
        url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'
        out_file = filename
        count = 0
        while count <5:
            try:
                urllib.request.urlretrieve(url, out_file)
                break
            except HTTPError:
                print(f"\tID#{book_id} did not work.\nTrying alternate URL")
                url = f'https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt'
                out_file = filename
                count +=1


    def add_texts_from_file(self, titles):
        '''
        Gets list of titles from text file, downloads their content as text
        (Does not download files we already have)
        '''  
        links_list = list()
        for title in titles:
            filename = 'data_raw/' + title.replace(" ", "_") + ".txt"

            if os.path.isfile(filename) and os.stat(filename).st_size != 0:
                print(f"{title} file already exists\n")
            else:
                print(f"{title} file does not already exist. Getting from Project Gutenberg")        
                book_id = get_id_by_title(title)
                get_text_by_id(book_id, filename)
                print(f"\t{title} added successfully\n")
                time.sleep(1) #Sleep for one second, so that we don't slam the website.

    def get_book_titles(self, filename):
        with open(filename) as f:
            titles = f.read().splitlines()
        return [title.replace(" ", "_") for title in titles]

    ## Annotation

    def chapterize_by_directory(self): 
        for file in os.listdir(self.raw_dir):
            if file.endswith('txt'):
                chapterized_folder = file.split(".")[0] + "-chapters"

                x = os.path.join(self.raw_dir, chapterized_folder)
                if os.path.isdir(x):
                    print(f"{chapterized_folder} folder already exists\n")
                else:
                    print(f"{chapterized_folder} folder does not already exist, chapterizing...")

                    os.system(f'cd data_raw; chapterize {file}')
                    # exec(chapterize({Path(in_dir + file)}))
                    print(f"\t{chapterized_folder} created successfully\n")

                    title = chapterized_folder.split("-")[0].replace("_", " ")
                    chapterized_dir = (os.path.join(self.raw_dir, chapterized_folder))
                    self.tag_chapterized_by_folder(title, chapterized_dir, self.formatted_dir)


    def tag_chapterized_by_folder(self, title, in_dir, out_dir):      
        for file in os.listdir(in_dir):
            with open(os.path.join(in_dir, file)) as f:
                chapter_text = f.read()
            # print(file)
            f = open(os.path.join(out_dir, str(self.current_id)) + "-tagged.txt", "w")
            f.write(f"<title>{title}</title>\n<text>{chapter_text}</text>")
            f.close()
            self.current_id += 1
    
    