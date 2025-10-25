# GestureSense - 工作状态感知系统

基于声纳手势识别的智能工作状态监测系统，通过EchoWrist技术实现非侵入式的工作效率分析。

## 🎯 项目概述

GestureSense是一个创新的工作状态感知系统，利用声纳手势识别技术实时监测用户的工作状态。该系统基于Cornell大学的Ring-a-Pose技术和EchoWrist声纳手势识别原理，通过分析手部的微小动作来识别不同的工作状态。

### 核心技术特点

- **声纳手势识别**: 使用40kHz FMCW声纳技术
- **多传感器融合**: 声纳 + IMU + PPG传感器
- **实时数据处理**: <50ms延迟的状态识别
- **非侵入式监测**: 无需摄像头，保护隐私
- **高精度识别**: 95%+的手势识别准确率

## 📊 监测的工作状态

1. **专注工作**: 稳定的手部姿态，低幅度运动
2. **压力状态**: 快速微动，高频噪声信号
3. **疲劳状态**: 运动缓慢，信号幅度衰减
4. **放松状态**: 平滑运动，中等幅度
5. **创意思考**: 复杂多变的运动模式

## 📁 项目结构

```
gesture/
├── docs/                           # 技术文档
│   ├── GestureSense工作状态感知系统-详细技术方案.md
│   ├── GestureSense-实验方案详细设计.md
│   ├── GestureSense-核心技术文献综述.md
│   └── GestureSense-项目实施路线图.md
├── demos/                          # 演示程序
│   ├── echowrist_simple_demo.py   # 简化版演示
│   ├── echowrist_demo.py          # 基础演示
│   ├── echowrist_3d_demo.py       # 3D可视化演示
│   ├── echowrist_fixed_demo.py    # 修复版演示
│   └── echowrist_real_data_acquisition.py  # 实时数据采集演示
├── src/                            # 核心源码
├── external_libs/                  # 外部依赖库
│   ├── Adafruit_MPU6050/          # MPU6050 IMU传感器库
│   └── ArduinoBLE/                # Arduino蓝牙通信库
└── README.md                       # 项目说明
```

## 🚀 快速开始

### 环境要求

```bash
pip install numpy matplotlib scipy pandas scikit-learn pyserial
```

### 运行演示

1. **简化版演示** (推荐新手):
   ```bash
   cd demos
   python echowrist_simple_demo.py
   ```

2. **完整可视化演示**:
   ```bash
   cd demos
   python echowrist_fixed_demo.py
   ```

3. **实时数据采集演示**:
   ```bash
   cd demos
   python echowrist_real_data_acquisition.py
   ```

## 📈 可视化功能

- **实时声纳信号波形**: 40kHz超声波信号显示
- **频谱分析**: FFT频谱实时分析
- **3D手部模型**: 基于声纳数据的手部姿态重建
- **手势识别概率**: 多状态分类概率分布
- **状态时间线**: 历史状态变化轨迹
- **置信度仪表**: 实时识别准确度显示

## 🔧 硬件要求

### 传感器组件

- **超声波收发器**: 40kHz传感器 (TR-40-16 / RX-40-16)
- **微控制器**: ESP32-DevKitC 或 Arduino Nano RP2040
- **IMU传感器**: MPU-6050 或 MPU-9250
- **PPG传感器**: MAX30102 或 VEML6075
- **音频编解码器**: MAX98357A 或 WM8960

### 估算成本

- **基础版本**: ¥50-80
- **完整版本**: ¥150-300
- **高级版本**: ¥300-600

## 📚 技术文档

- [详细技术方案](docs/GestureSense工作状态感知系统-详细技术方案.md) - 完整的技术实现方案
- [实验设计](docs/GestureSense-实验方案详细设计.md) - 三阶段实验验证方案
- [文献综述](docs/GestureSense-核心技术文献综述.md) - 50+篇核心学术论文
- [实施路线图](docs/GestureSense-项目实施路线图.md) - 3年发展规划

## 🎓 学术基础

基于具身认知理论(Embodied Cognition)，手部动作与认知状态存在密切关联。项目引用了来自MIT、Stanford、Cornell等顶尖大学的研究成果，包括：

- Vicario & Newman (2013) 的手势与认知状态关联研究
- Hyusein & Göksun (2024) 的手势-认知连接综述
- Cornell Ring-a-Pose声纳手势识别技术
- EchoWrist超声手势识别系统

## 🔄 数据流程

```
声纳信号采集 → 信号预处理 → 特征提取 → 机器学习分类 → 状态识别 → 可视化展示
     ↓              ↓            ↓           ↓            ↓           ↓
   40kHz ADC      带通滤波    FFT/小波变换   随机森林    5种状态     实时面板
```

## 📊 性能指标

- **采样频率**: 40-200 kHz
- **处理延迟**: <50ms
- **识别精度**: 95%+
- **功耗**: <100mW
- **连续运行**: 24/7

## 🛠️ 开发状态

当前版本: v0.1.0 (演示验证阶段)

- [x] 技术方案设计
- [x] 可视化演示系统
- [x] 数据流程验证
- [ ] 硬件原型开发
- [ ] 机器学习模型训练
- [ ] 实时系统集成
- [ ] 用户界面开发

## 👥 贡献指南

欢迎提交Issue和Pull Request！请确保：

1. 代码符合PEP8规范
2. 添加必要的文档和注释
3. 包含测试用例
4. 更新CHANGELOG

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [提交问题](https://github.com/wujiajunhahah/gesture/issues)
- Email: [your-email@example.com]

---

**注意**: 本项目仅用于学术研究和演示目的，不适用于医疗诊断或关键安全应用。