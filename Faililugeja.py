import pandas as pd
import json

# Takes a file path and reads the json data into a Pandas DataFrame
def ReadIntoDataframe(file):

    titles = []
    bodys = []
    dates = []
    columns = ["Title", "Body", "Date"]

    months = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    days = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"]

    with open(file) as f:
        data = json.load(f)

        for v in data.values():
            for month in months:
                for day in days:
                    try:
                        innder_data = v[month]
                    except KeyError: # This month does not exist in the data
                        break
                    try:
                        innder_data = innder_data[day]
                    except KeyError: # This day does not exist in the data
                        continue

                    for el in innder_data:
                        titles.append(el["päis"].strip())
                        bodys.append(el["sisu"].strip())
                        dates.append("2023-{0}-{1}".format(month, day)) # Dates format - YYYY-MM-DD
                                                                        # TODO - figure out how the choosing of year is managed

    df = pd.DataFrame(list(zip(titles, bodys, dates)), columns=columns)
    return df