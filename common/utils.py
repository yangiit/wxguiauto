import logging
from logging.handlers import RotatingFileHandler

class Logger:
    _instance = None

    def __new__(cls, name, level=logging.DEBUG,
                fmt='%(asctime)s - %(process)d - %(thread)d - %(name)s - %(levelname)s - %(message)s',
                file_path='../../log/run.log'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger(name)
            cls._instance.logger.setLevel(level)  # 动态设置级别

            # 配置格式
            formatter = logging.Formatter(fmt)  # 接收自定义格式

            # 控制台输出
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            cls._instance.logger.addHandler(stream_handler)

            # 文件输出（可选）
            if file_path:
                # 轮转配置参数
                max_bytes = 1 * 1024 * 1024 * 100  # 100MB
                backup_count = 5  # 保留5个文件

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

    # 扩展方法：支持不同级别日志
    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)