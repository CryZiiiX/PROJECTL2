import requests

def convertir_devises(montant, devise_base, devise_cible):
    url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/convert"
    querystring = {"from": devise_base, "to": devise_cible, "amount": montant}
    headers = {
	"X-RapidAPI-Key": "bf14f36e15msh34de1f4d075f571p1fbb59jsndb8e58302711",
	"X-RapidAPI-Host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
}

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if data['success']:
        resultat_conversion = data['result']
        print(f"{montant} {devise_base} est équivalent à {resultat_conversion:.2f} {devise_cible} au taux de change actuel.")
        return resultat_conversion
    else:
        print("Il y a eu une erreur avec la requête de conversion.")
        return None

# Utilisation de la fonction
montant_a_convertir = 750  # Vous pouvez changer ce montant
devise_base = 'USD'
devise_cible = 'EUR'
convertir_devises(montant_a_convertir, devise_base, devise_cible)

