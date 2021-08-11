#NOTE: LINKS WILL NOT DISPLAY UNLESS CODE IS COMMENTED OUT, AND LINES 87-91 EXPLAIN WHY THAT SUBSECTION OF CODE IS COMMENTED OUT TO BEGIN WITH. 

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import Counter
from gensim.parsing.preprocessing import remove_stopwords

#method to remove suffix for string manipulation
def removeSuffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

#get user link
link = input("please enter the wikipedia link: ")

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

#Find how many headings there are to store information in an array
numHeadings = 1
booleanTrue = True
while booleanTrue == True:
    if placeForTitleCount.text == "See also[edit]" or placeForTitleCount.text == "See_also":
        booleanTrue = False
        break
    elif placeForTitleCount.name == "h2" or placeForTitleCount.name == "h3" or placeForTitleCount.name == "h4":
        placeForTitleCount = placeForTitleCount.find_next_sibling()
        numHeadings += 1
    else:
        placeForTitleCount = placeForTitleCount.find_next_sibling()


#create the matrix/array that will store HEADING, TEXT, and LINKS (in that order)
height, width = numHeadings, 3
Matrix = [ [ "" for i in range(width) ] for j in range(height) ]

#Input values into matrix
place = soup.find(class_="mw-parser-output").findChild()
curIndex = 0
booleanRun = True
Matrix[0][0] = title.contents[0]
while booleanRun == True:
    if place.text== "See also[edit]" or place.id == "See_also": #Useless content beyond this point. Thus, break statement included
        break
    elif place.name == "h2" or place.name == "h3" or place.name == "h4": #Heading -> Store in matrix
        curIndex += 1
        curTitle = place.text.strip()
        Matrix[curIndex][0] = removeSuffix(curTitle, "[edit]")
        place = place.find_next_sibling()
    elif place.name != "p": #Useless content -> move to next sibling
        place = place.find_next_sibling()
    else: #by process of elimination, must be actual text. Store in matrix
        Matrix[curIndex][1] += place.text
        place = place.find_next_sibling()


#print for analysis
for whichHeading in range(height):
    for contentType in range(width):
        Matrix[whichHeading][contentType].lstrip("text: ")
        if contentType == 0:
            print(Matrix[whichHeading][contentType])
        elif contentType == 2:
            print("LINKS: Sorry, I had some trouble extracting links. I'll try to work that out before the interview (if given the opportunity).")
            print("\n")
            print("\n")
        else:
            curText = Matrix[whichHeading][contentType]
            noStopText = remove_stopwords(curText)
            listFirstText = noStopText.split()
            newCounter = Counter(listFirstText)
            mostFreq = newCounter.most_common(10)
            print(mostFreq)
            

#Could not locate href links in relevant areas (ie put it in the corrent part of the matrix). Uncomment this area to see the links.
'''
for hrefEmbeds in soup.findAll('a'):
    print(hrefEmbeds.get('href'))
'''  
