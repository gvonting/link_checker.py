#!python3
'''
TODO

- if a link is being recorded for the first time run an initialization test
    - If there is a dynamic element, figure out how to target it and remove it from all future requests to this website. (Need to figure ot a way to store this info alongside all the other relevant info regarding the link)
- if a link has been recorded before
    - Check by a certain percentage how much of the page has changed, if it has changed a lot (50-70%) maybe a website redesign has happened, so run a reinitialization of that link

    
- start working on frontend
    - set defined lengths for the table
    - get the top section looking good
    - get basic functions with python setup
- start webdriver at start of program so if the program fails use the try except to try to startup the browser, then quit browser if the program will fail anywhere
- add logic to take care of user mistakes such as no internet, broken links, links that are the same but seem different because it is missing www. or https or trailing / etc.
- add folders to separate link data to organize it
- add logic to let a user delete a link and associated files
- add option to create zipped up backup
- creating notes associated with website
- log file to troubleshoot bugs
- config file to save info such as user defined paths and wait time between checking links
- use a green fade or other color code to show recent changes, the longer it has been recently checked the more the color will fade
- Maybe add some logic to show where the link already exists on the frontend if the link the user is trying to add has already been added before, could use a way to highlight and scroll down to where that link is in the list. Rename the txt file that stores the notes and make a new unique id to associate it with
- Maybe add a try and except statement and try to run this line Where the program needs to connect to the internet, if it tries to get a webpage and the pc is not connected to the internet then show a message saying to check internet connection 
- Need to make a way for the user to input new info for a link, and when it has been submitted through the frontend, make the necessary changes in the csv file and the notes file associated with the link. The link_edit() function, this is in case a website ever changes the path to its page page
- see if i can install chromium with pip. or download the binary myself and include with py-installer
- use the same webdriver as the eel project, switch to the same chromium executable instead of firefox
'''

import html
import requests
import time
from datetime import datetime
from datetime import date
import csv
import os
from bs4 import BeautifulSoup
import hashlib
import glob
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

#Paths and other info needed for app operation
user_dir = ""

saved_data_dir = f'{user_dir}websiteCheckData/'
saved_link_data_notes = f'{saved_data_dir}linkDataNotes/'

link_list_file = saved_data_dir + "link_list.csv"

csv_header = ['link','date_added','latest_update','unique_id']

#selenium setup
options = Options()
options.add_argument('--headless')


#Some setup at startup
def on_startup():
    #Check for link list csv file, if one does not exist, create the folder structure and the link_list.csv file
    if not os.path.isfile(link_list_file):
        os.makedirs(saved_data_dir)
        os.makedirs(saved_link_data_notes)
        write_row_csv(csv_header, True)





