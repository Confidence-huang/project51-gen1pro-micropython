"""通过 EC200U 建立 4G、可信 UTC、证书校验的 MQTT 连接并发布快照。"""

import usocket as socket
import struct
import time


def attach_4g():
    """按官方 Network.init/attach 顺序接入；MQTT 连接再验证实际 IP 通路。"""
    from quectel import Network

    network = Network()
    network.init()
    network.attach()
    return network


def synchronize_utc(ntp_host):
    """从 NTP 响应设置板端 RTC；失败时上层禁止发布带伪时间的消息。"""
    import machine

    # NTP 秒数从 1900 起算，MicroPython 的 Unix epoch 可能是 1970 或 2000。
    ntp_delta = 2208988800 if time.gmtime(0)[0] == 1970 else 3155673600
    addresses = socket.getaddrinfo(ntp_host, 123)
    channel = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        channel.settimeout(5)
        channel.sendto(b"\x1b" + 47 * b"\0", addresses[0][-1])
        # NTP 回包是二进制；厂商 recv/recvfrom 会尝试 UTF-8 解码并抛 UnicodeError。
        packet = bytearray(48)
        received = channel.readinto(packet)
    finally:
        channel.close()
    if received != 48:
        raise RuntimeError("NTP reply is too short")
    if packet[0] >> 6 == 3 or packet[1] == 0:
        raise RuntimeError("NTP server reports unsynchronized time")

    seconds = struct.unpack("!I", packet[40:44])[0] - ntp_delta
    utc = time.gmtime(seconds)
    if utc[0] < 2025 or utc[0] > 2100:
        raise RuntimeError("NTP returned an implausible UTC year")
    machine.RTC().datetime((utc[0], utc[1], utc[2], utc[6] + 1,
                            utc[3], utc[4], utc[5], 0))
    return utc


def utc_sample_time():
    """RTC 校准后才产生网页可识别的 UTC 时间与跨重启递增的秒序号。"""
    utc = time.gmtime()
    if utc[0] < 2025 or utc[0] > 2100:
        raise RuntimeError("RTC is not synchronized")
    timestamp = "%04d-%02d-%02dT%02d:%02d:%02dZ" % utc[:6]
    return int(time.time()), timestamp


def connect_mqtt(settings):
    """用设备专用账号与根 CA 校验服务端；证书缺失时不降级明文。"""
    import tls
    from umqtt.robust import MQTTClient

    with open(settings.MQTT_CA_PATH, "rb") as certificate_file:
        certificate = certificate_file.read()
    context = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
    context.verify_mode = tls.CERT_REQUIRED
    context.load_verify_locations(certificate)

    client = MQTTClient(client_id=settings.DEVICE_ID,
                        server=settings.MQTT_HOST, port=settings.MQTT_PORT,
                        user=settings.MQTT_USER, password=settings.MQTT_PASSWORD,
                        keepalive=60, ssl=context)
    client.connect()
    return client


def publish_snapshot(client, topic, payload):
    """QoS 1 等待 Broker 确认；retain 在云端保留最新一条供新网页会话读取。"""
    client.publish(topic.encode("utf-8"), payload, qos=1, retain=True)


if __name__ == "__main__":
    # 临时运行本文件仅校准和打印 UTC，不读取设备账号或建立 MQTT 会话。
    demo_network = attach_4g()
    try:
        demo_utc = synchronize_utc("pool.ntp.org")
        print("NTP_UTC_OK", demo_utc[:6])
    finally:
        demo_network.deinit()
