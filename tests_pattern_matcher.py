from pattern_matcher import *

# dictionnaire contenant les informations correctes pour chaque facture
factures_reelles = {
    "facture1_nettoye.txt": {"date": "29-01-2019", "montant": 174.0, "devise": "EUR",
                             "categorie": "Autre"},
    "facture2_nettoye.txt": {"date": "12-01-2020", "montant": 2012.5, "devise": "EUR",
                             "categorie": "Service"},
    "facture3_nettoye.txt": {"date": "12-07-2023", "montant": 361.88, "devise": "CAD", "categorie":
        "Livres"},
    "facture4_nettoye.txt": {"date": None, "montant": 6720.0, "devise": "EUR", "categorie":
        "Service"},
    "facture5_nettoye.txt": {"date": "24-05-2007", "montant": 213781.06, "devise": "CAD",
                             "categorie": "Autre"},
    "facture6_nettoye.txt": {"date": "03-04-2023", "montant": 2138128.0, "devise": "XOF",
                             "categorie": "Travaux"},
    "facture7_nettoye.txt": {"date": "31-01-2017", "montant": 383.39, "devise": "EUR",
                             "categorie": "Services Publics"},
    "facture8_nettoye.txt": {"date": "01-03-2023", "montant": 63.99, "devise": "EUR", "categorie":
        "Téléphonie"},
    "facture9_nettoye.txt": {"date": "06-01-2025", "montant": 492.0, "devise": "EUR",
                              "categorie": "Autre"},
    "facture10_nettoye.txt": {"date": "26-12-2021", "montant": 1040.0, "devise": "EUR",
                              "categorie": "Service"},
    "facture11_nettoye.txt": {"date": "18-09-2023", "montant": 15.99, "devise": "EUR",
                              "categorie": "Téléphonie"},
    "facture12_nettoye.txt": {"date": "10-01-2024", "montant": 1535.0, "devise": "EUR",
                              "categorie": "Autre"},
    "facture13_nettoye.txt": {"date": "28-02-2024", "montant": 712.47, "devise": "EUR",
                              "categorie": "Autre"},
    "facture14_nettoye.txt": {"date": "19-12-2023", "montant": 11165.0, "devise": "EUR",
                              "categorie": "Travaux"},
    "facture15_nettoye.txt": {"date": "04-08-2023", "montant": 4680.0, "devise": "EUR",
                              "categorie": "Travaux"},
    "facture16_nettoye.txt": {"date": "03-07-2023", "montant": 489.69, "devise": "EUR",
                              "categorie": "Autre"},
    "facture17_nettoye.txt": {"date": "16-10-2023", "montant": 21.9, "devise": "EUR",
                              "categorie": "Autre"},
    "facture18_nettoye.txt": {"date": "27-11-2023", "montant": 1450.0, "devise": "EUR",
                              "categorie": "Électronique"},
    "facture19_nettoye.txt": {"date": "27-02-2024", "montant": 9636.0, "devise": "EUR",
                              "categorie": "Travaux"},
    "facture20_nettoye.txt": {"date": "19-07-2023", "montant": 1457.05, "devise": "EUR",
                              "categorie": "Logement"},
    "facture21_nettoye.txt": {"date": "01-02-2021", "montant": 129.9, "devise": "EUR",
                              "categorie": "Électronique"},
    "facture22_nettoye.txt": {"date": "28-04-2024", "montant": 0.99, "devise": "EUR",
                              "categorie": "Électronique"},
    "facture23_nettoye.txt": {"date": "09-11-2022", "montant": 586.0, "devise": "EUR",
                              "categorie": "Électronique"},
    "facture24_nettoye.txt": {"date": "17-04-2024", "montant": 38.01, "devise": "EUR",
                              "categorie": "Livres"},
    "facture25_nettoye.txt": {"date": "17-04-2024", "montant": 25.0, "devise": "EUR",
                              "categorie": "Livres"},
    "facture26_nettoye.txt": {"date": "10-01-2024", "montant": 301.52, "devise": "EUR",
                              "categorie": "Autre"},
    "facture27_nettoye.txt": {"date": "12-07-2022", "montant": 82.91, "devise": "EUR",
                              "categorie": "Prêt-à-porter"},
    "facture28_nettoye.txt": {"date": "28-03-2024", "montant": 50.94, "devise": "EUR", "categorie":
        "Autre"},
    "facture29_nettoye.txt": {"date": "27-03-2024", "montant": 76.20, "devise": "EUR", "categorie":
        "Livres"},
    "facture30_nettoye.txt": {"date": "16-04-2024", "montant": 18.15, "devise": None, "categorie":
        "Alimentaire"},
    "facture31_nettoye.txt": {"date": "01-04-2024", "montant": 265.98, "devise": None, "categorie":
        "Prêt-à-porter"},
    "facture32_nettoye.txt": {"date": "15-09-2022", "montant": 5247.0, "devise": "EUR",
                              "categorie": "Travaux"},
    "facture33_nettoye.txt": {"date": "25-04-2024", "montant": 1302.44, "devise": "EUR",
                              "categorie": "Services Publics"},
    "facture34_nettoye.txt": {"date": "06-03-2024", "montant": 220.23, "devise":
        "EUR", "categorie": "Travaux"},
    "facture36_nettoye.txt": {"date": "24-04-2024", "montant": 252.76, "devise": "EUR",
                              "categorie": "Services Publics"},
    "facture37_nettoye.txt": {"date": "23-12-2016", "montant": 29920.0, "devise": "EUR",
                              "categorie": "Travaux"},
}


