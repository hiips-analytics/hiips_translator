# Traducteur Local DOCX et PDF vers le Français

Un outil de traduction hors-ligne basé sur le CPU, conçu pour traduire des documents `.docx` et `.pdf` vers le français tout en préservant au mieux leur mise en page et leur structure.

## Caractéristiques

- **100% Local & Hors-ligne** : Aucune donnée n'est envoyée vers le cloud. Utilise des modèles neuronaux locaux (via HuggingFace Transformers).
- **Optimisé pour CPU** : Conçu pour fonctionner de manière performante sans GPU grâce au traitement multi-processus (multiprocessing) et à la traduction par lots (batching).
- **Support Multi-Formats** : 
  - Fichiers `.docx` : Préserve les styles, tableaux et la structure générale du document grâce à `python-docx`.
  - Fichiers `.pdf` : Extraction et recréation de PDF avec `PyMuPDF`.
- **Suivi de progression** : Barre de progression détaillée via `tqdm`.

## Prérequis

- Python 3.8+
- RAM : Minimum recommandé 8 Go (les modèles de traduction nécessitent un peu de mémoire).

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers sources.
2. Installez les dépendances requises via `pip` :

```bash
pip install -r requirements.txt
```

Les dépendances principales incluent :
- `transformers` & `torch` (Moteur de traduction neuronal)
- `python-docx` (Manipulation des fichiers Word)
- `PyMuPDF` (Manipulation des fichiers PDF)
- `tqdm` (Barre de progression)

*(Note : Au premier lancement, l'outil téléchargera automatiquement les poids du modèle de traduction depuis HuggingFace).*

## Utilisation

Le script principal est `main.py`. Il s'utilise via la ligne de commande.

### Commande de base

```bash
python main.py <fichier_source> <fichier_destination>
```

**Exemple :**
```bash
python main.py document_anglais.docx document_traduit.docx
```

### Options Avancées

- `--batch-size` : Définit la taille des lots envoyés au modèle. Par défaut : `4`. Réduisez cette valeur si vous manquez de mémoire RAM.
- `--workers` : Nombre de processus CPU alloués à la traduction. Par défaut, le script utilise tous les cœurs disponibles moins un. 

**Exemple avec options :**
```bash
python main.py rapport.pdf rapport_fr.pdf --batch-size 2 --workers 4
```

## Structure du Projet

- `main.py` : Point d'entrée de l'application (CLI).
- `translator.py` : Gestionnaire de traduction `LocalTranslator`, s'occupant du chargement du modèle et de la parallélisation.
- `docx_handler.py` : Logique d'extraction, de traduction et de reconstruction spécifique aux fichiers `.docx`.
- `pdf_handler.py` : Logique d'extraction, de traduction et de reconstruction spécifique aux fichiers `.pdf`.
- `requirements.txt` : Liste des dépendances Python.
- `INSTALLATION_NOTES.md` : Notes additionnelles sur l'installation et l'environnement.

## Avertissement

La traduction de documents complexes (en particulier les PDF avec des mises en page très spécifiques) peut parfois altérer l'alignement visuel exact. Le texte sera traduit, mais une relecture et un ajustement mineur de la mise en page peuvent être nécessaires sur le fichier de sortie.
