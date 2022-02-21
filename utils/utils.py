"""
Utility file: contains
- topic extraction (TO IMPROVE: use tf-idf with the wordfreq library in English + bigrams)
- summarization (TO IMPROVE: suppress if subject = article, suppress enumeration cf. Hearst patterns...)
- TO ADD: PDF PARSING
"""

# for topic extraction
from collections import defaultdict

# for summarization
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation

nlp = spacy.load('en_core_web_md')
extra_words = list(STOP_WORDS) + list(punctuation) + ['\n']

# ***************************************************
# TOPIC EXTRACTION
# ***************************************************
def topic_extraction(input_text, input_num):
    docx = nlp(input_text)

    my_dict = defaultdict(int)

    for ent in docx.ents:
      my_ent = ent.text.lower()
      my_dict[my_ent] += 1

    sorted_tuple = sorted(my_dict.items(), key=lambda item: -item[1])
    main_topics = [x for x,n in sorted_tuple]

    return main_topics


# ***************************************************
# SUMMARIZATION
# ***************************************************
def summarize(input_text, top_n=1):
  docx              = nlp(input_text)
  vocabulary        = [ word.text.lower() for word in docx]

  # Remove extra words and get word count
  word_count        = { word: vocabulary.count(word)
                          for word in vocabulary
                          if ( word not in extra_words and word.isalpha() )}

  # Sentence Strength
  sent_strength     = { sent:sum(word_count[word.text.lower()]
                          for word in sent
                          if word.text.lower() in word_count) / len(sent)
                                for sent in docx.sents}
  for sent in sent_strength:
      for token in sent:
          if 'subj' in token.dep_:
              if ('PR' in token.tag_) or ('DT' in token.tag_):
                  sent_strength[sent] /= 4
                  break
              for x in token.children:
                  if ('DT' in x.tag_):
                      sent_strength[sent] /= 4
                      break


  # Extracted sentences in chronological order
  top_sentences     = sorted(sent_strength.values(), reverse=True)
  top_sent          = top_sentences[:top_n]
  summary_list      = [sent.text.lstrip(chr(10)) for sent,strength in sent_strength.items() if strength in top_sent]
  #summary_text      = "".join(x.text for x in summary)
  # sentence.lstrip(chr(10)) => we suppress the line feed that starts some sentences

  return summary_list


# ***************************************************
# PRETTIFY SUMMARY (HTML tricks)
# ***************************************************
def prettify_summary(my_summary, main_topics, nb_sentences = 1):
    # trick to justify the text
    # https://docs.streamlit.io/en/stable/develop_streamlit_components.html#streamlit.components.v1.html
    html_component = """<div style="text-align: justify">"""
    html_component += """<ul>"""

    # list of summary sentences
    docx = nlp(my_summary)
    for sentence in docx.sents:
        if len(sentence) > 0:
            deb = """<span style="color:black">"""
            fin = """</span style="color:black">"""
            my_sentence_formatted = deb + sentence.text + fin
            #
            # faire plus joli (couleur de fond) & plus rapide (React)...
            # METTRE LES DEFINITIONS DANS UN DICT AVEC LES TOPICS
            # nb_sentences = pas forcément défini là...
            #
            for topic in main_topics:
                # if the topic is found in the sentence
                my_index = my_sentence_formatted.lower().find(topic.lower())
                if my_index != -1:
                    new_sentence_formatted = my_sentence_formatted[:my_index]
                    new_sentence_formatted += deb
                    new_sentence_formatted += my_sentence_formatted[my_index:my_index+len(topic)]
                    new_sentence_formatted += fin + """</mark>"""
                    new_sentence_formatted += my_sentence_formatted[my_index+len(topic):]
                    my_sentence_formatted = new_sentence_formatted
            html_component += """<li>"""
            html_component += my_sentence_formatted
            html_component += """</li>"""
            html_component += """</br>"""
    html_component += """</ul>"""
    html_component += """</div>"""

    return html_component
