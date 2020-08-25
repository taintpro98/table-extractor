#Create a function to process excel data
#create another function to create html page
#https://github.com/Knio/dominate/blob/master/README.md 
import logging, dominate, openpyxl, sys, os
from dominate.tags import *

#setup logging Debug
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

#create excel sheet processor

def excel_sheet_processor(workbookfilepath: str):
    '''
        Converts Excel Sheet data into an array with dictionaries
        arguments:
            workbookfilepath: filepath to workbook
        returns:
            list
    '''
    #open workbook
    wb = openpyxl.load_workbook(workbookfilepath)
    #select active sheet
    ws = wb.active
    #define list
    workbook_list = []
    #define keys as a list
    my_keys = []
    for col in range(0, ws.max_column):
        my_keys.append(ws.cell(row=1, column=col + 1).value)
    #define loop to convert rows to dictionaries
    for row in range(2, ws.max_row+1):
            #create dictionary
            dictionary = {}
            for pos in range(0, len(my_keys)):
                dictionary[my_keys[pos]] = ws.cell(row=row, column=pos+1).value
            workbook_list.append(dictionary)
    return workbook_list

def list_diction_to_html(workbook_list: list):
    '''
        Creates HTML Pages with table containing "list" data
        arguments:
            workbook_list; a list of dictionaries
        returns:
            html file path; str
    '''
    conv = lambda i : i or '' 

    doc = dominate.document(title="Excel Spread Sheet") #sets html title tag
    with doc.head:
        link(rel="stylesheet", href="style.css")
    with doc:
        with div(id="excel_table").add(table()):

            with thead():
                #add header
                dictionary = workbook_list[0]
                print('dictionary', dictionary)
                for key in dictionary.keys():
                    table_header = td()
                    table_header.add(p(conv(key)))

            for dictionary in workbook_list:
                #loop through row; create table row
                table_row = tr(cls="excel_table_row")
                #loop through each key in dictionary
                for key in dictionary:
                    with table_row.add(td()):
                        p(conv(dictionary[key]))
    return str(doc) #turns the document into a string

def save_dom_to_html(dom):
    '''
        Saves DOM string into newly generated HTML file
        arguments:
            dom- str
        returns:
            filepath; str
    '''
    filepath = os.path.abspath("excel.html")
    htmfile = open(filepath, "w")
    htmfile.write(dom)
    htmfile.close()
    return filepath
if __name__ == "__main__":
    filepath = os.path.abspath("/Users/macbook/Documents/Cinnamon/tabxd/scripts/Test_2/2018030500010_558404_03_2018030530002000410/pp22018030500010_558404_03_2018030530002000410.xlsx")
    list_work = excel_sheet_processor(filepath)
    if list_work:
        dom = list_diction_to_html(list_work)
        save_dom_to_html(dom)
        logging.info("test.html")