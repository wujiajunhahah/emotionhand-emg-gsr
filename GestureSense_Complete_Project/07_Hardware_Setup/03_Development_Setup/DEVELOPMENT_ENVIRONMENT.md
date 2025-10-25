# 💻 GestureSense 开发环境配置指南

## 📋 概述

本指南将详细说明如何配置GestureSense项目的完整开发环境，包括Arduino编程、Python数据处理和机器学习模型训练。

## 🎯 系统要求

### 电脑配置要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **内存**: 8GB+ RAM (推荐16GB)
- **存储**: 20GB+ 可用空间
- **USB端口**: 至少2个USB-A接口
- **网络**: 稳定的互联网连接

### 支持的开发平台
- **Windows**: Visual Studio Code + Arduino IDE
- **macOS**: VS Code + Arduino IDE
- **Linux**: VS Code + Arduino IDE

---

## 🛠️ 软件安装清单

### 1. Arduino开发环境

#### Arduino IDE 2.0
```bash
下载地址: https://www.arduino.cc/en/software
选择版本: Arduino IDE 2.0+
安装要求:
- Windows: Windows 10 or later
- macOS: macOS 10.15 or later
- Linux: 64-bit Linux
```

#### Arduino板包安装
```
1. 打开Arduino IDE
2. 文件 → 首选项
3. 附加开发板管理器网址添加:
   - Arduino Nano RP2040: https://github.com/arduino/ArduinoCore-mbed/releases/download/4.0.0/package_mbed_index.json
4. 工具 → 开发板 → 开发板管理器
5. 搜索并安装:
   - "Arduino Mbed OS Nano Boards" by Arduino
```

#### 必需库安装
```cpp
在Arduino IDE中安装以下库:
1. 工具 → 管理库 → 搜索并安装:
   - "MPU6050" by Electronic Cats
   - "Wire" by Arduino (内置)
   - "I2S" by Arduino (内置)
   - "MAX30102" by SparkFun
   - "Adafruit_SSD1306" by Adafruit
   - "Adafruit_GFX" by Adafruit
```

### 2. Python开发环境

#### Python 3.8+ 安装
```bash
# Windows: 从 python.org 下载安装包
# macOS: 使用 Homebrew
brew install python@3.9

# Ubuntu/Debian:
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# 验证安装:
python --version  # 应显示 Python 3.8+
pip --version
```

#### 虚拟环境创建
```bash
# 创建项目目录
mkdir ~/GestureSense_Development
cd ~/GestureSense_Development

# 创建虚拟环境
python -m venv echowrist_env

# 激活虚拟环境
# Windows:
echowrist_env\Scripts\activate
# macOS/Linux:
source echowrist_env/bin/activate
```

#### Python依赖安装
```bash
# 升级pip
pip install --upgrade pip

# 安装基础依赖
pip install numpy scipy matplotlib pandas scikit-learn

# 安装音频处理依赖
pip install librosa sounddevice pyaudio

# 安装机器学习依赖
pip install torch torchvision torchaudio

# 安装计算机视觉依赖
pip install opencv-python mediapipe

# 安装数据可视化依赖
pip install plotly seaborn streamlit

# 安装串口通信依赖
pip install pyserial

# 安装硬件控制依赖
pip install adafruit-circuitpython-mpu6050
pip install adafruit-circuitpython-max30102

# 安装Jupyter Notebook
pip install jupyter ipykernel

# 可选: 安装Conda (推荐数据科学)
# 下载: https://docs.conda.io/en/latest/miniconda.html
```

### 3. IDE和编辑器配置

#### Visual Studio Code
```bash
下载地址: https://code.visualstudio.com/

推荐扩展:
1. Python - Microsoft
2. Arduino - Microsoft
3. C/C++ - Microsoft
4. Jupyter - Microsoft
5. GitLens - GitKraken
6. Thunder Client (API测试)
7. Python Docstring Generator
```

#### Arduino IDE配置
```
1. 文件 → 首选项
2. 设置:
   - 编译器警告: "更多"
   - 验证上传后: "显示详细输出"
   - 代码格式化: 启用
3. 工具 → 开发板 → Arduino Nano RP2040
4. 工具 → 端口 → 选择对应端口
```

---

## 🚀 快速配置脚本

### Windows配置脚本 (setup_windows.bat)
```batch
@echo off
echo 正在配置GestureSense开发环境...

:: 创建Python虚拟环境
python -m venv echowrist_env
call echowrist_env\Scripts\activate

:: 安装Python依赖
echo 安装Python依赖包...
pip install --upgrade pip
pip install numpy scipy matplotlib pandas scikit-learn
pip install librosa sounddevice pyaudio
pip install torch torchvision torchaudio
pip install opencv-python mediapipe
pip install plotly seaborn streamlit
pip install pyserial
pip install adafruit-circuitpython-mpu6050
pip install adafruit-circuitpython-max30102
pip install jupyter ipykernel

echo 环境配置完成！
echo 每次开发前运行: echowrist_env\Scripts\activate
pause
```

