#NOTE: LINKS WILL NOT DISPLAY UNLESS CODE IS COMMENTED OUT, AND LINES 87-91 EXPLAIN WHY THAT SUBSECTION OF CODE IS COMMENTED OUT TO BEGIN WITH. 

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import Counter
from gensim.parsing.preprocessing import remove_stopwords, preprocess_string, strip_punctuation
import re

#method to remove suffix for string manipulation
def removeSuffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


f = open("demo.txt", "w")
f2 = open("linkWork.txt", 'w')

#get user link
#link = input("please enter the wikipedia link: ")
link = "https://en.wikipedia.org/wiki/Python_(programming_language)"

#setting up request
getter = requests.get(
	url=link,
)
if(getter.status_code != 200):
	print("REQUEST FAILED. PLEASE CHECK INTERNET CONNECTION")

#soup = parsing object
soup = BeautifulSoup(getter.content, 'html.parser')

#extracting and printing the title of the soup
title = soup.find(id="firstHeading")

#Point from where all sibling nodes will be wikipedia content
placeForTitleCount = soup.find(class_="mw-parser-output").findChild()

# placeForTitleCount.text == "See also[edit]" or 
#Find how many headings there are to store information in an array
numHeadings = 1
booleanTrue = True
while booleanTrue == True:
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
    elif placeForTitleCount.name == "h2" or placeForTitleCount.name == "h3" or placeForTitleCount.name == "h4":
        placeForTitleCount = placeForTitleCount.find_next_sibling()
        numHeadings += 1
    else:
        placeForTitleCount = placeForTitleCount.find_next_sibling()

#print("the number of headings is: " + str(numHeadings))
#create the matrix/array that will store HEADING, TEXT, and LINKS (in that order)
height, width = numHeadings, 4
Matrix = [ [ "" for i in range(width) ] for j in range(height) ]

#Input values into matrix
place = soup.find(class_="mw-parser-output").findChild()
curIndex = 0
booleanRun = True
Matrix[0][0] = title.contents[0]
while booleanRun == True:
    if place.text == "See also[edit]": #or place.id == "See_also": Useless content beyond this point. Thus, break statement included
        break
    elif place.text == "See also":
        break
    elif place.text == "References":
        break
    elif place.text == "References[edit]":
        break
    elif place.name == "h2" or place.name == "h3" or place.name == "h4": #Heading -> Store in matrix
        curIndex += 1  
        curTitle = place.text.strip()
        Matrix[curIndex][0] = removeSuffix(curTitle, "[edit]")
        place = place.find_next_sibling()
    else: #by process of elimination, must be actual text. Store in matrix
        Matrix[curIndex][1] += place.text
        for link in place.find_all('a'):
            url = link.get('href')
            strUrl = str(url)
            if(strUrl.startswith("/wiki/")):
                Matrix[curIndex][2] += (" " + strUrl)
            if(strUrl.startswith("#cite_note")):
                Matrix[curIndex][3] += (" " + strUrl)

            #contents = link.text
            #print(str(url))
            #f2.write(str(url, contents))
        place = place.find_next_sibling()
    '''
    elif place.name != "p": #Useless content -> move to next sibling
        Matrix[curIndex][1] += place.text
        place = place.find_next_sibling()
    '''
    


finderArray = Matrix[0][3].split()

#print for analysis
for whichHeading in range(height):
    for contentType in range(width):
        #Matrix[whichHeading][contentType].lstrip("text: ")
        if contentType == 0:
            f.write(Matrix[whichHeading][contentType])
            f2.write(Matrix[whichHeading][contentType])
            f2.write('\n')
            #print(Matrix[whichHeading][contentType])
        elif contentType == 2:
            #print("LINKS: Sorry, I had some trouble extracting links. I'll try to work that out before the interview (if given the opportunity).")
            #print("\n")
            #print("\n")
            f.write("LINKS: Sorry, I had some trouble extracting links. I'll try to work that out before the interview (if given the opportunity).")
            f.write("\n")
            f.write("\n")
            listLinks = Matrix[whichHeading][contentType]
            indivTokens = listLinks.split()
            f2.write(str(indivTokens))
            f2.write('\n')
        elif contentType == 3 :
            listLinks = Matrix[whichHeading][contentType]
            indivTokens = listLinks.split()

            f2.write(str(indivTokens))
            f2.write('\n')
        else:
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
            f.write(str(mostFreq))
            #print(mostFreq)
            

#Could not locate href links in relevant areas (ie put it in the corrent part of the matrix). Uncomment this area to see the links.
'''
for hrefEmbeds in soup.findAll('a'):
    print(hrefEmbeds.get('href'))
'''  

finderArray = Matrix[0][3].split()
#print(finderArray)

newPlace = soup.find()
for eachLink in finderArray:
    print(eachLink)
    newSoup = soup.find_all("ol", class_ = eachLink)
    pass

