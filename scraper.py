import requests #to request html
from bs4 import BeautifulSoup, NavigableString, Tag #to parse and navigate through html
from collections import Counter #for frequency counter
from gensim.parsing.preprocessing import remove_stopwords, preprocess_string, strip_punctuation #to remmove stopwords
import re #regex support 


def get_input():
    '''
    Gets the user's intended wikipedia page/input

    No Args

    Returns:
        A string representation of the wikipedia link
    '''
    print("Please enter a wikipedia link that you would like this script to scrape")
    print("If you're feeling uninspired, I've linked some cool articles down below")
    print("The place my family revisits every year: https://en.wikipedia.org/wiki/Niagara_Falls")
    print("plants? : https://en.wikipedia.org/wiki/Agriculture")
    print("The wikipedia page I may or may not have read before writing this script: https://en.wikipedia.org/wiki/Python_(programming_language)")
    chosen_page = input("Choose one, and enter one here:")
    return chosen_page

def file_setup():
    '''
    Sets up the file where output/scraping results will be displayed

    No Args

    Returns the file to be written in 
    '''
    f = open("output.txt", 'w')
    return f

def create_soup_object(wiki_link):
    '''
    Creates a beautifulsoup object that will scrape wikipedia

    Args:
        wiki_link (string): a string representation of the wiki link to be scraped
    
    Returns:
        soup: The BeautifulSoup object representation of the link
    '''    
    getter = requests.get(url=wiki_link,)
    if(getter.status_code != 200):
        print("REQUEST FAILED. PLEASE CHECK IF LINK IS VALID. SCRIPT TERMINATED")
        exit() #exit program if getter failed to prevent later runtime exceptions from beautifulsoup import
    soup = BeautifulSoup(getter.content, 'html.parser')
    return soup

def get_number_of_headings(soup_object):
    '''
    Fetches the number of (content) headings that a given wikipedia page has 
    
    Args:
        soup_object: the soup object of the wikipedia page

    Returns: 
        number_of_headings (int): Number of headings containing relevant information
    '''
    reference_point = soup_object.find(class_="mw-parser-output").findChild() #chose this point because displayed wiki text starts from here
    count = 1 #already 1 because title exists, and is ignored from chosen point since chosen point is past title
    while True:
        # stopping if program sees these sections because they have no relevant textual information to scrape
        # after all, why would one scrape word frequency of links?
        if reference_point.text == "See also[edit]":
            break
        elif reference_point.text == "See also":
            break
        elif reference_point.text == "References":
            break
        elif reference_point.text == "References[edit]":
            break
        # if reference point is a heading, then the count is incremented because another section exists
        elif reference_point.name == "h2" or reference_point.name == "h3" or reference_point.name == "h4":
            reference_point = reference_point.find_next_sibling()
            count += 1
        else:
            reference_point = reference_point.find_next_sibling() #must be useless -> skip
    return count
        
def create_matrix(number_of_headings):
    '''
    Creates a 2d array/matrix where scraped data will be temporarily stored.
    column 0: heading titles
    column 1: scraped text
    column 2: wikipedia redirect links
    column 3: outside references

    Args:
        number_of_headings (int): The number of headings
    
    Returns: 
        Matrix/2d array: The aforementioned array for data storage
    '''
    height, width = number_of_headings, 4
    matrix = [ [ "" for i in range(width) ] for j in range(height) ]
    return matrix


