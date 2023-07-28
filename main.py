"""This module has components that are used for testing tuya's device control and Pulsar massage queue."""
import logging
from modules import (
    TuyaOpenAPI,
    TUYA_LOGGER,
)

from config import settings
import mouse
import cv2
import mediapipe as mp
import math

def SmartAPI(api_endpoint, access_id, access_key, mq_endpoint, devices):

    # Enable debug log
    TUYA_LOGGER.setLevel(logging.DEBUG)

    # Init openapi and connect
    openapi = TuyaOpenAPI(api_endpoint, access_id, access_key)
    openapi.connect()

    # Camera config
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            #mouse.move(100, 100, absolute=False, duration=0.2)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    #print(results.multi_handedness)
                    d1 = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x)**2)
                    d2 = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x)**2)
                    d3 = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x)**2)
                    d4 = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x)**2)
                    d5 = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x)**2)
                    dt = d3 + d4 + d5
                    dn = math.sqrt((hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y-hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y)**2+(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x-hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x)**2)
                    #print(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x, hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y)
                    if dt < 0.8:
                        if dn < 0.03:

                            # Devices handling
                            for device in devices:

                                response = openapi.get("/v1.0/iot-03/devices/{}/status".format(device))

                                value = not response['result'][0]['value']

                                # Send commands
                                commands = {'commands': [{'code': 'switch_led', 'value': value}]}
                                openapi.post('/v1.0/iot-03/devices/{}/commands'.format(device), commands)

                        mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
            cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
        cap.release()

if __name__ == "__main__":

    api_endpoint = settings.API_ENDPOINT
    access_id = settings.ACCESS_ID
    access_key = settings.ACCESS_KEY
    mq_endpoint = settings.MQ_ENDPOINT
    devices = settings.DEVICES.split(",")

    SmartAPI(api_endpoint, access_id, access_key, mq_endpoint, devices)




