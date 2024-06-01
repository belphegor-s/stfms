# import serial
# import time
# from datetime import datetime
# import cv2
# import torch

# """ for test simulation """
# # def simulate_vehicle_detection(lane_code):
# #     """ Simulates the detection of vehicles. """
# #     base_count = random.randint(1, 20)
# #     return base_count

# def detect_vehicles(image_path):
#     """Detect vehicles in an image, count them, and annotate the image with labels and bounding boxes."""
#     model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

#     img = cv2.imread(image_path)

#     # Perform inference
#     results = model(img)

#     # Prepare to count and annotate each vehicle type
#     vehicle_counts = {2: 0, 3: 0, 5: 0, 7: 0}  # Car, Motorcycle, Bus, Truck
#     vehicle_labels = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck'}
#     colors = {2: (255, 0, 0), 3: (0, 255, 0), 5: (0, 0, 255), 7: (255, 255, 0)}

#     for *xyxy, conf, cls_id in results.xyxy[0]:
#         if cls_id.item() in vehicle_counts:
#             vehicle_counts[int(cls_id.item())] += 1
#             label = f"{vehicle_labels[int(cls_id.item())]} {vehicle_counts[int(cls_id.item())]}"
#             color = colors[int(cls_id.item())]
#             cv2.rectangle(img, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), color, 2)
#             cv2.putText(img, label, (int(xyxy[0]), int(xyxy[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#     current_datetime = datetime.now()
#     formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

#     # annotated_path = f"annotations/annotated_{datetime.now().timestamp()}_{image_path}"
#     annotated_path = f"annotations/annotated_{formatted_datetime}_{image_path}"
#     cv2.imwrite(annotated_path, img)  # Save the annotated image
#     total_count = sum(vehicle_counts.values())
#     return total_count, annotated_path, vehicle_counts

# def main():
#     port = 'COM5'
#     baud_rate = 9600
#     with serial.Serial(port, baud_rate) as ser:
#         print("Connected to Arduino.")
#         while True:
#             line = ser.readline().decode().strip()
#             print('Received Data:', line)
#             if line in ["00", "01", "10", "11"]:
#                 print(f"Received lane code: {line}")

#                 # for test simulation
#                 # vehicle_count = simulate_vehicle_detection(line)

#                 image_path = f"lane_{line}.png"
#                 vehicle_count, annotated_path, vehicle_counts = detect_vehicles(image_path)

#                 print(f"Sending vehicle count {vehicle_count} for lane {line}")
#                 ser.write(f"{vehicle_count}\n".encode())

#                 # Debug data ->
#                 # print(f"Annotated image saved as {annotated_path}")
#                 # for vehicle_type, count in vehicle_counts.items():
#                 #     print(f"{vehicle_type} - {count}")

#                 time.sleep(2)

# if __name__ == "__main__":
#     main()
import serial
import time
from datetime import datetime
import cv2
import torch
import numpy as np

def detect_vehicles(image_path):
    """Detect vehicles in an image, count them, and annotate the image with labels and bounding boxes."""
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

    img = cv2.imread(image_path)

    # Perform inference
    results = model(img)

    # Prepare to count and annotate each vehicle type
    vehicle_counts = {2: 0, 3: 0, 5: 0, 7: 0}  # Car, Motorcycle, Bus, Truck
    vehicle_labels = {2: 'Car', 3: 'Motorcycle', 5: 'Bus', 7: 'Truck'}
    colors = {2: (255, 0, 0), 3: (0, 255, 0), 5: (0, 0, 255), 7: (255, 255, 0)}

    for *xyxy, conf, cls_id in results.xyxy[0]:
        if cls_id.item() in vehicle_counts:
            vehicle_counts[int(cls_id.item())] += 1
            label = f"{vehicle_labels[int(cls_id.item())]} {vehicle_counts[int(cls_id.item())]}"
            color = colors[int(cls_id.item())]
            cv2.rectangle(img, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), color, 2)
            cv2.putText(img, label, (int(xyxy[0]), int(xyxy[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    annotated_path = f"annotations/annotated_{formatted_datetime}_{image_path}"
    cv2.imwrite(annotated_path, img)  # Save the annotated image
    total_count = sum(vehicle_counts.values())
    return total_count, annotated_path, vehicle_counts, img

def display_images_in_grid(images, current_lane, target_size=(360, 480)):
    """Display a list of images in a 2x2 grid with only the current lane shown and others blacked out."""
    h, w = target_size
    grid_image = np.zeros((2 * h, 2 * w, 3), dtype=np.uint8)

    resized_images = [cv2.resize(img, (w, h)) if img is not None else np.zeros((h, w, 3), dtype=np.uint8) for img in images]

    for i in range(4):
        if i == current_lane:
            if i == 0:
                grid_image[0:h, 0:w, :] = resized_images[i]
            elif i == 1:
                grid_image[0:h, w:2*w, :] = resized_images[i]
            elif i == 2:
                grid_image[h:2*h, 0:w, :] = resized_images[i]
            elif i == 3:
                grid_image[h:2*h, w:2*w, :] = resized_images[i]

    cv2.namedWindow("Traffic Lanes", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Traffic Lanes", 700, 500)
    cv2.imshow("Traffic Lanes", grid_image)
    cv2.waitKey(1)  # Display the window for 1 ms and process any GUI events

def main():
    port = 'COM5'
    baud_rate = 9600
    with serial.Serial(port, baud_rate) as ser:
        print("Connected to Arduino.")
        lane_images = [None, None, None, None]
        while True:
            line = ser.readline().decode().strip()
            print('Received Data:', line)
            if line in ["00", "01", "10", "11"]:
                lane_index = int(line, 2)
                print(f"Received lane code: {line}")

                image_path = f"lane_{line}.png"
                vehicle_count, annotated_path, vehicle_counts, img = detect_vehicles(image_path)
                lane_images[lane_index] = img

                display_images_in_grid(lane_images, lane_index)

                print(f"Sending vehicle count {vehicle_count} for lane {line}")
                ser.write(f"{vehicle_count}\n".encode())

                time.sleep(2)

if __name__ == "__main__":
    main()
