![Header Image](Visuals/ppe-public-view.png)  

# Construction Safety Detection - Mail Alert (Yolov8)

This project focuses on enhancing construction site safety through real-time detection of safety gear such as helmets, vests, and masks worn by workers, as well as detecting the presence of a person. The detection is performed using YOLOv8, a state-of-the-art object detection algorithm.


## Overview

Construction sites present various safety hazards, and ensuring that workers wear appropriate safety gear is crucial for accident prevention. This project automates the process of safety gear detection using computer vision techniques. By deploying YOLOv8, the system can detect whether a worker is wearing a helmet, a vest, a mask, or all, and identify people in real-time.

## Features

- **Helmet Detection:** Detects whether a worker is wearing a helmet.
- **Vest Detection:** Detects whether a worker is wearing a safety vest.
- **Mask Detection:** Detects whether a worker is wearing a mask.
- **Person Detection:** Detects the presence of a person within the construction site.
- **Count Display:** Displays real-time counts of detected helmets, vests, masks, and persons on a sideboard overlay.
- **Email Alerts:** Sends email alerts if a person is detected without a helmet, with a frame of the incident attached.
- **Non-Blocking Email Process:** Ensures video feed remains smooth while email alerts are sent in the background.
- **Mail Sent Notification:** A popup is displayed in the top-right corner of the video feed when an email alert is successfully sent.

## Requirements

- Python 3.9
- YOLOv8 dependencies (refer to YOLOv8 documentation for installation instructions)
- OpenCV
- Other dependencies as mentioned in the project code

## Installation

### Using `conda` (Recommended)

1. Create a conda environment from the `yolo_env.yml` file:

    ```bash
    conda env create -f yolo_env.yml
    ```

2. Activate the environment:

    ```bash
    conda activate yolo
    ```

3. Ensure the YOLOv8 weights file (`ppe.pt`) and place it in the designated directory.

## Configuration for Email Alerts

To enable email alert functionality, update the `.env` file in the project directory with your email details:

```text
SENDER_EMAIL=your_email@gmail.com
RECEIVER_EMAIL=receiver_email@example.com
EMAIL_PASSWORD=your_email_password
```

- **SENDER_EMAIL:** The email address that will send the alerts.
- **RECEIVER_EMAIL:** The email address that will receive the alerts.
- **EMAIL_PASSWORD:** The app-specific password or account password for the sender email. (For Gmail, you need to generate an [app-specific password](https://support.google.com/accounts/answer/185833?hl=en)).

> **Important:** Do not share your `.env` file publicly to avoid exposing sensitive information.

---

## Usage

1. Navigate to the project directory.

2. Run the detection script:

    ```bash
    python webcam.py
    ```

3. The script will initiate real-time detection using your webcam or process a video file.

4. Detected objects will be highlighted with bounding boxes indicating whether a helmet, vest, and/or mask is worn, and if a person is detected. The following features are included:

    - **Real-Time Detection Overlay:** Bounding boxes with class labels.
    - **Counts Display:** Real-time display of detected helmets, vests, masks, and persons.
    - **Email Alerts:** Alerts for any person without a helmet, with an image attachment of the frame.

---

