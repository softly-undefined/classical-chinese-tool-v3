# Classical Chiense Translation Tool v3

This is the third version of a tool for translating long documents of Classical Chinese text. Development begun 10/29/25 by Eric Bennett. It is inspired by the second version of this tool, an interactive version located here: https://github.com/softly-undefined/classical-chinese-tool-v2

## Methodology

Chunking logic can be found in the chunking.py file. The base idea is to create reasonably sized chunks of the original text, and then translate these chunks. A marker is then placed in the resulting English and original Chinese. 

