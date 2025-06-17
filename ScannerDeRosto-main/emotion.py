# RETORNA DADOS COMPLETOS

from deepface import DeepFace
import logging

def analisar_emocao(face_roi):
    """
    Analisa uma região de rosto e retorna o dicionário completo da análise.
    """
    try:
        # A análise do DeepFace retorna uma lista, pegamos o primeiro elemento
        analysis = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False, prog_bar=False)
        if analysis and isinstance(analysis, list) and len(analysis) > 0:
            return analysis[0] # Retorna todo o dicionário do primeiro rosto
    except Exception as e:
        # Usamos logging para registrar o erro no console para depuração
        logging.warning(f"Erro na análise de emoção: {e}")
    return None