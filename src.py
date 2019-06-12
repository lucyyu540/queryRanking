import stop_list
import re
import math
import string
import nltk
from nltk import word_tokenize
from nltk.tokenize import TreebankWordTokenizer
from collections import OrderedDict
tokenizer = TreebankWordTokenizer()

stopWords = stop_list.closed_class_stop_words
queryFile = "cran.qry"
articleFile = "cran.all.1400"

#Helper A
def cleanUp(tokenized): #takes  list returns clean list
    cleanToken = tokenized[:]
    for token in tokenized:
        if token in stopWords:#is in the list of stop words
            cleanToken.remove(token)
        elif re.search(r'[^\w\s]', token) != None:#it is a punctuation
            cleanToken.remove(token)
    return cleanToken
#Helper B
def getFrequency(words): # takes list returns dictionary
    frequencyOfWords = {}
    for word in words:
        if word in frequencyOfWords:
            frequencyOfWords[word] += 1
        else:
            frequencyOfWords[word] = 1
    return frequencyOfWords
#Helper C
def cosineSimilarity(A,B): #takes 2 dicts, returns float
    numerator = 0
    a2Sum = 0
    b2Sum = 0
    for aWord in A:
        for bWord in B:
            if aWord == bWord:#words overlap words
                numerator += A[aWord]*B[aWord]
                a2Sum += A[aWord]*A[aWord]
                b2Sum += B[aWord]*B[aWord]
    denumerator = math.sqrt(a2Sum*b2Sum)
    if denumerator == 0:
        return 0
    return float(numerator)/denumerator
#1 takes a file and organizes individually {sect1:{word:n, ...}, sect2:{},... }
def tokenize(file, TF): #takes string and dict
    fp = open(file, 'r')
    entire = fp.read().split("\n")
    end = len(entire)
    count = 1
    nextLineIsContent = False
    s = ""
    ind = 0
    for line in entire:
        if line[:2] == '.I' or ind == end - 1 and s != "" :
            token = tokenizer.tokenize(s)
            cleanToken = cleanUp(token)
            TF[count] = getFrequency(cleanToken)
            s = "" #reset
            count += 1
            nextLineIsContnet = False
        elif nextLineIsContent:
            s += " "+ line
        elif line[:2] == '.W':
            nextLineIsContent = True
        ind += 0
    fp.close()
#2 organize entire file {word:n, word: n, ...}
def getDocNumForWord(TF, C): #takes 2 dicts
    for doc in TF:
        for word in TF[doc]:
            if word not in C:
                C[word] = 1
            else:
                C[word] += 1

#3 get IDF&TFIDF values individually {doc1: {word:idf,...}, dpc2:{},...}
def getVector(TF, IDF, TFIDF, C, N): #takes 4 dicts, 1 int
    for doc in TF:
        idfV = {}
        tfidfV = {}
        for word in TF[doc]:
            idf = math.log10(N/float(C[word]))
            idfV[word] = idf
            tfidfV[word] = idf*float(TF[doc][word])
        IDF[doc] = idfV
        TFIDF[doc] = tfidfV
      

"""
QUERIES
Lines beginning with .I are ids for the queries (001 to 365)

Lines following .W are the queries
"""
queryTF = {}
queryIDF = {}
queryTFIDF = {}
queriesForWord = {}
queryNum = 225

tokenize(queryFile, queryTF)  
getDocNumForWord(queryTF, queriesForWord)
getVector(queryTF, queryIDF, queryTFIDF, queriesForWord, queryNum)

"""
ARTICLES
Lines beginning with .I are ids for the abstracts

Lines following .T are titles

Lines following .A are authors

Lines following .B are some sort of bibliographic notation

Lines following .W are the abstracts
"""
articleTF = {}
articleIDF = {}
articleTFIDF = {}
articlesForWord = {}
articleNum = 1400

tokenize(articleFile, articleTF)
getDocNumForWord(articleTF, articlesForWord)
getVector(articleTF, articleIDF, articleTFIDF, articlesForWord, articleNum)


#4 get cos similarity btw a query and all articles and rank
def getArticleRanking(qTFIDF, aTFIDF, qAS): #3 dicts 
    for q in qTFIDF:
        qVector = qTFIDF[q]
        qAS[q] = {} #create new dictionary for each query
        for a in aTFIDF: # for all articles
            aVector = aTFIDF[a]
            score = cosineSimilarity(qVector, aVector)
            #print("for query: ", q, " & art: " , a, "SCORE: ", score)
            qAS[q][a] = score


#5 output article ranks of each queries into text file
def printSortedqAS( qAS ):
    outputFile = open('output.txt', 'w')
    for q in qAS: #q = 1-225
        rank = qAS[q]
        sortedRank = sorted(rank, key = rank.get, reverse = True)
        #OrderedDict(sorted(rank.items(), key=lambda kv: kv
        for a in sortedRank:#a = 1-1400
            s = str(q) + " " + str(a) + " " + str(rank[a]) + "\n"
            #print(s)
            outputFile.write(s)
        

qAS = {}
getArticleRanking(queryTFIDF, articleTFIDF, qAS)
printSortedqAS(qAS)


"""
 the first column should be the query number
 the second column should be the abstract number
 third column should be the cosine similarity score

outputFile = open('output.txt', 'w')
for q in queryArticleRanking:
    for a in queryArticleRanking[q]: #sorted list
        s = q + " " + a + " " + qAS[q][a]
        outputFile.write(s + "\n")
outputFile.close()
"""

"""
            
    text = re.sub(r'[^\w\s]','',text) # rmv punctuations
    textAsList = text.split(" ")
    for word in textAsList: #rmv stop words
        if word is in stopWords:
            textAsList.remove(word)
    
    return textAsList
"""



