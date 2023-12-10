import pandas as pd
import json


# Takes a file path and reads the json data into a Pandas DataFrame
def ReadIntoDataframe(file, target_year):
    titles = []
    bodys = []
    dates = []
    columns = ["Title", "Body", "Date"]

    with open(file) as f:
        data = json.load(f)

        for year, months in data.items():
            if year == target_year:
                for month, days in months.items():
                    for day, articles in days.items():
                        for article in articles:
                            title = article.get("päis", "")
                            body = article.get("sisu", "")
                            titles.append(title)
                            bodys.append(body)
                            dates.append("{0}-{1}-{2}".format(year, month, day))

    df = pd.DataFrame(list(zip(titles, bodys, dates)), columns=columns)
    return df
