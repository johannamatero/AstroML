### Import needed modules
import pandas as pd
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request, urlretrieve
import urllib
from termcolor import colored
import os


### Functions
def jvo_table(project_code):
    '''Function to identify the present table on the webpage for a specific project code on JVO ALMA Fits Archive. This can be used to read several tables from JVO directly in python.
    Inputs:
        project_code: (string) on the same format as in the JVO ALMA Fits Archive. Ex: '2017.1.01310.S'
    Outputs:
        table corresponding to the one on the specific webpage on JVO
    '''
    scrapeLink = 'https://jvo.nao.ac.jp/portal/alma/archive.do?action=project.info&projectCode=' + project_code + '&orderBy=&order=&limit=20&offset=0'
    page = requests.get(scrapeLink)
    soup = BeautifulSoup(page.content, 'html.parser')

    all_tables = soup.find_all('table') # Finds all the tables of the web page
    correct_table = all_tables[0]       # desired table was the second one on the web page

    return correct_table


def jvo_image_link(project_code, correct_table=''):
    '''Function to extract the link to the thumbnails in the JVO table.
    Inputs:
        project_code: (string) on the same format as in the JVO ALMA Fits Archive. Ex: '2017.1.01310.S'
        correct_table: table which has already been identified using jvo_table
    Outputs:
        linkList: (list of strings) direct links to the thumbnails
        sourceList: (list of strings) the corresponding source name (defined in the table under target name) for the thumbnails
    '''
    correct_table = jvo_table(project_code) if correct_table=='' else correct_table

    imgLinkPrel = correct_table.find_all({'a':'id'})
    imgLink, sourceList = [], []

    for i in range(len(imgLinkPrel)):
        if 'dataset_' in str(imgLinkPrel[i]):
            imgLink.append(imgLinkPrel[i])
            sourceList.append(imgLinkPrel[i].text)

    linkList = []
    for it, s in enumerate(sourceList):
        linkList.append('https://jvo.nao.ac.jp/portal/alma/archive.do?pictSize=128&dataId=' + s + '_00_00_00&dataType=image&action=quicklook')

    return linkList, sourceList


def jvo_cube_size(project_code, correct_table=''):
    '''Function to identify the cube size for all files in a JVO table.
    Inputs:
        project_code: (string) on the same format as in the JVO ALMA Fits Archive. Ex: '2017.1.01310.S'
        correct_table: table which has already been identified using jvo_table
    Outputs:
        cube: list of the cube size for all files in the corresponding JVO table.
    '''
    correct_table = jvo_table(project_code) if correct_table=='' else correct_table
    cube = []

    imgLinkPrel = correct_table.find_all({'a':'id'})

    for i in range(len(imgLinkPrel)):
        if 'dataset_' in str(imgLinkPrel[i]):
            cube.append(correct_table.find_all({'a':'id'})[i].find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text)

    return cube


def jvo_source_id(project_code, correct_table=''):
    '''Function to get the source id from JVO table
    Inputs:
        project_code: (string) on the same format as in the JVO ALMA Fits Archive. Ex: '2017.1.01310.S'
        correct_table: table which has already been identified using jvo_table
    Outputs:
        (list of strings) list of source id's in JVO table
    '''
    return jvo_image_link(project_code, correct_table)[1]


def jvo_target_name(project_code, correct_table=''):
    '''Function to get the source id from JVO table
    Inputs:
        project_code: (string) on the same format as in the JVO ALMA Fits Archive. Ex: '2017.1.01310.S'
        correct_table: table which has already been identified using jvo_table
    Outputs:
        (list of strings) list of source id's in JVO table
    '''

    correct_table = jvo_table(project_code) if correct_table=='' else correct_table

    imgLinkPrel = correct_table.find_all({'a':'id'})
    targetName = []

    for i in range(len(imgLinkPrel)):
        if 'dataset_' in str(imgLinkPrel[i]):
            targetName.append(correct_table.find_all({'a':'id'})[i].find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text)
    return targetName

def jvo_member_uid(project_code, correct_table=''):

    correct_table = jvo_table(project_code) if correct_table=='' else correct_table

    imgLinkPrel = correct_table.find_all({'a':'id'})
    memberUidList = []

    for i in range(len(imgLinkPrel)):
        if 'dataset_' in str(imgLinkPrel[i]):
            memberUidList.append(correct_table.find_all({'a':'id'})[i].find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text)

    return memberUidList


def jvo_download_images(project_code, correct_table='', path=''):
    correct_table = jvo_table(project_code) if correct_table=='' else correct_table

    cube = jvo_cube_size(project_code)
    links, sources = jvo_image_link(project_code)

    imgPath = (os.path.join('Images', project_code) if path=='' else path)
    for it, c in enumerate(cube):
        if c[-5:]=='x1 x1':

            imgPath = os.path.join('Images', project_code)
            if not os.path.isdir(imgPath):
                os.makedirs(imgPath)

            imgName = os.path.join(imgPath, sources[it] + '.jpg')

            try:
                urllib.request.urlretrieve(links[it], imgName) # Downloads all the images from the saved links
            except:
                print('Image Not Found')

def jvo_download_alma(project_code, correct_table='', path='', printBool=True):
    correct_table = jvo_table(project_code) if correct_table=='' else correct_table

    cube = jvo_cube_size(project_code, correct_table)
    member_uid = jvo_member_uid(project_code, correct_table)

    link_general = 'https://almascience.nrao.edu/dataPortal/'

    filePath = (os.path.join('Files', project_code) if path=='' else path)

    for it, c in enumerate(cube):
        if it==0:
            print('DOWNLOADING FILES TO: ' + filePath)

        if c[-5:].replace(' ','') == 'x1x1':


            if not os.path.isdir(filePath):
                os.makedirs(filePath)

            if member_uid[it][:6] != 'member':
                member_uid[it] = 'member.' + member_uid[it] #name convention is not consistent in JVO

            fileName = os.path.join(filePath, member_uid[it])

            if not os.path.isfile(fileName):
                try:
                    urllib.request.urlretrieve(link_general+member_uid[it], fileName) # Downloads all the images from the saved links
                    if printBool:
                        print(colored('Downloaded: ' + member_uid[it], 'green'))
                except:
                    if printBool:
                        print(colored('File Not Found: ' + member_uid[it], 'red'))
            else:
                if printBool:
                    print(colored('File Already Exists: ' + member_uid[it], 'blue'))
