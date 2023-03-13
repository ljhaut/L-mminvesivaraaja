import requests
import xmltodict
import json
import time
#import RPi.GPIO as GPIO
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


# Palauttaa listan arvojen kolme halvinta tuntia
# tulos: palauttaa listan dictejä halvoista tunneista
# pos: palauttaa listan tunneista, jolloin halpaa
def halvimmat(lista):
    
    sort = sorted(lista, key=lambda x: float(x['price.amount']), reverse=False)
    
    tulos = [sort[0], sort[1], sort[2]]
    pos = [sort[0]['position'], sort[1]['position'], sort[2]['position']]
    print("halvimmat:", tulos, pos)

    return tulos, pos



def main():

    #Alustetaan relekortti
    ''' Relay = [5, 6, 13, 16, 19, 20, 21, 26]

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for i in range(0,8):
        GPIO.setup(Relay[i], GPIO.OUT)
        GPIO.output(Relay[i], GPIO.HIGH)
 '''

    päällä = False

    today, tomorrow = todayTomorrow()

    today = '20230310'
    tomorrow = '20230311'

    spot = getSPOT(today, tomorrow)

    spotToday = spot["Publication_MarketDocument"]["TimeSeries"][0]["Period"]["Point"]
    spotTomorrow = spot["Publication_MarketDocument"]["TimeSeries"][1]["Period"]["Point"]

    print(today)
    print(tomorrow)

    print(spotToday)
    print('\n')
    print(spotTomorrow)
    print('\n')
    tallennaArvot(spotToday, today)
    print('\n')

    keskiarvot(spotToday)

    halvat, halvpos = halvimmat(spotToday)

    while True:

        print("\n UUSI KIERROS \n")

        tunti = datetime.now() + timedelta(hours=1)
        tunti = tunti.replace(minute=0,second=0)
        pos = tunti.strftime("%H")
        tunti = tunti.strftime("%H:%M:%S")

        if pos[0] == '0': 
            pos = pos[1:]

        print("position:", pos)
        print("seuraava tunti:", tunti)

        while datetime.now().strftime("%H:%M:%S") < tunti:
                
                # Jos tämän tunnin hinta on halvimpien joukossa, kytketään rele päälle
                if any(d == pos for d in halvpos):
                    if not päällä:
                        time.sleep(2)
                        print("Rele päällä")
                        päällä = True
                        ''' try:
                            GPIO.output(5, GPIO.LOW)
                        except:
                            GPIO.cleanup() '''
                    else:
                        print("Rele on jo päällä")
                else: 
                    time.sleep(2)
                    print("Rele pois päältä")
                    päällä = False
                    #GPIO.output(5, GPIO.HIGH)

                nyt = datetime.now().strftime("%H:%M:%S")
                print(nyt)

                time.sleep(2)


main()