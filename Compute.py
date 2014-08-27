"""
Author: Bahar Salehi
Date: August 2014
"""

import re
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
import argparse
import sys


#parser arguments
desc = "Computes the compositionality of multiword expressions using Wiktionary dump"
parser = argparse.ArgumentParser(description=desc)

parser.add_argument("MWE_file", help="file that contains the multiword expressions")
parser.add_argument("wiktionary_dump", help="wiktionary dump file")
parser.add_argument("option", help="shows the approach to use")

args = parser.parse_args()



stopwords = ['e','.g.','with','etc','the','a','an','which','is','are','be','will','do','and','or','it','they',"'s","one's",'to','in','as','after','before','at','so',',',';','.','something','anything','that','cannot']


def getDefinition(rawtext):
    # this function gets the defintions from the raw text
    returnDefs = ''
    sentences = rawtext.split('\n')
    for s in sentences:
        if s.find('#')==0 and s.find(':')!=1 and s.find('*')!=1:
            returnDefs+=s.lower()+'\n'
            
    returnDefs = returnDefs.replace('#','')
    returnDefs = returnDefs.replace('[[','')
    returnDefs = returnDefs.replace(']]','')

    Begin = returnDefs.find('{{')
    while Begin!=-1:
        End = returnDefs.find('}}')
        if End<Begin:
            break

        if 'idiomatic' in returnDefs[Begin:End]:
            returnDefs = returnDefs[0:Begin]+' idiomatic '+returnDefs[End+2:]
        else:
            returnDefs = returnDefs[0:Begin]+returnDefs[End+2:]
        
        Begin = returnDefs.find('{{')

    returnDefs = returnDefs.replace(',',' ')
    returnDefs = returnDefs.replace(';',' ')
    returnDefs = returnDefs.replace('|',' ')
    returnDefs = returnDefs.replace("'",' ')
    returnDefs = returnDefs.replace(".",' ')
    return returnDefs

def getTranslations(rawtext):
    # this function returns the translations
    returnTrans = {}
    sentences = rawtext.split('\n')
    for s in sentences:
        if '{{t|' in s or '{{t+|' in s:
            translations= re.findall("{{t\+?\|.*?\|.*?}}", s)
            t = translations[0]
            t = t.replace('{{','')
            t = t.replace('}}','')
            t = t.split('|')
            
            language = t[1]
            returnTrans[language] = []

            for t in translations:
                
                t = t.replace('{{','')
                t = t.replace('}}','')
                t = t.split('|')

                t[2] = t[2].replace('[[','')
                t[2] = t[2].replace(']]','')
                returnTrans[language].append(t[2])


            


    return returnTrans
            

def getWord(word):
    # this functions finds the information of the given word in wiktionary dump
    fr.seek(0,0)
    r = fr.readline()
    
    
    while r!='':
        rawtext = ''
        if '<title>'+word+'</title>' in r:
            r= fr.readline()
            while '</page>' not in r:
                rawtext += r
                r = fr.readline()
            break

        r = fr.readline()
    return rawtext
    


def firstDef(mwe,definition):
    # this is the approach of using only the first definition
    if definition=='':
        return([1,1])
    definition = definition.split('\n')[0]
    definition = definition.replace(mwe,'')
    definition = definition.replace('(','')
    definition = definition.replace(')','')
    tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
    defineArr = tokenizer.tokenize(definition)
    
    lmtzr = WordNetLemmatizer()
    for i in range(0,len(defineArr)):
        defineArr[i] = lmtzr.lemmatize(defineArr[i])

        
    words = mwe.split()
    for i in range(0,len(words)):
        words[i] = lmtzr.lemmatize(words[i])
    



    if words[0] in defineArr and words[1] in defineArr:
        return([1,1])
        
    elif words[0] in defineArr:
        return([1,0])
        
    elif words[1] in defineArr:
        return([0,1])
    else:
        return([0,0])

def voteDefs(MWE,definitions):
    # this is the approach of considering all definitions and voring
    defns = definitions.split('\n')
    votes = [0,0]
    numberOfDefs = 0
    defFlag = False
    for defn in defns:
        defFlag = True
        numberOfDefs +=1
        

        result = firstDef(MWE,defn)
        
        votes[0] += result[0]
        votes[1] += result[1]

    if defFlag == False:
        votes[0] = 1
        votes[1] = 1


    return [int(votes[0]>numberOfDefs/2),int(votes[1]>numberOfDefs/2)]
    
