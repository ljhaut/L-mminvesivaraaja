import requests
import xmltodict
import json
from datetime import datetime, timedelta


# Haetaan data Entso-E:n API-rajapinnasta HTTP GET - requestilla, saadaan xml muotoista dataa
# Parametreina aikaperiodi, jolta halutaan dataa
def getSPOT(today, tomorrow):

    payload = {'securityToken':'3baa6934-0db0-4356-8687-c4ab205b6305','documentType':'A44','in_Domain':'10YFI-1--------U', 'out_Domain':'10YFI-1--------U',
    'periodStart': f'{today}0000','periodEnd':f'{tomorrow}0000'}

    r = requests.get('https://web-api.tp.entsoe.eu/api', params=payload)

    xml_string = r.content.decode('utf-8')

    xml_dict = xmltodict.parse(xml_string)

    return xml_dict



# Määritellään ja formatoidaan haluttavat päivämäärät oikein
def todayTomorrow():
    today = datetime.now().strftime('%Y%m%d')
    tomorrow = datetime.now() + timedelta(1)
    tomorrow = tomorrow.strftime('%Y%m%d')
    return today, tomorrow



# Laskee ja esittää päivän sähköhinnan keskiarvon neljältä peräkkäiseltä tunnilta, sekä etsii niistä halvimman ja kalleimman arvon
# Parametrina lista hinnoista tietyltä päivältä
def keskiarvot(lista):
    keskiarvot = []

    for i in range(len(lista)-3):
        ka = (float(lista[i]['price.amount'])+float(lista[i+1]['price.amount'])+float(lista[i+2]['price.amount'])+float(lista[i+3]['price.amount'])) / 4
        tunnit = str(int(lista[i]['position'])-1) + '-' + str(int(lista[i+3]['position']))

        keskiarvot.append({'keskiarvo': ka, 'tunnit': tunnit})

    print(keskiarvot)

    mi = min(keskiarvot, key=lambda x: float(x['keskiarvo']))
    ma = max(keskiarvot, key=lambda x: float(x['keskiarvo']))

    print('\n',"halvin:",mi,"kallein:", ma)



# Tallentaa arvot "data.json" tiedostoon
# Parametreina päivä ja sen päivän arvot
def tallennaArvot(lista, aika):

    tallennettava = {"pvm": aika, "hinnat": lista}

    with open("data.json") as f:
        file = json.load(f)
        f.close()

    if not any(d["pvm"] == aika for d in file):

        file.append(tallennettava)

        with open("data.json", "w", encoding="utf-8")as f:
            json.dump(file, f, ensure_ascii=False, indent=4)
            f.close()
        print("Tiedostoon tehty lisäys päivälle", aika)
    else:
        print("Päivällä", aika, "on jo olemassa listaus tiedostossa")
        return




today, tomorrow = todayTomorrow()

today = '20230310'
tomorrow = '20230311'

spot = getSPOT(today, tomorrow)

spotToday = spot["Publication_MarketDocument"]["TimeSeries"][0]["Period"]["Point"]
spotTomorrow = spot["Publication_MarketDocument"]["TimeSeries"][1]["Period"]["Point"]

sort = sorted(spotToday, key=lambda x: float(x['price.amount']), reverse=False)

print(today)
print(tomorrow)

print(spotToday)
print('\n')
tallennaArvot(spotToday, today)
print('\n')

keskiarvot(spotToday)