#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 硬件版 - 集成真实传感器数据
结合Arduino XIAO ESP32C3 + EMG+GSR传感器
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import serial
import serial.tools.list_ports
from collections import deque
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# 添加zcf项目路径
zcf_main_path = "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub"
if os.path.exists(zcf_main_path):
    sys.path.insert(0, zcf_main_path)

# 导入核心模块
try:
    from signal_processing_engine import RealTimeSignalProcessor
    from emotion_state_detector import EnsembleDetector
    from calibration_system import CalibrationSystem
    print("✅ 成功导入zcf核心模块")
except ImportError as e:
    print(f"⚠️ zcf模块导入失败: {e}")

class EmotionHandHardware:
    """EmotionHand 硬件版 - 真实传感器数据"""

    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EmotionHand 硬件版 - 真实传感器系统")
        self.root.geometry("1600x900")

        # 情绪状态定义
        self.emotion_states = {
            'Neutral': {'color': '#808080', 'emoji': '😐', 'description': '平静'},
            'Relaxed': {'color': '#4CAF50', 'emoji': '😌', 'description': '放松'},
            'Focused': {'color': '#4ECDC4', 'emoji': '🎯', 'description': '专注'},
            'Stressed': {'color': '#FF6B6B', 'emoji': '😰', 'description': '压力'},
            'Fatigued': {'color': '#9C27B0', 'emoji': '😴', 'description': '疲劳'},
            'Excited': {'color': '#FF1744', 'emoji': '🤩', 'description': '兴奋'}
        }

        # 手势定义
        self.gesture_states = {
            'Open': {'emoji': '👋', 'description': '张开'},
            'Pinch': {'emoji': '✌️', 'description': '捏合'},
            'Fist': {'emoji': '✊', 'description': '握拳'}
        }

        # 当前状态
        self.current_emotion = 'Neutral'
        self.current_gesture = 'Open'
        self.emotion_confidence = 0.5

        # 串口连接
        self.serial_port = None
        self.is_connected = False
        self.port_name = ""
        self.baud_rate = 115200

        # 数据存储
        self.emg_data = deque(maxlen=1000)
        self.gsr_data = deque(maxlen=1000)
        self.emotion_history = deque(maxlen=100)
        self.gesture_history = deque(maxlen=100)
        self.time_stamps = deque(maxlen=1000)
        self.quality_history = deque(maxlen=100)

        # 校准参数
        self.emg_baseline = 0.0
        self.gsr_baseline = 0.0
        self.calibration_count = 0
        self.calibration_mode = True
        self.calibration_target = 1000

        # 统计信息
        self.sample_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_data_time = 0

        # 核心组件
        self.signal_engine = None
        self.emotion_detector = None
        self.calibration_system = None
        self.init_core_components()

        # 动画控制
        self.animation = None
        self.is_running = False

        # 设置界面
        self.setup_ui()

    def init_core_components(self):
        """初始化核心组件"""
        try:
            config_path = os.path.join(zcf_main_path, "signal_processing_config.json")
            self.signal_engine = RealTimeSignalProcessor(config_path)
            self.signal_engine.start()
            print("✅ 信号处理引擎启动成功")
        except Exception as e:
            print(f"⚠️ 信号处理引擎启动失败: {e}")

        try:
            self.emotion_detector = EnsembleDetector()
            print("✅ 情绪检测器初始化成功")
        except Exception as e:
            print(f"⚠️ 情绪检测器初始化失败: {e}")

        try:
            self.calibration_system = CalibrationSystem()
            print("✅ 校准系统初始化成功")
        except Exception as e:
            print(f"⚠️ 校准系统初始化失败: {e}")

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame,
                               text="EmotionHand 硬件版 - 真实传感器系统",
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=5)

        # 硬件连接框架
        hardware_frame = ttk.LabelFrame(main_frame, text="硬件连接", padding=10)
        hardware_frame.pack(fill=tk.X, pady=5)

        self.create_hardware_controls(hardware_frame)

        # 系统状态框架
        status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.create_system_status(status_frame)

        # 创建图表
        self.create_plots(main_frame)

        # 控制面板
        self.create_control_panel(main_frame)

    def create_hardware_controls(self, parent):
        """创建硬件控制"""
        # 串口控制
        port_frame = ttk.Frame(parent)
        port_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(port_frame, text="串口:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var,
                                       state="readonly", width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(port_frame, text="刷新",
                                     command=self.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(port_frame, text="连接",
                                     command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        # 连接状态
        self.hardware_status = ttk.Label(parent, text="🔌 未连接",
                                         foreground="red", font=('Arial', 12, 'bold'))
        self.hardware_status.pack(side=tk.LEFT, padx=20)

        # 校准控制
        calib_frame = ttk.Frame(parent)
        calib_frame.pack(side=tk.LEFT, padx=10)

        self.calib_status = ttk.Label(calib_frame, text="等待校准...")
        self.calib_status.pack(side=tk.LEFT, padx=5)

        self.calib_btn = ttk.Button(calib_frame, text="重新校准",
                                    command=self.start_calibration)
        self.calib_btn.pack(side=tk.LEFT, padx=5)

        self.calib_progress = ttk.Progressbar(calib_frame, length=150, mode='determinate')
        self.calib_progress.pack(side=tk.LEFT, padx=5)

        # 初始化串口列表
        self.refresh_ports()

    def create_system_status(self, parent):
        """创建系统状态显示"""
        # 当前状态
        current_frame = ttk.Frame(parent)
        current_frame.pack(side=tk.LEFT, padx=20)

        self.emotion_label = ttk.Label(current_frame,
                                      text=f"😐 平静",
                                      font=('Arial', 16, 'bold'))
        self.emotion_label.pack()

        self.gesture_label = ttk.Label(current_frame,
                                       text="👋 手势: 张开",
                                       font=('Arial', 12))
        self.gesture_label.pack()

        self.confidence_label = ttk.Label(current_frame,
                                         text=f"置信度: 0.50",
                                         font=('Arial', 10))
        self.confidence_label.pack()

        # 性能指标
        performance_frame = ttk.Frame(parent)
        performance_frame.pack(side=tk.LEFT, padx=20)

        self.quality_label = ttk.Label(performance_frame,
                                      text="信号质量: 检测中...",
                                      font=('Arial', 11))
        self.quality_label.pack()

        self.performance_label = ttk.Label(performance_frame,
                                          text="采样率: 0Hz | 错误率: 0%",
                                          font=('Arial', 10))
        self.performance_label.pack()

    def create_plots(self, parent):
        """创建图表区域"""
        # 创建matplotlib图形
        self.fig = plt.figure(figsize=(16, 8), facecolor='white')

        # 创建子图布局
        gs = self.fig.add_gridspec(2, 4, hspace=0.3, wspace=0.3)

        # EMG信号图
        self.ax_emg = self.fig.add_subplot(gs[0, 0])
        self.ax_emg.set_title('EMG信号 (标准化)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('标准化值')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(-1, 1)

        # GSR信号图
        self.ax_gsr = self.fig.add_subplot(gs[0, 1])
        self.ax_gsr.set_title('GSR信号 (相对变化)', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('变化量 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        # 情绪状态时间线
        self.ax_emotion = self.fig.add_subplot(gs[0, 2])
        self.ax_emotion.set_title('情绪状态时间线', fontsize=12, fontweight='bold')
        self.ax_emotion.set_xlabel('时间 (s)')
        self.ax_emotion.set_ylabel('情绪状态')
        self.ax_emotion.set_ylim(-0.5, len(self.emotion_states) - 0.5)
        self.ax_emotion.set_yticks(range(len(self.emotion_states)))
        self.ax_emotion.set_yticklabels(list(self.emotion_states.keys()))
        self.ax_emotion.grid(True, alpha=0.3)

        # 手势识别时间线
        self.ax_gesture = self.fig.add_subplot(gs[0, 3])
        self.ax_gesture.set_title('手势识别', fontsize=12, fontweight='bold')
        self.ax_gesture.set_xlabel('时间 (s)')
        self.ax_gesture.set_ylabel('手势')
        self.ax_gesture.set_ylim(-0.5, 2.5)
        self.ax_gesture.set_yticks([0, 1, 2])
        self.ax_gesture.set_yticklabels(['张开', '捏合', '握拳'])
        self.ax_gesture.grid(True, alpha=0.3)

        # 信号质量监测
        self.ax_quality = self.fig.add_subplot(gs[1, 0])
        self.ax_quality.set_title('信号质量监测', fontsize=12, fontweight='bold')
        self.ax_quality.set_xlabel('时间')
        self.ax_quality.set_ylabel('质量评分')
        self.ax_quality.set_ylim(0, 1)
        self.ax_quality.grid(True, alpha=0.3)

        # EMG特征分布
        self.ax_features = self.fig.add_subplot(gs[1, 1])
        self.ax_features.set_title('EMG特征分布', fontsize=12, fontweight='bold')
        self.ax_features.set_xlabel('特征')
        self.ax_features.set_ylabel('值')
        self.ax_features.grid(True, alpha=0.3)

        # 状态分布统计
        self.ax_stats = self.fig.add_subplot(gs[1, 2])
        self.ax_stats.set_title('状态分布统计', fontsize=12, fontweight='bold')
        self.ax_stats.set_xlabel('状态')
        self.ax_stats.set_ylabel('频次')
        self.ax_stats.grid(True, alpha=0.3)

        # 实时数据面板
        self.ax_data = self.fig.add_subplot(gs[1, 3])
        self.ax_data.set_title('实时数据', fontsize=12, fontweight='bold')
        self.ax_data.axis('off')

        # 嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=10)

        # 主要控制按钮
        button_frame1 = ttk.Frame(control_frame)
        button_frame1.pack(side=tk.LEFT, padx=10)

        self.start_btn = ttk.Button(button_frame1, text="🚀 开始监测",
                                   command=self.start_monitoring, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame1, text="⏹️ 停止监测",
                                  command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 功能按钮
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(side=tk.LEFT, padx=10)

        ttk.Button(button_frame2, text="💾 保存数据",
                  command=self.save_data).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame2, text="🔄 重置系统",
                  command=self.reset_system).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame2, text="📊 导出报告",
                  command=self.export_report).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame2, text="ℹ️ 关于",
                  command=self.show_about).pack(side=tk.LEFT, padx=5)

    def refresh_ports(self):
        """刷新串口列表"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports

        if ports:
            # 尝试自动选择XIAO设备
            xiao_ports = [p for p in ports if 'USB' in p or 'SLAB' in p or 'CP210' in p]
            if xiao_ports:
                self.port_combo.set(xiao_ports[0])
            else:
                self.port_combo.set(ports[0])

        print(f"🔍 发现串口: {ports}")

    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        """连接串口"""
        if not self.port_var.get():
            messagebox.showerror("错误", "请选择串口")
            return

        try:
            self.serial_port = serial.Serial(
                port=self.port_var.get(),
                baudrate=self.baud_rate,
                timeout=0.1
            )
            self.is_connected = True
            self.port_name = self.port_var.get()
            self.hardware_status.config(text="🔌 已连接", foreground="green")
            self.connect_btn.config(text="断开")
            self.start_btn.config(state=tk.NORMAL)

            # 启动数据读取线程
            self.data_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.data_thread.start()

            # 开始校准
            self.start_calibration()

            print(f"✅ 串口连接成功: {self.port_name}")

        except Exception as e:
            messagebox.showerror("连接失败", f"无法连接串口: {e}")
            print(f"❌ 连接失败: {e}")

    def disconnect_serial(self):
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.hardware_status.config(text="🔌 未连接", foreground="red")
        self.connect_btn.config(text="连接")
        self.start_btn.config(state=tk.DISABLED)
        print("🔌 串口已断开")

    def start_calibration(self):
        """开始校准"""
        self.calibration_mode = True
        self.calibration_count = 0
        self.emg_baseline = 0.0
        self.gsr_baseline = 0.0
        self.calib_status.config(text="正在校准... 请保持肌肉放松！")
        self.calib_progress['value'] = 0
        print("🎯 开始校准，请保持肌肉放松...")

    def read_serial_data(self):
        """读取串口数据"""
        while self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        self.process_sensor_data(line)

            except Exception as e:
                self.error_count += 1
                print(f"❌ 数据读取错误: {e}")

            time.sleep(0.001)

    def process_sensor_data(self, line):
        """处理传感器数据"""
        try:
            # 解析CSV格式: EMG,GSR
            parts = line.split(',')
            if len(parts) >= 2:
                emg_raw = float(parts[0])  # 0-3.3V
                gsr_raw = float(parts[1])  # μS

                self.last_data_time = time.time()

                # 校准处理
                if self.calibration_mode:
                    self.process_calibration_data(emg_raw, gsr_raw)
                else:
                    self.process_normal_data(emg_raw, gsr_raw)

                self.sample_count += 1

        except ValueError as e:
            self.error_count += 1

    def process_calibration_data(self, emg_raw, gsr_raw):
        """处理校准数据"""
        self.emg_baseline += emg_raw
        self.gsr_baseline += gsr_raw
        self.calibration_count += 1

        # 更新进度
        progress = (self.calibration_count / self.calibration_target) * 100
        self.calib_progress['value'] = progress

        # 校准完成
        if self.calibration_count >= self.calibration_target:
            self.emg_baseline /= self.calibration_count
            self.gsr_baseline /= self.calibration_count
            self.calibration_mode = False

            self.calib_status.config(
                text=f"校准完成 - EMG基线: {self.emg_baseline:.3f}V"
            )
            self.calib_progress['value'] = 100

            print(f"✅ 校准完成: EMG基线={self.emg_baseline:.3f}V, GSR基线={self.gsr_baseline:.1f}μS")

    def process_normal_data(self, emg_raw, gsr_raw):
        """处理正常数据"""
        current_time = time.time() - self.start_time

        # 数据预处理
        emg_normalized = (emg_raw - self.emg_baseline) / 3.3 if self.emg_baseline > 0 else emg_raw / 3.3
        gsr_change = gsr_raw - self.gsr_baseline if self.gsr_baseline > 0 else gsr_raw

        # 存储数据
        self.time_stamps.append(current_time)
        self.emg_data.append(emg_normalized)
        self.gsr_data.append(gsr_change)

        # 检测情绪和手势
        emotion, gesture, confidence = self.detect_emotion_and_gesture(emg_normalized, gsr_change)

        self.current_emotion = emotion
        self.current_gesture = gesture
        self.emotion_confidence = confidence

        # 存储历史
        self.emotion_history.append(emotion)
        self.gesture_history.append(gesture)

        # 评估信号质量
        quality = self.assess_signal_quality(emg_normalized, gsr_change)
        self.quality_history.append(quality)

    def detect_emotion_and_gesture(self, emg_value, gsr_value):
        """检测情绪和手势"""
        # 手势检测（基于EMG强度）
        if abs(emg_value) > 0.6:
            gesture = 'Fist'
        elif abs(emg_value) > 0.3:
            gesture = 'Pinch'
        else:
            gesture = 'Open'

        # 情绪检测（基于EMG和GSR组合）
        emg_abs = abs(emg_value)
        gsr_abs = abs(gsr_value)

        if emg_abs > 0.7 and gsr_abs > 2.0:
            emotion = 'Stressed'
            confidence = 0.8
        elif 0.4 < emg_abs < 0.7 and gsr_abs < 1.0:
            emotion = 'Focused'
            confidence = 0.7
        elif emg_abs < 0.2 and gsr_abs < 0.5:
            emotion = 'Relaxed'
            confidence = 0.6
        elif emg_abs > 0.5 and 1.0 < gsr_abs < 3.0:
            emotion = 'Excited'
            confidence = 0.7
        elif emg_abs < 0.1 and gsr_abs < 0.2:
            emotion = 'Fatigued'
            confidence = 0.6
        else:
            emotion = 'Neutral'
            confidence = 0.5

        return emotion, gesture, confidence

    def assess_signal_quality(self, emg_value, gsr_value):
        """评估信号质量"""
        # 简化的质量评估
        quality = 1.0

        # EMG质量检查
        if abs(emg_value) > 0.95:  # 接近饱和
            quality -= 0.2
        elif abs(emg_value) < 0.01:  # 信号太弱
            quality -= 0.1

        # GSR质量检查
        if abs(gsr_value) > 10.0:  # 异常高值
            quality -= 0.2

        # 时间间隔检查
        time_since_last_data = time.time() - self.last_data_time
        if time_since_last_data > 0.1:  # 数据延迟
            quality -= 0.3

        return max(0, min(1, quality))

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 更新各个图表
        self.update_emg_plot()
        self.update_gsr_plot()
        self.update_emotion_plot()
        self.update_gesture_plot()
        self.update_quality_plot()
        self.update_features_plot()
        self.update_stats_plot()
        self.update_data_panel()

        # 更新状态显示
        self.update_status_display()

        # 刷新画布
        self.canvas.draw()

    def update_emg_plot(self):
        """更新EMG图"""
        self.ax_emg.clear()
        self.ax_emg.set_title('EMG信号 (标准化)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('标准化值')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(-1, 1)

        if len(self.emg_data) > 0:
            times = list(self.time_stamps)
            self.ax_emg.plot(times, list(self.emg_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)

            # 添加基线
            self.ax_emg.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='基线')
            self.ax_emg.legend()

    def update_gsr_plot(self):
        """更新GSR图"""
        self.ax_gsr.clear()
        self.ax_gsr.set_title('GSR信号 (相对变化)', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('变化量 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        if len(self.gsr_data) > 0:
            times = list(self.time_stamps)
            self.ax_gsr.plot(times, list(self.gsr_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)

            # 自动调整y轴
            if len(self.gsr_data) > 0:
                gsr_min = min(self.gsr_data)
                gsr_max = max(self.gsr_data)
                margin = max(1, (gsr_max - gsr_min) * 0.1)
                self.ax_gsr.set_ylim(gsr_min - margin, gsr_max + margin)

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

            self.ax_emotion.scatter(times, emotion_values, c=emotion_colors, s=20, alpha=0.7)

    def update_gesture_plot(self):
        """更新手势识别图"""
        self.ax_gesture.clear()
        self.ax_gesture.set_title('手势识别', fontsize=12, fontweight='bold')
        self.ax_gesture.set_xlabel('时间 (s)')
        self.ax_gesture.set_ylabel('手势')
        self.ax_gesture.set_ylim(-0.5, 2.5)
        self.ax_gesture.set_yticks([0, 1, 2])
        self.ax_gesture.set_yticklabels(['张开', '捏合', '握拳'])
        self.ax_gesture.grid(True, alpha=0.3)

        if len(self.gesture_history) > 0:
            times = list(self.time_stamps)[-len(self.gesture_history):]
            gesture_values = []
            gesture_colors = []

            gesture_map = {'Open': 0, 'Pinch': 1, 'Fist': 2}
            for gesture in self.gesture_history:
                if gesture in gesture_map:
                    gesture_values.append(gesture_map[gesture])
                    gesture_colors.append(self.emotion_states[self.current_emotion]['color'])

            self.ax_gesture.scatter(times, gesture_values, c=gesture_colors, s=15, alpha=0.7)

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

            self.ax_quality.plot(times, quality_values, 'g-', linewidth=2, alpha=0.8)
            self.ax_quality.axhline(y=0.8, color='orange', linestyle='--', alpha=0.5, label='良好阈值')
            self.ax_quality.legend()

    def update_features_plot(self):
        """更新特征分布图"""
        self.ax_features.clear()
        self.ax_features.set_title('实时特征', fontsize=12, fontweight='bold')
        self.ax_features.set_xlabel('特征')
        self.ax_features.set_ylabel('值')
        self.ax_features.grid(True, alpha=0.3)

        if len(self.emg_data) > 0 and len(self.gsr_data) > 0:
            # 计算统计特征
            emg_current = self.emg_data[-1]
            gsr_current = self.gsr_data[-1]

            emg_rms = np.sqrt(np.mean(np.array(list(self.emg_data))**2)) if len(self.emg_data) > 0 else 0
            gsr_mean = np.mean(list(self.gsr_data)) if len(self.gsr_data) > 0 else 0

            feature_names = ['EMG当前值', 'EMG RMS', 'GSR当前值', 'GSR均值']
            feature_values = [emg_current, emg_rms, gsr_current, gsr_mean]
            colors = ['blue', 'red', 'green', 'orange']

            bars = self.ax_features.bar(feature_names, feature_values, color=colors, alpha=0.7)

            # 添加数值标签
            for bar, value in zip(bars, feature_values):
                height = bar.get_height()
                self.ax_features.text(bar.get_x() + bar.get_width()/2., height,
                                     f'{value:.3f}', ha='center', va='bottom')

    def update_stats_plot(self):
        """更新状态分布统计"""
        self.ax_stats.clear()
        self.ax_stats.set_title('状态分布统计', fontsize=12, fontweight='bold')
        self.ax_stats.set_xlabel('状态')
        self.ax_stats.set_ylabel('频次')
        self.ax_stats.grid(True, alpha=0.3)

        if len(self.emotion_history) > 0:
            # 统计情绪分布
            emotion_counts = {}
            for emotion in self.emotion_history:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

            if emotion_counts:
                emotions = list(emotion_counts.keys())
                counts = list(emotion_counts.values())
                colors = [self.emotion_states[emotion]['color'] for emotion in emotions]

                self.ax_stats.bar(emotions, counts, color=colors, alpha=0.7)

                # 添加数值标签
                for i, (emotion, count) in enumerate(zip(emotions, counts)):
                    self.ax_stats.text(i, count, str(count), ha='center', va='bottom')

    def update_data_panel(self):
        """更新实时数据面板"""
        self.ax_data.clear()
        self.ax_data.set_title('实时数据', fontsize=12, fontweight='bold')
        self.ax_data.axis('off')

        current_time = time.time() - self.start_time

        if len(self.emg_data) > 0 and len(self.gsr_data) > 0:
            emg_current = self.emg_data[-1]
            gsr_current = self.gsr_data[-1]

            # 计算统计
            emg_rms = np.sqrt(np.mean(np.array(list(self.emg_data))**2)) if len(self.emg_data) > 0 else 0
            gsr_mean = np.mean(list(self.gsr_data)) if len(self.gsr_data) > 0 else 0

            # 信号质量
            quality = self.quality_history[-1] if len(self.quality_history) > 0 else 0

            info_text = f"""运行时间: {current_time:.1f}s

EMG信号:
  当前值: {emg_current:.3f}
  RMS值: {emg_rms:.3f}
  基线: {self.emg_baseline:.3f}V

GSR信号:
  当前值: {gsr_current:.2f}μS
  平均值: {gsr_mean:.2f}μS
  基线: {self.gsr_baseline:.1f}μS

系统状态:
  情绪: {self.current_emotion}
  手势: {self.current_gesture}
  置信度: {self.emotion_confidence:.2f}
  信号质量: {quality:.2f}

采样统计:
  总样本: {self.sample_count}
  错误数: {self.error_count}
  采样率: {self.sample_count/current_time:.1f}Hz"""

            self.ax_data.text(0.1, 0.5, info_text, transform=self.ax_data.transAxes,
                             fontsize=9, verticalalignment='center',
                             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    def update_status_display(self):
        """更新状态显示"""
        emotion_info = self.emotion_states[self.current_emotion]
        self.emotion_label.config(
            text=f"{emotion_info['emoji']} {emotion_info['description']}"
        )

        gesture_emoji = {'Open': '👋', 'Pinch': '✌️', 'Fist': '✊'}
        self.gesture_label.config(
            text=f"{gesture_emoji.get(self.current_gesture, '🤷')} {self.current_gesture}"
        )

        self.confidence_label.config(
            text=f"置信度: {self.emotion_confidence:.2f}"
        )

        # 更新信号质量
        if len(self.quality_history) > 0:
            quality_score = self.quality_history[-1]
            quality_text = "优秀" if quality_score > 0.8 else "良好" if quality_score > 0.6 else "一般"
            self.quality_label.config(
                text=f"信号质量: {quality_text} ({quality_score:.2f})",
                foreground='green' if quality_score > 0.8 else 'orange' if quality_score > 0.6 else 'red'
            )

        # 更新性能指标
        current_time = time.time() - self.start_time
        sample_rate = self.sample_count / current_time if current_time > 0 else 0
        error_rate = (self.error_count / (self.sample_count + self.error_count)) * 100 if (self.sample_count + self.error_count) > 0 else 0

        self.performance_label.config(
            text=f"采样率: {sample_rate:.1f}Hz | 错误率: {error_rate:.1f}%"
        )

    def start_monitoring(self):
        """开始监测"""
        if not self.is_connected:
            messagebox.showwarning("提示", "请先连接硬件")
            return

        if self.calibration_mode:
            messagebox.showwarning("提示", "请等待校准完成")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 创建动画
        from matplotlib.animation import FuncAnimation
        self.animation = FuncAnimation(self.fig, self.update_plots,
                                     interval=50, blit=False)
        self.canvas.draw()

        print("🚀 开始实时监测")

    def stop_monitoring(self):
        """停止监测"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            if self.animation is not None:
                self.animation.event_source.stop()
                self.animation = None

            print("⏹️ 停止监测")

    def save_data(self):
        """保存数据"""
        if len(self.emg_data) == 0:
            messagebox.showwarning("提示", "没有数据可保存")
            return

        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emotionhand_hardware_data_{timestamp}.json"

            data = {
                'timestamp': timestamp,
                'duration': time.time() - self.start_time,
                'hardware_info': {
                    'port': self.port_name,
                    'baud_rate': self.baud_rate,
                    'emg_sensor': 'Muscle Sensor v3',
                    'gsr_sensor': 'Grove GSR v1.2',
                    'microcontroller': 'XIAO ESP32C3'
                },
                'calibration': {
                    'emg_baseline': self.emg_baseline,
                    'gsr_baseline': self.gsr_baseline,
                    'calibration_samples': self.calibration_target
                },
                'statistics': {
                    'sample_count': self.sample_count,
                    'error_count': self.error_count,
                    'quality_history': list(self.quality_history)
                },
                'data': {
                    'timestamps': list(self.time_stamps),
                    'emg_data': list(self.emg_data),
                    'gsr_data': list(self.gsr_data),
                    'emotion_history': list(self.emotion_history),
                    'gesture_history': list(self.gesture_history)
                },
                'final_state': {
                    'emotion': self.current_emotion,
                    'gesture': self.current_gesture,
                    'confidence': self.emotion_confidence
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"数据已保存到: {filename}")
            print(f"✅ 数据已保存到: {filename}")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def reset_system(self):
        """重置系统"""
        if messagebox.askyesno("确认", "确定要重置系统吗？"):
            # 清空数据
            self.emg_data.clear()
            self.gsr_data.clear()
            self.emotion_history.clear()
            self.gesture_history.clear()
            self.time_stamps.clear()
            self.quality_history.clear()

            # 重置统计
            self.sample_count = 0
            self.error_count = 0
            self.start_time = time.time()

            # 重新校准
            self.start_calibration()

            messagebox.showinfo("完成", "系统已重置，开始重新校准")

    def export_report(self):
        """导出报告"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emotionhand_report_{timestamp}.txt"

            current_time = time.time() - self.start_time
            sample_rate = self.sample_count / current_time if current_time > 0 else 0

            report = f"""EmotionHand 硬件版监测报告
{'='*50}

报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
监测时长: {current_time:.1f}秒

硬件配置:
- 微控制器: XIAO ESP32C3
- EMG传感器: Muscle Sensor v3
- GSR传感器: Grove GSR v1.2
- 串口: {self.port_name}
- 波特率: {self.baud_rate}

校准信息:
- EMG基线: {self.emg_baseline:.3f}V
- GSR基线: {self.gsr_baseline:.1f}μS
- 校准样本数: {self.calibration_target}

数据统计:
- 总样本数: {self.sample_count}
- 错误样本数: {self.error_count}
- 采样率: {sample_rate:.1f}Hz
- 错误率: {(self.error_count/(self.sample_count+self.error_count)*100):.1f}%

识别结果:
- 当前情绪: {self.current_emotion}
- 当前手势: {self.current_gesture}
- 置信度: {self.emotion_confidence:.2f}

情绪状态分布:
"""

            # 统计情绪分布
            if len(self.emotion_history) > 0:
                emotion_counts = {}
                for emotion in self.emotion_history:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

                for emotion, count in sorted(emotion_counts.items()):
                    percentage = (count / len(self.emotion_history)) * 100
                    report += f"- {emotion}: {count}次 ({percentage:.1f}%)\n"

            report += f"""
手势识别分布:
"""

            # 统计手势分布
            if len(self.gesture_history) > 0:
                gesture_counts = {}
                for gesture in self.gesture_history:
                    gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

                for gesture, count in sorted(gesture_counts.items()):
                    percentage = (count / len(self.gesture_history)) * 100
                    report += f"- {gesture}: {count}次 ({percentage:.1f}%)\n"

            report += f"""
信号质量:
- 平均质量: {np.mean(list(self.quality_history)):.2f}
- 质量稳定性: {np.std(list(self.quality_history)):.2f}

技术说明:
- EMG信号范围: 0-3.3V (标准化为-1到1)
- GSR信号范围: 电导率变化 (μS)
- 采样频率: ~1000Hz
- 实时显示频率: 20Hz

报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)

            messagebox.showinfo("成功", f"报告已导出到: {filename}")
            print(f"✅ 报告已导出到: {filename}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def show_about(self):
        """显示关于信息"""
        about_text = """EmotionHand 硬件版 v1.0

🔧 硬件配置
• 微控制器: Seeed Studio XIAO ESP32C3
• EMG传感器: Advancer Technologies Muscle Sensor v3
• GSR传感器: Grove GSR v1.2
• 通信: 串口 (115200 baud)

📊 功能特性
• 实时EMG+GSR数据采集
• 自动基线校准
• 6种情绪状态识别
• 3种手势识别
• 信号质量监测
• 数据导出和报告生成

🎯 识别能力
• 情绪: Neutral, Relaxed, Focused, Stressed, Fatigued, Excited
• 手势: Open, Pinch, Fist
• 置信度评估
• 实时质量监控

💾 数据管理
• JSON格式数据保存
• 文本格式报告导出
• 完整的统计信息
• 时间序列数据

技术支持: EmotionHand Team
基于zcf项目核心模块"""

        messagebox.showinfo("关于 EmotionHand 硬件版", about_text)

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_monitoring()
            if self.is_connected:
                self.disconnect_serial()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 硬件版启动成功!")
        print("📋 硬件配置:")
        print("   • 微控制器: XIAO ESP32C3")
        print("   • EMG传感器: Muscle Sensor v3 (Pin D2)")
        print("   • GSR传感器: Grove GSR v1.2 (Pin D3)")
        print("   • 波特率: 115200")
        print("   • 输出格式: EMG,GSR")
        print("\n🎮 使用说明:")
        print("   1. 连接XIAO开发板")
        print("   2. 选择正确串口并连接")
        print("   3. 等待自动校准完成")
        print("   4. 开始实时监测")
        print("   5. 保存数据和导出报告")

        self.root.mainloop()

if __name__ == "__main__":
    app = EmotionHandHardware()
    app.run()