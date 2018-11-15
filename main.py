import requests
import re
import os
from PIL import Image
from bs4 import BeautifulSoup

def prepare_link(link):
    """
    Some links on MangaReader only have one index in the end,
    and you can end up downloading every book in the series.
    This function checks for this and fixes it if needed, then
    returns the fixed link.
    :param link, a string containing the original link:
    :return the fixed link, or the original depending on the case:
    """
    slash_count = 0
    for char in link:
        if char == "/":
            slash_count += 1
    if slash_count == 4:
        link += "/1"
    return link

def get_image(link, directory):
    """
    Function to get the given photos and write them
    to the images directory.
    :param link: link(string) to start of book
    :param directory: the directory of the images folder
    """
    counter = int(link[-1])
    link = link[:-1]
    finished = False
    while not finished:
        temp_link = link + str(counter)
        page = requests.get(temp_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        images = []
        for img in soup.findAll('img'):
            images.append(img.get('src'))
        if not images:
            finished = True
        else:
            for img in images:
                image = requests.get(img)
                with open(directory + "/" + str(counter)+".jpeg" , 'wb') as f:
                    f.write(image.content)
            counter += 1

def create_folder():
    """
    Function to create a folder to place images in
    :return: A string indicating the path of the images folder:
    """
    current_location = os.getcwd()
    image_directory = os.path.join(current_location, r'manga_reader_images')
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    return image_directory

def human_sort_key(str_arg):
    temp_str = ''
    for char in str_arg:
        if char.isdigit():
            temp_str += char
    return int(temp_str)

def convert_to_pdf(directory, pdf_name):
    """
    :param directory: filepath(string) from the create_folder function
    :param pdf_name: desired name(string) of the PDF
    """
    file_list = [i for i in os.listdir(directory)]
    #list of Image files, sorted by the numeric value of the file name
    image_list = [Image.open(directory + "\\" + f) for f in sorted(file_list, key=lambda s: human_sort_key(str(s)))]
    #creating first image for Pillow to write on
    img_1 = image_list.pop(0)
    pdf_file = pdf_name + ".pdf"
    for num, file in enumerate(image_list):
        img_1.save(pdf_file, "PDF", resolution=100.0, save_all=True, append_images=image_list)
        print("File {}/{} converted...".format(num + 1, len(image_list)),end="\r")
    #clean up jpeg files used in PDF creation
    clean_up(directory)
    print('\n')

def clean_up(directory):
    '''
    :param directory: directory string for images folder
    :return:
    '''
    for file in os.listdir(directory):
        if ".jpeg" in file:
            os.remove(directory + "//" + file)

def main():
    '''
    Main function; start by entering your desired page,
    script will start at the first page and loop until there
    are not any pages left. Converting and downloading PDF files can
    take some time, especially with larger series. Checking the
    folders while downloading can cause the PDF to be out of order.
    '''
    pdf_name = input("PDF Name: ") + ".pdf"
    link = input("Enter a link: ").lower()
    link = prepare_link(link)
    directory = create_folder()
    print("Downloading...")
    get_image(link, directory)
    print("Files Downloaded")
    print("Converting to PDF, this may take some time...")
    convert_to_pdf(directory, pdf_name)
    print("PDF Finished")

    
main()
