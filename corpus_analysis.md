---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
from BechdelCorpusBuilder import *
```

```python
## Edit this path
# HOME_DIR = '/Users/michelleyun/bechdel/src/bechdel_corpus'
HOME_DIR = '/Users/kmaurinjones/Desktop/School/UBC/UBC_Coursework/block_5/cl523/bechdel/src/bechdel_corpus'
```

```python
os.mkdir("data_formatted")
Bechdel = BechdelCorpus('books.txt', HOME_DIR)
```

```python
reader = Bechdel.read_corpus()
```

```python
import pandas as pd

books_df = pd.read_csv("corpus.csv")
books_df.head()
```

```python
books_df['title'].unique().tolist()
```

```python
from collections import Counter
from nltk.corpus import stopwords

def get_book_stats(book_df):
    """
    Given a passed Pandas dataFrame object containing information about the book, this will calculate relevant statistics about the book.

    Parameters:
    ------
    `book_df`: Pandas dataFrame object
    """
    
    book_tokens = []

    for row in book_df.index:
        for word in book_df.loc[row, 'text'].split(" "):
            book_tokens.append(word)

    book_types = set(book_tokens)
    total_male_speakers = book_df['male_speakers'].sum()
    total_female_speakers = book_df['female_speakers'].sum()
    bechdel_passes = book_df['bechdel'].sum()
    book_title = book_df['title'].unique().tolist()[0]
    book_overall_pass = None

    counter = Counter(word.lower() for word in book_tokens)
    stopwords_set = stopwords.words("English")
    stopwords_set.extend(["would", "could", "one", "may"])

    if bechdel_passes > 0:
        book_overall_pass = "Yes"
    else:
        book_overall_pass = "No"

    print(f"\nBook title: {book_title}")
    print(f"Number of chapters that pass the Bechdel Test: {bechdel_passes}, {round(bechdel_passes / len(book_df) * 100, 2)}% of all chapters")
    print(f"Number of chapters that fail the Bechdel Test: {len(book_df) - bechdel_passes}, {round((len(book_df) - bechdel_passes) / len(book_df) * 100, 2)}% of all chapters")
    print(f"Book Bechdel Test evaluation: {book_overall_pass}")
    print(f"Most common words: {(' '.join([pair[0] for pair in counter.most_common(10)]))}")
    print(f"Most common words excluding stopwords: {(' '.join([pair[0] for pair in counter.most_common(500) if pair[0].isalpha() and pair[0].lower() not in stopwords_set][:10]))}")
    print(f"Total instaces of male speakers: {total_male_speakers}")
    print(f"Total instaces of female speakers: {total_female_speakers}")
    print(f"Total tokens: {len(book_tokens)}")
    print(f"Total types: {len(book_types)}\n")
```

```python
list_of_dfs = []

moby_dick_df = books_df.query("title == 'Moby Dick'")
list_of_dfs.append(moby_dick_df)
p_and_p_df = books_df.query("title == 'Pride and Prejudice'")
list_of_dfs.append(p_and_p_df)
s_and_s_df = books_df.query("title == 'Sense and Sensibility'")
list_of_dfs.append(s_and_s_df)
w_heights_df = books_df.query("title == 'Wuthering Heights'")
list_of_dfs.append(w_heights_df)
persuasion_df = books_df.query("title == 'Persuasion'")
list_of_dfs.append(persuasion_df)
north_a_df = books_df.query("title == 'Northanger Abbey'")
list_of_dfs.append(north_a_df)
emma_df = books_df.query("title == 'Emma'")
list_of_dfs.append(emma_df)
mans_park_df = books_df.query("title == 'Mansfield Park'")
list_of_dfs.append(mans_park_df)
lil_wom_df = books_df.query("title == 'Little Women'")
list_of_dfs.append(lil_wom_df)
```

```python
for book_df in list_of_dfs:
    get_book_stats(book_df)
```
