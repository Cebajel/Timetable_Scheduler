# import pandas as pd

# df1 = pd.read_excel("Testing data/Core_Courses_Students_Details_2023_24_Au.xlsx", "2020_ME_Students")
# df2 = pd.read_excel("Testing data/Core_Courses_Students_Details_2023_24_Au.xlsx", "ME_Core_Courses_VII")

# df = pd.DataFrame(columns=["Course Code", "Roll No", "Core", "Priority"])

# # print(df1.head())

# roll_numbers = df1['Roll No'].to_list()
# courses_list = df2['Course code'].to_list()
# print(courses_list)
# print(roll_numbers)

# number_of_students = len(roll_numbers)
# for course in courses_list:
#     temp_df = pd.DataFrame({"Course Code":[course]*number_of_students,
#                             "Roll No":roll_numbers,
#                             "Core":["Yes"]*number_of_students,
#                             "Priority": [0]*number_of_students})
#     df = pd.concat([df, temp_df], ignore_index=True)

# # print(df)

# with pd.ExcelWriter("Test_data.xlsx", mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
#     df.to_excel(writer, sheet_name="Registrations", index=False, startrow=writer.sheets["Registrations"].max_row, header=None)  
#     writer.save()  

import pandas as pd

df = pd.read_excel("Test_data.xlsx", "Registrations")
courses = df["Course Code"].to_list()
courses = set(courses)
check = set(['CS 311', 'EE 201', 'EE 202', 'EE 205', 'EE 210',
         'EE 221', 'EE 229', 'EE 311', 'EE 315', 'EE 319',
         'EE 612', 'EE 613', 'EE 625', 'ME 201', 'ME 203',
         'ME 204', 'ME 207', 'ME 210', 'ME 212', 'ME 212',
         'ME 218', 'ME 311', 'ME 412', 'ME 413', 'ME 425',
         'ME 605', 'ME 607', 'ME 608', 'ME 609', 'ME 629',
         'ME 634', 'ME 634', 'ME 651', 'PH 302', 'PH 304',
         'X 1', 'X 10', 'X 2', 'X 3', 'X 6'])
print(courses.intersection(check))
print(len(courses.intersection(check)))