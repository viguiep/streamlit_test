# -*- coding: utf-8 -*-
# https://github.com/schneeboat/streamlit_nlp
# https://share.streamlit.io/schneeboat/streamlit_nlp/main/nlp.py

# https://blog.streamlit.io/
# https://towardsdatascience.com/intermediate-streamlit-d5a1381daa65
# RASA - https://blog.streamlit.io/rasalit/
# persistent data - https://blog.streamlit.io/streamlit-firestore/

# STREAMLIT TRICKS
# https://docs.streamlit.io/library/api-reference
# https://codingfordata.com/8-simple-and-useful-streamlit-tricks-you-should-know/

"""
RAJOUTER LE GIT EXCLUDE

BIG ISSUE: Wikipedia does not always work...

TRICKS:
- use the Machine Learning Toolbox (https://amitness.com/toolbox/)
- use wordfreq - https://github.com/rspeer/wordfreq
(library for looking up the frequencies of words in English & co)

TODO:
- 2e side bar => How to Add Layout to Streamlit Apps
    - (TB) https://blog.jcharistech.com/2020/10/10/how-to-add-layout-to-streamlit-apps/
- rajouter du joli HTML
    - https://docs.streamlit.io/en/stable/develop_streamlit_components.html#streamlit.components.v1.html
    - https://blog.streamlit.io/introducing-theming/
    - https://github.com/jrieke/traingenerator#adding-new-templates
    # ATTENTION: LA TAILLE DE LA BOITE SERA A AJUSTER
    avec le HTML, changer la couleur des mots clés + avoir la déf. Wikipedia en survol
- rajouter de quoi gérer les collections (Firebase? Sqlite? MongoDB?) & les users/sessions (Streamlit session state?)
- rajouter les références à la fin
- améliorer le résumé et l'extraction de thématiques (topic extraction)
    - Textacy for topic extraction
    - https://colab.research.google.com/drive/12hj292kacP6jqb4FU1Ni72bff3XqyBOW#scrollTo=UEXuhXcJ39CD
- rajouter un soulignage des points importants
    - cf. Annotated Text Component for Streamlit
    - https://github.com/tvst/st-annotated-text
    - pip install st-annotated-text
- rajouter les définitions Wikipedia en survol
    - Tooltips?
- avoir aussi les tables et le reste
- avoir une base de vocabulaire entraînée sur les articles scientifiques pour mieux différencier l'importance des mots
(par TF-IDF - ne pas retenir ni les trop communs, ni les trop rares)
- simplifier le code:
    - en enlevant les imports dont je ne me sers plus
    - en mettant dans d'autres fichiers les fonctions annexes & validées
- comprendre comment ils faisaient le summary (peut-être est-ce très bien)
- rajouter une évaluation ROUGE (cf. Github)
"""

# ******************************************
# IMPORTS
# ******************************************

import numpy as np
import re
import spacy #for summarization
import wikipedia # for definition
from io import StringIO # for file upload, drag & drop

import fitz # for pdfs
import trafilatura # for web content
import base64 # used to get the data for displaying the pdf

import streamlit as st
import streamlit.components.v1 as components # to insert HTML (ex. : to justify the text)

# utils = personal library => contains: topic extraction, summarization
from utils import utils, pdfparser


#st.set_page_config(layout="wide") # uncomment to have wide mode

# ******************************************
# INITIALIZATIONS
# ******************************************

input_text = ''
main_topics = []

def header(url):
     st.markdown(f'<p style="background-color:#0066cc;color:#33ff33;font-size:24px;border-radius:2%;">{url}</p>', unsafe_allow_html=True)

header("BETA VERSION 0.5")
# st.sidebar.markdown('_Author: Pascal Viguié._')

st.title('Summary of scientific articles')


# ******************************************
# SIDEBAR
# ******************************************

st.sidebar.title('Text upload:')

# upload
choice_A = "PDF file"
choice_B = "plain text"
choice_C = "web url"

source = st.sidebar.radio("Choose the kind of text you want to upload:",
                  (choice_A, choice_B, choice_C)
                  )

