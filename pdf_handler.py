import fitz  # PyMuPDF

def process_pdf(input_path, output_path, translator):
    """
    Traite un fichier PDF : extrait les blocs de texte, les traduit, 
    efface l'original et insère le texte traduit de manière 'best-effort'.
    """
    print(f"Chargement du document PDF: {input_path}")
    doc = fitz.open(input_path)
    
    texts_to_translate = []
    block_mapping = []  # Stocke (page_index, rect)
    
    total_text_length = 0
    
    # 1. Extraction
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            # type 0 signifie un bloc de texte
            if block.get("type") == 0:
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += "\n"
                    
                block_text = block_text.strip()
                if block_text:
                    total_text_length += len(block_text)
                    texts_to_translate.append(block_text)
                    block_mapping.append((page_num, fitz.Rect(block["bbox"])))
                    
    # Vérification anti-PDF scannés : Si le ratio texte / page est trop faible
    if len(doc) > 0 and (total_text_length / len(doc)) < 50:
        raise ValueError("Erreur de traitement: Le document semble être un PDF scanné (ou ne contient quasiment pas de texte). La reconnaissance optique (OCR) n'est pas supportée dans cette version hors-ligne pure.")
        
    if not texts_to_translate:
        print("Aucun texte à traduire trouvé dans le PDF.")
        doc.save(output_path)
        return
        
    print(f"{len(texts_to_translate)} blocs de texte extraits du PDF.")
    
    # 2. Traduction
    translated_texts = translator.translate_texts(texts_to_translate)
    
    # 3. Réinsertion
    for i, (page_num, rect) in enumerate(block_mapping):
        page = doc[page_num]
        translated = translated_texts[i]
        
        # On ajoute une zone de rédaction (masquage blanc) sur l'ancienne bounding box
        page.add_redact_annot(rect, fill=(1, 1, 1)) 
        page.apply_redactions()
        
        # On essaie d'insérer le texte traduit dans le rectangle
        # Le français étant souvent plus long, cela peut parfois déborder si l'espace est contraint.
        try:
            page.insert_textbox(
                rect, 
                translated, 
                fontsize=10, # Taille standard de repli
                fontname="helv", 
                color=(0, 0, 0),
                align=0 # Gauche
            )
        except Exception as e:
            # Si le rectangle est vraiment trop petit, on injecte au moins le texte au point de départ
            try:
                page.insert_text(rect.top_left, translated, fontsize=10, fontname="helv", color=(0,0,0))
            except Exception as e2:
                print(f"Impossible d'insérer le bloc de texte page {page_num}: {e2}")
                
    print(f"Sauvegarde du PDF traduit: {output_path}")
    doc.save(output_path)
