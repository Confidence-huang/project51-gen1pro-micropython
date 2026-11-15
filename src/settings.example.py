"""复制为 settings.py 后填写设备专用账号；此模板不包含秘密。"""

MQTT_HOST = "填入 EMQX 实例的公网域名"
MQTT_PORT = 8883
MQTT_USER = "填入设备专用发布账号"
MQTT_PASSWORD = "填入设备专用密码"
MQTT_CA_PATH = "/flash/mqtt_ca.pem"
MQTT_TOPIC = "classroom/room01/telemetry"
ROOM_ID = "room01"
DEVICE_ID = "f413zh-gen1pro-01"
NTP_HOST = "pool.ntp.org"
PUBLISH_INTERVAL_SECONDS = 10
