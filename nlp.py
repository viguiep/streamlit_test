# -*- coding: utf-8 -*-
# https://github.com/schneeboat/streamlit_nlp
# https://share.streamlit.io/schneeboat/streamlit_nlp/main/nlp.py

# https://blog.streamlit.io/
# https://towardsdatascience.com/intermediate-streamlit-d5a1381daa65
# RASA - https://blog.streamlit.io/rasalit/
# persistent data - https://blog.streamlit.io/streamlit-firestore/

"""
RAJOUTER LE GIT EXCLUDE

BIG ISSUE: Wikipedia does not always work...

TRICKS:
- use the Machine Learning Toolbox (https://amitness.com/toolbox/)
- use wordfreq - https://github.com/rspeer/wordfreq
(library for looking up the frequencies of words in English & co)

TODO:
- nb of words of topic extraction = do not change with the slider
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
- rajouter de quoi retrouver le texte original
- améliorer le résumé et l'extraction de thématiques (topic extraction)
    - Textacy for topic extraction
    - https://colab.research.google.com/drive/12hj292kacP6jqb4FU1Ni72bff3XqyBOW#scrollTo=UEXuhXcJ39CD
- mettre le résumé sous la forme de bullet points
- rajouter un soulignage des points importants
    - cf. Annotated Text Component for Streamlit
    - https://github.com/tvst/st-annotated-text
    - pip install st-annotated-text
- rajouter les définitions Wikipedia en survol
    - Tooltips?
- rajouter le parsing du pdf
- parser aussi les property
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
import spacy #for summarization
import wikipedia # for definition
from io import StringIO # for file upload, drag & drop

import fitz # for pdfs

import streamlit as st
import streamlit.components.v1 as components # to insert HTML (ex. : to justify the text)



# utils = personal library => contains: topic extraction, summarization
from utils import utils #, pdfparser


#st.set_page_config(layout="wide") # uncomment to have wide mode

# ******************************************
# INITIALIZATIONS
# ******************************************

input_text = ''

st.title('Summary of scientific articles')


# ******************************************
# SIDEBAR
# ******************************************

st.sidebar.title('Text upload:')

# upload
source = st.sidebar.radio("Choose how to upload your text:",
                  ("I want to input some text", "I want to upload a file")
                  )
if source == 'I want to input some text':
    input_text = st.sidebar.text_area("Write or paste your text in English (between 1,000 and 100,000 characters)",
                              max_chars=100000)
    if len(input_text) < 1000:
        st.error('Please enter a text in English of minimum 1,000 characters')

if source == 'I want to upload a file':
    uploaded_file = st.sidebar.file_uploader('Upload your file here',type=['txt'])
    if uploaded_file is not None:
        if uploaded_file.name[-3:] == 'txt':
            input_text = ''
            st.write("(text file)")
            with st.spinner('Processing...'):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                input_text = stringio.read()
                if len(input_text) < 1000 or len(input_text) > 10000:
                    st.error('Please upload a file between 1,000 and 10,000 characters')
        elif uploaded_file.name[-3:] == 'pdf':
            st.write("(pdf file)")
            input_text = ''
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as document:
                for page in document:
                    input_text+= page.getText()


# sidebar parameters
sample_col, upload_col = st.beta_columns(2)
input_top_n = sample_col.slider(label='How many sentences for the summary?', max_value=10, value=5)
input_num = upload_col.slider(label='How many words for the topic extraction?', max_value=20, value=10)



# ******************************************
# AFFICHAGE DES RESULTATS
# ******************************************

with st.beta_container():
    st.header('Main topics')
    if not input_text or not input_num:
     st.warning('Please input the text AND select a number :)')
    if input_num == 0:
     st.warning('Please select a number')
    if (len(input_text) > 0) and (input_num != 0):
        main_topics = utils.topic_extraction(input_text, input_num)
        output_main_topics = ' - '.join(main_topics[:input_num])
        st.write(output_main_topics)

with st.beta_container():
    st.sidebar.header('Definitions for main topics:')
    nb_sentences = 1
    for i, topic in enumerate(main_topics):
        st.sidebar.markdown('**'+topic.upper()+'**')
        try:
            definition = wikipedia.summary(topic, sentences = nb_sentences)
            st.sidebar.write(definition)
        except:
            st.sidebar.write('No definition found.')


with st.beta_container():
    st.header('Summary:')
    if not input_text:
        st.warning('Please input the text you want to analyze :)')
    else:
        my_summary = utils.summarize(input_text, input_top_n)
        html_component = utils.prettify_summary(my_summary, main_topics)
        components.html(html_component, height = len(my_summary) // 2 )

with st.beta_container():
    st.header('Original article:')
    html_component = """<p align="justify">""" + input_text + """</p>"""
    components.html(html_component, height = len(input_text) // 2)
