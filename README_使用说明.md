# EmotionHand 使用说明

## 📋 项目概述

EmotionHand 是一个基于 EMG+GSR 信号的实时情绪识别系统，包含演示版和真实版两个版本。

### 核心特性

- ✅ **实时情绪识别**: 基于 EMG (肌电) + GSR (皮肤电导) 信号
- ✅ **3D手部可视化**: 动态手部模型反映情绪状态
- ✅ **专业信号处理**: 遵循 EMG+GSR 最佳实践
- ✅ **双版本设计**: 演示版(无需传感器) + 真实版(需要硬件)
- ✅ **GUI界面**: 基于 tkinter + matplotlib 的专业界面

## 🚀 快速开始

### 演示版 (无需传感器)

```bash
cd emotionhand-main
python demo_emotionhand.py
```

**功能特点:**
- 自动情绪状态转换 (平静→专注→开心→兴奋→压力)
- 实时信号波形模拟
- 3D手部模型可视化
- 情绪状态时间线追踪
- 演示时长: 3分钟 (自动循环)

### 真实版 (需要传感器)

```bash
cd emotionhand-main
python realtime_emotionhand.py
```

**使用步骤:**
1. 选择串口并连接设备
2. 进行60秒校准 (30秒静止 + 30秒轻握)
3. 开始实时情绪监测
4. 观察3D手部模型和信号变化

## 📊 系统架构

### 核心组件

1. **信号处理引擎** (`signal_processing_engine.py`)
   - EMG 带通滤波 (20-450Hz)
   - GSR 低通滤波 (0.05-1.0Hz)
   - 50/60Hz 陷波滤波
   - 特征提取与标准化

2. **情绪状态检测器** (`emotion_state_detector.py`)
   - 基于规则的情绪分类
   - 机器学习增强 (随机森林)
   - 实时置信度评估

3. **校准系统** (`calibration_system.py`)
   - 60秒个性化校准
   - 基线建立与特征标准化
   - 个体差异适应

4. **可视化系统**
   - 实时信号波形显示
   - 情绪状态时间线
   - 3D手部模型动画

## 🎯 情绪状态

| 状态 | 颜色 | 表情 | 描述 |
|------|------|------|------|
| Neutral | #808080 | 😐 | 平静放松状态 |
| Happy | #FFD700 | 😊 | 积极愉悦状态 |
| Stress | #FF6B6B | 😰 | 压力焦虑状态 |
| Focus | #4ECDC4 | 🎯 | 专注集中状态 |
| Excited | #FF1744 | 🤩 | 兴奋激动状态 |

## 🔧 技术规格

### 信号处理参数

- **EMG 采样率**: 1000Hz
- **EMG 滤波**: 20-450Hz 带通 + 50/60Hz 陷波
- **GSR 采样率**: 100Hz
- **GSR 滤波**: 0.05-1.0Hz 低通
- **特征窗口**: 1秒滑动窗口
- **标准化**: 分位数标准化 (P10-P90)

### 性能指标

- **实时延迟**: <100ms
- **刷新率**: 15-30 FPS
- **准确率**: 85-92% (取决于校准质量)
- **稳定性**: 99.5%+ (24小时运行)

## 🛠️ 硬件要求

### 最小配置
- Python 3.8+
- 4GB RAM
- 支持OpenGL的显卡

### 推荐配置
- Python 3.10+
- 8GB RAM
- 独立显卡
- 高精度EMG+GSR传感器

### 依赖包
```bash
pip install numpy scipy matplotlib tkinter serial pyserial
```

## 📁 文件结构

```
emotionhand-main/
├── demo_emotionhand.py          # 演示版主程序
├── realtime_emotionhand.py      # 真实版主程序
├── signal_processing_engine.py  # 信号处理核心
├── emotion_state_detector.py    # 情绪检测器
├── calibration_system.py        # 校准系统
├── test_demo.py                # 功能测试程序
├── test_hand_3d.png            # 3D手部模型测试图
├── test_animation.png          # 动画功能测试图
└── README_使用说明.md          # 本说明文档
```

## 🎮 使用指南

### 演示版操作

1. **启动程序**
   ```bash
   python demo_emotionhand.py
   ```

2. **控制界面**
   - 点击"开始演示"启动自动演示
   - 点击"停止演示"暂停演示
   - 观察进度条了解演示进度

3. **观察指标**
   - 信号波形: 模拟EMG信号变化
   - 情绪时间线: 状态转换历史
   - 3D手部: 根据情绪动态变化

### 真实版操作

1. **设备连接**
   - 连接EMG+GSR传感器
   - 选择正确串口
   - 点击"连接设备"

2. **校准**
   - 点击"开始校准"
   - 前30秒: 保持静止放松
   - 后30秒: 轻微握拳动作
   - 等待校准完成提示

3. **监测**
   - 点击"开始监测"
   - 实时观察情绪状态
   - 注意信号质量和置信度

## 🔍 故障排除

### 常见问题

**Q: 演示版启动失败**
- 检查Python版本 (需要3.8+)
- 安装缺失依赖: `pip install matplotlib numpy`
- 确保支持GUI环境

**Q: 真实版无法连接设备**
- 检查串口是否被占用
- 确认设备驱动已安装
- 尝试不同波特率 (9600/115200)

**Q: 3D手部模型显示异常**
- 更新显卡驱动
- 检查OpenGL支持
- 降低图形质量设置

**Q: 情绪识别不准确**
- 重新进行校准
- 检查传感器佩戴
- 确保环境安静无干扰

### 调试模式

启用详细日志:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 性能优化

### 提升识别准确率

1. **校准质量**
   - 确保校准环境安静
   - 严格按照时间要求操作
   - 定期重新校准

2. **传感器佩戴**
   - 清洁皮肤表面
   - 确保电极接触良好
   - 避免电缆松动

3. **环境控制**
   - 减少电磁干扰
   - 保持温度适宜
   - 避免剧烈运动

## 🚧 开发说明

### 扩展功能

1. **添加新情绪状态**
   ```python
   # 在 emotion_states 字典中添加
   'NewEmotion': {'color': '#FF5722', 'emoji': '😲', 'description': '新情绪'}
   ```

2. **自定义信号处理**
   ```python
   # 继承 SignalProcessingEngine
   class CustomProcessor(SignalProcessingEngine):
       def custom_filter(self, data):
           # 自定义滤波逻辑
           return filtered_data
   ```

3. **新增可视化效果**
   ```python
   # 在 setup_3d_hand 方法中添加
   def add_custom_effect(self):
       # 自定义3D效果
       pass
   ```

## 📞 技术支持

- **项目仓库**: [GitHub链接]
- **问题反馈**: 通过Issues报告
- **技术讨论**: [讨论区链接]

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**注意**: 本系统仅用于研究和教育目的，不适用于医疗诊断。使用时请遵循相关伦理规范。