# import numpy as np
import pandas as pd
import math

df1 = pd.read_excel("Testing data/Common_Courses_Autumn_2023-24_2023 Batch.xlsx", "Sheet1")
# df1 = df1.drop(['Timestamp', 'Department', 'Programme', 'Choose your list of core courses'], axis=1)

# df2 = pd.read_excel("Test_data.xlsx", "Registrations") 

course_codes = df1['Course code'].to_list()

df = pd.DataFrame(columns=["Course Code", "Roll No", "Core", "Priority"])

print(course_codes)
for code in course_codes:
    # roll_number = 230010001
    # continue
    # print(courses)
    # print(priority)
    for roll_number in range(230010001, 230010301):
        temp_df = pd.DataFrame({"Course Code" : [code],
                                "Roll No": [roll_number],
                                "Core": ["Yes"],
                                "Priority": [0]})
        df = pd.concat([df, temp_df], ignore_index=True)
    # print(roll_number)
    # break

print(df)

# with pd.ExcelWriter("Test_data.xlsx", mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
#     sheet = "Registrations-test"
#     df.to_excel(writer, sheet_name=sheet, index=False, startrow=writer.sheets[sheet].max_row, header=None)  
#     writer.save()  
