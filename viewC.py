from ultralytics import YOLO

# Cargar el modelo
model = YOLO("Model/ppe.pt")  # Cambia la ruta si tu modelo está en otro lugar

# Imprimir las etiquetas
print("Etiquetas del modelo:")
for i, name in model.names.items():
    print(f"{i}: {name}")

