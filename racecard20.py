import json
import pandas as pd
import gspread
from itertools import cycle
from gspread_dataframe import set_with_dataframe
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials

#Test sheet

#1. Load JSON file
with open('C:/Users/conor/rpscrape/racecards/2025-04-20.json', 'r') as f: #set this to your path of ./rpscrape today (todays card)
    data = json.load(f)

#2. Prepare data rows
rows = []

# Go through each race
for country in data:
    for track in data[country]:
        for race_time in data[country][track]:
            race = data[country][track][race_time]
            off_time = race.get('off_time', race_time)
            course = track
            distance = race.get('distance', '')
            going = race.get('going', '')
            type = race.get('type', '')
            
            for runner in race.get('runners', []):
                course_stats = runner.get('course', {})
                distance_stats = runner.get('distance', {})
                going_stats = runner.get('going', {})
                field_stats = runner.get('field_size', {})
                class_stats = runner.get('class', {})
                type_stats = runner.get('type', {})
                
                rows.append({
                    'TIME': off_time,
                    'TRACK': course,
                    'TYPE': type,
                    'DISTANCE': distance,
                    'GOING': going,
                    'HORSE NAME': runner.get('name', ''),
                    'AGE': runner.get('age', ''),
                    'SEX': runner.get('sex', ''),
                    'JOCKEY': runner.get('jockey', ''),
                    'TRAINER': runner.get('trainer', ''),
                    'WEIGHT (lbs)': runner.get('lbs', ''),
                    'RPR': runner.get('rpr', ''),
                    'FORM': runner.get('form', ''),
                    'LAST RUN': runner.get('last_run', ''),
                    'Headgear': runner.get('headgear', ''),
                    'Headgear_first': runner.get('headgear_first', ''),
                    'SP': runner.get('sp', ''),
                    
                    # --- Now Performance Stats ---
                    'Course Runs': course_stats.get('runs', ""),
                    'Course Wins': course_stats.get('wins', ''),
                    'Distance Runs': distance_stats.get('runs', ''),
                    'Distance Wins': distance_stats.get('wins', ''),
                    'Going Runs': going_stats.get('runs', ''),
                    'Going Wins': going_stats.get('wins', ''),
                    'Field Size Runs': field_stats.get('runs', ''),
                    'Field Size Wins': field_stats.get('wins', ''),
                    'Class Runs': class_stats.get('runs', ''),
                    'Class Wins': class_stats.get('wins', ''),
                    'COMMENT': runner.get('comment', ''),
                })

#3. Make DataFrame
df = pd.DataFrame(rows)
#sort by time (note in 12 hour format - foreign racing (Sha tin, etc..) will be at the bottom..
df['TIME_SORTABLE'] = pd.to_datetime(df['TIME'], format='%I:%M').dt.time
df = df.sort_values('TIME_SORTABLE')
df = df.drop(columns=['TIME_SORTABLE'])

#4. Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\conor\Downloads\racecardstoday1.json', scope) #set this as your key from google cloud json
client = gspread.authorize(creds)

spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1y9SXRlao2lRuaEhzfyhQU2ID5xWtsuUKkSQ6wXMbyjI/edit#gid=0") #assign url manually
worksheet = spreadsheet.sheet1

# Step 5 - Upload DataFrame
worksheet.clear()
set_with_dataframe(worksheet, df)

# 1. Set up a few basic background colors to rotate
colors = cycle([
    (1, 0.9, 0.9),   # light pink
    (0.9, 1, 0.9),   # light green
    (0.9, 0.9, 1),   # light blue
    (1, 1, 0.8),     # light yellow
    (0.95, 0.85, 1), # light purple
])

# 2. Make a color map: TIME -> Color
unique_times = df['TIME'].drop_duplicates().tolist()
time_to_color = {time: next(colors) for time in unique_times}



# for bold text
bold_format = CellFormat(
    textFormat=TextFormat(bold=True)
)
#headers in bold
format_cell_range(worksheet, 'A1:Z1', bold_format) 

[]
# 3. Color each row by its race TIME
# Group rows by race time
race_time_groups = {}
for idx, row in enumerate(df.itertuples(), start=2):  # start=2 to skip header
    race_time = getattr(row, 'TIME')
    if race_time not in race_time_groups:
        race_time_groups[race_time] = []
    race_time_groups[race_time].append(idx)

# Apply formatting in bulk by race time
for race_time, rows in race_time_groups.items():
    color = time_to_color[race_time]
    fmt = CellFormat(
        backgroundColor=Color(*color),
        textFormat=TextFormat(bold=False),
    )
    # Apply formatting to the entire range for the grouped rows
    range_str = f'A{min(rows)}:Z{max(rows)}'  # Format from the first to the last row in the group
    format_cell_range(worksheet, range_str, fmt)

# 4. Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\conor\Downloads\racecardstoday1.json', scope) #set this as your key from google cloud json
client = gspread.authorize(creds)

# 5. Open your Google Sheet
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1y9SXRlao2lRuaEhzfyhQU2ID5xWtsuUKkSQ6wXMbyjI/edit#gid=0") #assign url manually
worksheet = spreadsheet.sheet1


# 6. Upload data
worksheet.clear()  # optional: clear old data
set_with_dataframe(worksheet, df)

print("✅ Racecard data uploaded to Google Sheets!")
