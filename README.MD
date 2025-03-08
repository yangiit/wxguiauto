
# WeChat自动化与网络监控工具

## 项目概述
本项目是一个基于UI自动化和网络事件驱动的微信操作与监控工具，主要功能包括：
- **微信界面自动化**：自动定位窗口、操作导航栏、管理会话列表、发送消息
- **网络流量监控**：实时捕获微信通信的IP流量，支持动态/历史IP分析
- **组合式架构**：通过组件化设计实现界面元素的灵活组合与管理

---

## 技术架构亮点

### 1. 组合模式 (Composite Pattern)
#### 应用场景
- **微信界面组件化**：将微信主窗口拆分为`Toolbar`(导航栏)、`SessionOptions`(会话列表)、`SessionWindow`(聊天窗口)等独立组件
- **层级关系**：
  ```plaintext
  WeChat (根组件)
  ├── Toolbar
  ├── SessionOptions
  │    ├── Searchbar
  │    └── SessionList
  └── SessionWindow
  ```
- **实现优势**：
  - 支持递归结构：每个组件可独立操作或组合使用
  - 新增组件类型无需修改现有架构（开闭原则）
  - 统一接口：所有组件通过`perform_action()`等方法提供标准操作

#### 代码示例
```python
# core/main.py
class WeChat:
    def __init__(self):
        # 组合子组件
        self.toolbar = Toolbar(...)
        self.session_options = SessionOptions(...)
        self.session_window = SessionWindow(...)
```

---

### 2. 网络事件驱动架构
#### 核心机制
- **双线程模型**：
  - **监控线程**：持续更新微信关联IP（`update_target_ips()`）
  - **嗅探线程**：实时捕获网络数据包（`sniff()`）

- **事件处理流程**：
  ```mermaid
  graph TD
    A[网络包到达] --> B{IP匹配检查}
    B -->|动态IP| C[实时日志记录]
    B -->|历史IP| D[带标记记录]
    C/D --> E[日志持久化]
  ```

#### 关键技术点
- **IP动态追踪**：
  ```python
  # 通过netstat获取微信进程网络连接
  cmd = f'netstat -ano -p TCP | findstr "{WEIXIN_PID}"'
  output = subprocess.check_output(cmd, shell=True, text=True, encoding='gbk')
  ```

- **流量分类处理**：
  ```python
  def packet_handler(packet):
      if src_ip in dynamic_ips:    # 优先处理动态IP
      elif src_ip in history_ips:  # 次级处理历史IP
  ```

---

## 快速开始

### 环境要求
- **操作系统**: Windows 10 或更高版本  
- **Python 环境**: Python 3.8+（需配置环境变量）  
- **微信客户端**: 微信PC版 3.9.12（[官方下载](https://weixin.qq.com/)）  
- **开发工具**（需手动安装）:  
  - `Inspect` - 微软UI元素定位工具（[Windows SDK 内置](https://developer.microsoft.com/zh-cn/windows/downloads/windows-sdk/)）  
  - `Procexp` - 进程资源管理器（[微软官方下载](https://learn.microsoft.com/zh-cn/sysinternals/downloads/process-explorer)）  

---

#### 工具说明
1. **Inspect**  
   - 用途：定位微信UI控件属性（如`ClassName`、`ControlType`）  
   - 验证：运行后能识别微信窗口的`WeChatMainWndForPC`类名  

2. **Procexp**  
   - 用途：监控微信进程网络活动（需以管理员权限运行）  
   - 验证：在工具中搜索`WeChat.exe`进程并查看TCP/UDP连接  

#### 版本注意
- 微信3.9.12版本存在以下依赖：  
  - 窗口层级结构固定（核心代码依赖`PaneControl`索引）  
  - 控件本地化名称为中文（如"清空"按钮）  
- 若使用其他版本，需自行适配UI自动化相关代码  

### 安装步骤
```bash
# 克隆仓库
git clone https://gitee.com/look-up-at-the-starspy/wx_auto.git

# 安装依赖
pip install -r requirements.txt

# 配置本地IP（修改core/event/wechat_monitor.py）
LOCAL_IP = "192.168.3.99"  # 改为实际本机IP
```

### 运行示例
```bash
# 启动微信自动化
python core/main.py

# 启动网络监控（需管理员权限）
python core/event/wechat_monitor.py
```

---

## 贡献指南
欢迎通过以下方式参与贡献：
1. 提交PR优化组件化架构
2. 扩展网络事件处理逻辑
3. 完善自动化测试用例
4. 文档翻译与改进

遵循MIT开源协议，请保留原始版权声明。

> 项目持续演进中，期待您的参与！