import logging
from modules import (
    TuyaOpenAPI,
    TUYA_LOGGER,
)

from config import settings
import cv2
import mediapipe as mp
import math

def DistanceBetweenIndexAndThumb(hand_landmarks, mp_hands):
    hd = hand_landmarks.landmark
    mp = mp_hands.HandLandmark
    return math.dist(
        [hd[mp.INDEX_FINGER_TIP].x, hd[mp.INDEX_FINGER_TIP].y], 
        [hd[mp.THUMB_TIP].x, hd[mp.THUMB_TIP].y]
        )

#Fixme: not working
def GetAvailableDevices(openapi, devices):
    # List of available devices
    available_devices = []

    # Get devices status
    for device in devices:
        response = openapi.post("/v1.0/iot-03/devices/{}/commands".format(devices[0]), {'commands': []})
        if response['success'] == True:
            available_devices.append(device)

    return available_devices

def ChangeDeviceStatus(openapi, device):
    # Get device current status
    response = openapi.get("/v1.0/iot-03/devices/{}/status".format(device))

    # New status
    value = not response['result'][0]['value']

    # Post new status
    commands = {'commands': [{'code': 'switch_led', 'value': value}]}
    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(device), commands)


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
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            max_num_hands=1) as hands:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:

                    d = DistanceBetweenIndexAndThumb(hand_landmarks, mp_hands)
                    if d < 0.03:
                        for device in devices:
                            ChangeDeviceStatus(openapi, device)

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




