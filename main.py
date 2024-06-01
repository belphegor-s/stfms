import cv2
import torch
import threading
import queue
import serial
import os

# ser = serial.Serial('COM5', 9600)

# Function for processing frames and detection
def process_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (output_width, output_height))
        results = model(frame)
        vehicle_count = {label: 0 for label in vehicle_labels_color}
        for det in results.pred[0]:
            if det[4] >= 0.4:
                label = int(det[5])
                if label in vehicle_labels_color:
                    vehicle_count[label] += 1
                    xyxy = det[:4].cpu().numpy().astype(int)
                    x1, y1, x2, y2 = xyxy
                    color = vehicle_labels_color[label]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        total_count = sum(vehicle_count.values())

        print(f'Total Vehicle Count: {total_count}')
        # ser.write(str(total_count).encode())  # Send total vehicle count to Arduino
        
        for label, count in vehicle_count.items():
            cv2.putText(frame, f'{vehicle_labels[label]}: {count}', (20, 30 + 30 * label), cv2.FONT_HERSHEY_SIMPLEX, 1, vehicle_labels_color[label], 2)
        frame_queue.put(frame)

model = torch.hub.load('ultralytics/yolov5', 'yolov5x')

# Image or video stream
# input_source = 'test.mp4'
input_source = 'image.png'

if os.path.splitext(input_source)[1] in ['.jpg', '.png', '.jpeg']:
    cap = cv2.VideoCapture(input_source)
    frame_rate = 1
else:
    cap = cv2.VideoCapture(input_source)
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

output_width = 992
output_height = 576

vehicle_labels_color = {
    2: (0, 255, 0),  # Car (Green)
    7: (0, 0, 255),  # Truck (Red)
    3: (0, 255, 255),  # Motorcycle (Yellow)
    5: (255, 0, 0),  # Bus (Blue)
}

vehicle_labels = {
    2: 'Car',
    7: 'Truck',
    3: 'Motorcycle',
    5: 'Bus',
}

frame_queue = queue.Queue()

frame_processing_thread = threading.Thread(target=process_frames)
frame_processing_thread.start()

while True:
    frame = frame_queue.get()
    if frame is None:
        break
    cv2.imshow('Vehicle Detection', frame)
    if cv2.waitKey(1000 // frame_rate) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
# ser.close()
