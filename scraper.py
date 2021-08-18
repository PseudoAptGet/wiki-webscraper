import requests #to request html
from bs4 import BeautifulSoup, NavigableString, Tag #to parse and navigate through html
from collections import Counter #for frequency counter
from gensim.parsing.preprocessing import remove_stopwords, preprocess_string, strip_punctuation #to remmove stopwords
import re #regex support 
import os #file existence checking support


#method to remove suffix for string manipulation
def removeSuffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

f = open("final_demo.txt", "w")
f2 = open("linkWork.txt", 'w')

#get user link
link = input("please enter the wikipedia link: ")

#setting up request
getter = requests.get(url=link,)
if(getter.status_code != 200):
    exit()

#soup = parsing object
soup = BeautifulSoup(getter.content, 'html.parser')

#extracting and printing the title of the soup
title = soup.find(id="firstHeading")

#Point from where all sibling nodes will be wikipedia content
placeForTitleCount = soup.find(class_="mw-parser-output").findChild()


#Find how many headings there are to store information in an array
numHeadings = 1
while True:
    #first four conditions of if/elif -> see also and references don't contain 
    #important textual information, and pop up at the end of the article, 
    #so if that's reached, then there are no more headings containing important 
    # info
    if placeForTitleCount.text == "See also[edit]":
        booleanTrue = False
        break
    elif placeForTitleCount.text == "See also":
        booleanTrue = False
        break
    elif placeForTitleCount.text == "References":
        break
    elif placeForTitleCount.text == "References[edit]":
        break
    #if it's a header under mw-parser-output, and it does not 
    #contain bibliographical information, then it must contain the textual
    #information that must be scraped
    elif placeForTitleCount.name == "h2" or placeForTitleCount.name == "h3" or placeForTitleCount.name == "h4":
        placeForTitleCount = placeForTitleCount.find_next_sibling()
        numHeadings += 1
    else:
        placeForTitleCount = placeForTitleCount.find_next_sibling()


#official matrix to store all info
#rows correspond to headings
#columns in the rows correspond to content 
#(0 = heading, 1 = text, 2 = local wiki links, 3 = outside references)
height, width = numHeadings, 4
Matrix = [ [ "" for i in range(width) ] for j in range(height) ]
Matrix[0][0] = title.contents[0] #input wiki page title into first row (for first heading) of matrix


#Input scraped data into matrix
place = soup.find(class_="mw-parser-output").findChild() #point where wiki content starts
curIndex = 0 #used to keep track of which heading the content and links are in
while True:
    #first four if elif -> must break because outside range of text info to scrape
    if place.text == "See also[edit]": 
        break
    elif place.text == "See also":
        break
    elif place.text == "References":
        break
    elif place.text == "References[edit]":
        break
    #if it's a header, then curIndex must be bumped because all text from 
    #existing header has been scraped. Incrementing curIndex moves the 
    #input location of the matrix to the next row, corresponding to the next header
    elif place.name == "h2" or place.name == "h3" or place.name == "h4": #Heading -> Store in matrix
        curIndex += 1  
        curTitle = place.text.strip()
        Matrix[curIndex][0] = removeSuffix(curTitle, "[edit]")
        place = place.find_next_sibling()
    else: #by process of elimination, must be actual text. Store in matrix
        Matrix[curIndex][1] += place.text #put text in column 1 
        for link in place.find_all('a'): #search for all links
            url = link.get('href')
            strUrl = str(url)
            if(strUrl.startswith("/wiki/")): #local links -> column 2 
                Matrix[curIndex][2] += (" " + strUrl)
            if(strUrl.startswith("#cite_note")): #non-local links -> column 3 
                Matrix[curIndex][3] += (" " + strUrl)
        place = place.find_next_sibling()

#write matrix into final_demo
#start off with basic iteration. Pick row, then go column by column within row
for whichHeading in range(height):
    for contentType in range(width):
        if contentType == 0: #title/headings
            f.write("title: " + Matrix[whichHeading][contentType])
            f.write('\n')
        elif contentType == 1: #content
            curText = Matrix[whichHeading][contentType]
            curText1 = curText.lower()
            noPuncText = strip_punctuation(curText1)
            noStopText = remove_stopwords(noPuncText)
            pattern = r'[0-9]'
            noDigText = re.sub(pattern, '', noStopText)
            noCommonText1 = noDigText.replace("the", "")
            noCommonText2 = noCommonText1.replace("The", "")
            noCommonText3 = noCommonText2.replace("•", "")
            #print(noStopText)
            listFirstText = noCommonText3.split()
            newCounter = Counter(listFirstText)
            mostFreq = newCounter.most_common(5)
            f.write("scraped text: " + str(mostFreq))
            f.write('\n')
            #print(mostFreq)
        elif contentType == 2: #local wiki links
            listLinks = Matrix[whichHeading][contentType]
            indivTokens = listLinks.split()
            f.write("wiki links: " + str(indivTokens))
            f.write('\n')
        else: #outside links
            listLinks = Matrix[whichHeading][contentType]
            indivTokens = listLinks.split()
            for i in range(0, len(indivTokens)):
                indivTokens[i] = indivTokens[i].removeprefix("#")
            referenceSoup = soup.find(class_="references")
            officialArray = []
            for eachLink in indivTokens:
                firstSoup = referenceSoup.find(id = eachLink)
                secondSoup = firstSoup.find(class_ = "reference-text") #changed from "reference-text" 
                for link in secondSoup.find_all('a'):
                    url = link.get("href")
                    strUrl = str(url)
                    officialArray.append(strUrl)
            
            f.write("outside links: " + str(officialArray))
            f.write('\n')
            f.write('\n')
            




