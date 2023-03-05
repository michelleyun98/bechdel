# bechdel-corpus

An annotated corpus of classic literature.

## Description

[The Bechdel test](https://en.wikipedia.org/wiki/Bechdel_test) was created by cartoonist Allison Bechdel as a measure of female representation in fiction. While typically applied to film, this corpus aims to extend the metric to the medium of long-form text.

### Dependencies

```
python >= 3.10
```

### Execution

1. Clone the repo:
```
git clone https://github.com/michelleyun98/bechdel.git
```
2. Open `BuilderDriver.ipynb` and run the following (replace`HOME_DIR` with your root directory):
```
from BechdelCorpusBuilder import *
HOME_DIR = "path-to-current-working-dir"
BechdelCorpus = BechdelCorpusBuilder("books.txt", HOME_DIR)
```

## Roadmap

- [ ] Build corpus
- [ ] Get corpus statistics
- [ ] Release on PyPi
    - [ ] Update version
- [ ] Ensure Windows compatibility

## Help
* The current source code *has not been tested for Windows compatability*. If you are unable to load any aspect of the corpus through the source code, the csv file can be found [here](https://drive.google.com/file/d/1ROzDxVOKK_J9WVFT7w2VgGGY4s9Jp9Vy/view?usp=share_link)

## Contributors

Jata MacCabe, Ananya Apparaju, Sara Mirjalili, Kai Maurin-Jones, Michelle Yun

## Acknowledgments
Corpus collected from [Standard ebooks](https://standardebooks.org)
