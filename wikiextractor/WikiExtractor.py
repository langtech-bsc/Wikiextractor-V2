#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
#  Version: 4.0 (June, 2023)
#  Author: Adrián Rubio, Barcelona Supercomputing Center
#
#   This project is an updated and improved fork of
#       https://github.com/attardi/wikiextractor
#
# =============================================================================
#  Copyright (c) 2009-2023. Giuseppe Attardi (attardi@di.unipi.it).
# =============================================================================
#  This file is part of Tanl.
#
#  Tanl is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Affero General Public License, version 3,
#  as published by the Free Software Foundation.
#
#  Tanl is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

"""Wikipedia Extractor:
Extracts and cleans text from a Wikipedia database dump and stores output in a
number of files of similar size in a given directory.
Each file will contain several documents.

The program performs template expansion by preprocesssng the whole dump and
collecting template definitions.
"""

import argparse
import bz2
import logging
import os.path
import re  # TODO use regex when it will be standard
import sys
from io import StringIO
from timeit import default_timer
import inspect
extract_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"extract")))
if extract_path not in sys.path:
     sys.path.insert(0, extract_path)
from extract import Extractor, ignoreTag, define_template, acceptedNamespaces


# ===========================================================================

# Program version
__version__ = '4.0'

##
# Defined in <siteinfo>
# We include as default Template, when loading external template file.
knownNamespaces = set(['Template'])

##
# The namespace used for template definitions
# It is the name associated with namespace key=10 in the siteinfo header.
templateNamespace = ''

##
# The namespace used for module definitions
# It is the name associated with namespace key=828 in the siteinfo header.
moduleNamespace = ''


# CONFIG MACROS

CONFIG_DISCARD_SECTIONS_PATH = "config/discard_sections.txt"
CONFIG_DISCARD_TEMPLATES_PATH = "config/discard_templates.txt"
CONFIG_IGNORE_TEMPLATES_PATH = "config/ignore_templates.txt"

# ----------------------------------------------------------------------
# Modules

# Only minimal support
# FIXME: import Lua modules.

modules = {
    'convert': {
        'convert': lambda x, u, *rest: x + ' ' + u,  # no conversion
    }
}
# ----------------------------------------------------------------------
# Expand using WikiMedia API
# import json

# def expandTemplates(text):
#     """Expand templates invoking MediaWiki API"""
#     text = urlib.urlencodew(text)
#     base = urlbase[:urlbase.rfind('/')]
#     url = base + "/w/api.php?action=expandtemplates&format=json&text=" + text
#     exp = json.loads(urllib.urlopen(url))
#     return exp['expandtemplates']['*']

# ------------------------------------------------------------------------------
# Output


# ----------------------------------------------------------------------

# Minimum size of output files
minFileSize = 200 * 1024


class NextFile():

    """
    Synchronous generation of next available file name.
    """

    # filesPerDir = 100

    def __init__(self, path_name, extension):
        self.path_name = path_name
        self.extension = extension
        self.dir_index = -1
        self.file_index = -1

    def next(self):
        self.file_index = self.file_index + 1
        # self.file_index = (self.file_index + 1) % NextFile.filesPerDir
        if self.file_index == 0:
            self.dir_index += 1
        dirname = self._dirname()
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return self._filepath()

    def _dirname(self):
        return self.path_name
        # char1 = self.dir_index % 26
        # char2 = int(self.dir_index / 26) % 26
        # return os.path.join(self.path_name, '%c%c' % (ord('A') + char2, ord('A') + char1))

    def _filepath(self):
        name = '%s/wiki_%02d' % (self._dirname(), self.file_index)
        return name + self.extension


class OutputSplitter():

    """
    File-like object, that splits output to multiple files of a given max size.
    """

    def __init__(self, nextFile, max_file_size=0, compress=True):
        """
        :param nextFile: a NextFile object from which to obtain filenames
            to use.
        :param max_file_size: the maximum size of each file.
        :para compress: whether to write data with bzip compression.
        """
        self.nextFile = nextFile
        self.compress = compress
        self.max_file_size = max_file_size
        self.file = self.open(self.nextFile.next())

    def reserve(self, size):
        if self.file.tell() + size > self.max_file_size:
            self.close()
            self.file = self.open(self.nextFile.next())

    def write(self, data):
        self.reserve(len(data))
        if self.compress:
            self.file.write(data)
        else:
            self.file.write(data)

    def close(self):
        self.file.close()

    def open(self, filename):
        if self.compress:
            return bz2.BZ2File(filename + '.bz2', 'w')
        else:
            return open(filename, 'w')


# ----------------------------------------------------------------------
# READER

tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')
#                    1     2               3      4


def load_templates(file, output_file=None):
    """
    Load templates from :param file:.
    :param output_file: file where to save (overwrite) templates and modules. OPTIONAL
    :return: number of templates loaded.
    """
    global templateNamespace
    global moduleNamespace, modulePrefix
    modulePrefix = moduleNamespace + ':'
    articles = 0
    templates = 0
    page = []
    inText = False

    if output_file:
        dir_name = os.path.dirname(output_file)
        try:
            if(dir_name and not os.path.exists(dir_name)): 
                #it has a folder in path but doesnt exist
                os.makedirs(dir_name)
        except:
                logging.error('Can not create: %s', output_file)
                return 0

        output = open(output_file, 'w')

    for line in file:
        # line = line.decode('utf-8')
        if '<' not in line:  # faster than doing re.search()
            if inText:
                page.append(line)
            continue
        m = tagRE.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'page':
            page = []
        elif tag == 'title':
            title = m.group(3)
            if not output_file and not templateNamespace:  # do not know it yet
                # we reconstruct it from the first title
                colon = title.find(':')
                if colon > 1:
                    templateNamespace = title[:colon]
                    Extractor.templatePrefix = title[:colon + 1]
            # FIXME: should reconstruct also moduleNamespace
        elif tag == 'text':
            inText = True
            line = line[m.start(3):m.end(3)]
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == '/text':
            if m.group(1):
                page.append(m.group(1))
            inText = False
        elif inText:
            page.append(line)
        elif tag == '/page':
            if title.startswith(Extractor.templatePrefix):
                define_template(title, page)
                templates += 1
            # save templates and modules to file
            if output_file and (title.startswith(Extractor.templatePrefix) or
                                title.startswith(modulePrefix)):
                output.write('<page>\n')
                output.write('   <title>%s</title>\n' % title)
                output.write('   <ns>10</ns>\n')
                output.write('   <text>')
                for line in page:
                    output.write(line)
                output.write('   </text>\n')
                output.write('</page>\n')
            page = []
            articles += 1
            if articles % 100000 == 0:
                logging.info("Preprocessed %d pages", articles)
    if output_file:
        output.close()
        logging.info("Saved %d templates to '%s'", templates, output_file)
    return templates


def decode_open(filename, mode='rt', encoding='utf-8'):
    """
    Open a file, decode and decompress, depending on extension `gz`, or 'bz2`.
    :param filename: the file to open.
    """
    ext = os.path.splitext(filename)[1]
    if ext == '.gz':
        import gzip
        return gzip.open(filename, mode, encoding=encoding)
    elif ext == '.bz2':
        return bz2.open(filename, mode=mode, encoding=encoding)
    else:
        return open(filename, mode, encoding=encoding)


def collect_pages(text):
    """
    :param text: the text of a wikipedia file dump.
    """
    # we collect individual lines, since str.join() is significantly faster
    # than concatenation
    page = []
    id = ''
    revid = ''
    last_id = ''
    inText = False
    redirect = False
    for line in text:
        if '<' not in line:     # faster than doing re.search()
            if inText:
                page.append(line)
            continue
        m = tagRE.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'page':
            page = []
            redirect = False
        elif tag == 'id' and not id:
            id = m.group(3)
        elif tag == 'id' and id:  # <revision> <id></id> </revision>
            revid = m.group(3)
        elif tag == 'title':
            title = m.group(3)
        elif tag == 'redirect':
            redirect = True
        elif tag == 'text':
            inText = True
            line = line[m.start(3):m.end(3)]
            page.append(line)
            if m.lastindex == 4:  # open-close
                inText = False
        elif tag == '/text':
            if m.group(1):
                page.append(m.group(1))
            inText = False
        elif inText:
            page.append(line)
        elif tag == '/page':
            colon = title.find(':')
            if ((colon < 0 or (title[:colon] in acceptedNamespaces))
                and (id != last_id)
                and (not redirect)
                and (not title.startswith(templateNamespace))
                ):
                yield (id, revid, title, page)
                last_id = id
            id = ''
            revid = ''
            page = []
            inText = False
            redirect = False


