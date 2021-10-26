import re
import cv2
import pytesseract
from pytesseract import Output

class DrivingLicense():
  def __init__(self, location):
    self.img = cv2.imread(location)
    self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
    self.img = cv2.resize(self.img, None, fx=2, fy=2)
    self.img_data = pytesseract.image_to_data(self.img, output_type=Output.DICT)
    self.img_data = self.remove_spaces()
    

  def clean_name(self, s):
    return re.sub('[^A-Za-z0-9]+', '', s)

  def remove_spaces(self):
    d = self.img_data
    regex = '\s*$'
    result_list = []
    for data in d['text']:
      if re.match(regex, data) == None:    # If it is not a Space
        result_list.append(data)
    d['text'] = result_list
    self.img_data = d 
    return d

  def license_number(self):
    d = self.img_data
    regex_state = '^([a-z|A-Z]{2}[0-9]{2})'
    regex_num = '^((19|20)[0-9][0-9])[0-9]{7}$'
    for i in range(len(d['text'])):
      if i<len(d['text'])-1 and re.match(regex_state, d['text'][i]) and re.match(regex_num, d['text'][i+1]):
        dl_no = d['text'][i].upper() +  d['text'][i+1]
        return dl_no
    

  def extract_name(self):
    d = self.img_data
    for i in range(len(d['text'])):
      if d['text'][i].lower() == 'name':
        if i+2 < len(d['text']):
          first_name = d['text'][i+1]
          last_name = d['text'][i+2]
    name = self.clean_name(first_name) + ' '+ self.clean_name(last_name)
    return name
  def extract_dates(self):
    d = self.img_data
    dates = {}
    for i in range(len(d['text'])):
      if re.match(r'\d{2}-\d{2}-\d{4}', d['text'][i]) != None:
        if i-1>=0 and d['text'][i-1].upper() == 'DOB':
          dates['DOB'] = d['text'][i]
        elif i-2>=0 and d['text'][i-2].upper() == 'ISSUED' and d['text'][i-1].upper() == 'ON':
          dates['ISSUE'] = d['text'][i]
        elif i-3>=0 and (d['text'][i-1].upper() == 'TILL' or d['text'][i-2].upper() == 'TILL'):
          dates['VALIDITY'] = d['text'][i]
    return dates

# dl = DrivingLicense('DrivingLicense.jpg')
# print(dl.license_number())
# print(dl.extract_name())