#This function runs when a new link is being added
def link_add(link):
    #Open link list csv file
    link_list = open_csv_link()
    print(link_list)
    
    

    #compare the link to every link in the link_list to make sure it is unique
    unique_link = True
    for row in link_list:
        if row[0] == link:
            unique_link = False
            print('same link')
    if unique_link == True:
        #Start the browser
        browser = webdriver.Firefox(options=options)

        date_added = datetime.now().strftime("%Y-%m-%d")
        unique_id = int(hashlib.sha1(link.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
        csv_link_row = [link,date_added,'N/A',unique_id]
        #Append the current row with the new link to link_list.csv
        write_row_csv(csv_link_row, True)

        #Check the new link, get first record
        link_checker(csv_link_row, browser)
        #If the link_checker ran successfully, then append the updated csv_link_row with the new recorded date
        link_list.append(csv_link_row)
        #Rewrite the link_list.csv file with the updated csv row
        write_row_csv(link_list, False)

        #Close browser
        browser.quit()


def write_row_csv(row_data, single):
    #If row has only one list, then append the single row, if it has multiple rows, then overwrite the current file. If single == True, then it is a single row to append to end of file. If single == False, then it is a list of rows to overwrite the current file
    if single == True:
        with open(link_list_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row_data)
    if single == False:
        row_data.insert(0, csv_header)
        with open(link_list_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(row_data)

def open_csv_link():
    #open the csv file and return a list for iterating through
    link_file = open(link_list_file)
    link_reader = csv.reader(link_file)
    link_list = list(link_reader)
    print(link_list)
    del(link_list[0])
    print(link_list)
    return link_list


def single_link_checker(row_data, index_num):
    print('temp')
    #this will be used when the user selects a link to check from the frontend. It will pass the row data, index num, or could also just pass the index num or row itself and the complete row info could be taken from the frontend. OR could still pass both row data and index num from the frontend, then when the total link_list is loaded grab that index num from the list and if the unique id in the given row data is the same as the one grabbed from the total list using the index number then continue to check it using the referenced list value from the total list, if it is not, use the unique id in the row data to search for the correct index location in the total list, although this may not be necessary


def total_link_checker():
    #open and read the link csv into a list
    link_list = open_csv_link()
    #Initialize the browser
    browser = webdriver.Firefox(options=options)
    #Iterate over all the rows and pass each row to the link_checker()
    for row in link_list:
        link_checker(row, browser)

    #Close the browser
    browser.quit()  
    #Pass the link_list to the csv writer to rewrite all the rows of the list since some may have been updated
    write_row_csv(link_list, False)

def link_checker(link_data, browser):
    date_checked = datetime.now().strftime("%Y-%m-%d")


    #print(f'This is link_checker {link_data[0]}')
    browser.get(link_data[0])
    requested_link_data = browser.page_source
    #Clean up the requested data
    requested_link_data = BeautifulSoup(requested_link_data, 'html.parser')
    
    #Get list of files that start with the same unique_id
    #This will grab any files that have the same unique ID in their file name
    glob_list = [os.path.basename(i) for i in glob.glob(f'{saved_link_data_notes}{link_data[3]}*.txt')]
    #print(f'This is glob list: {glob_list}')



    #Get first copy of website if previous copy does not exist
    if glob_list == []:
        #Change the date for the most recent update of website
        link_data[2] = date_checked
        with open(f'{saved_link_data_notes}{link_data[3]}_{date_checked}.txt', 'w') as f:
            f.write(requested_link_data.text)
        #Screenshot webpage
        web_fullpage = browser.find_element(By.TAG_NAME, 'body')
        web_fullpage.screenshot(f'{saved_link_data_notes}{link_data[3]}_{date_checked}.png')

    else:
        #Set baseline to compare other datetime values, and set default file
        #This takes the first file in glob list and isolates the date value in the filename
        recorded_recent_date = date.fromisoformat(((glob_list[0].split('_'))[1]).split('.txt')[0])
        recorded_recent_file = glob_list[0]

        #print(f'This is the most recent date: {recorded_recent_date}')
        #Iterate through all the files in the globlist, isolating the dates in each filename and comparing them to find the most recent date. If a more recent date is found, update the recorded_recent_date and recorded_recent_file values
        for i in glob_list:
            current_working_date = date.fromisoformat(((i.split('_'))[1]).split('.txt')[0])
            if recorded_recent_date < current_working_date:
                #print(f'recorded_recent_date is less than current_working_date -- {recorded_recent_date} < {current_working_date}')
                recorded_recent_date = current_working_date
                recorded_recent_file = i
        #Open and read most recent recorded file
        with open(f'{saved_link_data_notes}{recorded_recent_file}', 'r') as f:
            recorded_recent_file_contents = f.read()

        #Compare most recent recorded file with the newly requested link data, if they are the same double check the row has the correct recorded date, if not, make a new file to record the updated website
        if recorded_recent_file_contents == requested_link_data.text:
            #print('Link Data is the same, doing nothing')
            
            #In the event the program crashes before the csv can be updated with the updated date info, this if statement will set the correct date associated with the most recent recorded date
            recorded_recent_date_str = recorded_recent_date.strftime("%Y-%m-%d")
            if recorded_recent_date_str != link_data[2]:
                link_data[2] = recorded_recent_date_str
            
        else:
            #print('link data is not the same, need to save new data')
            with open(f'{saved_link_data_notes}{link_data[3]}_{date_checked}.txt', 'w') as f:
                f.write(requested_link_data.text)
            #Screenshot webpage
            web_fullpage = browser.find_element(By.TAG_NAME, 'body')
            web_fullpage.screenshot(f'{saved_link_data_notes}{link_data[3]}_{date_checked}.png')
            #Update date
            link_data[2] = date_checked




def link_edit():
    print('temp')
    #Add logic that will let the user edit a link in case the source of the webpage has been changed


def backup_files():
    print('temp')
    #Add logic that will gather all files and zip them to be backed up

#Run when program first starts, will need to call this in eel app later on
on_startup()

#Startup code needed to test the app through the terminal, later on functions will be called by user interactions through the frontend
flag = True
while flag == True:
    print('[1] - Record Link')
    print('[2] - Check Links')
    user_input = input('Would you like to record a new link or check all links?\n')

    if user_input == '1':
        user_link = input('What link to record?\n')
        link_add(user_link)
    elif user_input == '2':
        total_link_checker()
    else:
        print("Pick from options")
