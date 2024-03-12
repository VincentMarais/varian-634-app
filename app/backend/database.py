import csv
import sqlite3

# Connexion à la base de données SQLite
conn = sqlite3.connect('echantillons.db')
cur = conn.cursor()

# Créer une table pour les données d'absorbance
cur.execute('''CREATE TABLE IF NOT EXISTS absorbance
               (longueur_d_onde REAL, absorbance REAL)''')

# Lire le fichier CSV et insérer les données
with open('data.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        cur.execute('''INSERT INTO absorbance (longueur_d_onde, absorbance)
                       VALUES (?, ?)''', (row['longueur_d_onde'], row['absorbance']))

# Valider et fermer
conn.commit()
conn.close()
