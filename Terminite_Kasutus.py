import Faililugeja
import estnltk
from estnltk import Text
from collections import Counter
import matplotlib.pyplot as plt

# Columns = ["Title", "Body", "Date"]
faili_nimed = ["ERR_Artiklid.json"]

huvipakkuvad_sonad = ["chatgpt", "suitsiid", "enesetapp", "tehisintellekt"]
counts = Counter({'chatgpt': 0, 'suitsiid': 0, 'enesetapp': 0, 'tehisintellekt': 0})
#failinimi = "ERR_Artiklid.json"


for failinimi in faili_nimed:
    df = Faililugeja.ReadIntoDataframe(failinimi)
    #print(df["Date"].unique())

    for index, row in df.iterrows():
        text = Text(row["Body"])
        text = text.tag_layer()
        text = text.morph_analysis

        for el in text.lemma:
            for lemma in el:
                if (lemma.lower() in huvipakkuvad_sonad):
                    counts.update([lemma.lower()])

    with open("test.tsv", "w") as f:
        for k, v in counts.most_common():
            f.write("{0}\t{1}\n".format(k, v))

    print(counts)

plt.bar(*zip(*counts.items()))
plt.show()