def preprocess_dump(input_file, template_file, expand_templates=True):
    """
    :param input_file: name of the wikipedia dump file; '-' to read from stdin
    :param template_file: optional file with template definitions.
    :param out_file: directory where to store extracted data, or '-' for stdout
    :param file_size: max size of each extracted file, or None for no max (one file)
    :param file_compress: whether to compress files with bzip.
    :param file_extension: file extension of each generated file
    :param process_count: number of extraction processes to spawn.
    :param html_safe: whether to convert entities in text to HTML.
    :param expand_templates: whether to expand templates.
    """
    global knownNamespaces
    global templateNamespace
    global moduleNamespace, modulePrefix

    urlbase = ''                # This is obtained from <siteinfo>
    language = ''


    input = decode_open(input_file)

    # collect siteinfo
    for line in input:
        line = line #.decode('utf-8')
        m = tagRE.search(line)
        if not m:
            continue
        tag = m.group(2)
        if tag == 'base':
            # discover urlbase from the xml dump file
            # /mediawiki/siteinfo/base
            base = m.group(3)
            urlbase = base[:base.rfind("/")]
            language = urlbase.split(".")[0].split("//")[1]
            Extractor.language = language
        elif tag == 'namespace':
            knownNamespaces.add(m.group(3))
            if re.search('key="10"', line):
                templateNamespace = m.group(3)
                Extractor.templatePrefix = templateNamespace + ':'
            elif re.search('key="828"', line):
                moduleNamespace = m.group(3)
                modulePrefix = moduleNamespace + ':'
        elif tag == '/siteinfo':
            break


    if expand_templates:
        # preprocess
        template_load_start = default_timer()

        if template_file and os.path.exists(template_file):
            logging.info("Preprocessing '%s' to collect template definitions: this may take some time.", template_file)
            file = decode_open(template_file)
            templates = load_templates(file)
            file.close()
        else:
            if input_file == '-':
                # can't scan then reset stdin; must error w/ suggestion to specify template_file
                raise ValueError("to use templates with stdin dump, must supply explicit template-file")
            logging.info("Preprocessing '%s' to collect template definitions: this may take some time.", input_file)
            templates = load_templates(input, template_file)
            input.close()
            input = decode_open(input_file)

            
        template_load_elapsed = default_timer() - template_load_start
        logging.info("Loaded %d templates in %.1fs", templates, template_load_elapsed)


        # Discard articles if containing some templates by lang.
        if(Extractor.discardTemplates is not None):
            basedir = os.path.dirname(os.path.realpath(__file__))
            path_to_discard_templates = os.path.join(basedir, Extractor.discardTemplates)
            Extractor.discardTemplates = set()
            with open( path_to_discard_templates , "r") as f:
                take_lang_flag = False
                for line in f:
                    if(line[0] == '#' or line[0] in '\n'):
                        continue
                    elif(line[0] == '+'):# new lang templates names.
                        lang = line.split(': ')[1].split('\n')[0]
                        if( lang == Extractor.language or lang == 'en'):
                            logging.debug("Reading templates to discard from language:" + lang)
                            take_lang_flag = True
                        else:
                            take_lang_flag = False
                    elif(take_lang_flag): #take selected lang template names
                        discardTempName = line.replace('\n', '').lower()
                        logging.debug("\t\tDiscarding template name:" + discardTempName)
                        Extractor.discardTemplates.add(discardTempName)
                    else:
                        continue
        else:
            Extractor.discardTemplates = set()

        # Discard articles if containing some templates by lang.
        if(Extractor.ignoreTemplates is not None):
            basedir = os.path.dirname(os.path.realpath(__file__))
            path_to_ignore_templates = os.path.join(basedir, Extractor.ignoreTemplates)
            Extractor.ignoreTemplates = set()
            with open( path_to_ignore_templates , "r") as f:
                take_lang_flag = False
                for line in f:
                    if(line[0] == '#' or line[0] in '\n'):
                        continue
                    elif(line[0] == '+'):# new lang templates names.
                        lang = line.split(': ')[1].split('\n')[0]
                        if( lang == Extractor.language or lang == 'en'):
                            logging.debug("Reading templates to ignore from language:" + lang)
                            take_lang_flag = True
                        else:
                            take_lang_flag = False
                    elif(take_lang_flag): #take selected lang template names
                        ignoreTempName = line.replace('\n', '').lower()
                        logging.debug("\tIgnoring template name:" + ignoreTempName)
                        Extractor.ignoreTemplates.add(ignoreTempName)
                    else:
                        continue        
        else:
            Extractor.ignoreTemplates = set()



    # Discard some Wikipedia sections (current lang) specifying their title
    if(Extractor.discardSections is not None): 
        basedir = os.path.dirname(os.path.realpath(__file__))
        path_to_discard_sections = os.path.join(basedir , Extractor.discardSections)
        Extractor.discardSections = set()
        with open( path_to_discard_sections , "r") as f:
            take_lang_flag = False
            for line in f:
                if(line[0] == '#' or line[0] in '\n'):
                    continue
                elif(line[0] == '+'):# new lang section names.
                    lang = line.split(': ')[1].split('\n')[0]
                    if( lang == Extractor.language or lang == 'en'):
                        logging.debug("Reading sections to discard from language:" + lang)
                        take_lang_flag = True
                    else:
                        take_lang_flag = False
                elif(take_lang_flag): #take selected lang template names
                    discardSecName = line.replace('\n', '').lower()
                    logging.debug("\t\tDiscarding sections name:" + discardSecName)
                    Extractor.discardSections.add(discardSecName)
                else:
                    continue
    else:
        Extractor.discardSections = set()

    input_opened = input
    return input_opened, urlbase


