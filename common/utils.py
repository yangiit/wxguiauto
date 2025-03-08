import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


class Logger:
    _instance = None

    def __new__(cls, name, level=logging.DEBUG,
                fmt='%(asctime)s - %(process)d - %(thread)d - %(name)s - %(levelname)s - %(message)s',
                file_path=None):  # 默认路径改为None，内部生成
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger(name)
            cls._instance.logger.setLevel(level)

            # 配置格式
            formatter = logging.Formatter(fmt)

            # 控制台输出
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(stream_handler)

            # 动态生成默认日志路径
            if file_path is None:
                # 获取当前文件（Logger类）的绝对路径
                current_file_path = Path(__file__).resolve()
                # 定位到wx_auto目录（假设Logger类位于wx_auto/utils/logger.py）
                wx_auto_dir = current_file_path.parent.parent  # 调整层级根据实际项目结构
                log_dir = wx_auto_dir / 'log'
                file_path = log_dir / 'run.log'
                file_path = str(file_path)

            # 确保日志目录存在
            log_dir = os.path.dirname(file_path)
            os.makedirs(log_dir, exist_ok=True)

            # 配置轮转文件处理器
            max_bytes = 100 * 1024 * 1024  # 100MB
            backup_count = 5
            file_handler = RotatingFileHandler(
                filename=file_path,
                mode='a',
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(file_handler)

        return cls._instance

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)