import requests

url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/symbols"

headers = {
	"X-RapidAPI-Key": "bf14f36e15msh34de1f4d075f571p1fbb59jsndb8e58302711",
	"X-RapidAPI-Host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())