import logging
import os


def extract_first_n_pages(input_path, output_path, n_pages):
    count = 0
    in_page = False
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        outfile.write('<?xml version="1.0"?>\n<mediawiki>\n')

        for line in infile:
            if '<page>' in line:
                in_page = True
                count += 1
                if count > n_pages:
                    break
            if in_page:
                outfile.write(line)
            if '</page>' in line and in_page:
                in_page = False

        outfile.write('</mediawiki>')


def extract_first_n_pages_titles(input_path, n_pages=-1, print_each=False):
    count = 0
    in_page = False
    with open(input_path, 'r', encoding='utf-8') as infile:

        rows = []
        page_row = {}

        for line in infile:
            

            if '<page>' in line:
                in_page = True
                count += 1

                if count % 100000 == 0 and print_each:
                    cprint(f"Page {count}", 'red')

            # Parse title
            if '<title>' in line:
                title = line.split('<title>')[1].split('</title>')[0]
                page_row['title'] = title

            # Parse ns
            if '<ns>' in line:
                ns = line.split('<ns>')[1].split('</ns>')[0]
                page_row['ns'] = ns

            # Parse id
            if '<id>' in line:
                id_ = line.split('<id>')[1].split('</id>')[0]
                page_row['id'] = id_


            if '</page>' in line and in_page:
                rows.append(page_row)
                page_row = {}
                in_page = False

            # print(count)
                # <page>
                #     <title>Àbac</title>
                #     <ns>0</ns>
                #     <id>1</id>

            if count > n_pages:
                break


        return rows



        # outfile.write('</mediawiki>')





def sample_first_n_pages(input_path, output_path, n_pages, print_every=1000):

    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    # Open the input and output files
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        inside_page = False
        page_count = 0
        header_done = False
        i = 0
        
        for line in infile:
            
            # Update line counter
            i += 1
            
            # Copy the header until </siteinfo>
            if not header_done:
                outfile.write(line)
                if '</siteinfo>' in line:
                    header_done = True
                continue

            # Handle <page> sections
            # =============================================================================

            if '<page>' in line:
                i_page = i
                if page_count >= n_pages:
                    break
                inside_page = True
                page_count += 1
                inside_page_line = 0

            if inside_page:
                outfile.write(line)
                
                # Print the first line every 1000th pages
                if inside_page_line == 1 and page_count % print_every == 0:
                    # Print first line of the page
                    logging.info(f"Page {page_count} content (line {i_page}): {line.strip()}")


                inside_page_line += 1

            if '</page>' in line and inside_page:
                inside_page = False
            # =============================================================================

        # Close the XML structure
        outfile.write('</mediawiki>')




if __name__ == "__main__":

    """Sample the first N pages from a Wikipedia XML dump.
    
    n=1000
    input=../../_data/cawiki/dumps/cawiki-20250501-pages-articles.xml
    output=../../_data/cawiki/small_dumps/cawiki-20250501-pages-articles-sample_${n}.xml

    python src/utils/xml_sampler.py -f $input -o $output -n $n
    """


    # Set up logging
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(filename)s][%(levelname)s] - %(message)s')
    log = logging.getLogger(__name__)


    # Handle command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Sample the first N pages from a Wikipedia XML dump.')



    # Input file (-f)
    # Output file (-o)
    # Number of pages (-n)
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the input XML file.')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output XML file.')
    parser.add_argument('-n', '--number', type=int, required=True, help='Number of pages to sample.')
    

    # Parse the arguments
    args = parser.parse_args()
    # Get the input and output file paths and number of pages
    input_path = args.file
    output_path = args.output
    n_pages = args.number

    # Log the input parameters
    log.info(f"Input file: {input_path}")
    log.info(f"Output file: {output_path}")
    log.info(f"Number of pages to sample: {n_pages}")


    sample_first_n_pages(input_path, output_path, n_pages)
