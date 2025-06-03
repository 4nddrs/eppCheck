import os
from dotenv import load_dotenv
import cv2
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from ultralytics import YOLO
import threading

# Load environment variables from .env file
load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
email_password = os.getenv("EMAIL_PASSWORD")

def draw_text_with_background(frame, text, position, font_scale=0.4, color=(255, 255, 255), thickness=1, bg_color=(0, 0, 0), alpha=0.7, padding=5):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_width, text_height = text_size
    overlay = frame.copy()
    x, y = position
    cv2.rectangle(overlay, (x - padding, y - text_height - padding), (x + text_width + padding, y + padding), bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)

def draw_dashboard(frame, hardhat_count, vest_count, person_count):
    panel_width = 200
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (panel_width, frame.shape[0]), (50, 50, 50), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    y_offset = 40
    line_height = 30
    texts = [
        ("ESTADO", (255, 255, 255)),
        (f"Cascos: {hardhat_count}", (0, 255, 255)),
        (f"Personas: {person_count}", (0, 255, 0)),
        (f"Chalecos: {vest_count}", (255, 128, 0)),
        ("Presiona Q para salir", (200, 200, 200))
    ]
    for i, (text, color) in enumerate(texts):
        draw_text_with_background(frame, text, (10, y_offset + i * line_height), font_scale=0.5, color=color, bg_color=(0, 0, 0), alpha=0.4)

def send_email_alert(image_path):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Alerta: Persona sin casco detectada"
    body = "Se detectó una persona sin casco durante más de 10 segundos. Imagen adjunta."
    message.attach(MIMEText(body, "plain"))

    with open(image_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={image_path}")
        message.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Correo enviado.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def send_email_in_background(image_path):
    email_thread = threading.Thread(target=send_email_alert, args=(image_path,))
    email_thread.start()

def main():
    model = YOLO("Model/ppe.pt")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    print("Presiona 'q' para salir.")
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 128), (128, 128, 0), (0, 128, 128), (128, 128, 128)
    ]

    last_hardhat_time = time.time()
    last_email_time = time.time()
    email_sent_flag = False
    email_sent_time = 0

    cv2.namedWindow("YOLOv8 Annotated Feed", cv2.WINDOW_NORMAL)

    label_translation = {
    "Hardhat": "Casco",
    "Mask": "Mascarilla",
    "NO-Hardhat": "Sin casco",
    "NO-Mask": "Sin mascarilla",
    "NO-Safety Vest": "Sin chaleco",
    "Person": "Persona",
    "Safety Cone": "Cono de seguridad",
    "Safety Vest": "Chaleco",
    "machinery": "Maquinaria",
    "vehicle": "Vehículo"
}

    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al leer la cámara.")
            break

        hardhat_count = vest_count = person_count = 0
        hardhat_detected = person_detected = False

        results = model(frame)

        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = box.conf[0]
                    cls = int(box.cls[0])

                    original_label = model.names[cls]
                    translated_label = label_translation.get(original_label, original_label)
                    label = f"{translated_label} ({confidence:.2f})"

                    color = colors[cls % len(colors)]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    draw_text_with_background(frame, label, (x1, y1 - 10), font_scale=0.4, color=(255, 255, 255), bg_color=color, alpha=0.8)

                    if model.names[cls] == "Hardhat":
                        hardhat_count += 1
                        hardhat_detected = True
                    elif model.names[cls] == "Safety Vest":
                        vest_count += 1
                    elif model.names[cls] == "Person":
                        person_count += 1
                        person_detected = True

        # Tiempo desde último casco detectado
        if hardhat_detected:
            last_hardhat_time = time.time()

        no_helmet_duration = time.time() - last_hardhat_time

        # Enviar correo si no hay casco durante 10s y hay persona
        if person_detected and not hardhat_detected and (time.time() - last_email_time) >= 10:
            image_path = "no_hardhat_frame.jpg"
            cv2.imwrite(image_path, frame)
            send_email_in_background(image_path)
            email_sent_flag = True
            email_sent_time = time.time()
            last_email_time = time.time()

        # Mostrar panel lateral
        draw_dashboard(frame, hardhat_count, vest_count, person_count)

        # Mostrar franja de alerta si aplica
        if person_detected and not hardhat_detected:
            draw_text_with_background(frame, "ALERTA: Persona sin casco", (220, 20), font_scale=0.7, color=(255, 255, 255), bg_color=(0, 0, 255), alpha=0.9)

        # Mostrar cronómetro de ausencia de casco
        draw_text_with_background(frame, f"⏱️ Sin casco: {no_helmet_duration:.1f}s", (frame.shape[1] - 210, 60), font_scale=0.5, color=(255, 255, 255), bg_color=(30, 30, 30), alpha=0.6)

        # Parpadeo de notificación de correo
        if email_sent_flag and (time.time() - email_sent_time) < 3:
            if int((time.time() - email_sent_time) * 2) % 2 == 0:
                draw_text_with_background(frame, "Correo enviado", (frame.shape[1] - 200, 30), font_scale=0.5, color=(0, 255, 0), bg_color=(0, 0, 0), alpha=0.8)

        # Redimensionar la imagen para mejor visualización
        resized_frame = cv2.resize(frame, (960, 720), interpolation=cv2.INTER_LINEAR)
        cv2.imshow("YOLOv8 Annotated Feed", resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
