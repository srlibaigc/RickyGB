"""
心跳检测模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出主要功能
try:
    from .gateway_heartbeat import main as heartbeat_main
    from .gateway_heartbeat import GatewayHeartbeat
    
    __all__ = ['heartbeat_main', 'GatewayHeartbeat']
except ImportError as e:
    print(f"导入心跳检测模块时出错: {e}")
    __all__ = []