def removeSuffix(input_string, suffix):
    '''
    removes a specified suffix from a given string

    Args: 
        input_string: the string that a suffix must be removed from
        suffix: the suffix that must be removed
    
    Returns:
        input_string: the updated input string that does not have specified suffix
    '''
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def fill_matrix(matrix, number_of_headings, soup_object):
    '''
    Fills in the matrix with relevant information of scraped data in the relevant columns
    Do note that the rows correspond to individual sections.
    Column 0 of each row : title
    Column 1 of each row : scraped text 
    Column 2 of each row : wiki redirects
    Column 3 of each row : referenced links (typically outside wikipedia)

    Args:
        Matrix: The matrix where data will be stored
        number_of_headings: Number of headings in wikipedia page
        soup_object: Beautiful Soup object of the wikipedia page

    No Returns: merely updates official matrix, which is a list (mutable)
    '''
    matrix[0][0] = soup_object.find(id="firstHeading").contents[0] #inputs column 0's first entry with wiki page title
    place = soup_object.find(class_="mw-parser-output").findChild() #point from which main page html is stored
    cur_index = 0
    while True:
        # stopping if program sees these sections because they have no relevant textual information to scrape
        # after all, why would one scrape word frequency of links?
        if place.text == "See also[edit]": 
            break
        elif place.text == "See also":
            break
        elif place.text == "References":
            break
        elif place.text == "References[edit]":
            break
        elif place.name == "h2" or place.name == "h3" or place.name == "h4": #Heading -> Store in matrix
            cur_index += 1  #onto a new row since new title/heading has been found
            cur_title = place.text.strip() 
            matrix[cur_index][0] = removeSuffix(cur_title, "[edit]") #input title into matrix, but get rid of edit suffix because it's useless
            place = place.find_next_sibling()
        else: #by process of elimination, must be actual text. Store in matrix
            matrix[cur_index][1] += place.text
            for link in place.find_all('a'): #find all html links
                url = link.get('href')
                strUrl = str(url)
                if(strUrl.startswith("/wiki/")): #if wiki, store in column 2 because it's localized
                    matrix[cur_index][2] += (" " + strUrl)
                if(strUrl.startswith("#cite_note")): 
                #if in references/citations, then store in column 3 because it's not localized and actual link must be fetched from references section
                    matrix[cur_index][3] += (" " + strUrl)   
            place = place.find_next_sibling()

def output_matrix_into_file(matrix, file_object, num_headings, soup):
    '''
    Outputs matrix info into file_object

    Args:
        matrix: The matrix where (scraped) data is stored
        file_object: The file where information will be written
        num_headings: Number of headings in wikipedia page
        soup: Beautiful Soup object of the wikipedia page

    No Returns: merely updates official matrix, which is a list (mutable)
    '''
    #iterate through each row's columns
    for each_heading in range(num_headings):
        for each_matrix_info_type in range(0,4): 
            if each_matrix_info_type == 0: #title/headings
                file_object.write("title: " + matrix[each_heading][each_matrix_info_type])
                file_object.write('\n')
            elif each_matrix_info_type == 1: #scraped text
                current_text = matrix[each_heading][each_matrix_info_type]
                #basic scraping. Punctuation, stop words, and additional stop words not in gensim library removed
                current_text = remove_stopwords(strip_punctuation(current_text.lower()))
                pattern = r'[0-9]'
                current_text = re.sub(pattern, '', current_text)
                current_text = current_text.replace("the", "")
                current_text = current_text.replace("•", "")
                #split text into list
                current_textArray = current_text.split()
                #count the frequencyy of words
                word_arraylist = Counter(current_textArray)
                most_frequent_words = word_arraylist.most_common(5)
                file_object.write("scraped text: " + str(most_frequent_words))
                file_object.write('\n')
            elif each_matrix_info_type == 2: #local wiki links
                each_local_link_as_str = matrix[each_heading][each_matrix_info_type]
                each_local_link_as_list = each_local_link_as_str.split()
                file_object.write("wiki links: " + str(each_local_link_as_list))
                file_object.write('\n')
            else: #outside links
                each_local_link_as_str = matrix[each_heading][each_matrix_info_type]
                each_local_link_as_list = each_local_link_as_str.split()
                # all outside links are in the format #cite-note-(insert number or title) for class
                # removing the # so that link can be searched by class
                for i in range(0, len(each_local_link_as_list)):
                    each_local_link_as_list[i] = each_local_link_as_list[i].removeprefix("#")
                soup_reference_section_location = soup.find(class_="references") # search in reference section
                outside_links_array = [] # will contain all outside links (not the cite-notes that the matrix contains)
                for each_cite_note in each_local_link_as_list:
                    li_cite_note_finder = soup_reference_section_location.find(id = each_cite_note) #find the li that contains the cite note
                    outside_link = li_cite_note_finder.find(class_ = "reference-text") #point in html where links are contained 
                    #scrape all links
                    for link in outside_link.find_all('a'):
                        url = link.get("href")
                        url_as_string = str(url)
                        outside_links_array.append(url_as_string)
                file_object.write("outside links: " + str(outside_links_array))
                file_object.write('\n\n')
                file_object.write('\n')

def main():
    link = get_input()
    output_file = file_setup()
    main_soup = create_soup_object(link)
    num_headings = get_number_of_headings(main_soup)
    official_matrix = create_matrix(num_headings)
    fill_matrix(official_matrix, num_headings, main_soup)
    output_matrix_into_file(official_matrix, output_file, num_headings, main_soup)
    print("All done. If you're still getting errors, apologies on my part. Wikipedia is hard to scrape, and their class naming convention is irregular")
    print("Please start this script again and try some of the links I recommended. They seem to work just fine")
    

main()
