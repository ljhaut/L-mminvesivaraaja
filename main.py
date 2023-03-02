import requests
import xmltodict
from datetime import datetime, timedelta

def getSPOT(today, tomorrow):

    payload = {'securityToken':'3baa6934-0db0-4356-8687-c4ab205b6305','documentType':'A44','in_Domain':'10YFI-1--------U', 'out_Domain':'10YFI-1--------U',
    'periodStart': f'{today}0000','periodEnd':f'{tomorrow}0000'}

    r = requests.get('https://web-api.tp.entsoe.eu/api', params=payload)

    xml_string = r.content.decode('utf-8')

    xml_dict = xmltodict.parse(xml_string)

    return xml_dict

def todayTomorrow():
    today = datetime.now().strftime('%Y%m%d')
    tomorrow = datetime.now() + timedelta(1)
    tomorrow = tomorrow.strftime('%Y%m%d')
    return today, tomorrow

def keskiarvot():
    keskiarvot = []

    for i in range(len(spotToday)-3):
        ka = (float(spotToday[i]['price.amount'])+float(spotToday[i+1]['price.amount'])+float(spotToday[i+2]['price.amount'])+float(spotToday[i+3]['price.amount'])) / 4
        tunnit = str(int(spotToday[i]['position'])-1) + '-' + str(int(spotToday[i+3]['position'])-1)

        keskiarvot.append({'keskiarvo': ka, 'tunnit': tunnit})

    print(keskiarvot)

    mi = min(keskiarvot, key=lambda x: float(x['keskiarvo']))
    ma = max(keskiarvot, key=lambda x: float(x['keskiarvo']))

    print('\n',mi, ma)


today, tomorrow = todayTomorrow()

spot = getSPOT(today, tomorrow)

spotToday = spot["Publication_MarketDocument"]["TimeSeries"][0]["Period"]["Point"]
spotTomorrow = spot["Publication_MarketDocument"]["TimeSeries"][1]["Period"]["Point"]

sort = sorted(spotToday, key=lambda x: float(x['price.amount']), reverse=False)

print(today)
print(tomorrow)

print(spotToday)
print('\n')

keskiarvot()