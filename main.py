import requests
import xmltodict
from datetime import datetime, timedelta
from operator import itemgetter

def getSPOT(today, tomorrow):

    payload = {'securityToken':'3baa6934-0db0-4356-8687-c4ab205b6305','documentType':'A44','in_Domain':'10YFI-1--------U', 'out_Domain':'10YFI-1--------U',
    'periodStart': f'{today}0000','periodEnd':f'{tomorrow}0000'}

    r = requests.get('https://web-api.tp.entsoe.eu/api', params=payload)

    xml_string = r.content.decode('utf-8')

    xml_dict = xmltodict.parse(xml_string)

    return xml_dict

today = datetime.now().strftime('%Y%m%d')
tomorrow = datetime.now() + timedelta(1)
tomorrow = tomorrow.strftime('%Y%m%d')
print(today)
print(tomorrow)

today = '20230218'
tomorrow = '20230219'

spot = getSPOT(today, tomorrow)

spotToday = spot["Publication_MarketDocument"]["TimeSeries"][0]["Period"]["Point"]
spotTomorrow = spot["Publication_MarketDocument"]["TimeSeries"][1]["Period"]["Point"]

sort = sorted(spotToday, key=lambda x: float(x['price.amount']), reverse=False)

print(sort)