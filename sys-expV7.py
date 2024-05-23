from experta import *
import re
import os
import shutil
from read_date import *



class Document(Fact):
    """ Représente un document avec son nom, contenu et type. """
    pass


class DocumentClassifier(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.document_types = {}  # Dictionnaire pour stocker les types de documents

    @Rule(Document(content=MATCH.content, name=MATCH.name))
    def classify_document(self, name, content):
        # Initialise le type de document à 'Autre'
        doc_type = 'Autre'
        # Détermine le type de document basé sur des expressions régulières pour identifier des mots clés spécifiques
        # Les règles suivantes vérifient la présence de certains mots clés pour classifier le document dans une catégorie appropriée
        if re.search(r'\b(facture|tva)\b', content, re.IGNORECASE):
            # Plusieurs branches de conditions qui correspondent à différentes catégories comme 'Logement', 'Transport', etc.
            # Exemple pour Logement:
            if re.search(r'\b(logement|loyer|appartement|maison)\b', content, re.IGNORECASE):
                doc_type = 'Logement'
                print("Facture : Logement")
            elif re.search(
                    r'\b(SNCF|RATP|Keolis|Transdev|Blablacar|CMA CGM|Corsica Ferries|Air France|Transavia France|Corsair International|Air Caraïbes|French Bee|La Compagnie |Eurolines|Ouibus|Blablabus|Lyon Turin Ferroviaire|Louis Dreyfus Armateurs|Compagnie du Ponant|ASL Airlines France|transport|bus|train|billet)\b',
                    content, re.IGNORECASE):
                doc_type = 'Transport'
                print("Facture : Transport")
            elif re.search(
                    r'\b(AXA|Allianz|Groupama|MAIF|MACIF|Mutuelle Générale|Hiscox|AXA Entreprises|Generali Professionnels|Assurances Agricoles|Groupama |Crédit Agricole Assurances |SMACL Assurances |La Parisienne Assurances |Direct Assurance |Matmutassurance|couverture|police)\b',
                    content, re.IGNORECASE):
                doc_type = 'Assurances'
                print("Facture : Assurances")
            elif re.search(
                    r'\b(AXA Santé|Allianz Santé|Harmonie Mutuelle|Mutuelle Générale|MACIF Santé|MAIF Santé|Groupama Santé|AG2R La Mondiale|MGEN|April Santé santé|pharmacie|docteur|clinique)\b',
                    content, re.IGNORECASE):
                doc_type = 'Santé'
                print("Facture : Santé")
            elif re.search(
                    r'\b(IKEA|Roche Bobois|Maisons du Monde|Habitat|Gautier|Fly|Cinna|BoConcept ameublement|meuble|décor)\b',
                    content, re.IGNORECASE):
                doc_type = 'Ameublement'
                print("Facture : Ameublement")
            elif re.search(
                    r'\b(OrangeSFR|Bouygues Telecom|Free|La Poste Mobile|Coriolis Telecom|Prixtel|Red by SFR|Sosh|B&YOU|téléphone|mobile|internet)\b',
                    content, re.IGNORECASE):
                doc_type = 'Téléphonies'
                print("Facture : Téléphonies")
            # Ajoute de conditions qui permettent de s'assurer que les documents de type prêt-à-porter associés à Carrefour ne sont classés que si les marques spécifiques de vêtements de Carrefour sont mentionnées, ce qui augmente la précision de la classification dans ce contexte.
            elif re.search(
                    r"\b(Zara|H&M|Uniqlo|Levi's|Lacoste|The Kooples|Maje|Promod|Etam|Celio|Kiabi|Bonobo|undiz|habillement|vêtement|mode)\b",
                    content, re.IGNORECASE) or (re.search(r'\b(Carrefour)\b', content, re.IGNORECASE) and (
            re.search(r'\b(Tex|In Extenso|Canda)\b', content, re.IGNORECASE))):
                doc_type = 'Prêt-à-porter'
                print("Facture : Prêt-à-porter")
            elif re.search(
                    r'\b(Carrefour|ED|Casino|Monoprix|Tesco|Aldi|Lidl|Auchan|Costco|Intermarché|Leclerc|Franprix|Super U|Leader Price|Géant Casino|Dia|Biocoop|alimentation|supermarché|épicerie)\b',
                    content, re.IGNORECASE):
                if re.search(r'5.5%|5,5%|TVA 5.5%|TVA 5,5%',
                             content):  # Vérification de la présence de "5.5%" ou "5,5%"
                    doc_type = 'Alimentaire'
                    print("Facture : Alimentaire")
            elif re.search(
                    r"\b(BNP Paribas|Société Générale|La Banque Postale|HSBC France|Banque Populaire|Caisse d'epargne|Crédit Mutuel|LCL |Hello Bank!|Boursorama|frais bancaires|banque)\b",
                    content, re.IGNORECASE):
                if re.search(
                        r'frais de gestion|frais de tenue de compte|commission|intérêts débiteurs|agios|frais de découvert|frais mensuels|frais annuels',
                        content):  # Vérification de la présence de "5.5%" ou "5,5%"
                    doc_type = 'Frais bancaires'
                    print("Facture : Frais bancaires")
            else:
                doc_type = 'Facture - Autre'
                print("Facture : Autre")
        else:
            doc_type = 'Inconnu'
            print("Facture : Inconnu")
        # Enregistrement du type de document dans le dictionnaire avec le nom comme clé
        self.document_types[name] = doc_type

    # Lit le contenu d'un fichier et le retourne sous forme de chaîne.


def read_file_content(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def get_file_type(files):
    # Crée une instance de DocumentClassifier, déclare des documents pour chaque fichier, exécute le moteur et récupère les types de documents.
    engine = DocumentClassifier()
    engine.reset()
    documents = []

    for file in files:
        content = read_file_content(file)
        engine.declare(Document(name=file, content=content))
        engine.run()
        file_type = engine.document_types.get(file, 'Inconnu')
        documents.append((file, file_type))
        save_document(file, file_type, content)

    return documents


def extract_amount(content):
    match = re.search(r'\b(TOTAL|total|montant total|Total TTC)\s*[\: ]\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                      content, re.IGNORECASE)
    if match:
        return match.group().split()[-1].strip('€')  # Extrait le montant
    return "0"



def save_document(filename, folder, content):
    amount = extract_amount(content)
    date = extract_date(content)
    _, file_extension = os.path.splitext(filename)
    new_filename = f"{os.path.splitext(filename)[0]}_{amount}_{date}{file_extension}"
    directory = os.path.join("Trie_documents", folder)
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_path = os.path.join(directory, new_filename)
    if not os.path.exists(save_path):
        shutil.copy2(filename, save_path)
    else:
        count = 1
        while os.path.exists(save_path):
            save_path = os.path.join(directory,
                                     f"{os.path.splitext(filename)[0]}_{amount}_{date}_{count}{file_extension}")
            count += 1
        shutil.copy2(filename, save_path)
    print(f"Fichier sauvegardé sous : {save_path}")


#files = [
#    "extractionTesseractOCR"]  # Nom de fichier a entrer ici. ( Je vais le modifier pour passer le nom de fichier en argument plus tard pour le faire fonctionner avce le reste du projet. )
#sorted_documents = get_file_type(files)

# Test pour le réenregistrement d'une image
# save_document("eTicket.pdf", "test")
# save_document("facture1.png", "test")

#for doc in sorted_documents:
 #   print(doc)
