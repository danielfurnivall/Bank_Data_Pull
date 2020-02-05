import pandas as pd
import os
import datetime
import numpy as np
bdata = 'w:/Bank Data v2/bankcurrent.xlsx'

size = os.path.getsize(bdata)
print(size)
if size > 31457280:
 print("file is too large")
 time1 = datetime.datetime.now()

 df = pd.read_excel(bdata)
 print(df.dtypes)
 df['Month'] = pd.to_datetime(df['Month'], dayfirst=True)
 df['Date'] = pd.to_datetime(df['Date'])

 time2 = datetime.datetime.now()
 print((time2 - time1), ' seconds')
 lowestmonth = (df['Month'].min())
 time3 = datetime.datetime.now()

 print((time3-time2), ' seconds')
 df = df[df['Month'] != lowestmonth]
 df['Month'] = df['Date'].dt.strftime('01/%m/%y')
 df['Date'] = df['Date'].dt.strftime('%m/%d/%y')
 df['Text of month'] = np.where(df['Hours'] == 0, '',
                                np.where(df['Hours'] == 11, '11',
                                         np.where(df['Hours'] == '', '',
                                                  np.where(df['Hours'] > 11.5, 'Over 11.5',
                                                           np.where((df['Hours'] > 11) & (df['Hours'] <= 11.5),
                                                                    '11-11.5',
                                                                    np.where(df['Hours'] < 11, '01-10', '?'))))))
 df.to_excel('W:/Bank Data v2/onemonthgone.xlsx', index=False)
 print(os.path.getsize('W:/Bank Data v2/onemonthgone.xlsx'))
else:
    print("File to ")


