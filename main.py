import requests
import json
import xmltodict

def getSPOT():

    payload = {'securityToken':'3baa6934-0db0-4356-8687-c4ab205b6305','documentType':'A44',
    'periodStart':'202210280000','periodEnd':'202210290000'}

    r = requests.get('https://web-api.tp.entsoe.eu/api', params=payload)

    print (r.content)

    with open(r.content) as xmlfile:
        data = xmltodict.parse(xmlfile.read())
        jsondata = json.dumps(data)


    return jsondata

getSPOT()