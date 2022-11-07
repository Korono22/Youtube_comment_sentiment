import config
from googleapiclient.discovery import build
from textblob import TextBlob
import translators
import re
import statistics

ILOSC_KOMENTARZY = 15

link = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})')
id = link.match(input("Podaj link do filmiku:\n"))
video_id = id.group('id')

#Youtube API jest schowany w config.py
resource = build('youtube', 'v3', developerKey=config.YOUTUBE_API)
request = resource.commentThreads().list(part="snippet", videoId=video_id, maxResults=ILOSC_KOMENTARZY, order="orderUnspecified") # orderUnspecified, time, relevance
response = request.execute()
items = response["items"][:ILOSC_KOMENTARZY]
lista = [] # lista sentymentu komentarzy
pierwsza_iteracja = True
for item in items:
    komentarz = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    # Tłumaczymy ponieważ analizator czyta tylko po angielsku
    tlumaczenie = translators.google(komentarz) # default: from_language='auto', to_language='en'
    sentyment = TextBlob(tlumaczenie)
    ocena = sentyment.sentiment.polarity
    # w razie czego jakby pierwszy badany komentarz był najlepszy bądź najgorszy
    if pierwsza_iteracja == True:
        najlepszy_komentarz = komentarz
        najgorszy_komentarz = komentarz
        pierwsza_iteracja = False
    try:
        if ocena > poprzednia_ocena:
            najlepszy_komentarz = komentarz
            ocena_najlepszego = ocena
        if ocena < poprzednia_ocena:
            najgorszy_komentarz = komentarz
            ocena_najgorszego = ocena
    except:
        pass
    lista.append(ocena)
    poprzednia_ocena = ocena

    if sentyment.polarity > ocena:
        najlepszy_komentarz = sentyment
print(f"Srednia sentymentu {ILOSC_KOMENTARZY} komentarzy w skali -1 do 1 to {statistics.mean(lista)}")
print(f"Najlepszy komentarz to \"{najlepszy_komentarz}\" z ocena {ocena_najlepszego}")
print(f"Najgorszy komentarz to \"{najgorszy_komentarz}\" z ocena {ocena_najgorszego}")