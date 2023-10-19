# import numpy as np
import pandas as pd
import math

df1 = pd.read_excel("Testing data/Pre-registration_Au_2023-24.xlsx", "Sheet 1 - Pre-registration_Au_2")
df1 = df1.drop(['Timestamp', 'Department', 'Programme', 'Choose your list of core courses'], axis=1)

# df2 = pd.read_excel("Test_data.xlsx", "Registrations") 

df = pd.DataFrame(columns=["Course Code", "Roll No", "Core", "Priority"])

print(df1.head())

for _, value in df1.iterrows():
    roll_number = value['Username']
    roll_number = roll_number.split("@")[0]
    my_val = dict(value[1:])
    # print(my_val)
    priority = []
    courses = []

    for key, course in my_val.items():
        if(not math.isnan(course)):
            priority.append(int(course))
            key = key.split(":")[0]
            key = key.split("[")[1]
            courses.append(key)
    # continue
    # print(courses)
    # print(priority)

    number_of_courses = len(courses)
    temp_df = pd.DataFrame({"Course Code":courses,
                            "Roll No":[roll_number]*number_of_courses,
                            "Core":["No"]*number_of_courses,
                            "Priority": priority})
    df = pd.concat([df, temp_df], ignore_index=True)
    # print(roll_number)
    # break

print(df)

# with pd.ExcelWriter("Test_data.xlsx", mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
#     df.to_excel(writer, sheet_name="Registrations", index=False, startrow=writer.sheets["Registrations"].max_row, header=None)  
#     writer.save()  
