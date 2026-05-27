import argparse
import os
import sys

from translator import LocalTranslator
from docx_handler import process_docx
from pdf_handler import process_pdf

def main():
    parser = argparse.ArgumentParser(
        description="Traducteur Local DOCX et PDF vers le Français (CPU)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input_file", help="Chemin vers le fichier source (.docx ou .pdf)")
    parser.add_argument("output_file", help="Chemin vers le fichier de destination (.docx ou .pdf)")
    parser.add_argument("--batch-size", type=int, default=4, help="Taille des lots de traduction (réduire si RAM limitée)")
    parser.add_argument("--workers", type=int, default=None, help="Nombre de processus CPU (par défaut: tous - 1)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    output_path = args.output_file
    
    if not os.path.exists(input_path):
        print(f"Erreur : Le fichier '{input_path}' n'existe pas.", file=sys.stderr)
        sys.exit(1)
        
    ext_in = os.path.splitext(input_path)[1].lower()
    ext_out = os.path.splitext(output_path)[1].lower()
    
    if ext_in not in ['.docx', '.pdf']:
        print(f"Erreur : Format source '{ext_in}' non supporté. (.docx, .pdf uniquement)", file=sys.stderr)
        sys.exit(1)
        
    if ext_in != ext_out:
        print(f"Avertissement : Les extensions diffèrent ({ext_in} -> {ext_out}). Le fichier final pourrait être invalide.")
        
    print("Initialisation du moteur de traduction neuronal hors-ligne...")
    try:
        translator = LocalTranslator(num_workers=args.workers, batch_size=args.batch_size)
    except Exception as e:
        print(f"Échec de l'initialisation du modèle : {e}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Début du traitement de {os.path.basename(input_path)}...")
    try:
        if ext_in == '.docx':
            process_docx(input_path, output_path, translator)
        elif ext_in == '.pdf':
            process_pdf(input_path, output_path, translator)
            
        print("Opération terminée avec succès !")
    except Exception as e:
        print(f"\nErreur lors du traitement : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # La protection __main__ est cruciale pour le module 'multiprocessing' de Python
    main()
