# Plan d'implémentation de l'outil de traduction de documents hors-ligne

Ce document présente l'approche technique pour développer un script Python complet permettant de traduire des documents `.docx` et `.pdf` vers le français de manière entièrement locale, sans appel à des API externes, en utilisant le processeur (CPU) et en limitant l'empreinte mémoire.

## Modèle d'architecture

L'application sera divisée en modules distincts pour assurer la maintenabilité et la lisibilité du code :

1. **`main.py`** : Point d'entrée du script (CLI), gérant les arguments (fichier source, fichier de destination) et orchestrant l'exécution.
2. **`translator.py`** : Le moteur de traduction neural. Il utilisera `transformers` (Hugging Face) avec un modèle léger `Helsinki-NLP/opus-mt-en-fr` (ou `opus-mt-mul-fr` pour traduire depuis plusieurs langues). Le module implémentera le `multiprocessing` (via `concurrent.futures.ProcessPoolExecutor`) pour paralléliser la traduction par lots (batches) sur les cœurs du CPU.
3. **`docx_handler.py`** : Le module gérant l'extraction et la réinsertion de texte pour les fichiers `.docx` via `python-docx`, tout en préservant le formatage (paragraphes, tableaux).
4. **`pdf_handler.py`** : Le module gérant les PDF via `PyMuPDF` (`fitz`). Il extraira les blocs de texte, les traduira, appliquera des annotations de rédaction (redaction annotations) pour effacer le texte d'origine et insérera le texte traduit aux mêmes coordonnées.
5. **`INSTALLATION_NOTES.md`** : Guide complet pour l'installation des dépendances et le premier lancement pour mettre le modèle en cache.
6. **`requirements.txt`** : Liste des dépendances.

## User Review Required

> [!IMPORTANT]
> **Stratégie de formatage DOCX (niveau Run vs Paragraphe) :**
> La traduction neuronale donne de bien meilleurs résultats sur des phrases complètes. Dans un fichier Word, une phrase peut être divisée en plusieurs "runs" (par exemple si un seul mot est en **gras**).
> - *Approche proposée* : Extraire et traduire le texte entier du paragraphe pour garantir une bonne qualité de traduction, puis appliquer la traduction au premier "run" et vider les autres. Le formatage global du paragraphe sera préservé, mais les styles intra-phrase (comme un seul mot en gras) seront perdus. 
> - *Alternative* : Traduire "run" par "run". Le formatage est parfaitement préservé, mais la grammaire de la traduction peut être gravement affectée.
> **Êtes-vous d'accord pour privilégier la qualité de la traduction (niveau paragraphe) ?**

> [!WARNING]
> **Limites de la modification PDF :**
> Modifier un PDF in-place (redessiner du texte par-dessus) avec PyMuPDF fonctionne, mais le texte traduit (souvent plus long en français) pourrait déborder de son cadre d'origine (bounding box) ou superposer d'autres éléments. La police d'origine (nom exact) ne peut pas toujours être recréée si elle n'est pas installée sur le système, le script utilisera donc une police standard (Helvetica) de taille appropriée.

## Changements proposés

### Moteur de traduction (NLP)

#### [NEW] [translator.py](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/translator.py)
- Contient une fonction d'initialisation du modèle par processus (pour le multiprocessing).
- Utilise `device="cpu"`.
- Charge `Helsinki-NLP/opus-mt-en-fr`.
- Expose une fonction `translate_blocks(texts, batch_size)` qui utilise `tqdm` pour la barre de progression.

### Gestionnaire de Fichiers

#### [NEW] [docx_handler.py](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/docx_handler.py)
- Fonctions `process_docx(input_path, output_path)` pour parcourir `doc.paragraphs` et `doc.tables`.

#### [NEW] [pdf_handler.py](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/pdf_handler.py)
- Fonctions `process_pdf(input_path, output_path)` utilisant `fitz`.
- Détection des fichiers corrompus ou PDF scannés (en mesurant la quantité de texte extraite par rapport au nombre de pages).

### CLI & Configuration

#### [MODIFY] [main.py](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/main.py)
- Traitement des arguments de ligne de commande (`argparse`).
- Routage vers le bon handler en fonction de l'extension de fichier.

#### [NEW] [requirements.txt](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/requirements.txt)
- `transformers`, `torch`, `python-docx`, `PyMuPDF`, `tqdm`.

#### [NEW] [INSTALLATION_NOTES.md](file:///mnt/windows/workspace/tools/translators/fr_docx_and_pdf_translator/INSTALLATION_NOTES.md)
- Instructions d'installation.

## Plan de vérification

### Tests automatisés / manuels
1. Création d'un document texte factice `.docx` avec des titres et paragraphes, et lancement du script. Vérification que le fichier de sortie est en français.
2. Création d'un document `.pdf` avec texte, lancement du script. Vérification de l'encodage du texte traduit (accents français).
3. Test avec un document `.pdf` vide ou constitué d'images pour vérifier le déclenchement de l'exception "PDF scanné".
4. Vérification de l'empreinte mémoire et du lancement multi-processus avec CPU.