### macOS配置脚本 (setup_macos.sh)
```bash
#!/bin/bash
echo "正在配置GestureSense开发环境..."

# 安装Homebrew (如果未安装)
if ! command -v brew &> /dev/null; then
    echo "安装Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 安装Python
echo "安装Python..."
brew install python@3.9

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3.9 -m venv echowrist_env
source echowrist_env/bin/activate

# 安装Python依赖
echo "安装Python依赖包..."
pip install --upgrade pip
pip install numpy scipy matplotlib pandas scikit-learn
pip install librosa sounddevice pyaudio
pip install torch torchvision torchaudio
pip install opencv-python mediapipe
pip install plotly seaborn streamlit
pip install pyserial
pip install adafruit-circuitpython-mpu6050
pip install adafruit-circuitpython-max30102
pip install jupyter ipykernel

echo "环境配置完成！"
echo "每次开发前运行: source echowrist_env/bin/activate"
```

### Linux配置脚本 (setup_linux.sh)
```bash
#!/bin/bash
echo "正在配置GestureSense开发环境..."

# 更新系统包
sudo apt update

# 安装系统依赖
echo "安装系统依赖..."
sudo apt install -y python3.9 python3.9-pip python3.9-venv
sudo apt install -y build-essential python3-dev
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y libasound2-dev
sudo apt install -y git curl wget

# 安装Python依赖
echo "创建Python虚拟环境..."
python3.9 -m venv echowrist_env
source echowrist_env/bin/activate

echo "安装Python依赖包..."
pip install --upgrade pip
pip install numpy scipy matplotlib pandas scikit-learn
pip install librosa sounddevice
pip install torch torchvision torchaudio
pip install opencv-python mediapipe
pip install plotly seaborn streamlit
pip install pyserial
pip install adafruit-circuitpython-mpu6050
pip install adafruit-circuitpython-max30102
pip install jupyter ipykernel

echo "环境配置完成！"
echo "每次开发前运行: source echowrist_env/bin/activate"
```

---

## 📁 项目结构配置

### 创建工作目录
```bash
# 主项目目录
mkdir ~/GestureSense_Project
cd ~/GestureSense_Project

# 子目录结构
mkdir -p {01_Arduino_Code,02_Python_Code,03_Data,04_Models,05_Tests,06_Docs}

# 数据子目录
mkdir -p 03_Data/{Raw,Processed,Models,Results}

# 模型子目录
mkdir -p 04_Models/{Arduino,Python,ML}
```

### 目录说明
```
GestureSense_Project/
├── 01_Arduino_Code/          # Arduino固件代码
│   ├── GestureSense_Base/     # 基础功能
│   ├── Sensor_Reader/        # 传感器读取
│   └── Real_Time_Process/    # 实时处理
├── 02_Python_Code/           # Python处理代码
│   ├── Data_Collection/      # 数据采集
│   ├── Signal_Processing/    # 信号处理
│   ├── ML_Training/          # 机器学习训练
│   └── Visualization/        # 数据可视化
├── 03_Data/                  # 数据存储
│   ├── Raw/                  # 原始数据
│   ├── Processed/            # 处理后数据
│   ├── Models/               # 模型文件
│   └── Results/              # 结果数据
├── 04_Models/                # 训练好的模型
├── 05_Tests/                 # 测试代码
├── 06_Docs/                  # 文档
└── requirements.txt          # Python依赖列表
```

---

## 🔧 开发工具配置

### 1. Arduino开发配置

#### 创建Arduino项目模板
```cpp
// File: 01_Arduino_Code/GestureSense_Base/GestureSense_Base.ino

#include <Wire.h>
#include <MPU6050.h>
#include <I2S.h>

// 引脚定义
#define I2S_WS_PIN   3
#define I2S_SCK_PIN  2
#define I2S_SD_PIN   4
#define I2S_DIN_PIN  5
#define ULTRASONIC_TX_PIN 6
#define ULTRASONIC_RX_PIN A0

// 传感器对象
MPU6050 mpu6050;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("🚀 GestureSense 初始化...");

  // 初始化I2C
  Wire.begin();

  // 初始化MPU6050
  mpu6050.initialize();
  if (mpu6050.testConnection()) {
    Serial.println("✅ MPU6050 连接成功");
  } else {
    Serial.println("❌ MPU6050 连接失败");
  }

  // 初始化I2S
  if (!I2S.begin(I2S_PHILIPS_MODE, 16000, 16)) {
    Serial.println("❌ I2S 初始化失败");
  } else {
    Serial.println("✅ I2S 初始化成功");
  }

  Serial.println("🎯 GestureSense 准备就绪!");
}

void loop() {
  // 读取MPU6050数据
  int16_t ax, ay, az, gx, gy, gz;
  mpu6050.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

  // 发送数据到Python
  Serial.print("MPU6050:");
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);

  delay(100); // 10Hz采样率
}
```

#### Arduino IDE配置
```
1. 工具 → 开发板 → Arduino Nano RP2040
2. 工具 → 端口 → 选择对应的COM端口
3. 工具 → 编译器优化 → "优化 (-Os)"
4. 工具 → USB栈 → "TinyUSB"
```

