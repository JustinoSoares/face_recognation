# face_recognation

## Colocar a rodar
docker run -it --name face_container --device=/dev/video1 -p 5000:5000 face_app

docker run -it --name face_container --device=/dev/video0:/dev/video0 -p 5000:5000 face_app

## Coisas que devo fazer
- Colocar a aplicação no conteiner

- fazer a conexao com banco de dados

- fazer o registo de que um rosto foi encontrado

- Ajustar a api em nodejs para que a lógica funcione tudo muito bem

- Testar e mostrar tudo funcionando em tempo real 
