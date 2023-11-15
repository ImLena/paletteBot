from bs4 import BeautifulSoup
import requests

if __name__ == '__main__':
    url_name = "https://masterkraski.ru/koler/ncs.php"
    url = requests.get(url_name)
    page = BeautifulSoup(url.text, "html.parser")
    colors = page.find_all("div", {"class": "col-sm-2 col-xs-6 koler"})

    file = open("../data/ncs_code.csv", "w")
    file.write("id,r,g,b\n")

    for color in colors:
        id = color.find("span")
        rgb = color.find_all("p")
        pair = []
        for p in rgb:
            s = p.text
            if "Код RGB" in s:
                s = s.split()
                pair = [id.string, s[2], s[3], s[4]]
                file.write(','.join(pair))
                file.write("\n")

    file.close()
