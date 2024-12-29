import cv2
import face_recognition
import base64
from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def adjust_brightness(image, beta=50):
    """Ajusta o brilho da imagem usando OpenCV."""
    return cv2.convertScaleAbs(image, alpha=1, beta=beta)  # alpha=1 mantém o contraste, beta ajusta o brilho

# Carrega e codifica rostos conhecidos
known_faces = {
    "Justino Soares": ["./know/Justino Soares.jpg", "./know/56.jpg", "./know/jusino.jpg"],
    "Milénia Teresa": ["./know/Milénia.jpg"],
    "João Santos": ["./know/Paulo.jpg"]
}

known_encodings = {}
for name, image_paths in known_faces.items():
    encodings = []
    for image_path in image_paths:
        known_image = face_recognition.load_image_file(image_path)
        encodings.append(face_recognition.face_encodings(known_image)[0])
    known_encodings[name] = encodings

video_capture = cv2.VideoCapture(1)

TOLERANCE = 0.4

@socketio.on('connect')
def handle_connect():
    print("Client connected")
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

def process_video():
    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue

        adjusted_frame = adjust_brightness(frame)
        face_locations = face_recognition.face_locations(adjusted_frame)
        unknown_encodings = face_recognition.face_encodings(adjusted_frame, face_locations)

        for (top, right, bottom, left), unknown_encoding in zip(face_locations, unknown_encodings):
            match_results = {}
            for name, encodings in known_encodings.items():
                for known_encoding in encodings:
                    result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=TOLERANCE)
                    if result[0]:
                        match_results[name] = match_results.get(name, 0) + 1

            label = max(match_results, key=match_results.get) if match_results else "Desconhecido"

            # Exibe o nome no frame
            cv2.rectangle(adjusted_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(adjusted_frame, label, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Converte o frame para base64
        _, buffer = cv2.imencode('.jpg', adjusted_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # Envia o frame ao frontend
        socketio.emit('video_frame', {'frame': frame_base64})

@socketio.on('start_video')
def start_video_stream():
    process_video()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