def compare_resultats(fichier_nettoye, releve, correct):
    """
    Compare les valeurs extraites avec les valeurs réelles et affiche les résultats.
    :param fichier_nettoye: le nom du fichier de la facture (texte nettoyé)
    :param releve: dictionnaire contenant les valeurs extraites.
    :param real: dictionnaire contenant les valeurs réelles.
    """
    extracted_str = (f"Fichier: {fichier_nettoye}, Date extraite: {releve['date']},  Montant extrait:"
                     f" {releve['montant']}, Devise extraite: {releve['devise']},  "
                     f"Catégorie extraite: {releve['categorie']}, Mot correspondant:"
                     f" {releve['match_mot']}")

    # affichage des valeurs extraites
    print(extracted_str)

    # affichage des informations incorrectes
    print("Informations incorrectes:")
    if releve['date'] != correct['date']:
        print(f"Date extraite: {releve['date']}, date correcte: {correct['date']}")
    if releve['montant'] != correct['montant']:
        print(f"Montant extrait: {releve['montant']}, montant correct: {correct['montant']}")
    if releve['devise'] != correct['devise']:
        print(f"Devise extraite: {releve['devise']}, devise correcte: {correct['devise']}")
    if releve['categorie'] != correct['categorie'] and releve['categorie'] != "Autre":
        print(f"Catégorie extraite: {releve['categorie']}, catégorie correcte: {correct['categorie']}")
    print("\n")


def lance_tests(directory):
    """
    lance les tests sur les fichiers de factures dans le répertoire donné.
    :param directory: le chemin du répertoire contenant les fichiers de factures.
    """

    # parcourt tous les fichiers dans le répertoire spécifié
    for filename in os.listdir(directory):
        # vérifie si le fichier se termine par "_nettoye.txt"
        if filename.endswith("_nettoye.txt"):
            # construit le chemin complet du fichier
            filepath = os.path.join(directory, filename)
            # ouvre et lit le contenu du fichier
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

                # extrait les informations du contenu du fichier
                releve = {
                    "date": extract_date(content),
                    "montant": extract_amount(content),
                    "devise": extract_currency(content),
                    "categorie": get_categorie(content)[0],
                    "match_mot": get_categorie(content)[1]
                }

                # récupère les informations correctes pour le fichier actuel
                correct = factures_reelles.get(filename, {})
                if correct:
                    # compare et affiche les résultats
                    compare_resultats(filename, releve, correct)


if __name__ == '__main__':
    # obtient le chemin du répertoire courant
    repertoire_courant = os.getcwd()
    # construit le chemin du répertoire de test
    repertoire_test = os.path.join(repertoire_courant, 'tests_pattern_matcher')
    # lance les tests
    lance_tests(repertoire_test)