def process_dump_script(input_opened,input_file, out_file, file_size, file_compress,
                 file_extension,urlbase):
    # Write to docs or to stdout.

    # Output configuration if path is stdout
    if (out_file == '-'):
        output = sys.stdout
        if file_compress:
            logging.warn("writing to stdout, so no output compression (use an external tool)")
    else:
        #output = out_file
        nextFile = NextFile(out_file,file_extension)
        output = OutputSplitter(nextFile, file_size, file_compress)

    ##
    #  Generatics doc files
    logging.info("Starting page extraction from %s.", input_file )
    extract_start = default_timer()

    ordinal = 1  # page count

    for id, revid, title, page in collect_pages(input_opened): 
        #out :output folder path
        if ( Extractor(id, revid, urlbase, title, page).extract(output, html_safe=True) ):
            ordinal += 1
            #logging.debug("\t Doc. saved:" + str(ordinal))
        #else empty doc

    input_opened.close()


    # Script time statistics
    if output != sys.stdout and not Extractor.generator:
        output.close()
    extract_duration = default_timer() - extract_start
    extract_rate = ordinal / extract_duration
    logging.info("Finished 1-process extraction of %d articles in %.1fs (%.1f art/s)",
                 ordinal, extract_duration, extract_rate)

    return





def process_dump_generator(input_opened,input_file, urlbase):

    ##
    #  Generatics doc files
    logging.info("Starting page extraction from %s.", input_file )
    extract_start = default_timer()

    ordinal = 1  # page count
    for id, revid, title, page in collect_pages(input_opened): 
        doc_info = Extractor(ordinal, revid, urlbase, title, page).extract(out=None, html_safe=True)
        if (doc_info):
            ordinal += 1
            yield doc_info
            #logging.debug("\t Doc. saved:" + str(ordinal))



    input_opened.close()

    # Script time statistics
    extract_duration = default_timer() - extract_start
    extract_rate = ordinal / extract_duration
    logging.info("Finished 1-process extraction of %d articles in %.1fs (%.1f art/s)",
                 ordinal, extract_duration, extract_rate)

    return





def reduce_process(output_queue, output):
    """
    Pull finished article text, write series of files (or stdout)
    :param output_queue: text to be output.
    :param output: file object where to print.
    """

    interval_start = default_timer()
    period = 100000
    # FIXME: use a heap
    ordering_buffer = {}  # collected pages
    next_ordinal = 0  # sequence number of pages
    while True:
        if next_ordinal in ordering_buffer:
            output.write(ordering_buffer.pop(next_ordinal))
            next_ordinal += 1
            # progress report
            if next_ordinal % period == 0:
                interval_rate = period / (default_timer() - interval_start)
                logging.info("Extracted %d articles (%.1f art/s)",
                             next_ordinal, interval_rate)
                interval_start = default_timer()
        else:
            # mapper puts None to signal finish
            pair = output_queue.get()
            if not pair:
                break
            ordinal, text = pair
            ordering_buffer[ordinal] = text


