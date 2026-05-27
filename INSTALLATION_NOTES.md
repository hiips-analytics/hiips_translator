# Notes d'Installation - Traducteur DOCX et PDF Hors-ligne

Cet outil est conçu pour fonctionner **exclusivement en local sur processeur (CPU)** afin de garantir la confidentialité des données et de fonctionner sans GPU.

## 1. Prérequis Système
- Python 3.8 à 3.11.
- RAM : 4 à 8 Go minimum recommandés (le modèle linguistique chargé occupe environ 300 à 500 Mo en mémoire).

## 2. Installation des dépendances
Ouvrez un terminal ou invite de commande et exécutez la commande suivante à la racine du projet :

```bash
pip install -r requirements.txt
```

*(Si vous obtenez des erreurs liées à `PyMuPDF`, essayez d'utiliser `pip install pymupdf` ou de mettre à jour pip avec `pip install --upgrade pip`)*.

## 3. Initialisation et téléchargement du modèle (Premier lancement)
Lors du **premier lancement** du script, la bibliothèque `transformers` d'Hugging Face va automatiquement télécharger le modèle de traduction (`Helsinki-NLP/opus-mt-en-fr`).
Le modèle `opus-mt` a été choisi car il est extrêmement léger et performant, parfait pour une utilisation CPU sans surcharger la mémoire.

**Ce premier lancement nécessite obligatoirement une connexion Internet**.

Une fois le modèle téléchargé, il sera stocké dans le cache local de Hugging Face (généralement dans `~/.cache/huggingface/hub`).
**Tous les lancements suivants seront 100% hors-ligne**.

### Pour forcer le téléchargement manuel avant utilisation :
Vous pouvez exécuter ce petit script Python dans votre terminal pour précharger le modèle :

```python
from transformers import MarianMTModel, MarianTokenizer

model_name = "Helsinki-NLP/opus-mt-en-fr"
print(f"Téléchargement de {model_name}...")
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)
print("Modèle téléchargé et prêt pour une utilisation hors-ligne !")
```

## 4. Notes sur le Matériel (CPU)
- Le script utilise `device='cpu'` et désactive toute tentative d'initialisation de `CUDA` (la technologie GPU de NVIDIA).
- Le script utilise `multiprocessing` (plusieurs processus en parallèle) pour diviser la traduction des paragraphes sur tous les cœurs disponibles de votre processeur. Ceci permet d'accélérer considérablement le traitement sur un CPU standard.
