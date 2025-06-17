import cv2
import dlib

# Configurações visuais e fontes
TEXT_COLOR = (0, 255, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
LINE_THICKNESS = 2

ELLIPSE_MARGIN_X_FACTOR = 0.15
ELLIPSE_MARGIN_Y_FACTOR = 0.10


def get_face_detector(upsample_factor=1):
    return lambda img: dlib.get_frontal_face_detector()(img, upsample_factor)

def desenhar_elipse(frame, x, y, w, h):
    margin_x = int(w * ELLIPSE_MARGIN_X_FACTOR)
    margin_y = int(h * ELLIPSE_MARGIN_Y_FACTOR)
    center = (x + w // 2, y + h // 2)
    axis_x = int((w - 2 * margin_x) // 2)
    axis_y = int((h + 2 * margin_y) // 2)
    cv2.ellipse(frame, center, (axis_x, axis_y), 0, 0, 360, TEXT_COLOR, LINE_THICKNESS)