def hasIdiom(MWE, definition):
    # this is the approach of using idioma tag or voting approach
    defns = definition.split('\n')
    votes = [0,0]
    numberOfDefs = 0
    idiomFlag = False
    defFlag = False
    for defn in defns:
        defFlag = True
        numberOfDefs +=1
        
        if 'idiomatic' in defn:
            idiomFlag = True
            
        #definition = clean(definition)  #now an array not a string

        result = firstDef(MWE,defn)
        if idiomFlag==True:
            return result
            break
        
        votes[0] += result[0]
        votes[1] += result[1]

    if defFlag == False:
        votes[0] = 1
        votes[1] = 1


    return [int(votes[0]>numberOfDefs/2),int(votes[1]>numberOfDefs/2)]


def firstDefSyn(mwe,definition):
    # this is the approach of using only the first definition and the synonym-based approach
    result = firstDef(mwe,definition)
    if result[0]==0 or result[1]==0:
        definition = definition.split('\n')[0]
        definition = definition.replace(mwe,'')
        definition = definition.replace('(','')
        definition = definition.replace(')','')
        tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
        defineArr = tokenizer.tokenize(definition)
        
        lmtzr = WordNetLemmatizer()


            
        words = mwe.split()
        for i in range(0,len(words)):
            words[i] = lmtzr.lemmatize(words[i])

        defdef = ''
        for d in defineArr:
            if d not in stopwords and d!='idiomatic':

                rawdefdef = getWord(d)
                defdef= getDefinition(rawdefdef)
                
                defdefArr = tokenizer.tokenize(defdef)
                for i in range(0,len(defdefArr)):
                    defdefArr[i] = lmtzr.lemmatize(defdefArr[i])        
                

                if result[0]==0 and words[0] in defdefArr:
                    result[0] = 1
                if result[1]==0 and words[1] in defdefArr:
                    result[1] = 1

                if result[1]==1 and result[0]==1:
                    return result
                

    return result 
        
        
def voteDefSyn(mwe,definitions):
    # this is the approach of cosiders all definitions and the synonym-based approach    
    if definitions=='':
        return [1,1]

    numberOfDefs = 0
    votes = [0,0]
    while definitions.find('\n')!=-1:
        numberOfDefs+=1
        result = firstDefSyn(mwe,definitions)
        votes[0]+=result[0]
        votes[1]+=result[1]
        removeInd = definitions.find('\n')
        definitions = definitions[removeInd+1:]
    



    return [int(votes[0]>numberOfDefs/2),int(votes[1]>numberOfDefs/2)]  


def hasIdiomSyn(mwe,definitions):
    # this is the approach of using idiomatic tag and the synonym-based approach
    if definitions=='':
        return [1,1]

    numberOfDefs = 0
    votes = [0,0]
    idiomFlag = False
    while definitions.find('\n')!=-1:
        numberOfDefs+=1
        currentDef = definitions.split('\n')[0]
        if 'idiomatic' in currentDef:
            idiomFlag = True
            
        result = firstDefSyn(MWE,definitions)
        if idiomFlag==True:
            return result

        
        votes[0] += result[0]
        votes[1] += result[1]


        removeInd = definitions.find('\n')
        definitions = definitions[removeInd+1:]
    



    return [int(votes[0]>numberOfDefs/2),int(votes[1]>numberOfDefs/2)]  
    

fr = open(args.wiktionary_dump,'r')
fr2 = open(args.MWE_file,'r')
option = int(args.option)

for r in fr2:
    
    MWE = r.replace('\n','')
   
    rawtext = getWord(MWE)
    if rawtext!='':
        definitions = getDefinition(rawtext)
        
        if option  == 0:
            result = firstDef(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
        elif option ==1:
            result = voteDefs(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
        elif option ==2:
            result = hasIdiom(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
        elif option==3:
            result = firstDefSyn(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
            
        elif option==4:
            result = voteDefSyn(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
            
        elif option ==5:
            result = hasIdiomSyn(MWE,definitions)
            print(str(result[0])+' '+str(result[1]))
            
        elif option==6:
            translations()
        else:
            print('wrong choice!')
    else:
        print('1 1')
                
    
 




fr.close()
fr2.close()
