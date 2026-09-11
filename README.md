# face-recognition-5pt

A CPU-only face recognition pipeline: Haar detection + MediaPipe 5-point
landmarks + similarity-transform alignment + ArcFace ONNX embeddings.

See the accompanying book for full explanations. Quick start:

1. Install Python 3.11 (MediaPipe FaceMesh legacy API is not available on Python 3.13).
2. py -3.11 -m venv .venv
3. .venv\Scripts\Activate.ps1      (Windows PowerShell)
3. pip install -r requirements.txt
4. python -m src.camera            (validate webcam)
5. python -m src.detect            (validate face box)
6. python -m src.landmarks         (validate 5 points)
7. python -m src.align             (validate alignment)
8. Download the real ArcFace model into models/embedder_arcface.onnx, or keep it as models/w600k_r50.onnx
9. python -m src.embed             (validate embeddings)
10. python -m src.enroll           (enroll people)
11. python -m src.evaluate         (tune threshold)
12. python -m src.recognize        (live recognition)

Optional ESP8266 servo pan over MQTT

1. Open hardware/esp8266_servo_pan/esp8266_servo_pan.ino in Arduino IDE.
2. Set WIFI_SSID and WIFI_PASS, then upload to the ESP8266MOD / NodeMCU.
3. Wire servo signal to D1/GPIO5, servo power to external 5V, and connect all grounds together.
4. Install the Arduino PubSubClient library if Arduino IDE asks for it.
5. Confirm Serial Monitor shows WiFi connected, MQTT connected, and subscribed to:
   face-recognition/servo/pan
6. Install Python requirements:
   python -m pip install -r requirements.txt
7. Test automatic camera pan:
   python -m src.camera --servo-mqtt --auto-scan
8. Run face-following recognition:
   python -m src.recognize --servo-mqtt

Defaults:
- MQTT broker: broker.benax.rw
- MQTT port: 1883
- MQTT topic: face-recognition/servo/pan
"# face-recognition" 
