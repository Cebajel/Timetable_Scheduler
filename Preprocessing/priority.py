import numpy as np
import pandas as pd

registrations = pd.read_excel("Data.xlsx", "Registrations")
# columns = registrations.columns
print(registrations.head())
previous = None
current = None
priority_Number = 1

priority_list = []

for value in registrations.iterrows():
    value = value[1]
    current = value[1]
    if (current != previous):
        previous = current
        priority_Number = 1
    
    if value[2] == 'Yes':
        priority_list.append(0)
    else:
        priority_list.append(priority_Number)
        priority_Number += 1

registrations.Priority = priority_list
# print(registrations.head())
# with pd.ExcelWriter("Data.xlsx", mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
    # registrations.to_excel(writer, sheet_name="Registrations", index=False)  
    # writer.save()  
