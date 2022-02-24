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


st.set_page_config(layout="wide") # takes the whole width of the screen

# ******************************************
# INITIALIZATIONS
# ******************************************

# SESSION STATE
# if no previous 'input_text', I create a session variable.
input_text  = '' if 'input_text'  not in st.session_state else st.session_state['input_text']
remarks_default_remark = 'I do not have any remark.' if 'remarks_default_remark' not in st.session_state else st.session_state['remarks_default_remark']

st.session_state['input_text'] = input_text
st.session_state['remarks_default_remark'] = remarks_default_remark


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
remarks_message = "Please enter your personal remarks on the document/summary (1,000 char max):"

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
    else:
        # extract content from pdf file
        if uploaded_file.name[-3:] == 'pdf':
            input_text = pdfparser.get_input_text_from_pdf(uploaded_file)
        else:
            st.sidebar.error('This is not a pdf file.')
            input_text = ''


# ***************************************************
# GET THE NB OF SENTENCES & TOPICS
# ***************************************************

# utility function for error/warning messages on left & right columns
def message_for_nb_sentences_or_topics(msg_variable, msg_warning, msg_left):
    # msg_left = True if left column, else False (right column)
    my_col = left_main_col if msg_left else right_main_col
    if msg_variable == 0:
        my_col.error('Please select a number')
    else:
        my_col.warning(msg_warning % msg_variable)



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
        st.session_state['input_text'] = input_text
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
        left_main_col.header('Main topics')
        left_main_col.write('**' + output_main_topics + '**')

        # ******** DISPLAY SUMMARY ********
        left_main_col.header('Summary:')
        if not input_text:
            left_main_col.warning('There is no text to analyze yet.')
        else:
            for sentence in summary_list:
                left_main_col.write('- ' + sentence)

        # ******** PERSONAL REMARKS ********
        left_main_col.header('Personal remarks')
        remark_form = left_main_col.form(key='remark_form')
        remarks_default_remark = remark_form.text_area(remarks_message, value = remarks_default_remark, max_chars=10000)
        remark_submit = remark_form.form_submit_button(label='Update the Summary PDF')

        if remark_submit:
            st.session_state['remarks_message'] = remarks_default_remark

        # ******** SUMMARY PDF ********
        # ToDo: improve the codec part (have it UTF not ASCII-latin1)

        pdfcreator.create_summary_pdf(summary_list, output_main_topics, remarks_default_remark)

        # DISPLAY SUMMARY PDF (+ if checked box, includes the original document)
        # cf. https://blog.jcharistech.com/2020/11/30/how-to-embed-pdf-in-streamlit-apps/

        right_main_col.header('Summary PDF file')
        agree = right_main_col.checkbox('Include original article')

        with fitz.open("Summary.pdf") as doc_summary:
            # if source is NOT a pdf (=> plain text, web page), we create a PDF for the original article
            if source != choice_A:
                pdfcreator.create_pdf(input_text)

            if agree:
                with fitz.open("tempo.pdf") as doc_original:
                    doc_summary.insertPDF(doc_original)

            doc_summary.save("Original_with_summary.pdf")

        # load the pdf file of the summary (option: with the original article)
        with open('Original_with_summary.pdf', 'rb') as summary_file:
            summary_df_data = summary_file.read()
            base64_summary_pdf = base64.b64encode(summary_df_data).decode('latin1')
            summary_pdf_display = F'<embed src="data:application/pdf;base64,{base64_summary_pdf}" width="700" height="1000" type="application/pdf">'

        right_main_col.markdown(summary_pdf_display, unsafe_allow_html=True)
