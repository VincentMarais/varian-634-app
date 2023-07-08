import datetime


date_aujourdhui = datetime.date.today()
date_formatee = date_aujourdhui.strftime("%d_%m_%Y")
print(date_formatee)

def Taille_de_Fente():
    n=input("Taille de fente : Fente_2nm, Fente_1nm , Fente_0_5nm, Fente_0_2nm : ")
    return n

Taille_de_fente=Taille_de_Fente()

print(Taille_de_fente)