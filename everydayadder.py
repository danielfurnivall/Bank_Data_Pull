import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

path = 'W:/Bank Data v2/'
bdata = 'w:/Bank Data v2/bankcurrent.xlsx'
print (os.path.getsize(bdata))

#These files are dictionaries comprising of lookups for Grade & Agency Name

grades = eval(open(path+'Grades_dic.txt').read())
agencies = eval(open(path+'Agency_dic.txt').read())

bpdcols = ['Agency Name', 'Cost Centre', 'Sector', 'Directorate', 'Hospital',
       'Ward Name (BSMS)', 'Staff Group', 'Date', 'Reason', 'Grade',
       'Shift Start', 'Shift End', 'Hours', 'Requester Name', 'Requested',
       'Filled-Bank', 'Filled-Agency', 'Area', 'Month', 'Text of month']




def initialise():
    global df

    df['Grade'] = df['Request Grade'].map(grades)



    #Rename the staff group column to prevent any nonsense
    renames = {'Nursing':'Nursing & Midwifery',
               'Admin & Clerical':'Administrative Services',
               'Midwifery':'Nursing & Midwifery'}
    df['Staff Group'] = df['Staff Group'].map(renames)

    #remove all non nursing/admin
    df = df.loc[df['Staff Group'].isin(['Nursing & Midwifery','Admin & Clerical'])]



def org_structure():
    global df
    # Text to columns on 'Org Structure' column
    split = df['Org Structure'].str.split(">", n=5, expand = True)
    df['Area'] = split[1].str.strip()
    df = df.loc[df['Area'].isin(['Acute', 'Other Functions', 'Partnership'])]
    df['Sector'] = split[2].str.strip()
    df['Hospital'] = split[3].str.split('-', n=1, expand = True)[1]
    df['Ward Name (BSMS)'] = split[4]



def request_bank_agency():
    global df
    # Make columns for request/filled-bank/filled-agency
    df['Requested'] = 1
    df['Filled-Bank'] = np.where((df['Staff'].notnull()) & (df['Agency'].isnull()),1,'')
    df['Filled-Agency'] = np.where((df['Staff'].notnull()) & (df['Agency'].notnull()),1, '')

#deal with dates
def dates():
    global df
    df['Month'] = pd.to_datetime(df['Date'], format='%d-%b-%Y').dt.strftime('01/%m/%y')
    df['Date'] = pd.to_datetime(df['Date'], format= '%d-%b-%Y').dt.strftime('%m/%d/%y')



#build agencyname columns
def agencyname():
    global df
    df['Agency Name'] = np.where(df['Filled-Agency'] == '1', df['Agency'].map(agencies),
                             np.where(df['Filled-Bank'] == '1', 'Bank','Unfilled'))


def hours():
    global df
    #deal with hours
    df.loc[df['Actual Hours'] == '24:00', 'Actual Hours'] = 0 #to fix 24 or 23:30hrs shifts that are actually 0
    df.loc[df['Actual Hours'] == '23:30', 'Actual Hours'] = 0
    #Convert mins to decimals
    df['Hours'] = np.where(df['Agency Name'] == 'Unfilled', 0,
                           np.where((df['Actual Hours'] == '24:00')|(df['Actual Hours'] == '00:00')|df['Actual Hours'] == '', 0,
                                    (pd.DatetimeIndex(df['Actual Hours']).hour) + (pd.DatetimeIndex(df['Actual Hours']).minute/60)))

def text_of_month():
    global df
    df['Text of month'] = np.where(df['Hours'] == 0, '',
                                np.where(df['Hours'] == 11, '11',
                                    np.where(df['Hours'] == '', '',
                                        np.where(df['Hours'] > 11.5, 'Over 11.5',
                                            np.where((df['Hours'] > 11) & (df['Hours'] <= 11.5), '11-11.5',
                                                np.where(df['Hours'] < 11, '01-10', '?'))))))


def cleaning():
    global df, dffinal
    df1 = df.loc[df['Request Grade'] == '']
    if len(df1) > 0:
        for i in df1:
            print('WARNING: '+df1['Request Grade'][i]+' - not found in existing lookup - please address this')
    df['Shift Start'] = df['Start']
    df['Shift End'] = df['End']

    df['Reason'] = df['Request Reason']
    df['Requester Name'] = df['Booking Source']
    df['Directorate'] = df['Request Grade'].str.split().str[-1]
    dffinal = df[bpdcols]
#dffinal.to_excel(path+'testdata.xlsx', index=False)
#df['Agency'] = np.where(df['Filled-Bank'] == 1, )

def filework():
    global df, dffinal
    if os.path.exists(path+'bankcurrent.xlsx'):
        dfmain = pd.read_excel(path+'bankcurrent.xlsx')
        # dfmain['Date'] = dfmain['Date'].dt.strftime('%m/%d/%y')
        # dfmain['Month'] = dfmain['Date'].dt.strftime('%m/01/%y')
        # dfmain['Date'] = dfmain['Date'].dt.strftime('%d-%b-%Y')

        dfmain = dfmain.append(dffinal)

        print(len(dfmain))
        dfmain.drop_duplicates(keep='last', inplace=True)
        print(len(dfmain))
        dfmain.to_excel(path+'bankcurrent.xlsx', index=False)

    else:
        dffinal.to_excel(path + 'bankcurrent.xlsx', index=False)

def parent():
    initialise()
    org_structure()
    request_bank_agency()
    dates()
    agencyname()

    hours()
    text_of_month()
    cleaning()
    filework()

list_of_files = glob.glob(path + 'extracts/*')
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)
df = pd.read_csv(latest_file)
parent()
# for i in os.listdir(path+'Extracts/'):
#
#     df = pd.read_csv(path + 'extracts/' + i)  # opens extract file
#     print('Current file - ' + i)
#     parent()