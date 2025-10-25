# 🎭 EmotionHand - 基于EMG+GSR的情绪状态识别系统

## 🎯 项目概述

**核心思路**: 离线训练 + 在线推理
- **离线**: 公开数据集 + 小样本微调实现跨人泛化
- **在线**: LibEMG特征提取 → GRT实时分类 → Unity 3D可视化
- **实时性**: <100ms延迟的实时状态识别
- **个性化**: 2分钟个体校准解决电极位置差异

## 🛠️ 技术栈

### 核心组件
- **LibEMG (Python)**: EMG信号滤波、特征提取、窗口处理
- **GRT (C++/Python)**: 实时分类管线、低延迟推理
- **Unity 3D**: UDP/UDP接收、实时3D可视化
- **Muscle Sensor v3**: 8通道sEMG传感器 (A0)
- **GSR传感器**: 电皮电导传感器 (A1)

### 技术特点
- **多模态融合**: EMG(肌电) + GSR(皮电) 双通道
- **跨人泛化**: 基于公开数据集迁移学习
- **个性化适应**: 2分钟快速个体校准
- **实时性能**: 目标延迟<100ms

## 📁 项目结构

```
EmotionHand/
├── data/                    # 数据集
│   ├── public/              # 公开数据集
│   │   ├── NinaPro/         # NinaPro数据库
│   │   ├── CapgMyo/         # CapgMyo数据库
│   │   └── Myo/             # Myo二次整理集
│   └── private/             # 私有采集数据
│       ├── raw/             # 原始信号
│       ├── processed/        # 预处理特征
│       └── annotations.csv  # 标注文件
├── scripts/                 # Python脚本
│   ├── data_collection.py   # 数据采集
│   ├── preprocessing.py      # 信号预处理
│   ├── feature_extraction.py # 特征提取
│   ├── training.py          # 模型训练
│   ├── real_time_infer.py   # 实时推理
│   └── calibration.py       # 个体校准
├── models/                  # 训练好的模型
│   ├── gesture_classifier.pkl
│   ├── state_classifier.pkl
│   └── calibration_models/
├── unity/                   # Unity项目
│   ├── Assets/
│   │   └── Scripts/
│   │       ├── UdpReceiver.cs
│   │       ├── EmotionHandVisualizer.cs
│   │       └── CalibrationUI.cs
│   └── Scenes/
│       └── EmotionHand.unity
├── utils/                   # 工具函数
│   ├── signal_processor.py
│   ├── feature_utils.py
│   └── visualization.py
├── docs/                     # 文档
│   ├── protocol.md          # 实验协议
│   ├── results/             # 实验结果
│   └── figures/             # 图片/图表
├── requirements.txt          # Python依赖
├── environment.yml           # Conda环境
└── README.md               # 本文件
```

## 🚀 快速开始

### 1. 一键启动 (推荐)

```bash
# 克隆项目
git clone https://github.com/yourusername/EmotionHand.git
cd EmotionHand

# 一键安装依赖和设置项目
python run.py setup
python run.py install

# 运行完整演示
python run.py demo --mode full

# 或使用交互式菜单
python run.py
```

### 2. 环境配置

```bash
# 克隆项目
git clone https://github.com/yourusername/EmotionHand.git
cd EmotionHand

# 创建Conda环境
conda env create -f environment.yml
conda activate emotionhand

# 或使用pip
pip install -r requirements.txt
```

### 2. 硬件连接

**Muscle Sensor v3连接**:
- A0: 8通道EMG信号
- 波特率: 115200
- 采样率: 1000Hz

**GSR传感器连接**:
- A1: 电皮电导信号
- 波特率: 9600
- 采样率: 100Hz

### 3. 数据采集

```bash
# 使用一键脚本
python run.py collect

# 或直接运行
python scripts/data_collection.py

# 按提示采集手势和状态数据
# 每个状态采集2-3分钟
```

### 4. 个性化校准

```bash
# 使用一键脚本 (2分钟快速校准)
python run.py calibrate

# 或直接运行
python scripts/calibration.py
```

### 5. 训练模型

```bash
# 使用一键脚本
python run.py train

# 或分别训练
python scripts/training.py --mode gesture
python scripts/training.py --mode state
```

### 6. 实时推理

```bash
# 使用一键脚本
python run.py inference

# 或直接运行
python scripts/real_time_inference.py

# 启动Unity可视化
# Unity中打开Scenes/EmotionHand.unity
```

### 7. 快速演示

```bash
# 运行完整演示 (无需硬件)
python run.py demo --mode full

# 或运行交互式演示
python scripts/demo.py --interactive
```

## 📊 数据集与标注

### 公开数据集

#### NinaPro Database
- **来源**: 多个公开数据库的集合
- **内容**: 几十个受试者，几十种手势
- **通道**: 8-16通道sEMG
- **用途**: 跨人泛化训练

#### CapgMyo Database
- **来源**: 高密度前臂sEMG数据集
- **特点**: 强基线性能，高信噪比
- **通道**: 16通道高密度sEMG
- **用途**: 高精度模型训练

#### Myo Database
- **来源**: 8通道腕式EMG二次整理
- **特点**: 便携式设备，易获取
- **通道**: 8通道sEMG
- **用途**: 快速原型验证

### 标注协议

#### 手势标签
- **握拳** (Fist): 手指完全弯曲
- **张开** (Open): 手指完全伸展
- **捏合** (Pinch): 拇指和食指接触
- **点按** (Point): 食指伸直
- **旋拧** (Twist): 手腕旋转动作

