import requests
import re
from datetime import datetime
import yaml

days = {"Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch", "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samdtag", "Sunday": "Sonntag"} 

def get_config():
    with open("/home/maxlkp/mensa_bot/src/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

def get_day_date():
    date = datetime.now().strftime("%d.%m.%Y")
    day = days[f"{datetime.now().strftime("%A")}"]
    return date, day

def get_gerichte(mensa, day = None, date = None):
    config = get_config()
    if day == None and date == None:
        date, day = get_day_date()
    elif day != None and date != None:
        day = day
        date = date

    try:
        url = config["mensen"][f"{mensa}"]
        response = requests.get(url).text

        pattern = rf"{day}, {date}"
        substrings = re.findall(rf"{pattern}(.*?)(?={pattern}|$)", response)
        kategorien = ["Tellergericht", "Tellergericht vegetarisch", "Vegetarisch", "Klassiker", "Pizza des Tages", "Express", "Pizza Classics", "Wok", "Burger Classics", "Burger der Woche", "Hauptbeilagen", "Nebenbeilage"]

        results = {}
        gerichte_raw = {}
        gerichte = {}

        for kategorie in kategorien:
            result = substrings[0].find(kategorie)
            results[kategorie] = result

        for i in range(len(kategorien) - 1):
            gerichte_raw[f"{kategorien[i]}"] = substrings[0][results[f"{kategorien[i]}"]:results[f"{kategorien[i + 1]}"]]
        gerichte_raw[f"{kategorien[-1]}"] = substrings[0][results[f"{kategorien[-1]}"]:]

        for kategorie in kategorien:
            if kategorie in gerichte_raw and len(gerichte_raw[kategorie]) != 0:
                if "Geschlossen" in gerichte_raw[kategorie]:
                    gerichte[kategorie] = "Geschlossen"
                else:
                    gerichte[kategorie] = gerichte_raw[kategorie].split(r'menue-nutr', 1)[1].split(r"</span>", 1)[1].split(r"<sup>", 1)[0].split(r"<span", 1)[0]
            else: gerichte[kategorie] = "Kein Gericht"

        return gerichte
    except Exception as e:
        print("Couldn't find entries. Is the date set correct?")
        for kategorie in kategorien:
            gerichte[kategorie] = "Kein Gericht"
        return gerichte
