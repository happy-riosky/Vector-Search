from colorama import init, Fore, Style  # type: ignore
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(module)s.%(funcName)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 初始化 colorama
init(autoreset=True)

# 定义日志级别对应的颜色
LOG_COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}

# 日志轮转配置
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # 保留5个备份文件

# 日志文件路径
LOG_DIR = "./logs"

def get_log_filepath(name: str, log_dir: str = LOG_DIR) -> str:
    timestamp = datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"{name}_{timestamp}.log")

class ColoredFormatter(logging.Formatter):
    """自定义格式化器，为日志级别添加颜色"""

    def format(self, record):
        # 获取原始日志消息
        message = super().format(record)

        # 为日志级别添加颜色
        level_color = LOG_COLORS.get(record.levelname, "")
        if level_color:
            # 只对日志级别关键字进行着色
            level_name = record.levelname
            colored_level = f"{level_color}{level_name}{Style.RESET_ALL}"
            message = message.replace(level_name, colored_level)

        return message


class Logger:
    _instances: dict[str, "Logger"] = {}  # 存储不同名称的 logger 实例

    def __new__(cls, name, log_dir=LOG_DIR, level=LOG_LEVEL, max_bytes=MAX_BYTES, backup_count=BACKUP_COUNT):
        if name not in cls._instances:
            cls._instances[name] = super(Logger, cls).__new__(cls)
        return cls._instances[name]

    def __init__(self, name, log_dir=LOG_DIR, level=LOG_LEVEL, max_bytes=MAX_BYTES, backup_count=BACKUP_COUNT):
        # 如果已经初始化过，直接返回
        if hasattr(self, "logger"):
            return

        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Generate log file name with timestamp
        log_file = get_log_filepath(name, log_dir)

        # Configure logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create formatters
        colored_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        plain_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

        # Rotating file handler
        rotating_handler = RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count, 
            encoding="utf-8"
        )
        rotating_handler.setLevel(level)
        rotating_handler.setFormatter(plain_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(colored_formatter)

        # Add handlers to logger
        self.logger.addHandler(rotating_handler)
        self.logger.addHandler(console_handler)

    @property
    def log(self):
        return self.logger


logger = Logger("default").log
