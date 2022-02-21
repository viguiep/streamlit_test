# -*- coding: utf-8 -*-


# ******************************************
# IMPORTS
# ******************************************

import numpy as np
import re
import spacy #for summarization
import wikipedia # for definition
from io import StringIO # for file upload, drag & drop

import fitz # for reading PDFs
import trafilatura # for web content
import base64 # used to get the data for displaying the PDF

import streamlit as st
import streamlit.components.v1 as components # to insert HTML (ex. : to justify the text)

# utils = personal library => contains: topic extraction, summarization
from utils import utils, pdfparser, pdfcreator




# ******************************************
# INITIALIZATIONS
# ******************************************

input_text = ''
pdf_display = ''
main_topics = []
output_main_topics = ''

# sidebar variables (upload)
choice_A = "PDF file"
choice_B = "plain text"
choice_C = "web url"
message_A = 'Type the URL:'
message_B = 'Write or paste your text in English (between 1,000 and 100,000 characters)'
message_C = 'Upload your file here'
sidebar_title = 'Text upload:'
sidebar_radio_text = 'Choose the kind of text you want to upload:'
sidebar_CHOICES = (choice_A, choice_B, choice_C)

def header(url):
     st.markdown(f'<p style="background-color:#0066cc;color:#33ff33;font-size:24px;border-radius:2%;">{url}</p>', unsafe_allow_html=True)

# ******************************************
# SIDEBAR (upload)
# ******************************************

st.sidebar.title(sidebar_title)
source = st.sidebar.radio(sidebar_radio_text, sidebar_CHOICES)

if source == choice_C:
    # Declare a form and call methods directly on the returned object
    PV_form = st.sidebar.form(key='my_form')
    web_url = PV_form.text_input(label=message_A)
    PV_submit = PV_form.form_submit_button(label='Submit')

    if PV_submit:
        downloaded = trafilatura.fetch_url(web_url)
        input_text = trafilatura.extract(downloaded)
    else:
        input_text = ''
        st.sidebar.error('Enter a valid web url on the side menu.')

if source == choice_B:
    # Declare a form and call methods directly on the returned object
    PV_form = st.sidebar.form(key='my_form')
    input_text = PV_form.text_area(message_B, max_chars=100000)
    PV_submit = PV_form.form_submit_button(label='Submit')

    if len(input_text) < 1000:
        st.sidebar.error('Please enter a text in English of minimum 1,000 characters')

if source == choice_A:

    uploaded_file = st.sidebar.file_uploader(message_C,type=['pdf'])

    if uploaded_file is None:
        st.sidebar.error('Upload a pdf file.')

    # extract content from pdf file
    if uploaded_file is not None:

        # constructs the data variable to show the pdf file
        df_data = uploaded_file.getvalue()
        base64_pdf = base64.b64encode(df_data).decode('utf-8')
        pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'


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

# ***************************************************
# GET THE NB OF SENTENCES & TOPICS
# ***************************************************

def message_for_nb_sentences_or_topics(msg_variable, msg_warning, msg_left):
    # msg_left = True if left column, else False (right column)
    my_col = left_main_col if msg_left else right_main_col
    if msg_variable == 0:
        my_col.error('Please select a number')
    else:
        my_col.warning(msg_warning % msg_variable)


# ***************************************************
# SUMMARY & TOPICS
# ***************************************************


# ******** ORIGINAL ARTICLE ********
max_chars_output = 5000
output_text = input_text[:max_chars_output]
output_text = output_text.replace('\n', '<BR><BR>')
html_article = """<p align="justify">""" + output_text + """</p>"""


# ******************************************
# DISPLAY RESULTS
# ******************************************

with st.container():

    # Header & Main title
    header("BETA VERSION 0.5")
    st.title('Summary of scientific articles')
    # st.sidebar.markdown('_Author: Pascal Viguié._')

    # 2 columns to choose the nb of sentences (for the summary) & the nb of topics
    left_main_col, right_main_col = st.columns(2)
    nb_sentences = left_main_col.slider(label='How many sentences for the summary?', max_value=10, value=5)
    nb_topics = right_main_col.slider(label='How many words for the topic extraction?', max_value=20, value=10)

    message_for_nb_sentences_or_topics(nb_sentences, 'Your summary will have %i sentences.', msg_left=True)
    message_for_nb_sentences_or_topics(nb_topics, 'We will extract %i main topics.', msg_left=False)


    if input_text:
        # ******** SUMMARY ********
        # suppress references (and other content) inside parenthesis
        pattern = r'\([^)]*\)'
        filtered_text = re.sub(pattern, '', input_text)

        # compute the summary
        summary_list = utils.summarize(filtered_text, nb_sentences)
        summary_len = len(''.join([x for x in summary_list]))

        # ******** MAIN TOPICS ********
        output_main_topics = ''
        if (len(input_text) > 0) and (nb_topics != 0):
            main_topics = utils.topic_extraction(input_text, nb_topics)
            main_topics = main_topics[:nb_topics]
            output_main_topics = ' - '.join(main_topics).upper()

        # ******** DISPLAY MAIN TOPICS ********
        st.header('Main topics')
        st.write('**' + output_main_topics + '**')

        # ******** DISPLAY SUMMARY ********
        st.header('Summary:')
        if not input_text:
            st.warning('There is no text to analyze yet.')
        else:
            for sentence in summary_list:
                st.write('- '+sentence)

        # ******** SUMMARY PDF ********
        # Improve the codec part (have it UTF not ASCII-latin1)

        pdfcreator.create_summary_pdf(summary_list, output_main_topics)

        # DISPLAY SUMMARY PDF
        # cf. https://blog.jcharistech.com/2020/11/30/how-to-embed-pdf-in-streamlit-apps/
        with open('Summary.pdf', 'rb') as summary_file:
            summary_df_data = summary_file.read()
            base64_summary_pdf = base64.b64encode(summary_df_data).decode('latin1')
            summary_pdf_display = F'<embed src="data:application/pdf;base64,{base64_summary_pdf}" width="700" height="1000" type="application/pdf">'
            st.header('Summary PDF file')
            st.markdown(summary_pdf_display, unsafe_allow_html=True)


    # ******** ORIGINAL PDF ********
    if source == choice_A:
        st.header('Original PDF file')
        st.markdown(pdf_display, unsafe_allow_html=True)


    # ******** ORIGINAL ARTICLE ********
    st.header('Original article (first %i characters):' % max_chars_output)
    components.html(html_article, height = len(output_text) // 2)
