# src/servo.py
"""
Optional ESP8266 servo-pan control over MQTT.

Python publishes angle commands to:
  broker.benax.rw:1883
  face-recognition/servo/pan
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

try:
    import paho.mqtt.client as mqtt
except Exception as e:
    mqtt = None
    _MQTT_IMPORT_ERROR = e


@dataclass
class ServoPanConfig:
    min_angle: int = 20
    max_angle: int = 160
    center_angle: int = 90
    gain: float = 10.0
    deadzone_frac: float = 0.08
    update_every_s: float = 0.12


class ServoPanClient:
    def __init__(
        self,
        enabled: bool = False,
        cfg: ServoPanConfig | None = None,
        broker: str = "broker.benax.rw",
        port: int = 1883,
        topic: str = "face-recognition/servo/pan",
        client_id: str = "face-recognition-python",
    ):
        self.cfg = cfg or ServoPanConfig()
        self.angle = int(self.cfg.center_angle)
        self.broker = broker
        self.port = int(port)
        self.topic = topic
        self.client_id = client_id
        self._enabled = bool(enabled)
        self._last_send = 0.0
        self._last_error: Optional[str] = None
        self._client: Optional[mqtt.Client] = None

        if self._enabled:
            self._connect()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def close(self) -> None:
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()

    def center(self) -> None:
        self.send_angle(self.cfg.center_angle, force=True)

    def step(self, delta: int) -> None:
        self.send_angle(self.angle + int(delta), force=True)

    def track_x(self, target_x: float, frame_width: int) -> None:
        if not self.enabled or frame_width <= 0:
            return

        frame_center = frame_width * 0.5
        error_frac = (float(target_x) - frame_center) / frame_center
        if abs(error_frac) < self.cfg.deadzone_frac:
            return

        next_angle = self.angle + int(round(error_frac * self.cfg.gain))
        self.send_angle(next_angle)

    def send_angle(self, angle: int, force: bool = False) -> bool:
        if not self.enabled:
            return False

        now = time.time()
        if not force and (now - self._last_send) < self.cfg.update_every_s:
            return False

        angle = int(max(self.cfg.min_angle, min(self.cfg.max_angle, angle)))
        if self._client is None:
            self._connect()
        if self._client is None:
            self._last_send = now
            return False

        info = self._client.publish(self.topic, str(angle), qos=0, retain=False)
        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            self.angle = angle
            self._last_send = now
            self._last_error = None
            return True

        self._print_error(f"publish failed with MQTT rc={info.rc}")
        self._last_send = now
        return False

    def _connect(self) -> None:
        if mqtt is None:
            raise RuntimeError(
                f"paho-mqtt is required for servo control: {_MQTT_IMPORT_ERROR}\n"
                "Install it with: python -m pip install paho-mqtt"
            )

        try:
            if hasattr(mqtt, "CallbackAPIVersion"):
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)
            else:
                client = mqtt.Client(client_id=self.client_id)
            client.connect(self.broker, self.port, keepalive=30)
            client.loop_start()
            self._client = client
            print(f"[servo] MQTT connected: {self.broker}:{self.port}, topic={self.topic}")
        except OSError as e:
            self._print_error(f"MQTT connection failed: {e}")
            self._client = None

    def _print_error(self, msg: str) -> None:
        if msg != self._last_error:
            print(f"[servo] {msg}")
            self._last_error = msg
