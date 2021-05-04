import numpy as np
import pandas as pd

import sys

sys.path.append('./modules')
import sqldb
import pdfreader
import PyPDF2

pdffile = "C:\\Users\\chery\\Documents\\BBD\\ESPN\\2019_auction_values.pdf"
# creating a pdf file object
pdfFileObj = open(pdffile, 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(0)

# extracting text from page
print(pageObj.extractText())

# closing the pdf file object
pdfFileObj.close()