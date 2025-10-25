# 🚀 快速启动指南

## 一键环境配置

```bash
# 1. 克隆项目
git clone https://github.com/wujiajunhahah/gesture.git
cd gesture

# 2. 创建环境
conda create --name echowrist --file EchoWristEnv.txt
conda activate echowrist

# 3. 验证安装
python -c "import torch; import cv2; print('环境配置成功!')"
```

## 5分钟快速体验

### 1. 运行演示程序
```bash
cd data_collection
python data_collection.py -cd 3 -c 5fingers -f 1 -r 1 -t 1 --audio True --noserial -p ../demo_data -o quick_demo
```

### 2. 查看数据可视化
```bash
cd ../data_preparation
python visualize.py --path ../demo_data/quick_demo --height 400 --echo_length 20
```

### 3. 训练小型模型
```bash
cd ../dl_model
python train.py -o quick_train -f original -p ../demo_data/quick_demo --epochs 10
```

## 测试硬件连接

```bash
# 测试音频设备
python -c "import pyaudio; p=pyaudio.PyAudio(); print('音频设备数量:', p.get_device_count())"

# 测试摄像头
python -c "import cv2; cap=cv2.VideoCapture(0); print('摄像头状态:', cap.isOpened())"
```

## 常用命令速查

```bash
# 数据采集
cd data_collection
python data_collection.py -cd 6 -c 5fingers -f 3 -r 5 -t 2 -cam 0 --noserial -p ../datasets -o session_001

# 数据预处理
cd ../data_preparation
python data_preparation.py -md 500000000 -nd -500000000 -f --path ../datasets/session_001

# 模型训练
cd ../dl_model
python train.py -o train_output -f both -p ../datasets/session_001

# 实时推理
python tcp_realtime.py --model ../train_output/best_model.ptl --port 8888
```

## 环境故障排除

| 问题 | 解决方案 |
|------|----------|
| PyTorch安装失败 | 使用pip安装: `pip install torch torchvision` |
| OpenCV错误 | 安装: `pip install opencv-python` |
| 音频设备权限 | 检查系统麦克风权限设置 |
| GPU不可用 | 安装CUDA版本PyTorch或使用CPU模式 |

## 下一步

- 查看 [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) 了解详细开发流程
- 查看 [原始README](README.md) 了解EchoWrist基础功能
- 查看GitHub Issues获取社区支持