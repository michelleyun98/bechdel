# bechdel-corpus

An annotated corpus of classic literature.

## Description

[The Bechdel test](https://en.wikipedia.org/wiki/Bechdel_test) was created by cartoonist Allison Bechdel as a measure of female representation in fiction. While typically applied to film, this corpus aims to extend the metric to the medium of long-form text.

## Getting Started

### Dependencies

```
python >= 3.10
```

### Execution

1. Clone the repo:
```
git clone https://github.com/michelleyun98/bechdel.git
```
2. Open BuilderDriver.ipynb and run the following (replace`HOME_DIR` with your root directory):
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

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
