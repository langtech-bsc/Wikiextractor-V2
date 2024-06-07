# WikiExtractor V2
WikiExtractor V2 is a Python script that extracts and cleans text from a [Wikipedia database backup dump](https://dumps.wikimedia.org/), e.g. https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2 for English.


![alt text](https://github.com/TeMU-BSC/Wikiextractor-V2/blob/main/img/example0.jpg "Example of output 0")


WikiExtractor V2 is a fork of the project https://github.com/attardi/wikiextractor. It fixes bugs of the orginal tool and adds new features. It has been tested with 2023 Wikipedia dumps.



# Details

WikiExtractor V2 performs template expansion by preprocessing the whole dump and extracting template definitions. 

In order to speed up processing a cache is kept of parsed templates (only useful for repeated extractions of the same language dump).The file is cached in a file, which route can be specified with the argument `--templates`.

## New features

Here is a *brief summary* of the new features:

- Support for list and nested lists
- Support for UNICODE chars.
- Support for math and chemical formulas.
- Plain text (.txt) as an output format
- Plain json (.json) as an output format
- Includes doc title by deafult
- Several issues with specific templates handled (segle, coords,etc)
- Option to ban specific sections, templates or entire documents containing some templates (e.g. References, Biliography) by a config file.
- Now the tool can be used both as a single tool or as a module ready-to-connect to a pipline (improving memory and time consumption)
- Lots of issues solved and several improvements...

Please note that depending on the dump's language, there still might be some issues. This is caused by bad-formatted dumps. The frequency of this errors depends on the chosen  dump. Despite of that, this version tries to handle most of common issues :D



# Setup

Some libraries must be installed in order to execute the tool. They are specified in requirements.txt. To do this use the following command:

    pip install -r requirements.txt 

Tested under python 3.7.

# Use as a script
Here is an **easy example of use** as a single tool to extract text-plain chunks of size 1MB with the best cleaning available:
```python
python -m wikiextractor/WikiExtractor.py INPUT_DUMP_FILE \
                        --output OUTPUT_FOLDER \
                        --bytes 1M \
                        --templates TEMPLATES_PATH \
                        --txt \
                        --discard_sections \
                        --discard_templates \
                        --ignore_templates \
```

# Use as a module

You can easily import Wikiextractor V2 and use it as a generator importing it as a module and passing with the following example code:

```python
import wikiextractor as wikie

aargs = [INPUT_DUMP_FILE,
				'--generator'
				'--txt',
				'--discard_sections',
				'--discard_templates',
				'--ignore_templates',
				]
kkwargs = {
	'--templates': TEMPLATES_PATH,
}

# DO SOMETHING PARALLELIZABLE
for docinfo in wikie.main(*aargs, **kkwargs):
   title, url, language, text = docinfo

```



# Further Usage

```
usage: WikiExtractor.py [-h] [-o OUTPUT] [-b n[KMG]] [--generator] [--html] [-l] [--json] [--txt] [-c] [--templates TEMPLATES] [--discard_sections] [--discard_templates]
                        [--ignore_templates] [--html_safe HTML_SAFE] [-ns ns1,ns2] [-q] [--debug] [-v]
                        input



POSITIONAL ARGUMENTS:
input                 
        (PATH) XML (also compressed in gz or .bz2) wiki dump file



OUTPUT ARGUMENTS:
  
  -o OUTPUT, --output OUTPUT
			    directory for extracted files (or '-' for dumping to stdout)
  
  -b n[KMG], --bytes n[KMG]
			    maximum bytes per output file (default 1M)
  
  --generator 
        output file will be ignored and the script will behave as a   generator. 
        It will yield the folllowing info:doc_id,title,url,languages,text.
        WARNING: This option will only work if the code is used as a module.
  
  --html                
          produce HTML output, subsumes --links. Used as a default
  
  -l, --links           
          preserve links
  
  --json 
          write output in json format instead of the default <doc> format
  
  --txt                
        write output in txt format instead of the default <doc> format
  
  -c, --compress        
        compress output files using bzip




PROCESSING ARGUMENTS:
  
  --templates TEMPLATES
	use or create(if not exits, preprocess the dump) file containing templates.
  
  --discard_sections 
          Highly recommended.
          If specified, it will discard some non-desired sections by their titles 
          (e.g. References, Bibliography). 
          Sections (alredy-given) under  config/discard_sections.txt
 
  --discard_templates
          Highly recommended.
          If specified, it will discard some wikipedia docs if they contain containg some non-desired templates  (e.e.g. Disambiguation, Desambiguación).
          Sections (alredy-given) under config/discard_templates.txt
  
  --ignore_templates
          Highly recommended.
          If specified, it will not expand some non-desired templates. 
          (e.g. Millorar format).
          Names (alredy-given) under config/ignore_templates.txt 

  
  --html_safe 
			    used to produce HTML safe output within <doc>...</doc>
  
  -ns ns1,ns2, --namespaces ns1,ns2
			    accepted namespaces

SPECIAL ARGUMENTS:
  -h, --help            show this help message and exit
  -q, --quiet           suppress reporting progress info
  -v, --version         print program version
  --debug               print debug info
```




## Input

The script is invoked with a Wikipedia dump file as an argument. An input **dump file** is a .xml file (it can be compressed as .gz or .bz2 format).

You can download all Wikimedia dumps with the [wiki_dump_download.py](https://github.com/langtech-bsc/Wikiextractor-V2/blob/main/wiki_dump_download.py) script, using the [wiki-data-dump library](https://pypi.org/project/wiki-data-dump/), which handles requests to the [Wikimedia Data Dumps](https://dumps.wikimedia.org/) and its [mirrors](https://dumps.wikimedia.org/mirrors.html). By default, it downloads 'pages-articles.xml.bz2' files for each language, which appear corrupted when extracted (bzip2 or any other extraction command won't work with these files). Just rename the file and remove the .bz2 extension, and it will appear as a normal XML file that the Wikiextractor-V2 can handle. Otherwise, download 'pages-multistream-articles.xml', which is downloaded as XML by default.

```python wiki_dump_download.py --download wikipedia --output_path "/home/downloads/"```

## Output
The output can **behave** in **two diferent ways**.
1. One of them is to store output in several files of similar size in a given directory, given by `--output`. Each file located in "output" is a **chunk of data** of size N (bytes) wich can be specified with ``--bytes`. Each chunk will be compressed if `--compress` arg is passed.

Different docs will be isolated inside each chunk by the separator given by the MARCRO: `FILE_SEPARATOR'.
`

2.  The script can behave as a **generator** if `--generator` argument is given. This is very useful when using Wikiextractor V2 as an external module. This will yield a doc each time is processed by the script, so the docs. can be paralelized in the future in an external pipeline invoking Wikiextractor V2, for performance reasons.

### Output Format

Each generated document will have an html format by deafult. To change this use:

- `--txt` arg to produce a plain text as a document. If combined with `--generator`prgram will yield a tuple with the following info: ``` (doc_id,doc_title,doc_url,doc_language,doc_text)```

- `--json` arg to produce a json file as a document. If combined with `--generator`prgram will yield json files with the following fields: ```doc_id,title,url,language,text.```


## Templates and sections
The option `--templates` extracts the templates to a local file, which can be reloaded to reduce the time to perform extraction. If the file exists it will automatically load the file. If this option is not specified the tool won't expand any template. This will lead to empty words in text, in most  of the situations.

Saving templates to a file will speed up performing extraction the next time,
assuming template definitions have not changed.

In order to improve the output cleaning, **it's highly recommended to use the following 3 options**:

- Since some template names are language-dependent, with some dump files,some disambiguation and other non-desired templates are expanded, eventually yielding a document which is not very useful. In order to avoid this, `--discard_templates` can be used to **discard the whole doc** if it **contains a template** with the name specified under already-completed file config/discard_templates.txt Note that this file contains autotranslated template names for several languages, an some of them may not match with the one used in Wikipedia. To avoid this, add or edit new entries in this file.

- In other cases , we don't want to discard the whole document, only to not expand and ignore some language-dependent templates like 'Improve format'. Since expanding them will produce trash info, the only way to address this is controlling it manually. In order to do that use `--ignore_templates`, which will **ignore templates names** specified under already-completed file config/ignore_templates.txt

- Just like template, some sections are not labeled globally for all the dumps, and they are language dependent. The only way to address this problem its also in a manually way. This sections usually may not always be very useful e.g. Refences, Bibliografy... To avoid them use `--discard_sections`, which will ignore sections with titles specified under config/discard_sections.txt

*The content under config/ has been generated using its corresponding included scripts located under utils/ folder. Feel free to use them if you want to automatically add an entry for several languages.* 











## Some Screenshots :)

### Example of output 1
![alt text](https://github.com/TeMU-BSC/Wikiextractor-V2/blob/main/img/example1.jpg "Example of output 1")

### Example of output 2
![alt text](https://github.com/TeMU-BSC/Wikiextractor-V2/blob/main/img/example2.jpg "Example of output 2")

### Example of output 3
![alt text](https://github.com/TeMU-BSC/Wikiextractor-V2/blob/main/img/example3.jpg "Example of output 3")

## License
The code is made available under the [GNU Affero General Public License v3.0](LICENSE). 

