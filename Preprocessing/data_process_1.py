import numpy as np
import pandas as pd

df1 = pd.read_excel("Testing data/Pre-registration_Au_2023-24.xlsx", "Sheet 1 - Pre-registration_Au_2")

df = pd.DataFrame(columns=["Course Code", "Roll No", "Core", "Priority"])

print(df1.head())

for _, value in df1.iterrows():
    roll_number = value[1]
    roll_number = roll_number.split("@")[0]
    courses = value[4]
    if(type(courses) == str):
        courses = courses.split(";")
        for index, course in enumerate(courses):
            courses[index] = course.split(":")[0]
    else:
        courses = []
    number_of_courses = len(courses)
    temp_df = pd.DataFrame({"Course Code":courses,
                            "Roll No":[roll_number]*number_of_courses,
                            "Core":["Yes"]*number_of_courses,
                            "Priority": [0]*number_of_courses})
    df = pd.concat([df, temp_df], ignore_index=True)
    # print(roll_number)
    # break

print(df)

# with pd.ExcelWriter("Test_data.xlsx", mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
#     df.to_excel(writer, sheet_name="Registrations", index=False, startrow=writer.sheets["Registrations"].max_row, header=None)  
#     writer.save()  
