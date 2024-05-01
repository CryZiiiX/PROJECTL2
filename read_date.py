from datetime import datetime
import dateparser
# pip install dateparser
import re
import os

def extract_date(content):

    # on accepte 29-04-2024 et 29/04/2024 et 29.04.2024 et 29 04 2024 et 29_04_2024
    match = re.search(r'\b(\d{1,2})[-_/. ](\d{1,2})[-_/. ](\d{4})\b', content)

    if match:
        # r'[]: on prend ce qui suit comme une raw string (pas d'échappement)
        # on cherche tous les caractères qui appartiennent à '-', '_', '/', '.', ou un espace.
        # on remplace les caractères par un tiret
        # on renvoie la chaîne entière modifiée sous forme de string
        date_str = re.sub(r'[-_/. ]', '-', match.group(0))

        try:
            # on convertit la str date_str au format DD-MM-YYYY en objet date
            date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()

            # on formatte l'objet date en chaîne au format DD-MM-YYYY
            date_str_format = date_obj.strftime('%d-%m-%Y')

            # on retourne une str
            return date_str_format

        except ValueError:
            pass  # Ignorer les dates qui ne correspondent pas au format attendu

    # pour les formats 29 avril 2024
    match2 = re.search(r'\b(\d{1,2}) (\w+),? (\d{4})\b', content)
    if match2:
        try:
            # Récupération du texte correspondant à la date
            date_text = match2.group(0)
            date_obj = dateparser.parse(date_text, languages=['fr'])

            # on formatte l'objet date en chaîne au format DD-MM-YYYY
            date_str_format = date_obj.strftime('%d-%m-%Y')

            return date_str_format  # Retourne l'objet date
        except ValueError:
            pass
    else:
        return None


def transf_datestr_obj(date_str):
    if date_str is not None:
        # on convertit la str date_str au format DD-MM-YYYY en objet date
        date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
        return date_obj


def lance_extract_dates(directory):
    # on parcourt tous les fichiers du répertoire
    for filename in os.listdir(directory):
        # on veut traiter tous les fichiers terminant par "_text.txt"
        if filename.endswith("_text.txt"):
            # on ajoute le nom du fichier au chemin du répertoire "facture_integration"
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
               # on extrait le contenu du fichier text
                content = file.read()
                # on obtient la date en appelant la fonction extract_date
                date = extract_date(content)
                # on imprime le nom du fichier et la date trouvée
                print(f"{filename}: {date}")
                transf_datestr_obj(date)


if __name__ == '__main__':
    # on obtient le chemin du répertoire courant du fichier
    repertoire_courant = os.getcwd()

    # on s'intéresse au dossier factures_integration du répertoire courant
    repertoire_test = os.path.join(repertoire_courant, 'factures_integration')

    # on appelle la fonction
    lance_extract_dates(repertoire_test)