def main(*args, **kwargs):

    global acceptedNamespaces
    global templateCache

    parser = argparse.ArgumentParser(prog='Wikiextractor.py',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)

    all_args = []
    all_args.extend([str(i) for i in args])
    for k, v in kwargs.items():
        all_args.append(str(k))
        all_args.append(v)

    parser.add_argument("input",
                        help="XML wiki dump file")

    groupO = parser.add_argument_group('Output')
    groupO.add_argument("-o", "--output", default="text",
                        help="directory for extracted files (or '-' for dumping to stdout)")

    groupO.add_argument("-b", "--bytes", default="1M",
                        help="maximum bytes per output file (default %(default)s); 0 means to put a single article per file",
                        metavar="n[KMG]")
    groupO.add_argument("--generator", action="store_true",
                        help="output file will be ignored and the script will behave as a yield generator.\n \
                            OUTPUT format:  doc_id,\n \
                                            title,\n \
                                            url,\n \
                                            languages, \n \
                                            text")
    groupO.add_argument("--html", action="store_true",
                        help="produce HTML output, subsumes --links")
    groupO.add_argument("-l", "--links", action="store_true",
                        help="preserve links")
    groupO.add_argument("--json", action="store_true",
                        help="write output in json format instead of the default <doc> format")
    groupO.add_argument("--txt", action="store_true",
                        help="write output in plain text format instead of the default <doc> format")
    groupO.add_argument("-c", "--compress", action="store_true",
                        help="compress output files using bzip")

    groupP = parser.add_argument_group('Processing')
    groupP.add_argument("--templates",
                        help="use or create file containing templates")
    groupP.add_argument("--discard_sections", action="store_true",
                        help="If specified, it will discard \
                              some wikipedia sections by their titles (e.g. References, Bibliography). \
                            The ones(alredy-given) under  config/discard_sections.txt ")

    groupP.add_argument("--discard_templates", action="store_true",
                        help="If specified, it will discard \
                              some wikipedia docs if containg some templates titles (e.g. Disambiguation, Desambiguación). \
                              \Since most template names are usually tranlated.  \
                                See an example under config/discard_templates.txt ")
    groupP.add_argument("--ignore_templates", action="store_true",
                        help="If specified, it will not expand \
                              some templates (e.g. Millorar format). \
                              \Since most template names are usually tranlated.  \
                                See an example under config/ignore_templates.txt ")
    groupP.add_argument("--html_safe", default=True,
                        help="use to produce HTML safe output within <doc>...</doc>")
    groupP.add_argument("-ns", "--namespaces", default="", metavar="ns1,ns2",
                        help="accepted namespaces")

    groupS = parser.add_argument_group('Special')
    groupS.add_argument("-q", "--quiet", action="store_true",
                        help="suppress reporting progress info")
    groupS.add_argument("--debug", action="store_true",
                        help="print debug info")
    groupS.add_argument("-v", "--version", action="version",
                        version='%(prog)s ' + __version__,
                        help="print program version")

    args = parser.parse_args(all_args)

    Extractor.keepLinks = args.links
    Extractor.HtmlFormatting = args.html
    if args.html:
        Extractor.keepLinks = True
    Extractor.to_json = args.json
    Extractor.to_txt = args.txt
    Extractor.generator = args.generator

    # Discard some Wikipedia sections specifying their title
    if (args.discard_sections):
        Extractor.discardSections = CONFIG_DISCARD_SECTIONS_PATH

    # Discard some Wikipedia articles if containig some templates
    if (args.discard_templates and args.templates):
        Extractor.discardTemplates = CONFIG_DISCARD_TEMPLATES_PATH

        # Discard some Wikipedia articles if containig some templates
    if (args.ignore_templates and args.templates):
        Extractor.ignoreTemplates = CONFIG_IGNORE_TEMPLATES_PATH

    try:
        power = 'kmg'.find(args.bytes[-1].lower()) + 1
        # 0 bytes means put a single article per file.
        file_size = 0 if args.bytes == '0' else int(
            args.bytes[:-1]) * 1024 ** power
        if file_size and file_size < minFileSize:
            raise ValueError()
    except ValueError:
        logging.error('Insufficient or invalid size: %s', args.bytes)
        return

    if args.namespaces:
        acceptedNamespaces = set(args.namespaces.split(','))

    FORMAT = '%(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT)

    logger = logging.getLogger()
    if not args.quiet:
        logger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    input_file = args.input

    if not Extractor.keepLinks:
        ignoreTag('a')

    output_path = args.output
    if output_path != '-' and not os.path.isdir(output_path):
        try:
            os.makedirs(output_path)
        except:
            logging.error('Could not create: %s', output_path)
            return
    elif (output_path is None and args.generator is None):
        output_path = '-'

    if (args.bytes):
        file_extension = '.txt'
    elif (args.json):
        file_extension = '.json'
    else:
        file_extension = ''


    # Preproces dump:header and templates
    input_opened, urlbase = preprocess_dump(    input_file, 
                                                args.templates, 
                                                expand_templates=bool(args.templates)
                                            )

    if (args.generator): #Using the tool as a module
        return process_dump_generator(input_opened,input_file, urlbase)

    else:  #Using the tool as a a script
        process_dump_script(    input_opened = input_opened, 
                                input_file = input_file,
                                out_file = output_path,
                                file_size=file_size,
                                file_compress=args.compress,
                                file_extension=file_extension,
                                urlbase = urlbase
                            )



if __name__ == '__main__':
    args = sys.argv  # Exclude the script name (first argument)
    main(*args[1:])  # kwargs
