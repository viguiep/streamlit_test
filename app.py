# Core Pkgs
import streamlit as st
import os
from PIL import Image

# NLP Pkgs
import spacy
import nltk
import spacy_streamlit
from gensim.summarization.summarizer import summarize
from textblob import TextBlob

nlp = spacy.load('en_core_web_sm')
nltk.download('punkt')

from nltk.tokenize import sent_tokenize

# Function to take in dictionary of entities, type of entity, and returns specific entities of specific type
def entRecognizer(entDict, typeEnt):
    entList = [ent for ent in entDict if entDict[ent] == typeEnt]
    return entList

def main():
    """A Simple NLP app with Spacy-Streamlit"""
    st.title("Spacy-Streamlit NLP App")
    #our_image = Image.open(os.path.join('SpaCy_logo.svg.png'))
    #st.image(our_image)
    menu = ["Tokenization","NER", "Sentiment analysis", "Entity extraction", "Text summarization"]
    choice = st.sidebar.selectbox("Menu",menu)
    if choice == "Tokenization":
        st.subheader("Tokenization")
        raw_text = st.text_area("Your Text","Enter Text Here")
        doc = nlp(raw_text)
        if st.button("Tokenize"):
            spacy_streamlit.visualize_tokens(doc,attrs=['text','pos_','dep_','ent_type_'])

    elif choice == "NER":
        st.subheader("Named Entity Recognition")
        raw_text = st.text_area("Your Text","Enter Text Here")
        doc = nlp(raw_text)
        spacy_streamlit.visualize_ner(doc,labels=nlp.get_pipe('ner').labels)

    elif choice == "Sentiment analysis":
        st.subheader("Sentiment analysis")
        raw_text = st.text_area("Your Text","Enter Text Here")
	
        # Creating graph for sentiment across each sentence in the text inputted
        sents = sent_tokenize(raw_text)
        entireText = TextBlob(raw_text)
        sentScores = []
        for sent in sents:
            text = TextBlob(sent)
            score = text.sentiment[0]
            sentScores.append(score)

        # Plotting sentiment scores per sentencein line graph
        st.line_chart(sentScores)

        # Polarity and Subjectivity of the entire text inputted
        sentimentTotal = entireText.sentiment
        st.write("The sentiment of the overall text below.")
        st.write(sentimentTotal)
	
    elif choice == "Entity extraction":
        st.subheader("Entity extraction")
        raw_text = st.text_area("Your Text","Enter Text Here")
        doc = nlp(raw_text)
	
        # Getting Entity and type of Entity
        entities = []
        entityLabels = []
        for ent in doc.ents:
            entities.append(ent.text)
            entityLabels.append(ent.label_)
        entDict = dict(zip(entities, entityLabels)) #Creating dictionary with entity and entity types

        # Using function to create lists of entities of each type
        entOrg = entRecognizer(entDict, "ORG")
        entCardinal = entRecognizer(entDict, "CARDINAL")
        entPerson = entRecognizer(entDict, "PERSON")
        entDate = entRecognizer(entDict, "DATE")
        entGPE = entRecognizer(entDict, "GPE")

        # Displaying entities of each type
        st.write("Organization Entities: " + str(entOrg))
        st.write("Cardinal Entities: " + str(entCardinal))
        st.write("Personal Entities: " + str(entPerson))
        st.write("Date Entities: " + str(entDate))
        st.write("GPE Entities: " + str(entGPE))

    elif choice == "Text summarization":
        st.subheader("Text summarization")
        raw_text = st.text_area("Your Text","Enter Text Here")
	summWords = summarize(raw_text)
        st.subheader("Summary")
        st.write(summWords)

if __name__ == '__main__':
	main()
