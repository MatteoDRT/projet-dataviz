# 📥 Instructions pour Télécharger les Données INSEE

Les fichiers de données brutes INSEE sont trop volumineux pour être hébergés sur GitHub (>100 MB).  
Vous devez les télécharger manuellement et les placer dans le dossier `data/raw/`.

## Fichiers Requis

### 1. Base Emploi et Population Active 2020

**Fichier** : `base-cc-emploi-pop-active-2020_v2.CSV` (143 MB)

**Source** : INSEE - Bases de données communales  
**Lien** : https://www.insee.fr/fr/statistiques/fichier/6456178/base-cc-emploi-pop-active-2020_v2.zip

**Instructions** :
1. Télécharger le fichier ZIP
2. Extraire `base-cc-emploi-pop-active-2020_v2.CSV`
3. Placer dans `data/raw/`

**Métadonnées** : Le fichier `meta_base-cc-emploi-pop-active-2020_v2.CSV` est déjà inclus dans le repo.

---

### 2. Base Logement 2021

**Fichier** : `base-cc-logement-2021.CSV` (94 MB)

**Source** : INSEE - Bases de données communales  
**Lien** : https://www.insee.fr/fr/statistiques/fichier/6456310/base-cc-logement-2021.zip

**Instructions** :
1. Télécharger le fichier ZIP
2. Extraire `base-cc-logement-2021.CSV`
3. Placer dans `data/raw/`

**Métadonnées** : Le fichier `meta_base-cc-logement-2021.CSV` est déjà inclus dans le repo.

---

### 3. Niveau de Vie 2013 par Commune

**Fichier** : `Niveau_de_vie_2013_a_la_commune-Global_Map_Solution (1).xlsx` (1.4 MB)

**Source** : DGFiP via data.gouv.fr  
**Lien** : https://www.data.gouv.fr/fr/datasets/niveau-de-vie-par-commune/

**Instructions** :
1. Télécharger le fichier Excel
2. Placer dans `data/raw/`

---

## Structure Finale du Dossier

Après téléchargement, votre dossier `data/raw/` devrait contenir :

```
data/raw/
├── base-cc-emploi-pop-active-2020_v2.CSV        (143 MB)
├── base-cc-logement-2021.CSV                     (94 MB)
├── Niveau_de_vie_2013_a_la_commune-Global_Map_Solution (1).xlsx  (1.4 MB)
├── meta_base-cc-emploi-pop-active-2020_v2.CSV   (inclus dans repo)
└── meta_base-cc-logement-2021.CSV               (inclus dans repo)
```

## Vérification

Une fois les fichiers en place, lancez l'application :

```bash
streamlit run app.py
```

Vous devriez voir :
- ✅ Données INSEE chargées: 34,963 communes
- ✅ Données logements chargées: 34,963 communes  
- ✅ Données revenus chargées: 36,572 communes

## Notes

- Les fichiers CSV sont trop grands pour GitHub (limite de 100 MB par fichier)
- Le cache (`data/cache/`) sera généré automatiquement au premier lancement
- Les métadonnées sont incluses dans le repo pour référence
