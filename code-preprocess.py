#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 23:29:10 2022
"""
import os
import re
import time
import html
import pandas as pd
import pickle
import spacy
# import stanza
nlp = spacy.load('en_core_web_sm')


new_data_dir = '/Users/leiyuan/Downloads/1128227-1326428'
os.chdir(new_data_dir)
df_dir = '/Users/leiyuan/Downloads/MFIN7036_project'
new_df = 'data-new-total.csv'


# Note an extra dir before file, change dir first
def clean_corpus(cik_year_list, file_type):
    """
    cik_year_list should be a list of tuples, with the first element of tuple the 10-digit cik string, second 
    element of tuple the 4-digit year. file_type can be either 'business' or 'MD&A'. 
    Return: a corpus list containing all docs, after some clean-up.
    """
    corpus = []
    missing = []
    
    for index, (cik, year) in enumerate(cik_year_list):
        file_dir = cik
        try:
            filename = f'data-{cik}-{year}-10K-{file_type}.txt'
            try:
                with open(os.path.join(file_dir, filename), 'r') as f:
                    section = f.read()
            except UnicodeDecodeError:
                with open(os.path.join(file_dir, filename), encoding='latin-1') as f:
                    section = f.read()
            section = html.unescape(section)
            section = re.sub(r'- \d+? -', '', section)
            section = re.sub(r"\'", r"'", section)
            corpus.append(section)
        except:
            print(f'{cik} do not have {file_type} file at {year}.')
            missing.append(index)
    return corpus, missing

def para_corpus(corpus_list, title_len = 8):
    """
    corpus_list should be a list of documents, with each documents having paragraphs and sub-titles separated by 
    a blankline (\n\n between paragraphs). This function will split corpus into corpus_titles list (with title_len as 
    maximum title length) and corpus_paras list. 
    Return: corpus_titles list and corpus_paras list with same length as corpus_list.
    """
    corpus_titles = []
    corpus_paras = []
    for doc in corpus_list:
        paras = doc.split('\n\n') # get paragraphs
        paras = [para.strip() for para in paras if para.strip()] # discard blank paras, and strip spaces
        paras = [para for para in paras if para[0].isalnum()] # discard page number lines
        corpus_paras.append(paras)
        possible_titles = [paras[0]] # item 1 business (dollars .....)
        possible_titles.extend([para for para in paras[1:] if len(para.split()) <= title_len]) # if one paragraph has fewer than 8 words
        corpus_titles.append(possible_titles)
    assert len(corpus_paras) == len(corpus_titles) and len(corpus_paras) == len(corpus_list)
    return corpus_titles, corpus_paras

def iter_flag(flag_list, title_list, para_list):
    """
    flag_list should be a list of tuples, with first element of tuple index in title_list, second element of tuple
    title in title_list. This function will iterate over the titles in flag_list and take out contents from para_list.
    Return: contents list with all sections extended together (i.e., in one flat list).
    """
    contents = []
    search_field = para_list
    end_idx = 0
#     print(f'Length of the flag_list is {len(flag_list)}.')
    for index, (idx, title) in enumerate(flag_list):
        search_field = search_field[end_idx :] # update paras search field
        start_idx = search_field.index(title) # the 2nd title
        try: # having less than 3 items
            next_title = title_list[idx+1]
            end_idx = search_field.index(next_title)
            section = search_field[start_idx+1 : end_idx] # do not include competition titles
            contents.extend(section)
        except:
            section = search_field[start_idx+1 : ]
            contents.extend(section)
#         print(f'Appending No. {index} of the compete_flag.')
    return contents


def get_nouns(texts):
    """
    texts should be string. This function uses spacy to filter out nouns, proper nouns as organization names.
    Organization names are concatenated together to avoid confusion.
    Return: a list of nouns.
    """
    pos_nouns = ['NOUN', 'PROPN']
    tag_nouns = ['NN', 'NNP', 'NNPS', 'NNS']
    noun_list = []
    org_list = []

    doc = nlp(texts)
    for token in doc:
        
        if (not token.is_stop) and len(token.text) >= 3: # discard stopwords          
            if (token.pos_ in pos_nouns) or (token.tag_ in tag_nouns):  # only keep nouns and proper nouns
                if (token.ent_type_ == 'ORG'): # NER only keep ORG
                    org_list.append(token)
                elif (not token.ent_type_):
                    noun_list.append(token.text)
                else:
                    pass
    # paste ORG together
    ent_Bs = [index for (index, token) in enumerate(org_list) if token.ent_iob_ == 'B']
    org_names = []
    for index, pos in enumerate(ent_Bs):
        if index != (len(ent_Bs) - 1):
            name = ''.join([token.text for token in org_list[pos:ent_Bs[index+1]]])
        else:
            name = ''.join([token.text for token in org_list[pos:]])
        org_names.append(name)
    noun_list.extend(org_names)
    return noun_list


df = pd.read_csv(os.path.join(df_dir, new_df))
df = df.astype({'year': 'str'})
df['cik'] = df['cik'].apply(lambda x: str(x).rjust(10, '0'))

# deal with business and MD&A separately
df_bus = df[df['type'].apply(lambda x: x.startswith('business'))]
df_bus.reset_index(drop=True, inplace=True)
df_mda = df[df['type'].apply(lambda x: x.startswith('MD&A'))]
df_mda.reset_index(drop=True, inplace=True)

# define cik-year pairs for business and MD&A
cik_year_bus = list(zip(df_bus['cik'], df_bus['year']))
business_corpus, bus_missing = clean_corpus(cik_year_bus, 'business')
cik_year_bus = [item for index, item in enumerate(cik_year_bus) if index not in bus_missing]

cik_year_mda = list(zip(df_mda['cik'], df_mda['year']))
mda_corpus, mda_missing = clean_corpus(cik_year_mda, 'MD&A')
cik_year_mda = [item for index, item in enumerate(cik_year_mda) if index not in mda_missing]

print(f'Length of cik_year_bus is {len(cik_year_bus)}, corpus is {len(business_corpus)}')
print(f'Length of cik_year_mda is {len(cik_year_mda)}, corpus is {len(mda_corpus)}')

# get titles and paras
bus_doc_titles, bus_doc_paras = para_corpus(business_corpus)
mda_doc_titles, mda_doc_paras = para_corpus(mda_corpus)
assert len(bus_doc_titles) == len(bus_doc_paras)
assert len(bus_doc_titles) == len(cik_year_bus)
assert len(mda_doc_titles) == len(mda_doc_paras)
assert len(mda_doc_titles) == len(cik_year_mda)
print(f'Length of bus_doc_titles, bus_doc_paras are {len(bus_doc_titles)}')
print(f'Length of mda_doc_titles, mda_doc_paras are {len(mda_doc_titles)}')

## business section (product)
product_contents = []
product_error = []
for index, (doc_titles, doc_paras) in enumerate(zip(bus_doc_titles, bus_doc_paras)):
    item_titles = [title for title in doc_titles if (''.join(title.split())).lower()[0:4] == 'item']
    if len(item_titles) >= 3:
        item_titles = item_titles[0:3]
        start_idx = doc_paras.index(item_titles[0])
        end_idx = doc_paras.index(item_titles[1])
        if 'business' in (''.join(item_titles[0].split())).lower():
            section = doc_paras[start_idx+1 : end_idx] # don't keep item 1. business line; slcing is still a list
        else:
            section = doc_paras[start_idx+2: end_idx] # when item 1 and business are on separate lines
        product_contents.append(section)
    elif (1 <= len(item_titles) <= 2) and ((''.join(item_titles[0].split())).lower()[0:6] in ['item1.', 'item1:', 'item1-']):
        start_idx = doc_paras.index(item_titles[0])
        if 'business' in (''.join(item_titles[0].split())).lower():
            section = doc_paras[start_idx+1 :] # don't keep item 1. business line
        else:
            section = doc_paras[start_idx+2 :] 
        product_contents.append(section)
    else:
        cik, year = cik_year_bus[index]
        product_error.append(index)    
        # print(f'Do not find 3 items for {cik} at {year}.')
if product_error:
    cik_year_bus = [item for index, item in enumerate(cik_year_bus) if index not in product_error]
else:
    pass
assert len(product_contents) == len(cik_year_bus) 
print(f'Discarding samples with product errors, the length of cik_year_bus/product_contents is {len(product_contents)}')

# get nouns from product section
start = time.time()
print('Start getting nouns from product_contents.')

n_dict_new = {key: {} for key in [str(x) for x in range(2010, 2023)]} # DF_DICT
for (cik, year), content in zip(cik_year_bus, product_contents):
    content = '\n'.join(content) # content is a list of texts, join them
    nouns = get_nouns(content)
    n_dict_new[year].update({cik: nouns})
end = time.time()
print(f'It took {(end-start)/60:.2f} minutes to finish {len(product_contents)} product contents.')
print(f'Dictionary has {len(n_dict_new["2010"].keys())} in 2010, {len(n_dict_new["2011"].keys())} in 2011, +\
      {len(n_dict_new["2012"].keys())} in 2012, {len(n_dict_new["2013"].keys())} in 2013, +\
      {len(n_dict_new["2014"].keys())} in 2014, {len(n_dict_new["2015"].keys())} in 2015, +\
      {len(n_dict_new["2016"].keys())} in 2016, {len(n_dict_new["2017"].keys())} in 2017, +\
      {len(n_dict_new["2018"].keys())} in 2018, {len(n_dict_new["2019"].keys())} in 2019, +\
      {len(n_dict_new["2020"].keys())} in 2010, {len(n_dict_new["2021"].keys())} in 2021, +\
      {len(n_dict_new["2022"].keys())} in 2022')

with open(os.path.join(df_dir, 'nouns_new.pickle'), 'wb') as f: # DF_DICT
    pickle.dump(n_dict_new, f, pickle.HIGHEST_PROTOCOL)
    
## MDA section (competition mentions)
mda_contents = []
mda_error = []
for index, (doc_titles, doc_paras) in enumerate(zip(mda_doc_titles, mda_doc_paras)):
    item_titles = [title for title in doc_titles if (''.join(title.split())).lower()[0:4] == 'item']
    if len(item_titles) >= 2:
        item_titles = item_titles[0:2]
        start_idx = doc_paras.index(item_titles[0])
        end_idx = doc_paras.index(item_titles[1])
        if 'discussion' in (''.join(item_titles[0].split())).lower():
            section = doc_paras[start_idx+1 : end_idx] # don't keep item 1. business line
        else:
            section = doc_paras[start_idx+2: end_idx] # when item 1 and business are on separate lines
        mda_contents.append(section)
    elif (len(item_titles) == 1) and (''.join(item_titles[0].split())).lower()[0:6] in ['item7.', 'item7:', 'item7-']:
        start_idx = doc_paras.index(item_titles[0])
        if 'discussion' in (''.join(item_titles[0].split())).lower():
            section = doc_paras[start_idx+1 : ] # don't keep item 1. business line
        else:
            section = doc_paras[start_idx+2 : ] # when item 1 and business are on separate lines
        mda_contents.append(section)
    else:
        mda_error.append(index)
#         cik, year = cik_year_mda[index]
#         print(f'Do not find 2 items for {cik} at {year}.')

## deal with errors in product section
if mda_error:
    cik_year_mda = [item for index, item in enumerate(cik_year_mda) if index not in mda_error]
else:
    pass
assert len(mda_contents) == len(cik_year_mda)
print(f'Discarding samples with MD&A errors, the length of cik_year_mda/comp_contents is {len(mda_contents)}')   

# count competition-related words
start = time.time()
print('Start getting competition words from mda_contents.')

c_dict_new = {key: {} for key in [str(x) for x in range(2010, 2023)]} # DF_DICT
for (cik, year), content in zip(cik_year_mda, mda_contents):
    content = '\n'.join(content)
    try:
        doc = nlp(content)
    except ValueError:
        nlp.max_length = len(content)
    total = len(doc)
    if total <= 100:
        pass
    else:
        count = 0
        for token in doc:
            if (token.lemma_ == 'competition') or (token.lemma_ == 'competitor') or (token.lemma_ == 'compete'):
                count += 1
        counter = [count, total]
        c_dict_new[year].update({cik: counter})
#     print(f'MD&A has total word count {counter[1]}, competition-related word count {counter[0]}.')
end = time.time()
print(f'It took {(end-start)/60} minutes to finish {len(mda_contents)} MD&A contents.')
print(f'Dictionary has {len(c_dict_new["2010"].keys())} in 2010, {len(c_dict_new["2011"].keys())} in 2011, +\
      {len(c_dict_new["2012"].keys())} in 2012, {len(c_dict_new["2013"].keys())} in 2013, +\
      {len(c_dict_new["2014"].keys())} in 2014, {len(c_dict_new["2015"].keys())} in 2015, +\
      {len(c_dict_new["2016"].keys())} in 2016, {len(c_dict_new["2017"].keys())} in 2017, +\
      {len(c_dict_new["2018"].keys())} in 2018, {len(c_dict_new["2019"].keys())} in 2019, +\
      {len(c_dict_new["2020"].keys())} in 2010, {len(c_dict_new["2021"].keys())} in 2021, +\
      {len(c_dict_new["2022"].keys())} in 2022')

with open(os.path.join(df_dir, 'counts_new.pickle'), 'wb') as f: # DF_DICT
    pickle.dump(c_dict_new, f, pickle.HIGHEST_PROTOCOL)






































