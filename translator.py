import os
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import torch
from transformers import MarianMTModel, MarianTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-en-fr"

# Variables globales pour chaque processus worker
_model = None
_tokenizer = None

def init_worker():
    """Initialise le modèle NLP pour chaque processus worker."""
    global _model, _tokenizer
    
    # Limiter les threads PyTorch par processus pour éviter la surcharge de changements de contexte
    # (le multiprocessing gère déjà la parallélisation sur les cœurs).
    torch.set_num_threads(1)
    
    # Désactiver explicitement CUDA
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    
    try:
        # Désactiver les avertissements de symlinks pour huggingface_hub sur Windows
        os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
        
        _tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
        _model = MarianMTModel.from_pretrained(MODEL_NAME)
        _model.to('cpu')
    except Exception as e:
        print(f"Erreur d'initialisation du modèle (worker) : {e}")
        raise

def translate_batch(texts):
    """Traduit une liste de textes (batch) avec le modèle local."""
    global _model, _tokenizer
    if not texts:
        return []
        
    # Les entrées vides posent parfois problème au modèle, on s'assure d'avoir au moins un espace
    valid_texts = [t if t.strip() else " " for t in texts]
    
    try:
        inputs = _tokenizer(valid_texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to('cpu') for k, v in inputs.items()}
        
        with torch.no_grad():
            translated = _model.generate(**inputs)
            
        result = _tokenizer.batch_decode(translated, skip_special_tokens=True)
        
        # Remettre le texte original si c'était juste des espaces ou vide
        final_result = []
        for i, original in enumerate(texts):
            if not original.strip():
                final_result.append(original)
            else:
                final_result.append(result[i])
                
        return final_result
    except Exception as e:
        print(f"Erreur de traduction du batch : {e}")
        return texts # Fallback de sécurité

class LocalTranslator:
    def __init__(self, num_workers=None, batch_size=4):
        # Laisser un cœur libre pour le système si possible
        self.num_workers = num_workers or max(1, os.cpu_count() - 1)
        self.batch_size = batch_size

    def translate_texts(self, texts):
        """Traduit l'intégralité des textes en utilisant le ProcessPoolExecutor."""
        if not texts:
            return []

        batches = [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        results = []
        
        print(f"Lancement de la traduction ({len(batches)} lots) sur {self.num_workers} processus CPU...")
        
        with ProcessPoolExecutor(max_workers=self.num_workers, initializer=init_worker) as executor:
            # Map retourne un itérateur, tqdm l'enveloppe pour la progression
            for batch_res in tqdm(executor.map(translate_batch, batches), total=len(batches), desc="Traduction"):
                results.extend(batch_res)
                
        return results