#### 状态标签
- **放松** (Relaxed): 自然休息状态
- **专注** (Focused): 专注工作状态
- **压力** (Stressed): 紧张焦虑状态
- **疲劳** (Fatigued): 长时间工作后状态

## 🧠 算法与技术

### 特征提取

#### EMG特征
- **RMS** (均方根): 信号幅度
- **MDF** (平均差分频率): 变化频率
- **ZC** (过零率): 信号变化点
- **WL** (波形长度): 信号复杂度
- **波段能量**: 不同频段的能量分布

#### GSR特征
- **均值**: 基线电平
- **差分**: 变化趋势
- **峰计数**: 峰值活动
- **标准差**: 变异程度

### 模型架构

#### 基础模型
- **LDA**: 线性判别分析，快速基线
- **SVM**: 支持向量机，非线性分类
- **LightGBM**: 梯度提升，高精度

#### 深度学习模型
- **TCN**: 时间卷积网络，序列建模
- **1D-CNN**: 一维卷积，特征学习
- **注意力机制**: 重要特征加权

### 实时推理管线

```
信号采集 → 滤波处理 → 窗口切分 → 特征提取 → 标准化 → 分类 → 平滑 → 拒识 → UDP发送
    ↓         ↓         ↓         ↓         ↓       ↓     ↓      ↓       ↓
  1000Hz   20-450Hz  256样本   64样本   多维特征  [0,1]  分类器  0.6    9001端口
```

## 🔧 个性化校准

### 个体差异处理

#### 1. 分位归一化
```python
# 首次60秒静息 + 60秒轻握
p10, p90 = percentile(data, [10, 90])
normalized = (data - p10) / (p90 - p10)
```

#### 2. Few-shot微调
```python
# 冻结骨干网络，只训练分类头
# 训练2-3分钟，每个状态10-15秒
model.fit(X_calib, y_calib, freeze_backbone=True)
```

#### 3. 拒识机制
```python
# 置信度阈值
confidence = model.predict_proba(X)[0]
if max(confidence) < 0.6:
    label = "Neutral"  # 拒识为中性状态
else:
    label = model.classes_[np.argmax(confidence)]
```

## 📈 性能指标

### 分类精度
- **Macro-F1**: 多类别平均F1分数
- **准确率**: 预测正确率
- **召回率**: 类别覆盖率

### 实时性能
- **延迟**: 从信号到预测的总时间
- **吞吐量**: 每秒处理的样本数
- **内存使用**: 程序运行时内存占用

### 个性化效果
- **校准前**: Macro-F1 ≈ 0.70
- **校准后**: Macro-F1 ≈ 0.85-0.90
- **延迟**: <100ms (目标)

## 🎨 Unity 3D可视化

### 实时效果

#### 手部可视化
- **颜色映射**: 不同状态对应不同颜色
  - 放松: 蓝色
  - 专注: 绿色
  - 压力: 红色
  - 疲劳: 黄色

#### 动画效果
- **粒子系统**: 情绪粒子效果
- **材质变化**: 手部材质动态调整
- **骨骼动画**: 3D手部模型变形

#### 数据展示
- **实时曲线**: 置信度和特征值
- **状态历史**: 状态变化时间线
- **性能监控**: 延迟和精度指标

## 📊 实验设计

### 协议文档
详细的实验协议和记录表格，详见 `docs/protocol.md`

### 评估方法
- **Leave-One-Subject-Out (LOSO)**: 留一受试者验证泛化能力
- **Cross-Validation**: K折交叉验证模型稳定性
- **A/B测试**: 对比不同算法的效果

### 结果分析
- **混淆矩阵**: 类别间混淆情况
- **延迟曲线**: 实时性能变化趋势
- **特征重要性**: 关键特征贡献分析

## 🚧 开发指南

### 添加新手势
1. 在`scripts/data_collection.py`中添加新手势
2. 更新标注协议
3. 重新训练模型
4. 更新Unity可视化

### 模型优化
1. 调整特征提取参数
2. 尝试不同分类算法
3. 优化实时性能
4. 评估泛化能力

### 可视化增强
1. 添加新的视觉效果
2. 优化粒子系统
3. 增加交互界面
4. 改善用户体验

## 🔮 未来扩展

### 多模态融合
- **MediaPipe Hands**: 视觉手势识别
- **语音识别**: 语音命令辅助
- **眼动追踪**: 注意力监测

### 云端集成
- **模型训练**: 云端大规模训练
- **数据同步**: 跨设备数据同步
- **远程监控**: 在线状态监测

### 商业化应用
- **健康监测**: 压力和疲劳预警
- **游戏交互**: 无控制器游戏
- **辅助工具**: 残障人士辅助

## 📞 技术支持

### 常见问题
- **硬件连接**: 传感器连接和调试
- **环境配置**: 依赖包安装和配置
- **训练问题**: 模型训练和优化
- **部署问题**: Unity集成和运行

### 获取帮助
- **GitHub Issues**: 提交技术问题
- **文档查阅**: 参考`docs/`目录
- **社区讨论**: 相关技术论坛

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🎉 致谢

感谢以下开源项目和技术社区的支持：
- **LibEMG**: sEMG信号处理库
- **GRT**: 机器学习实时分类库
- **Unity**: 3D可视化引擎
- **数据集提供者**: NinaPro、CapgMyo等

---

**最后更新**: 2025年10月21日
**版本**: v1.0.0