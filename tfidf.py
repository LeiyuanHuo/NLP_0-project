#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 18:10:01 2022

@author: yangjingjing
"""

for year in ['2010','2011','2012','2018','2019']:
    #read pickle
    import pickle
    p=r'/Users/yangjingjing/Desktop/noun/n_'+year+'.txt'
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
    
    
    from nltk.stem import WordNetLemmatizer
    wnl = WordNetLemmatizer()
    #wnl.lemmatize('dogs')
    
    import enchant
    d = enchant.Dict("en_US")
    #d.check("Hello")
    
    lst1=[]
    lst2=[]
    lst3=[]
    
    for i in cik:
        w=b[i]
        lst1=[]
        for j in w:
            if j.isalpha() and len(j)>1:
    
                if j.isupper() or j.istitle(): #judge if it is a proper noun
                    j=j.lower()
                    if not d.check(j): #append proper nouns even if they cannot be looked up in dic
                        lst1.append(j)
                    else: #append lemmatization if it can be looked up in dic
                        lst1.append(wnl.lemmatize(j,pos='n'))
                elif d.check(j) and (j not in stop_words): #judge if it is a word
                    j=j.lower() #lowering words helps de-duplication
                    lst1.append(wnl.lemmatize(j,pos='n'))
        
        lst2.append(' '.join(lst1))
        lst3.append(lst1)
        
    
    
    
    
        
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    v = TfidfVectorizer(max_df=0.98,min_df=0.02)#remove the top and bottom 2%
    
    v.fit_transform(lst2)
    word_list=v.get_feature_names_out().tolist()#word vector
    
    result_matrix=v.transform(lst2).toarray()#word matrix
    
    
    
    
    
    
    # result_matrix=result_matrix.astype(float)#change from int to float
    
    # #normalize
    # for i in range(len(result_matrix)):
    #       s=result_matrix[i].sum()#compute the sqaure of matrix length
    #       if s>0:
    #           result_matrix[i]=result_matrix[i]/(s**0.5)#let every vector's length be 1
    
    
    
    #cluster
    from sklearn.cluster import KMeans
    import sklearn.metrics
    
    kmeans_model = KMeans(n_clusters=30, random_state=1).fit(result_matrix)
    labels = kmeans_model.labels_
    
    print('Silhouette Coefficient: ',sklearn.metrics.silhouette_score(result_matrix, labels, metric='euclidean'))
    #Evaluate the effect: Silhouette Coefficient ->[-1,1]
    #The smaller Silhouette Coefficient is, the better clustering is.
    
    
    
    #compute comp
    from collections import Counter
    label=[str(x) for x in labels]
    c = Counter(label)
    
    
    #distribution
    import matplotlib.pyplot as plt
    x=[str(n) for n in range(30)]
    y=[c[key] for key in x]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.bar(x=x, height=y)
    ax.set_title('Product_competition_'+year, fontsize=10)
    ax.set_xlabel("labels")
    ax.set_ylabel("#companies")
    
    
    
    count_dic={}
    for i in range(len(cik)):
        count_dic[cik[i]]=c[label[i]]
        
    #save result    
    import pandas as pd
    df=pd.DataFrame()
    df['cik']=list(count_dic.keys())
    df['prod_comp']=list(count_dic.values())
    df.to_csv(r'/Users/yangjingjing/Downloads/product_competition_'+year+'.csv') 