#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 集成版 - 结合企业级信号处理引擎与实时可视化
整合了zcf项目中的专业信号处理系统
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from collections import deque
import queue
import json
import logging
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# 添加zcf项目路径
zcf_paths = [
    "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub",
    "/Users/wujiajun/Downloads/zcf/gesture",
    "/Users/wujiajun/Downloads/zcf/GestureSense_Complete_Project"
]

for path in zcf_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)

# 尝试导入专业信号处理引擎
try:
    from signal_processing_engine import RealTimeSignalProcessor
    from emotion_state_detector import EmotionStateDetector
    from calibration_system import CalibrationSystem
    PROFESSIONAL_ENGINE_AVAILABLE = True
    print("✅ 成功加载企业级信号处理引擎")
except ImportError as e:
    print(f"⚠️ 企业级信号处理引擎加载失败: {e}")
    print("🔄 使用简化版信号处理")
    PROFESSIONAL_ENGINE_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmotionHandIntegrated:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EmotionHand 集成版 - 企业级信号处理 + 实时可视化")
        self.root.geometry("1600x900")

        # 情绪状态定义
        self.emotion_states = {
            'Neutral': {'color': '#808080', 'emoji': '😐', 'description': '平静放松'},
            'Happy': {'color': '#FFD700', 'emoji': '😊', 'description': '积极愉悦'},
            'Stress': {'color': '#FF6B6B', 'emoji': '😰', 'description': '压力焦虑'},
            'Focus': {'color': '#4ECDC4', 'emoji': '🎯', 'description': '专注集中'},
            'Excited': {'color': '#FF1744', 'emoji': '🤩', 'description': '兴奋激动'}
        }

        # 当前状态
        self.current_emotion = 'Neutral'
        self.emotion_confidence = 0.5

        # 数据存储
        self.emg_data = deque(maxlen=1000)
        self.gsr_data = deque(maxlen=1000)
        self.emotion_history = deque(maxlen=100)
        self.time_stamps = deque(maxlen=1000)
        self.quality_history = deque(maxlen=100)

        # 信号处理引擎
        self.signal_engine = None
        self.emotion_detector = None
        self.calibration_system = None

        # 初始化信号处理引擎
        self.init_signal_engine()

        # 数据队列
        self.data_queue = queue.Queue()

        # 动画控制
        self.animation = None
        self.is_running = False
        self.start_time = time.time()

        # 设置界面
        self.setup_ui()

    def init_signal_engine(self):
        """初始化信号处理引擎"""
        if PROFESSIONAL_ENGINE_AVAILABLE:
            try:
                # 查找配置文件
                config_paths = [
                    "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub/signal_processing_config.json",
                    "signal_processing_config.json"
                ]

                config_path = None
                for path in config_paths:
                    if os.path.exists(path):
                        config_path = path
                        break

                # 初始化专业引擎
                self.signal_engine = RealTimeSignalProcessor(config_path or "signal_processing_config.json")
                self.signal_engine.start()

                # 初始化情绪检测器
                self.emotion_detector = EmotionStateDetector()

                # 初始化校准系统
                self.calibration_system = CalibrationSystem()

                logger.info("✅ 企业级信号处理引擎初始化成功")

            except Exception as e:
                logger.error(f"❌ 企业级引擎初始化失败: {e}")
                self.signal_engine = None
        else:
            logger.warning("🔄 使用简化信号处理模式")

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame,
                               text="EmotionHand 集成版 - 企业级EMG+GSR情绪识别系统",
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=5)

        # 引擎状态显示
        engine_status = "企业级引擎" if PROFESSIONAL_ENGINE_AVAILABLE else "简化引擎"
        status_label = ttk.Label(main_frame, text=f"🔧 信号处理引擎: {engine_status}",
                               font=('Arial', 12), foreground='green' if PROFESSIONAL_ENGINE_AVAILABLE else 'orange')
        status_label.pack(pady=2)

        # 顶部状态框架
        top_frame = ttk.LabelFrame(main_frame, text="实时状态监控", padding=10)
        top_frame.pack(fill=tk.X, pady=5)

        # 创建状态显示
        self.create_status_display(top_frame)

        # 创建图表区域
        self.create_plots(main_frame)

        # 控制面板
        self.create_control_panel(main_frame)

    def create_status_display(self, parent):
        """创建状态显示"""
        # 情绪状态显示
        emotion_frame = ttk.Frame(parent)
        emotion_frame.pack(side=tk.LEFT, padx=20)

        self.emotion_label = ttk.Label(emotion_frame,
                                      text=f"😐 平静放松",
                                      font=('Arial', 16, 'bold'))
        self.emotion_label.pack()

        self.confidence_label = ttk.Label(emotion_frame,
                                         text=f"置信度: 0.50",
                                         font=('Arial', 12))
        self.confidence_label.pack()

        # 信号质量显示
        quality_frame = ttk.Frame(parent)
        quality_frame.pack(side=tk.LEFT, padx=20)

        self.quality_label = ttk.Label(quality_frame,
                                      text="信号质量: 优秀",
                                      font=('Arial', 12),
                                      foreground='green')
        self.quality_label.pack()

        self.performance_label = ttk.Label(quality_frame,
                                          text="延迟: 0ms | FPS: 0",
                                          font=('Arial', 10))
        self.performance_label.pack()

        # 连接状态
        connection_frame = ttk.Frame(parent)
        connection_frame.pack(side=tk.LEFT, padx=20)

        mode_text = "演示模式" if self.demo_mode else "实时模式"
        self.connection_label = ttk.Label(connection_frame,
                                        text=f"🔗 {mode_text}",
                                        font=('Arial', 12))
        self.connection_label.pack()

        if self.demo_mode:
            ttk.Label(connection_frame, text="🤖 模拟数据驱动",
                     font=('Arial', 10), foreground='blue').pack()

    def create_plots(self, parent):
        """创建图表区域"""
        # 创建matplotlib图形
        self.fig = plt.figure(figsize=(16, 8), facecolor='white')

        # 创建子图布局
        gs = self.fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

        # EMG信号图
        self.ax_emg = self.fig.add_subplot(gs[0, 0])
        self.ax_emg.set_title('EMG信号 (8通道)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(-1, 1)

        # GSR信号图
        self.ax_gsr = self.fig.add_subplot(gs[0, 1])
        self.ax_gsr.set_title('GSR信号', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)
        self.ax_gsr.set_ylim(0, 5)

        # 情绪状态时间线
        self.ax_emotion = self.fig.add_subplot(gs[0, 2])
        self.ax_emotion.set_title('情绪状态时间线', fontsize=12, fontweight='bold')
        self.ax_emotion.set_xlabel('时间 (s)')
        self.ax_emotion.set_ylabel('情绪状态')
        self.ax_emotion.set_ylim(-0.5, len(self.emotion_states) - 0.5)
        self.ax_emotion.set_yticks(range(len(self.emotion_states)))
        self.ax_emotion.set_yticklabels(list(self.emotion_states.keys()))
        self.ax_emotion.grid(True, alpha=0.3)

        # 3D手部模型
        self.ax_3d = self.fig.add_subplot(gs[1, 0], projection='3d')
        self.ax_3d.set_title('3D手部模型', fontsize=12, fontweight='bold')

        # 信号质量监测
        self.ax_quality = self.fig.add_subplot(gs[1, 1])
        self.ax_quality.set_title('信号质量监测', fontsize=12, fontweight='bold')
        self.ax_quality.set_xlabel('时间')
        self.ax_quality.set_ylabel('质量评分')
        self.ax_quality.set_ylim(0, 1)
        self.ax_quality.grid(True, alpha=0.3)

        # 特征分布
        self.ax_features = self.fig.add_subplot(gs[1, 2])
        self.ax_features.set_title('实时特征分布', fontsize=12, fontweight='bold')
        self.ax_features.set_xlabel('特征')
        self.ax_features.set_ylabel('归一化值')
        self.ax_features.set_ylim(0, 1)
        self.ax_features.grid(True, alpha=0.3)

        # 嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=10)

        # 主要控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, padx=10)

        self.start_btn = ttk.Button(button_frame, text="🚀 开始监测",
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏹️ 停止监测",
                                  command=self.stop_monitoring,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.calibrate_btn = ttk.Button(button_frame, text="🎯 开始校准",
                                       command=self.start_calibration)
        self.calibrate_btn.pack(side=tk.LEFT, padx=5)

        # 功能按钮
        function_frame = ttk.Frame(control_frame)
        function_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(function_frame, text="📊 保存数据",
                  command=self.save_data).pack(side=tk.LEFT, padx=5)

        ttk.Button(function_frame, text="🔄 重置",
                  command=self.reset_system).pack(side=tk.LEFT, padx=5)

        ttk.Button(function_frame, text="ℹ️ 关于",
                  command=self.show_about).pack(side=tk.LEFT, padx=5)

    def generate_professional_demo_data(self):
        """生成专业的演示数据"""
        current_time = time.time() - self.start_time

        # 生成更真实的EMG数据 (8通道)
        emg_data = []
        for channel in range(8):
            # 基础信号频率根据通道不同
            base_freq = 10 + channel * 2

            # 肌肉激活模式
            activation = 0.1 * np.sin(2 * np.pi * base_freq * current_time)

            # 根据情绪添加特征
            if self.current_emotion == 'Stress':
                # 压力：高频成分增加
                activation += 0.2 * np.sin(2 * np.pi * 80 * current_time)
                activation += 0.1 * np.random.randn()
            elif self.current_emotion == 'Excited':
                # 兴奋：多频率混合
                activation += 0.15 * np.sin(2 * np.pi * 30 * current_time)
                activation += 0.1 * np.sin(2 * np.pi * 60 * current_time)
            elif self.current_emotion == 'Focus':
                # 专注：稳定低频
                activation *= 0.7
                activation += 0.05 * np.sin(2 * np.pi * 5 * current_time)
            elif self.current_emotion == 'Happy':
                # 开心：中等频率
                activation += 0.12 * np.sin(2 * np.pi * 20 * current_time)

            # 添加噪声
            activation += 0.02 * np.random.randn()

            emg_data.append(np.clip(activation, -1, 1))

        # 生成更真实的GSR数据
        base_gsr = 2.0 + 0.3 * np.sin(2 * np.pi * 0.1 * current_time)

        if self.current_emotion == 'Stress':
            base_gsr += 0.5  # 压力时皮电反应增强
        elif self.current_emotion == 'Excited':
            base_gsr += 0.3 + 0.1 * np.sin(2 * np.pi * 0.5 * current_time)

        gsr_data = max(0.1, base_gsr + 0.05 * np.random.randn())

        return emg_data, gsr_data

    def get_demo_emotion(self):
        """获取演示模式的情绪状态"""
        current_time = time.time() - self.start_time
        emotion_cycle_time = 30  # 30秒一个周期
        phase = (current_time % emotion_cycle_time) / emotion_cycle_time

        # 更复杂的情绪转换模式
        if phase < 0.15:
            return 'Neutral'
        elif phase < 0.3:
            return 'Focus'
        elif phase < 0.5:
            return 'Happy'
        elif phase < 0.7:
            return 'Excited'
        elif phase < 0.85:
            return 'Stress'
        else:
            return 'Neutral'

    def process_data(self):
        """处理数据"""
        if self.demo_mode:
            # 演示模式：生成模拟数据
            emg_data, gsr_data = self.generate_professional_demo_data()
            target_emotion = self.get_demo_emotion()

            # 模拟处理延迟
            processing_time = np.random.uniform(0.005, 0.015)  # 5-15ms

            # 模拟信号质量
            quality_score = np.random.uniform(0.7, 0.95)  # 高质量信号

            return {
                'emg_data': emg_data,
                'gsr_data': gsr_data,
                'emotion': target_emotion,
                'confidence': 0.7 + 0.2 * np.random.random(),
                'processing_time': processing_time,
                'quality_score': quality_score,
                'timestamp': time.time()
            }

        # 实时模式：处理真实数据
        if self.signal_engine:
            try:
                result = self.signal_engine.process_window()
                if result:
                    # 从处理结果中检测情绪
                    emotion_result = self.emotion_detector.detect_emotion(
                        result['normalized_features']
                    )

                    return {
                        'emg_data': list(result['emg_features']['rms']) if isinstance(result['emg_features']['rms'], list) else [result['emg_features']['rms']] * 8,
                        'gsr_data': result['gsr_features']['tonic'],
                        'emotion': emotion_result.get('emotion', 'Neutral'),
                        'confidence': emotion_result.get('confidence', 0.5),
                        'processing_time': result['processing_time'],
                        'quality_score': result['quality']['overall'],
                        'timestamp': result['timestamp'],
                        'features': result['normalized_features']
                    }
            except Exception as e:
                logger.error(f"数据处理错误: {e}")

        return None

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 处理数据
        result = self.process_data()
        if not result:
            return

        # 更新当前状态
        self.current_emotion = result['emotion']
        self.emotion_confidence = result['confidence']

        # 存储数据
        current_time = time.time() - self.start_time
        self.time_stamps.append(current_time)

        if len(result['emg_data']) > 0:
            self.emg_data.append(np.mean(result['emg_data']))
        self.gsr_data.append(result['gsr_data'])
        self.emotion_history.append(result['emotion'])
        self.quality_history.append(result['quality_score'])

        # 清除并更新图表
        self.update_emg_plot()
        self.update_gsr_plot()
        self.update_emotion_plot()
        self.update_3d_hand()
        self.update_quality_plot()
        self.update_features_plot(result.get('features', {}))

        # 更新状态显示
        self.update_status_display(result)

        # 刷新画布
        self.canvas.draw()

    def update_emg_plot(self):
        """更新EMG图"""
        self.ax_emg.clear()
        self.ax_emg.set_title('EMG信号 (平均值)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)

        if len(self.emg_data) > 0:
            times = list(self.time_stamps)[-len(self.emg_data):]
            self.ax_emg.plot(times, list(self.emg_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_emg.set_ylim(-1, 1)

    def update_gsr_plot(self):
        """更新GSR图"""
        self.ax_gsr.clear()
        self.ax_gsr.set_title('GSR信号', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        if len(self.gsr_data) > 0:
            times = list(self.time_stamps)[-len(self.gsr_data):]
            self.ax_gsr.plot(times, list(self.gsr_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_gsr.set_ylim(0, 5)

    def update_emotion_plot(self):
        """更新情绪状态图"""
        self.ax_emotion.clear()
        self.ax_emotion.set_title('情绪状态时间线', fontsize=12, fontweight='bold')
        self.ax_emotion.set_xlabel('时间 (s)')
        self.ax_emotion.set_ylabel('情绪状态')
        self.ax_emotion.set_ylim(-0.5, len(self.emotion_states) - 0.5)
        self.ax_emotion.set_yticks(range(len(self.emotion_states)))
        self.ax_emotion.set_yticklabels(list(self.emotion_states.keys()))
        self.ax_emotion.grid(True, alpha=0.3)

        if len(self.emotion_history) > 0:
            times = list(self.time_stamps)[-len(self.emotion_history):]
            emotion_values = []
            emotion_colors = []

            for emotion in self.emotion_history:
                if emotion in self.emotion_states:
                    idx = list(self.emotion_states.keys()).index(emotion)
                    emotion_values.append(idx)
                    emotion_colors.append(self.emotion_states[emotion]['color'])

            self.ax_emotion.scatter(times, emotion_values, c=emotion_colors, s=30, alpha=0.7)

    def update_3d_hand(self):
        """更新3D手部模型"""
        self.ax_3d.clear()
        self.ax_3d.set_title('3D手部模型', fontsize=12, fontweight='bold')

        # 手部基础参数
        palm_width = 0.08
        palm_length = 0.10

        # 获取当前情绪颜色
        emotion_info = self.emotion_states[self.current_emotion]
        rgb_color = self.hex_to_rgb(emotion_info['color'])

        # 创建手掌
        u = np.linspace(0, 2 * np.pi, 15)
        v = np.linspace(0, np.pi/3, 8)

        x_palm = palm_width * np.outer(np.cos(u), np.sin(v))
        y_palm = palm_length * np.outer(np.sin(u), np.sin(v)) * 0.5
        z_palm = palm_width * np.outer(np.ones(np.size(u)), np.cos(v)) * 0.3

        self.ax_3d.plot_surface(x_palm, y_palm, z_palm,
                               alpha=0.6, color=rgb_color,
                               linewidth=0, antialiased=True)

        # 绘制手指
        finger_positions = [
            [-0.025, 0.08, 0.01],
            [-0.012, 0.09, 0.01],
            [0, 0.10, 0.01],
            [0.012, 0.09, 0.01],
            [0.025, 0.06, 0.01]
        ]

        # 根据情绪调整手指
        emotion_multiplier = self.get_emotion_multiplier()

        for i, pos in enumerate(finger_positions):
            finger_extension = emotion_multiplier * 0.04
            finger_x = [pos[0], pos[0]]
            finger_y = [pos[1], pos[1] + finger_extension]
            finger_z = [pos[2], pos[2] + 0.01]

            self.ax_3d.plot(finger_x, finger_y, finger_z,
                           color=rgb_color, linewidth=4, alpha=0.8)
            self.ax_3d.scatter([finger_x[1]], [finger_y[1]], [finger_z[1]],
                             color=rgb_color, s=50, alpha=1.0)

        # 设置坐标轴
        self.ax_3d.set_xlim([-0.15, 0.15])
        self.ax_3d.set_ylim([-0.05, 0.20])
        self.ax_3d.set_zlim([-0.05, 0.10])
        self.ax_3d.set_xlabel('X')
        self.ax_3d.set_ylabel('Y')
        self.ax_3d.set_zlabel('Z')

        # 添加情绪标签
        self.ax_3d.text2D(0.5, 0.95, f'{emotion_info["emoji"]} {self.current_emotion}',
                          transform=self.ax_3d.transAxes,
                          fontsize=14, ha='center', weight='bold')

    def update_quality_plot(self):
        """更新信号质量图"""
        self.ax_quality.clear()
        self.ax_quality.set_title('信号质量监测', fontsize=12, fontweight='bold')
        self.ax_quality.set_xlabel('时间')
        self.ax_quality.set_ylabel('质量评分')
        self.ax_quality.set_ylim(0, 1)
        self.ax_quality.grid(True, alpha=0.3)

        if len(self.quality_history) > 0:
            times = list(range(len(self.quality_history)))
            quality_values = list(self.quality_history)

            # 根据质量设置颜色
            colors = ['red' if q < 0.3 else 'orange' if q < 0.7 else 'green' for q in quality_values]

            for i in range(len(times)-1):
                self.ax_quality.plot(times[i:i+2], quality_values[i:i+2],
                                   color=colors[i], linewidth=2, alpha=0.8)

    def update_features_plot(self, features):
        """更新特征分布图"""
        self.ax_features.clear()
        self.ax_features.set_title('实时特征分布', fontsize=12, fontweight='bold')
        self.ax_features.set_xlabel('特征')
        self.ax_features.set_ylabel('归一化值')
        self.ax_features.set_ylim(0, 1)
        self.ax_features.grid(True, alpha=0.3)

        if features:
            feature_names = list(features.keys())
            feature_values = list(features.values())

            colors = [self.emotion_states[self.current_emotion]['color']] * len(feature_names)
            bars = self.ax_features.bar(feature_names, feature_values, color=colors, alpha=0.7)

            # 添加数值标签
            for bar, value in zip(bars, feature_values):
                height = bar.get_height()
                self.ax_features.text(bar.get_x() + bar.get_width()/2., height,
                                     f'{value:.2f}', ha='center', va='bottom')

    def update_status_display(self, result):
        """更新状态显示"""
        # 更新情绪显示
        emotion_info = self.emotion_states[self.current_emotion]
        self.emotion_label.config(
            text=f"{emotion_info['emoji']} {emotion_info['description']}"
        )

        # 更新置信度
        self.confidence_label.config(
            text=f"置信度: {result['confidence']:.2f}"
        )

        # 更新信号质量
        quality_score = result['quality_score']
        if quality_score >= 0.8:
            quality_text = "优秀"
            quality_color = 'green'
        elif quality_score >= 0.6:
            quality_text = "良好"
            quality_color = 'blue'
        elif quality_score >= 0.4:
            quality_text = "一般"
            quality_color = 'orange'
        else:
            quality_text = "较差"
            quality_color = 'red'

        self.quality_label.config(
            text=f"信号质量: {quality_text} ({quality_score:.2f})",
            foreground=quality_color
        )

        # 更新性能指标
        processing_time_ms = result['processing_time'] * 1000
        fps = 1.0 / result['processing_time'] if result['processing_time'] > 0 else 0
        self.performance_label.config(
            text=f"延迟: {processing_time_ms:.1f}ms | FPS: {fps:.1f}"
        )

    def get_emotion_multiplier(self):
        """根据情绪获取手指伸展倍数"""
        multipliers = {
            'Neutral': 1.0,
            'Happy': 1.2,
            'Stress': 0.6,
            'Focus': 1.1,
            'Excited': 1.4
        }
        return multipliers.get(self.current_emotion, 1.0)

    def hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    def start_monitoring(self):
        """开始监测"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # 重启信号引擎
            if self.signal_engine:
                self.signal_engine.start()

            # 创建动画
            from matplotlib.animation import FuncAnimation
            self.animation = FuncAnimation(self.fig, self.update_plots,
                                         interval=100, blit=False)
            self.canvas.draw()

            logger.info("🚀 开始实时监测")

    def stop_monitoring(self):
        """停止监测"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            if self.animation is not None:
                self.animation.event_source.stop()
                self.animation = None

            # 停止信号引擎
            if self.signal_engine:
                self.signal_engine.stop()

            logger.info("⏹️ 停止监测")

    def start_calibration(self):
        """开始校准"""
        if not self.calibration_system:
            messagebox.showinfo("提示", "校准系统不可用")
            return

        self.calibrate_btn.config(state=tk.DISABLED)

        def calibrate():
            try:
                if PROFESSIONAL_ENGINE_AVAILABLE:
                    # 使用专业校准系统
                    success = self.calibration_system.run_calibration()
                    if success:
                        messagebox.showinfo("成功", "校准完成！")
                    else:
                        messagebox.showerror("失败", "校准失败！")
                else:
                    # 模拟校准
                    messagebox.showinfo("提示", "演示模式校准完成")
            except Exception as e:
                messagebox.showerror("错误", f"校准过程出错: {e}")
            finally:
                self.calibrate_btn.config(state=tk.NORMAL)

        threading.Thread(target=calibrate, daemon=True).start()

    def save_data(self):
        """保存数据"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"emotionhand_data_{timestamp}.json"

            data = {
                'timestamp': timestamp,
                'duration': time.time() - self.start_time if self.is_running else 0,
                'emotion_history': list(self.emotion_history),
                'quality_history': list(self.quality_history),
                'settings': {
                    'demo_mode': self.demo_mode,
                    'engine_type': 'professional' if PROFESSIONAL_ENGINE_AVAILABLE else 'simplified'
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"数据已保存到: {filename}")

        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {e}")

    def reset_system(self):
        """重置系统"""
        result = messagebox.askyesno("确认", "确定要重置系统吗？所有数据将被清空。")
        if result:
            # 清空数据
            self.emg_data.clear()
            self.gsr_data.clear()
            self.emotion_history.clear()
            self.time_stamps.clear()
            self.quality_history.clear()

            # 重置状态
            self.current_emotion = 'Neutral'
            self.emotion_confidence = 0.5
            self.start_time = time.time()

            # 重启信号引擎
            if self.signal_engine:
                self.signal_engine.stop()
                self.signal_engine.start()

            messagebox.showinfo("完成", "系统已重置")

    def show_about(self):
        """显示关于信息"""
        about_text = """EmotionHand 集成版 v1.0

🔧 企业级信号处理引擎
• EMG: 8通道, 20-450Hz, 1000Hz采样
• GSR: 0.05-1.0Hz滤波, 专业特征提取
• 实时质量监测与异常处理

🎯 情绪识别功能
• 5种基本情绪状态识别
• 个性化校准系统
• 置信度评估

📊 实时可视化
• 多通道信号监控
• 3D手部模型
• 质量与性能监测

🚀 技术特点
• <100ms处理延迟
• 15-30 FPS刷新率
• 企业级架构设计

开发者: EmotionHand Team
技术支持: 企业级信号处理引擎"""

        messagebox.showinfo("关于 EmotionHand", about_text)

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_monitoring()

            # 停止信号引擎
            if self.signal_engine:
                self.signal_engine.stop()

            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 集成版启动成功!")
        print(f"🔧 信号处理引擎: {'企业级' if PROFESSIONAL_ENGINE_AVAILABLE else '简化版'}")
        print(f"📊 运行模式: {'演示模式' if self.demo_mode else '实时模式'}")
        print("📋 功能特点:")
        print("   • 专业EMG+GSR信号处理")
        print("   • 实时情绪状态识别")
        print("   • 3D手部模型可视化")
        print("   • 信号质量监测")
        print("   • 个性化校准系统")

        self.root.mainloop()

if __name__ == "__main__":
    # 创建应用实例
    app = EmotionHandIntegrated(demo_mode=True)
    app.run()