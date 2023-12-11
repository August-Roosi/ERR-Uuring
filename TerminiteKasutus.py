import Faililugeja
import estnltk
from estnltk import Text
from collections import Counter
import matplotlib.pyplot as plt

faili_nimed = ["ERR_Artiklid_Umbes_Kolm_Aastat/ERR_Artiklid.json"]

huvipakkuvad_sonad = [
    "chatgpt",
    "suitsiid",
    "enesetapp",
    "tehisintellekt",
    "pandeemia",
    "valitsus",
    "5g",
    "vandenõuteooria",
    "sõda",
    "ukraina",
    "nutitelefon",
    "telefon",
    "krüpto",
    "krüptovaluuta",
    "annekteerima",
    "tuumasõda",
    "kaugtöö",
    "kodukontor",
    "distantsõpe",
    "kaugõpe",
    "bitcoin",
    "vr",
    "virtuaalreaalsus",
]
counts = Counter(
    {
        "chatgpt": 0,
        "suitsiid": 0,
        "enesetapp": 0,
        "tehisintellekt": 0,
        "pandeemia": 0,
        "valitsus": 0,
        "5g": 0,
        "vandenõuteooria": 0,
        "sõda": 0,
        "ukraina": 0,
        "nutitelefon": 0,
        "telefon": 0,
        "krüpto": 0,
        "krüptovaluuta": 0,
        "annekteerima": 0,
        "tuumasõda": 0,
        "kaugtöö": 0,
        "kodukontor": 0,
        "distantsõpe": 0,
        "kaugõpe": 0,
        "bitcoin": 0,
        "vr": 0,
        "virtuaalreaalsus": 0,
    }
)
# failinimi = "ERR_Artiklid.json"
j = 0

output_failid = ["2023_sonade_sagedus.csv"]
aastad = ["2023"]

for failinimi in faili_nimed:
    df = Faililugeja.ReadIntoDataframe(failinimi, aastad[j])
    print(df.head())
    i = 0

    for index, row in df.iterrows():
        if i % 2000 == 0:
            print(i)

        text = Text(row["Body"])
        text = text.tag_layer()
        text = text.morph_analysis

        for el in text.lemma:
            for lemma in el:
                if lemma.lower() in huvipakkuvad_sonad:
                    counts.update([lemma.lower()])

        i += 1

    with open(output_failid[j], "w") as f:
        for k, v in counts.most_common():
            f.write("{0},{1}\n".format(k, v))

    j += 1

print(i)
# plt.bar(*zip(*counts.items()))
# plt.show()