if source == choice_C:
    web_url = st.sidebar.text_input('Type the URL:')
    downloaded = trafilatura.fetch_url(web_url)
    input_text = trafilatura.extract(downloaded)
    if not input_text:
        input_text = 'Enter a valid web url on the side menu.'

if source == choice_B:
    input_text = st.sidebar.text_area("Write or paste your text in English (between 1,000 and 100,000 characters)",
                              max_chars=100000)
    if len(input_text) < 1000:
        st.sidebar.error('Please enter a text in English of minimum 1,000 characters')

if source == choice_A:

    uploaded_file = st.sidebar.file_uploader('Upload your file here',type=['pdf'])

    # constructs the data variable to show the pdf file
    df_data = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(df_data).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'

    # extract content from pdf file
    if uploaded_file is not None:
        if uploaded_file.name[-3:] == 'pdf':
            document = pdfparser.getPDF(uploaded_file)
            st.write("(pdf file)")
            my_blocks = pdfparser.getConjugatedBlocks(document)
            police = pdfparser.getMostCommon(my_blocks, 'police')
            size = pdfparser.getMostCommon(my_blocks, 'size')
            color = pdfparser.getMostCommon(my_blocks, 'color')

            input_text = ''
            for x in my_blocks:
                if x['police'] == police and x['size'] == size and x['color'] == color:
                    input_text += x['text']
                    input_text += '\n'



# sidebar parameters
left_main_col, right_main_col = st.columns(2)
nb_sentences = left_main_col.slider(label='How many sentences for the summary?', max_value=10, value=5)
nb_topics = right_main_col.slider(label='How many words for the topic extraction?', max_value=20, value=10)


# ******************************************
# AFFICHAGE DES RESULTATS
# ******************************************

with st.container():
    # possible: "warning" instead of "error"
    if nb_sentences == 0:
        left_main_col.error('Please select a number')
    else:
        left_main_col.warning('Your summary will have %i sentences.' % nb_sentences)

    if nb_topics == 0:
        right_main_col.error('Please select a number')
    else:
        right_main_col.warning('We will extract %i main topics.' % nb_topics)


# ***************************************************
# MAIN TOPICS
# ***************************************************
with st.container():
    st.header('Main topics')
    if (len(input_text) > 0) and (nb_topics != 0):
        main_topics = utils.topic_extraction(input_text, nb_topics)
        main_topics = main_topics[:nb_topics]
        output_main_topics = ' - '.join(main_topics).upper()
        st.write('**' + output_main_topics + '**')


# ***************************************************
# SUMMARY
# ***************************************************
with st.container():
    st.header('Summary:')
    if not input_text:
        st.warning('There is no text to analyze yet.')
    else:
        # suppress references (and other content) inside parenthesis
        pattern = r'\([^)]*\)'
        filtered_text = re.sub(pattern, '', input_text)

        # compute the summary
        summary_list = utils.summarize(filtered_text, nb_sentences)

        # output the summary
        summary_len = len(''.join([x for x in summary_list]))
        html_component = "<ul>"
        html_component += ''.join(["<br><li>" + x + "</li>" for x in summary_list])
        html_component += "</ul>"

        components.html(html_component, height = summary_len // 1.5)

        #html_component = utils.prettify_summary(my_summary, main_topics)
        #components.html(html_component, height = len(my_summary) // 2 )


# ***************************************************
# ORIGINAL PDF
# ***************************************************
if source == choice_A:
    with st.container():
        st.header('Original PDF file')
        st.markdown(pdf_display, unsafe_allow_html=True)


# ***************************************************
# ORIGINAL ARTICLE
# ***************************************************
with st.container():
    max_chars_output = 5000
    st.header('Original article (first %i characters):' % max_chars_output)
    output_text = input_text[:max_chars_output]
    output_text = output_text.replace('\n', '<BR><BR>')
    html_component = """<p align="justify">""" + output_text + """</p>"""
    components.html(html_component, height = len(output_text) // 2)
