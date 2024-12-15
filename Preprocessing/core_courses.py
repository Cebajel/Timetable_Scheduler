import numpy as np
import pandas as pd

df = pd.read_excel("Data.xlsx", "Registrations")
grouped = df.groupby('Course Code')
courses = grouped.groups.keys()
# print(grouped.groups.keys())
cores = []
# print(len(grouped.groups['PH 212']))
for cour in courses:
    length = len(grouped.groups[cour])
    # print(length)
    if length < 25:
        temp = ['No'] * length
    else:
        temp = ['Yes'] * length
    cores.extend(temp)

df.Core = cores

# with pd.ExcelWriter('Data.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
#     df.to_excel(writer, 'Registrations', index=False)
#     writer.save()


