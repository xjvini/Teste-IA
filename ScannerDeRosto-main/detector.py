import cv2
import os
from emotion import analisar_emocao
from utils import desenhar_elipse, get_face_detector, TEXT_COLOR, FONT, LINE_THICKNESS

def process_frame_for_gui(frame):
    """
    Processa um frame e retorna a imagem processada e os resultados da análise.
    Não exibe a imagem, apenas retorna os dados.
    """
    processed_frame = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_dlib = get_face_detector()(gray)
    
    if not faces_dlib:
        return frame, None

    face = faces_dlib[0]
    x, y, w, h = face.left(), face.top(), face.width(), face.height()

    desenhar_elipse(processed_frame, x, y, w, h)

    analysis_result = {
        "caminho_original": None,
        "nome_identificador": None,
        "emocao_detectada": "Nenhuma",
        "confianca": 0,
        "emotion": {} # Adicionado para garantir que a chave sempre exista
    }

    face_roi = frame[max(0, y):min(frame.shape[0], y+h), max(0, x):min(frame.shape[1], x+w)]
    if face_roi.size > 0:
        emocao = analisar_emocao(face_roi) # 'emocao' contém o dicionário completo
        if emocao:
            # Atualiza o dicionário de resultados
            analysis_result["emocao_detectada"] = emocao['dominant_emotion']
            analysis_result["confianca"] = f"{emocao['confidence']:.2f}%"
            
            # --- INÍCIO DA CORREÇÃO ---
            # A linha abaixo estava faltando. Ela adiciona o dicionário completo
            # com todas as emoções ao resultado final.
            analysis_result['emotion'] = emocao.get('emotion', {})
            # --- FIM DA CORREÇÃO ---
            
            # Adiciona o texto na imagem processada
            text = f"{emocao['dominant_emotion']} ({emocao['confidence']:.2f}%)"
            cv2.putText(processed_frame, text, (x, y - 10), FONT, 0.9, TEXT_COLOR, LINE_THICKNESS, cv2.LINE_AA)
            
    return processed_frame, analysis_result

