# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 14:22:55 2022

"""
import os
import pandas as pd
from sec_api import QueryApi
from sec_api import ExtractorApi
from joblib import Parallel, delayed


def text_create(path,name,msg):
    full_path = os.path.join(path, name)
    with open(full_path, 'a') as file:
        file.write(msg)   
      
def extract_10K(cik): 
    year_list = [i+2010 for i in range(11)]
    queryApi = QueryApi(api_key="f7fd8d3a3797e6d8f97e2a94687bd2ac1ac29057d7ecb1f596e97f158a78a4ac")
    extractorApi = ExtractorApi("f7fd8d3a3797e6d8f97e2a94687bd2ac1ac29057d7ecb1f596e97f158a78a4ac")
    c = cik
    
    for j in year_list:
            
            query = {
              "query": { "query_string": { 
                  "query": "cik:"+str(c)+" AND filedAt:{"+str(j)+"-01-01 TO "+str(j)+"-12-31} AND formType:\"10-K\"" 
                } },
              "from": "0",
              "size": "3",
              "sort": [{ "filedAt": { "order": "desc" } }]
            }
    
            filings = queryApi.get_filings(query)
            
            if filings['total']['value'] == 0:
                print(str(j)+':没有对应文件')
                pass
            
            else:
                doc_link = filings['filings'][0]['linkToFilingDetails']
                print(str(j)+':'+ doc_link)
                
                extractorApi = ExtractorApi("f7fd8d3a3797e6d8f97e2a94687bd2ac1ac29057d7ecb1f596e97f158a78a4ac")
                filing_url = doc_link
    
                sec_1 = extractorApi.get_section(filing_url, "1", "text")
                sec_2 = extractorApi.get_section(filing_url, "1A", "text")
                sec_3 = extractorApi.get_section(filing_url, "1B", "text")
    
                sec_bus = sec_1+'\n'+sec_2+'\n'+sec_3
                
                sec_4 = extractorApi.get_section(filing_url, "7", "text")
                sec_5 = extractorApi.get_section(filing_url, "7A", "text")
                
                sec_mda = sec_4+'\n'+sec_5
    
                text_create(business_dir, f"data-{str(c).rjust(10,'0')}-{str(j)}-10K-business.txt", sec_bus)
                text_create(mda_dir, f"data-{str(c).rjust(10,'0')}-{str(j)}-10K-MD&A.txt", sec_mda)
    
if os.getcwd() == '/Users/leiyuan/Downloads/MFIN7036_project':
    pass
else:
    os.chdir('/Users/leiyuan/Downloads/MFIN7036_project') 

business_dir = 'data-txts-business'
mda_dir = 'data-txts-MD&A'
df = pd.read_csv('data-cik-division/cik_count2654.csv')
cik =list(df['cik'])
for i in range(2627, 2654, 100):
    cik_group = cik[i : i+100]                
    Parallel(n_jobs=2, verbose=100)(delayed(extract_10K)(cik) for cik in cik_group)






