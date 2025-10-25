# GestureSense 二次开发指南

## 📋 项目概述

本项目基于 [EchoWrist](https://github.com/xyd22/EchoWrist) 声纳手势识别系统，专门针对工作状态感知场景进行二次开发。通过整合我们的手势识别技术研究，实现非侵入式的工作效率监测。

## 🚀 快速启动

### 1. 环境配置

#### 方案A: 使用Conda环境 (推荐)
```bash
# 使用项目提供的环境文件
conda create --name echowrist --file EchoWristEnv.txt
conda activate echowrist
```

#### 方案B: 手动安装
```bash
pip install torch torchvision opencv-python matplotlib pandas numpy scipy seaborn scikit-learn
```

### 2. 数据采集
```bash
cd data_collection
python data_collection.py -cd 6 -c 5fingers -f 2 -r 2 -t 2 -cam 0 --audio True --noserial -p ../datasets -pilot_study
```

### 3. 数据处理
```bash
cd data_preparation
python data_preparation.py -md 500000000 -nd -500000000 -f --path ../datasets/pilot_study
```

### 4. 模型训练
```bash
cd dl_model
python train.py -o train_output -f original-ts -p ../datasets/pilot_study
```

## 🔗 相关项目链接

### 核心技术项目
- **EchoWrist (主项目)**: https://github.com/xyd22/EchoWrist
  - 原始声纳手势识别系统
  - 完整的数据采集、处理、训练流程

- **Ring-a-Pose (Cornell)**: https://github.com/cornell-lab/ring-a-pose
  - Cornell大学声纳手势识别原型
  - 理论基础和技术参考

### 相关开源项目
- **Solit**: https://github.com/andybarry/Solit
  - 声纳手势识别的早期实现
  - 硬件设计和信号处理算法

- **mmWave-Gesture-Recognition**: https://github.com/hughkk/mmWave-Gesture-Recognition
  - 毫米波手势识别项目
  - 可供参考的信号处理技术

- **Gesture-Recognition-with-Radar**: https://github.com/mohammadkarimi/Gesture-Recognition-with-Radar
  - 雷达手势识别项目
  - 多种雷达技术的实现

### 学术资源
- **Google Scholar - EchoWrist**: https://scholar.google.com/scholar?q=echowrist+gesture+recognition
- **IEEE Xplore - Acoustic Gesture Recognition**: https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=acoustic%20gesture%20recognition

## 📁 项目结构详解

```
gesture/
├── data_collection/           # 数据采集模块
│   ├── data_collection.py    # 主采集程序
│   ├── commands.py           # 手势命令定义
│   ├── speed_study.py        # 速度研究工具
│   ├── audios/               # 音频命令文件
│   └── videos/               # 示范视频
├── data_preparation/         # 数据预处理模块
│   ├── data_preparation.py   # 数据预处理主程序
│   ├── audio_auto_sync.py    # 音视频同步
│   ├── echo_profiles.py      # 声纳信号处理
│   ├── visualize.py          # 数据可视化
│   └── tx_signals/           # 发射信号模板
├── dl_model/                 # 深度学习模块
│   ├── train.py              # 模型训练
│   ├── trace_model.py        # 实时推理模型
│   ├── tcp_realtime.py       # TCP实时通信
│   └── libs/                 # 核心算法库
├── my_tools/                 # 辅助工具
│   ├── generate_commands.ipynb  # 手势命令生成
│   └── generate_raw.ipynb    # 原始数据生成
├── EchoWristEnv.txt          # Conda环境配置
├── rotate_video.py           # 视频旋转工具
└── README.md                 # 原项目说明
```

## 🔧 硬件要求

### 传感器硬件
- **超声波传感器**: 40kHz FMCW传感器
  - 推荐型号: TR-40-16 (发射) / RX-40-16 (接收)
  - 购买链接: https://www.mouser.com/ProductDetail/400-TR-40-16

- **微控制器**:
  - Arduino Nano RP2040: https://www.arduino.cc/en/Guide/NANORP2040Connect
  - ESP32-DevKitC: https://www.espressif.com/en/products/devkits

- **音频设备**:
  - USB声卡: https://www.amazon.com/dp/B07MQ5M4KZ
  - 麦克风: https://www.amazon.com/dp/B07K946LWZ

### 开发硬件建议
- **开发机**: 配备NVIDIA GPU (GTX 1060或更高)
- **内存**: 16GB+ RAM
- **存储**: 100GB+ 可用空间

## 🎯 工作状态感知定制

### 1. 新增手势类型

在 `data_collection/commands.py` 中添加工作状态相关的手势:

```python
WORK_STATE_GESTURES = {
    'focused_work': {
        'name': '专注工作手势',
        'description': '稳定手部，轻微手指活动',
        'duration': 3.0,
        'audio_cue': 'focused.wav'
    },
    'stress_state': {
        'name': '压力状态手势',
        'description': '快速微动，握拳姿势',
        'duration': 2.5,
        'audio_cue': 'stress.wav'
    },
    'fatigue_state': {
        'name': '疲劳状态手势',
        'description': '手部下垂，缓慢运动',
        'duration': 3.0,
        'audio_cue': 'fatigue.wav'
    },
    'relaxed_state': {
        'name': '放松状态手势',
        'description': '手部张开，平滑运动',
        'duration': 2.5,
        'audio_cue': 'relaxed.wav'
    },
    'creative_thinking': {
        'name': '创意思考手势',
        'description': '多样化手部动作，频繁变化',
        'duration': 3.5,
        'audio_cue': 'creative.wav'
    }
}
```

### 2. 数据采集策略

针对工作状态感知的数据采集建议:

```bash
# 采集工作状态数据
python data_collection.py \
    -cd 10 \
    -c focused_work,stress_state,fatigue_state,relaxed_state,creative_thinking \
    -f 5 \
    -r 10 \
    -t 3 \
    -cam 0 \
    --audio True \
    --noserial \
    -p ../work_state_dataset \
    -o work_session_001
```

### 3. 模型定制

修改 `dl_model/train.py` 中的模型配置:

```python
# 工作状态感知专用配置
class WorkStateConfig:
    num_classes = 5  # 5种工作状态
    sequence_length = 30  # 30帧序列
    feature_dim = 64  # 特征维度

    # 数据增强
    augmentation = {
        'noise_level': 0.1,
        'time_shift': 0.2,
        'amplitude_scale': 0.3
    }
```

## 📊 性能监控

### 实时监控脚本

创建 `monitor_work_state.py`:

```python
import numpy as np
from dl_model.trace_model import TraceModel
import matplotlib.pyplot as plt

class WorkStateMonitor:
    def __init__(self, model_path):
        self.model = TraceModel(model_path)
        self.state_history = []

    def process_real_time_data(self, audio_data):
        prediction = self.model.predict(audio_data)
        self.state_history.append(prediction)
        return prediction

    def generate_report(self):
        # 生成工作效率报告
        pass
```

### 可视化仪表板

使用Streamlit创建监控界面:

```bash
pip install streamlit
streamlit run dashboard.py
```

## 🧪 实验设计

### 1. 基础验证实验
- **目标**: 验证手势与工作状态的关联性
- **参与者**: 20-30人
- **时长**: 每人30分钟
- **任务**: 编程、写作、设计等典型工作

### 2. 实时环境实验
- **目标**: 验证实际工作环境中的效果
- **周期**: 2-4周
- **数据量**: 100+小时
- **指标**: 识别准确率、误报率、响应时间

### 3. 商业化验证
- **目标**: 用户体验和商业价值验证
- **规模**: 100+用户
- **周期**: 3个月
- **反馈**: 用户满意度、工作效率提升

## 📈 数据分析

### 1. 信号特征提取
```python
# 声纳信号特征
def extract_acoustic_features(audio_signal):
    features = {
        'spectral_centroid': librosa.feature.spectral_centroid(y=audio_signal),
        'spectral_rolloff': librosa.feature.spectral_rolloff(y=audio_signal),
        'zero_crossing_rate': librosa.feature.zero_crossing_rate(audio_signal),
        'mfcc': librosa.feature.mfcc(y=audio_signal)
    }
    return features
```

### 2. 状态分类算法
```python
# 工作状态分类器
class WorkStateClassifier:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestClassifier(),
            'svm': SVC(kernel='rbf'),
            'lstm': Sequential()
        }

    def ensemble_predict(self, features):
        predictions = []
        for model in self.models.values():
            pred = model.predict(features)
            predictions.append(pred)
        return majority_vote(predictions)
```

## 📱 部署方案

### 1. 本地部署
- **优势**: 数据隐私，低延迟
- **配置**: 本地GPU服务器
- **成本**: 一次性硬件投入

### 2. 云端部署
- **优势**: 可扩展性强，维护简单
- **平台**: AWS/Azure/GCP
- **成本**: 按使用量付费

### 3. 边缘部署
- **优势**: 实时性好，离线工作
- **硬件**: NVIDIA Jetson系列
- **成本**: 中等硬件投入

## 🔍 故障排除

### 常见问题

1. **数据采集失败**
   - 检查音频设备权限
   - 确认传感器连接
   - 验证采样率设置

2. **模型训练慢**
   - 增加batch size
   - 使用混合精度训练
   - 检查GPU利用率

3. **识别准确率低**
   - 增加训练数据量
   - 调整数据增强策略
   - 优化模型架构

## 📚 学习资源

### 技术文档
- [PyTorch官方文档](https://pytorch.org/docs/)
- [LibROSA音频处理](https://librosa.org/doc/)
- [OpenCV计算机视觉](https://opencv.org/)

### 学术论文
- EchoWrist原论文: 查找IEEE Xplore
- 声纳手势识别综述: Google Scholar
- 工作状态检测研究: ACM Digital Library

### 社区资源
- [Stack Overflow - Gesture Recognition](https://stackoverflow.com/questions/tagged/gesture-recognition)
- [Reddit - MachineLearning](https://www.reddit.com/r/MachineLearning/)
- [GitHub - Awesome Gesture Recognition](https://github.com/topics/gesture-recognition)

## 🤝 贡献指南

### 开发流程
1. Fork项目到个人仓库
2. 创建功能分支
3. 提交代码变更
4. 发起Pull Request

### 代码规范
- Python PEP8
- 添加类型注释
- 编写单元测试
- 更新文档

## 📞 支持联系

- **GitHub Issues**: https://github.com/wujiajunhahah/gesture/issues
- **技术讨论**: 微信群/钉钉群
- **商务合作**: 邮箱联系

---

**注意**: 本指南基于EchoWrist项目，专门针对工作状态感知场景进行优化。开发过程中请遵守相关开源协议和学术规范。