### 2. Python开发配置

#### 创建Python项目模板
```python
# File: 02_Python_Code/Data_Collection/serial_reader.py

import serial
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

class GestureSenseDataReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.data_buffer = []

    def connect(self):
        """连接到Arduino"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"✅ 成功连接到 {self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def read_data(self, duration=30):
        """读取数据"""
        print(f"📊 开始采集数据，持续 {duration} 秒...")

        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < duration:
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8').strip()
                if line.startswith("MPU6050:"):
                    data = line.replace("MPU6050:", "").split(",")
                    data = [int(x) for x in data]
                    data.append(datetime.now())
                    self.data_buffer.append(data)

        print(f"✅ 采集完成，共 {len(self.data_buffer)} 个数据点")

    def save_data(self, filename=None):
        """保存数据到CSV"""
        if filename is None:
            filename = f"gesture_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        df = pd.DataFrame(self.data_buffer,
                         columns=['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'timestamp'])
        df.to_csv(filename, index=False)
        print(f"💾 数据已保存到 {filename}")

    def visualize_data(self):
        """可视化数据"""
        if not self.data_buffer:
            print("❌ 没有数据可视化")
            return

        data = np.array(self.data_buffer)

        fig, axes = plt.subplots(2, 3, figsize=(15, 8))

        # 加速度数据
        axes[0, 0].plot(data[:, 0], label='ax')
        axes[0, 0].plot(data[:, 1], label='ay')
        axes[0, 0].plot(data[:, 2], label='az')
        axes[0, 0].set_title('加速度数据')
        axes[0, 0].legend()

        # 陀螺仪数据
        axes[0, 1].plot(data[:, 3], label='gx')
        axes[0, 1].plot(data[:, 4], label='gy')
        axes[0, 1].plot(data[:, 5], label='gz')
        axes[0, 1].set_title('陀螺仪数据')
        axes[0, 1].legend()

        # 数据分布
        axes[0, 2].hist(data[:, 0], alpha=0.5, label='ax')
        axes[0, 2].hist(data[:, 1], alpha=0.5, label='ay')
        axes[0, 2].hist(data[:, 2], alpha=0.5, label='az')
        axes[0, 2].set_title('加速度分布')
        axes[0, 2].legend()

        plt.tight_layout()
        plt.show()

# 使用示例
if __name__ == "__main__":
    reader = GestureSenseDataReader()

    if reader.connect():
        reader.read_data(duration=30)  # 采集30秒数据
        reader.save_data()
        reader.visualize_data()
```

---

## 🧪 环境测试

### 1. Arduino硬件测试
```bash
1. 连接Arduino到电脑
2. 打开Arduino IDE
3. 上传测试代码
4. 打开串口监视器 (波特率115200)
5. 观察输出: 应该看到 "🚀 GestureSense 初始化..." 等信息
```

### 2. Python环境测试
```python
# 创建测试文件: test_environment.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import serial
import torch

print("🧪 测试Python环境...")

# 测试基础包
try:
    import numpy as np
    print("✅ NumPy:", np.__version__)
except ImportError:
    print("❌ NumPy 安装失败")

try:
    import pandas as pd
    print("✅ Pandas:", pd.__version__)
except ImportError:
    print("❌ Pandas 安装失败")

try:
    import matplotlib.pyplot as plt
    print("✅ Matplotlib 可用")
except ImportError:
    print("❌ Matplotlib 安装失败")

try:
    import serial
    print("✅ PySerial 可用")
except ImportError:
    print("❌ PySerial 安装失败")

try:
    import torch
    print("✅ PyTorch:", torch.__version__)
except ImportError:
    print("❌ PyTorch 安装失败")

print("🎯 环境测试完成!")
```

### 3. 串口连接测试
```python
# 创建测试文件: test_serial.py
import serial
import time

def test_serial_ports():
    """测试所有可用串口"""
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]

    print("📡 可用串口:")
    for port in available_ports:
        print(f"  - {port}")

    return available_ports

def test_arduino_connection(port):
    """测试Arduino连接"""
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        print(f"✅ 成功连接到 {port}")

        # 等待Arduino启动
        time.sleep(2)

        # 读取几行数据
        for _ in range(5):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"📨 收到: {line}")
            time.sleep(0.5)

        ser.close()
        return True

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    ports = test_serial_ports()

    for port in ports:
        print(f"\n🔍 测试端口: {port}")
        test_arduino_connection(port)
```

---

## 🚀 下一步

1. **完成软件安装** - 按照本指南安装所有必需软件
2. **配置开发环境** - 运行配置脚本
3. **连接硬件** - 按照《硬件连接指南》连接组件
4. **运行环境测试** - 确认所有组件工作正常
5. **上传基础代码** - 将Arduino代码上传到硬件
6. **运行Python程序** - 开始数据采集和处理

---

**💡 提示**:
- 建议使用虚拟环境，避免包冲突
- 定期备份代码和数据
- 使用Git版本控制管理代码
- 遇到问题时查看相应的故障排除指南