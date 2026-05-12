
### MatInf
- 'Type',
- 'Modèle',
- 'Impact'

### Personnel
- 'ID_PERSONNEL'
- 'NOM_PERSONNEL'
- 'PRENOM_PERSONNEL'
- 'DT_NAISS',
- 'VILLE_NAISS'
- 'PAYS_NAISS', 
- 'NUM_SECU', 
- 'IND_PAYS_NUM_TELP',
- 'NUM_TELEPHONE',
- 'NUM_VOIE',
- 'DSC_VOIE',
- 'CMPL_VOIE',
- 'CD_POSTAL',
- 'VILLE',
- 'PAYS',
- 'FONCTION_PERSONNEL',
- 'TS_CREATION_PERSONNEL',
- 'TS_MAJ_PPERSONNEL'

### Mission
- 'ID_MISSION',
- 'ID_PERSONNEL',
- 'NOM_PERSONNEL',
- 'PRENOM_PERSONNEL',
- 'DATE_MISSION',
- 'TYPE_MISSION',
- 'VILLE_DEPART',
- 'PAYS_DEPART',
- 'VILLE_DESTINATION', 
- 'PAYS_DESTINATION', 
- 'TRANSPORT', 
- 'ALLER_RETOUR'


## Infos nécessaires
#### FAITS MATINF
#ID_PERSONNEL
#ID_MATERIELINFO

#### FAITS MISSION
#ID_PERSONNEL 
#ID_MISSION 
#### Personnel
FONCTION_PERSONNEL
DATE_NAISSANCE
VILLE
PAYS

#### MatInf
TYPE (exemple : PC fixe sans écran -> PC fixe)
ECRAN (boolean oui/non)
DATE_ACHAT
IMPACT

#### Mission
DATE_MISSION
TYPE_MISSION
VILLE_DEPART
VILLE_DESTINATION
TRANSPORT
ALLER_RETOUR
colonne calculée - IMPACT CARBONE

#### Localisation
#VILLE
PAYS
CONTINENT



## Ce qui reste
#### L'ETL 
- [ ] Faire les tables caches - RZ
- [ ] finaliser mission - RZ

### Base
- [ ] Nettoyage des données 
	- [ ] Vérifier où sont les valeurs manquantes
	- [ ] Faire des choix de remplacement
		- [ ] Mettre None, quand on sait pas comment remplacer
		- [ ] Faire des déductions sur comment remplacer possiblement la donnée par un truc vraisemblable
- [ ] Charger toutes les tables du modèle et les enregistrer sous format csv
- [ ] Faire les requêtes pour les questions