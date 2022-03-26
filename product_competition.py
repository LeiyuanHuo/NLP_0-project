#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 12:42:45 2022

@author: yangjingjing
"""

import time
start=time.time()


#read pickle
import pickle
p=r'/Users/yangjingjing/Desktop/noun/n_2019.txt'
with open (p,'rb') as file:
    b = pickle.load(file)


#remove empty list
for key in list(b.keys()):
    if not b[key]:
        b.pop(key)

cik=list(b.keys())




#matrix
from nltk.corpus import stopwords
stop_words=stopwords.words('english')
stop_words.extend(['item','general','business','overview'])
#from nltk.stem import PorterStemmer
#ps = PorterStemmer()

from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
#wnl.lemmatize('dogs')

import enchant
d = enchant.Dict("en_US")
#d.check("Hello")

lst1=[]
lst2=[]


for i in cik:
    w=b[i]
    lst1=[]
    for j in w:
        if j.isalpha() and len(j)>1:

            if j.isupper(): #judge if it is a proper noun
                j=j.lower()
                if not d.check(j): #append proper nouns even if they cannot be looked up in dic
                    lst1.append(j)
                else: #append lemmatization if it can be looked up in dic
                    lst1.append(wnl.lemmatize(j,pos='n'))
            elif d.check(j) and (j not in stop_words): #judge if it is a word
                j=j.lower() #lowering words helps de-duplication
                lst1.append(wnl.lemmatize(j,pos='n'))
    lst1=list(set(lst1))
    lst2.append(' '.join(lst1))
    




    
from sklearn.feature_extraction.text import CountVectorizer
v = CountVectorizer(stop_words='english',max_df=0.98,min_df=0.02)#remove the top and bottom 10%
v.fit_transform(lst2)
word_list=v.get_feature_names_out().tolist()#word vector

result_matrix=v.transform(lst2).toarray()#word matrix
result_matrix=result_matrix.astype(float)#change from int to float

#normalize
for i in range(len(result_matrix)):
    s=result_matrix[i].sum()#compute the sqaure of matrix length
    if s>0:
        result_matrix[i]=result_matrix[i]/(s**0.5)#let every vector's length be 1

#initialize
import numpy as np
ll=len(result_matrix)
np1 = np.arange(ll*ll)
cos = np1.reshape(ll,ll)
for i in range(ll-1):
    cos[i][i]=1
    for j in range(i+1,ll):
        cos[i][j]=np.dot(result_matrix[i], result_matrix[j].T)
        cos[j][i]=cos[i][j]


l=len(cik)
cik1=[]
for i in range(l):
    cik1.append([])

for i in range(l):
    cik1[i].append(cik[i])#at first assign every co. in one industry


target_ind_num=30
for t in range(l-target_ind_num):
    print(t)
    #initialize
    st=[]
    l0=len(cik1)
    
    #compute smilarity between every two industries
    for n in range(l0-1):
        for i in range(n+1,l0):
            inf=[]
            su=0
            l1=len(cik1[n])
            l2=len(cik1[i])
            for j in range(l1):
                for k in range(l2):
                    index1=cik.index(cik1[n][j])
                    index2=cik.index(cik1[i][k])
                    cos_v=cos[index1][index2]/(l1*l2)#similarity between two co.
                    su+=cos_v
            inf.append(n)    
            inf.append(i)
            inf.append(su)
            st.append(inf)
    
    st1=sorted(st,key=lambda x:x[2],reverse=True)#sort similarity values, pick the largest    
    combine=cik1[st1[0][0]]+cik1[st1[0][1]]
    c1=cik1[st1[0][0]]
    c2=cik1[st1[0][1]]
    #remove the old two industries
    cik1.remove(c1)
    cik1.remove(c2)   
    cik1.append(combine)#add the new industry


#compute how many competitors every co. has    
industry={}
for q in range(len(cik1)):
    comp_num=len(cik1[q])
    for e in cik1[q]:
        industry[e]=comp_num



#save the result    
import pandas as pd
df=pd.DataFrame()
df['cik']=list(industry.keys())   
df['product_competition']=list(industry.values()) 
df.to_csv(r'/Users/yangjingjing/Downloads/product_competition_2019.csv')    
    
    
num=[]
for i in cik1:
    num.append(len(i))
    

from collections import Counter

c = Counter(num)


count_dic={}
for i in list(c.keys()):
    if i <=50:
        count_dic[i]=c[i]/target_ind_num
count_dic['>50']=sum([c[x] for x in list(c.keys()) if x>50])/target_ind_num

import matplotlib.pyplot as plt

import numpy as np

x=[str(x) for x in count_dic.keys()]

y=list(count_dic.values())

fig, ax = plt.subplots(figsize=(10, 7))
ax.bar(x=x, height=y)
ax.set_title("Product_competition", fontsize=10)
ax.set_xlabel("labels")
ax.set_ylabel("#companies")    
    
print((time.time()-start)/60)    
    