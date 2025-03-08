from scapy.all import sniff, IP, TCP, UDP
from scapy.arch.windows import get_windows_if_list
from datetime import datetime
from threading import Thread, Lock
import psutil
import time
import subprocess
import json
import os

from common.utils import Logger

logger = Logger('Network')

# 配置参数
LOCAL_IP = "192.168.3.99"  # 本机IP
LOG_FILE = "wechat_traffic.log"  # 日志文件
IP_STORE_FILE = "wechat_ips.json"  # IP存储文件
CHECK_INTERVAL = 2  # IP更新间隔（秒）
MAX_HISTORY_IPS = 100  # 最大历史IP存储数量

# 全局变量
target_ips = set()  # 内存中的动态IP集合
history_ips = set()  # 持久化存储的历史IP集合
ips_lock = Lock()  # 线程锁
WEIXIN_PID = None  # 微信进程PID


def get_active_interface(local_ip):
    """根据本机IP获取活动网卡名称"""
    for iface in get_windows_if_list():
        # 检查IPv4地址
        if 'ips' in iface and local_ip in iface['ips']:
            return iface['name']
    return None


def get_weixin_pid():
    """获取微信进程PID"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'WeChat.exe':
            return proc.info['pid']
    return None


def load_history_ips():
    """加载历史IP记录"""
    global history_ips
    try:
        if os.path.exists(IP_STORE_FILE):
            with open(IP_STORE_FILE, 'r') as f:
                data = json.load(f)
                history_ips = set(data['ips'][-MAX_HISTORY_IPS:])  # 保留最新记录
                print(f"[*] 已加载 {len(history_ips)} 个历史IP")
    except Exception as e:
        print(f"[!] 历史IP加载失败: {str(e)}")


def save_history_ips():
    """保存历史IP记录（线程安全）"""
    with ips_lock:
        save_data = {'ips': list(history_ips)}
    try:
        with open(IP_STORE_FILE, 'w') as f:
            json.dump(save_data, f, indent=2)
    except Exception as e:
        print(f"[!] 历史IP保存失败: {str(e)}")


def update_target_ips():
    """增强版IP更新（含持久化）"""
    global WEIXIN_PID, target_ips, history_ips
    while True:
        # 自动刷新PID
        if not WEIXIN_PID or not psutil.pid_exists(WEIXIN_PID):
            WEIXIN_PID = get_weixin_pid()
            if not WEIXIN_PID:
                logger.error("[!] 微信进程未找到")
                time.sleep(5)
                continue

        # 获取新IP
        try:
            cmd = f'netstat -ano -p TCP | findstr "{WEIXIN_PID}"'
            output = subprocess.check_output(
                cmd, shell=True, text=True, encoding='gbk'
            )

            logger.debug(output)

            new_ips = set()
            for line in output.strip().split('\n'):
                parts = line.split()
                if len(parts) < 5:
                    continue
                remote_addr = parts[2]
                if '.' in remote_addr and ':' in remote_addr:
                    ip = remote_addr.split(':')[0]
                    if ip != LOCAL_IP:
                        new_ips.add(ip)

            # 更新集合
            with ips_lock:
                # 更新动态IP
                target_ips = new_ips.copy()
                # 更新历史IP（自动去重）
                history_ips.update(new_ips)
                # 控制历史记录大小
                if len(history_ips) > MAX_HISTORY_IPS:
                    history_ips = set(list(history_ips)[-MAX_HISTORY_IPS:])

                if new_ips:
                    logger.debug(f"[*] 动态IP更新: {new_ips} | 历史IP总数: {len(history_ips)}")

                # 每5分钟自动保存
                if time.time() % 300 < CHECK_INTERVAL:
                    save_history_ips()

        except Exception as e:
            logger.error(f"[!] IP更新失败: {str(e)}")

        time.sleep(CHECK_INTERVAL)


def packet_handler(packet):
    """增强版数据包处理（含历史IP追踪）"""
    if not packet.haslayer(IP):
        return

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst

    # 获取IP集合
    with ips_lock:
        dynamic_ips = target_ips.copy()
        historical_ips = history_ips.copy()

    # 判断是否目标IP（动态优先）
    target_ip = None
    if src_ip in dynamic_ips or dst_ip in dynamic_ips:
        target_ip = src_ip if src_ip in dynamic_ips else dst_ip
        ip_type = "动态"
    elif src_ip in historical_ips or dst_ip in historical_ips:
        target_ip = src_ip if src_ip in historical_ips else dst_ip
        ip_type = "历史"
    else:
        return

    # 确定流量方向
    direction = "↑ 出站" if src_ip == LOCAL_IP else "↓ 入站"

    # 协议解析
    proto = ""
    src_port = dst_port = 0
    if packet.haslayer(TCP):
        proto = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif packet.haslayer(UDP):
        proto = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
    else:
        return

    # 构造日志
    log_entry = {
        "time": datetime.fromtimestamp(packet.time).strftime("%Y-%m-%d %H:%M:%S.%f"),
        "direction": direction,
        "proto": proto,
        "src": f"{src_ip}:{src_port}",
        "dst": f"{dst_ip}:{dst_port}",
        "size": f"{len(packet)} B",
        "server_ip": target_ip,
        "ip_type": ip_type
    }

    log_str = (
        f"{log_entry['direction']} | "
        f"{log_entry['proto']} {log_entry['src']} → {log_entry['dst']} | "
        f"Size: {log_entry['size']} | "
        f"Server: {log_entry['server_ip']} ({log_entry['ip_type']} IP)"
    )
    logger.debug(log_str)

    # # 写入日志
    # if LOG_FILE:
    #     with open(LOG_FILE, "a") as f:
    #         f.write(log_str + "\n")


def start_monitor():
    """启动监控（含初始化）"""
    load_history_ips()  # 加载历史记录
    logger.info(f"[*] 开始监控微信流量 (本机IP: {LOCAL_IP})")
    logger.info(f"[*] 当前历史IP数量: {len(history_ips)}")
    target_iface = get_active_interface(LOCAL_IP)
    if target_iface:
        logger.info(f"[*] 使用网卡: {target_iface}")
        sniff(
            filter=f"host {LOCAL_IP} and (tcp or udp)",
            prn=packet_handler,
            store=0,
            iface=target_iface
        )
    else:
        logger.error("[!] 未找到匹配的网卡")


if __name__ == "__main__":
    # 启动IP更新线程
    Thread(target=update_target_ips, daemon=True).start()

    # 主线程抓包
    try:
        start_monitor()
    except KeyboardInterrupt:
        save_history_ips()
        logger.error("\n[!] 监控已停止，历史IP已保存")
