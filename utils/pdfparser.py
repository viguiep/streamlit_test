import fitz
import streamlit as st

from collections import defaultdict
import spacy

nlp = spacy.load('en_core_web_sm')


"""
Get the pdf file
"""
def getPDF(uploaded_file):
    try:
        document = fitz.open(stream=uploaded_file.read(), filetype="pdf") # leads to a sys.stderr message:
        st.write('Nb of pages:', len(document))
        st.write('The pdf document was opened without problem.')

        return document
    except:
        st.error('Problem with pdf document.')
        #st.error("document.is_dirty:", document.is_dirty)
        document = None

"""
Most common element of a list (weighted byt the text length)
"""
# ******************************************
# get the most common element in a list (weighted by text length)
# ******************************************
def getMostCommon(LINES, key):

    myDict = defaultdict(int)
    for x in LINES:
        myElement, myCount = x[key], x['text'] # DIFFERENCE
        myDict[myElement] += len(myCount)

    # sort from most common to less common
    sorted_dict = sorted(myDict.items(), key=lambda x: -x[1])


    # extract the element of the most common tuple (indice 0)
    result = sorted_dict[0][0]

    return result

# ******************************************
# get the lines of conjugated sentences
# ******************************************
def getConjugatedBlocks(document_pdf):

    list_of_blocks = []

    for i, page in enumerate(document_pdf):
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            new_block = ''
            if b['type'] == 0:  # block contains text

                for l in b["lines"]:  # iterate through the text lines
                    new_line = ''
                    for s in l["spans"]:
                        new_line += s['text']
                    # special case of cut words ('Orga- nization') at line end
                    # we add a space only if not a "cut word" at the line end
                    if new_line[-1] == '-':
                        new_line = new_line[:-1]
                    else:
                        new_line += ' '
                    new_block += new_line

                # I check if this correspond to conjugated sentences (main text or abstract)
                doc = nlp(new_block)
                nb_sentences = len([1 for s in doc.sents])
                nb_root_verbs = len([1 for s in doc.sents if s.root.pos_ == 'VERB'])

                if nb_sentences > 0:

                    # we only consider blocks of "conjugated" sentences (= where there is at least x=30% of sentences with a root verb)
                    if nb_root_verbs / nb_sentences > 0.3:

                        # I suppress the last space that I added (if necessary)
                        if new_block[-1:] == ' ':
                            new_block = new_block[:-1]

                        # I compute the most popular font police, font size & font colors of the block
                        block_sizes = [{'size': s['size'],
                                        'font': s['font'],
                                        'color': s['color'],
                                        'text': s['text'],
                                        }
                                      for l in b["lines"] for s in l["spans"] ]
                        most_common_size = getMostCommon(block_sizes, 'size')
                        most_common_font = getMostCommon(block_sizes, 'font')
                        most_common_color = getMostCommon(block_sizes, 'color')

                        # I add the corresponding dictionary to my list
                        myDict = {  'police': most_common_font,
                                    'size': most_common_size,
                                    'color': most_common_color,
                                    'text': new_block,
                                  }
                        list_of_blocks.append(myDict)
    # print(s)
    return list_of_blocks
