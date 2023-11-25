import Faililugeja

file_path = "ERR_Artiklid.json"

df = Faililugeja.ReadIntoDataframe(file_path)
print(df["Date"].unique())