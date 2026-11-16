"""临时验证 STM32 经 EC200U 建立 4G 数据通路，不使用 MQTT 凭据。

在 VS Code 打开此文件并运行“板端：运行当前脚本（不上传）”。
本脚本只检查 USIM、附着与一个公开域名的 DNS 解析，不保存或上报数据。
"""

import usocket as socket

from quectel import Network


def run():
    """依照官方初始化顺序接入，并在测试后释放网络对象。"""
    network = Network()
    print("CELLULAR_INIT_START")
    network.init()
    try:
        # 只检查调用是否成功；USIM 标识可能是敏感信息，不打印返回值。
        network.query_usim()
        network.attach()
        print("CELLULAR_ATTACH_OK")

        # DNS 证明数据通路可用；不向该网站发送 HTTP 请求。
        addresses = socket.getaddrinfo("example.com", 80)
        if not addresses:
            raise RuntimeError("DNS returned no address")
        print("CELLULAR_DNS_OK")
    finally:
        network.deinit()


if __name__ == "__main__":
    run()
