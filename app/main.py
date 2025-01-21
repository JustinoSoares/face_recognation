import cv2
import face_recognition
import base64
from flask import Flask
from flask_socketio import SocketIO
from prisma import Prisma
import io
import httpx
from PIL import Image
import numpy as np
import asyncio
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
prisma = Prisma()

def adjust_brightness(image, beta=50):
    return cv2.convertScaleAbs(image, alpha=1, beta=beta)

async def load_image_from_url(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        image = Image.open(io.BytesIO(response.content))
        return np.array(image)

async def get_known_faces_from_db():
    alunos = await prisma.alunos.find_many(include={'Fotos': True})
    known_faces = {}
    alunos_map = {}
    for aluno in alunos:
        name = aluno.nome_completo
        known_faces[name] = []
        alunos_map[name] = aluno.id
        for foto in aluno.Fotos:
            img_url = foto.url
            image = await load_image_from_url(img_url)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces[name].append(encodings[0])
    return known_faces, alunos_map

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

async def process_video():
    video_capture = cv2.VideoCapture(0)
    try:
        known_encodings, alunos_map = await get_known_faces_from_db()
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
                        result = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.35)
                        if result[0]:
                            match_results[name] = match_results.get(name, 0) + 1
                label = max(match_results, key=match_results.get) if match_results else "Desconhecido"
                if label != "Desconhecido":
                    aluno_id = alunos_map[label]
                     #Cria o registro na tabela reconhecido
                    novo_registro = await prisma.reconhecimento.create(
                        data={
                            "alunoId": aluno_id,
                            "createdAt": datetime.now(),
                            "updatedAt": datetime.now(),
                        }
                    )
                    # Emite o evento via WebSocket
                    socketio.emit('novo_registro', {
                        "id" : novo_registro.alunoId,
                        "alunoId" : novo_registro.alunoId,
                        "createdAt" : novo_registro.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
                     })
                cv2.rectangle(adjusted_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(adjusted_frame, label, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            _, buffer = cv2.imencode('.jpg', adjusted_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            socketio.emit('video_frame', {'frame': frame_base64})
    finally:
        video_capture.release()

@socketio.on('start_video')
def start_video_stream():
    def wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_video())

    socketio.start_background_task(wrapper)

if __name__ == "__main__":
    async def main():
        await prisma.connect()
        socketio.run(app, host="0.0.0.0", port=5000)
    asyncio.run(main())
