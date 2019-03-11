
file = "CSV_filepath"
import pandas as pd

data = pd.read_csv(file)                #use read_csv to create dataframe
print(data.columns)                     #print key names
for i in range (0,len(data.index)):
   print(data.iloc[i])                  #print each row