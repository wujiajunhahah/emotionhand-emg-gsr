#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时情绪可视化器 - 基于EMG+GSR的实时情绪识别与可视化
修复字体和状态映射问题
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import threading
import time
from collections import deque
import queue
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# 导入核心模块
try:
    from signal_processing_engine import SignalProcessingEngine
    from emotion_state_detector import EmotionStateDetector
except ImportError:
    print("⚠️ 核心模块未找到，使用演示模式")
    SignalProcessingEngine = None
    EmotionStateDetector = None

class RealtimeEmotionVisualizer:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EmotionHand - 实时情绪可视化")
        self.root.geometry("1200x800")

        # 情绪状态定义
        self.emotion_states = {
            'Neutral': {'color': '#808080', 'emoji': '😐', 'range': (0.4, 0.6)},
            'Happy': {'color': '#FFD700', 'emoji': '😊', 'range': (0.6, 0.8)},
            'Stress': {'color': '#FF6B6B', 'emoji': '😰', 'range': (0.8, 1.0)},
            'Focus': {'color': '#4ECDC4', 'emoji': '🎯', 'range': (0.2, 0.4)},
            'Excited': {'color': '#FF1744', 'emoji': '🤩', 'range': (0.0, 0.2)}
        }

        # 当前状态
        self.current_emotion = 'Neutral'
        self.emotion_confidence = 0.5

        # 数据存储
        self.emg_data = deque(maxlen=1000)
        self.gsr_data = deque(maxlen=1000)
        self.emotion_history = deque(maxlen=100)
        self.time_stamps = deque(maxlen=1000)

        # 信号处理组件
        if SignalProcessingEngine and not demo_mode:
            self.signal_engine = SignalProcessingEngine()
            self.emotion_detector = EmotionStateDetector()
        else:
            self.signal_engine = None
            self.emotion_detector = None

        # 动画相关
        self.animation = None
        self.is_running = False
        self.start_time = time.time()

        # 设置界面
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame, text="EmotionHand 实时情绪可视化",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)

        # 状态显示框架
        status_frame = ttk.LabelFrame(main_frame, text="当前状态", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        # 情绪状态显示
        self.emotion_label = ttk.Label(status_frame,
                                      text=f"😐 平静 - 置信度: 0.50",
                                      font=('Arial', 14))
        self.emotion_label.pack()

        # 模式显示
        mode_text = "演示模式" if self.demo_mode else "实时模式"
        self.mode_label = ttk.Label(status_frame, text=f"模式: {mode_text}")
        self.mode_label.pack()

        # 创建图形区域
        self.setup_plots(main_frame)

        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(control_frame, text="开始监测",
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="停止监测",
                                  command=self.stop_monitoring,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        if self.demo_mode:
            ttk.Label(control_frame,
                     text="演示模式：自动生成模拟数据驱动状态变化").pack(side=tk.LEFT, padx=20)

    def setup_plots(self, parent):
        """设置图表"""
        # 创建matplotlib图形
        self.fig = plt.Figure(figsize=(12, 6), facecolor='white')

        # EMG信号图
        self.ax_emg = self.fig.add_subplot(131)
        self.ax_emg.set_title('EMG信号')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(-1, 1)

        # GSR信号图
        self.ax_gsr = self.fig.add_subplot(132)
        self.ax_gsr.set_title('GSR信号')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)
        self.ax_gsr.set_ylim(0, 5)

        # 情绪状态图
        self.ax_emotion = self.fig.add_subplot(133)
        self.ax_emotion.set_title('情绪状态时间线')
        self.ax_emotion.set_xlabel('时间 (s)')
        self.ax_emotion.set_ylabel('情绪状态')
        self.ax_emotion.set_ylim(-0.5, len(self.emotion_states) - 0.5)
        self.ax_emotion.set_yticks(range(len(self.emotion_states)))
        self.ax_emotion.set_yticklabels(list(self.emotion_states.keys()))
        self.ax_emotion.grid(True, alpha=0.3)

        # 设置图形布局
        self.fig.tight_layout()

        # 嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def generate_demo_data(self):
        """生成演示数据"""
        current_time = time.time() - self.start_time

        # 生成周期性变化的模拟数据
        emg_signal = 0.3 * np.sin(2 * np.pi * 0.5 * current_time)  # 0.5Hz
        emg_signal += 0.1 * np.sin(2 * np.pi * 5 * current_time)   # 5Hz
        emg_signal += 0.05 * np.random.randn()  # 噪声

        gsr_signal = 2.0 + 0.5 * np.sin(2 * np.pi * 0.1 * current_time)  # 0.1Hz
        gsr_signal += 0.1 * np.random.randn()  # 噪声
        gsr_signal = max(0.5, gsr_signal)  # 确保非负

        # 根据时间自动切换情绪状态
        emotion_cycle_time = 30  # 30秒一个周期
        phase = (current_time % emotion_cycle_time) / emotion_cycle_time

        if phase < 0.2:
            target_emotion = 'Neutral'
        elif phase < 0.4:
            target_emotion = 'Focus'
        elif phase < 0.6:
            target_emotion = 'Happy'
        elif phase < 0.8:
            target_emotion = 'Excited'
        else:
            target_emotion = 'Stress'

        # 添加情绪相关的信号特征
        if target_emotion == 'Stress':
            emg_signal += 0.2 * np.random.randn()
            gsr_signal += 0.3
        elif target_emotion == 'Excited':
            emg_signal += 0.15 * np.sin(2 * np.pi * 10 * current_time)
            gsr_signal += 0.2
        elif target_emotion == 'Happy':
            emg_signal += 0.1 * np.sin(2 * np.pi * 3 * current_time)
        elif target_emotion == 'Focus':
            emg_signal *= 0.7  # 降低信号变化

        return emg_signal, gsr_signal, target_emotion

    def process_real_data(self, emg_raw, gsr_raw):
        """处理真实数据"""
        if self.signal_engine and self.emotion_detector:
            try:
                # 信号处理
                emg_processed = self.signal_engine.process_emg(emg_raw)
                gsr_processed = self.signal_engine.process_gsr(gsr_raw)

                # 情绪检测
                emotion_result = self.emotion_detector.detect_emotion(
                    emg_processed, gsr_processed
                )

                if emotion_result:
                    return np.mean(emg_processed), gsr_processed, emotion_result['emotion']
            except Exception as e:
                print(f"❌ 数据处理错误: {e}")

        return np.mean(emg_raw), gsr_raw, 'Neutral'

    def update_data(self):
        """更新数据"""
        current_time = time.time() - self.start_time

        if self.demo_mode:
            # 生成演示数据
            emg_val, gsr_val, emotion = self.generate_demo_data()
        else:
            # 这里应该从传感器获取数据
            # 暂时用演示数据代替
            emg_val, gsr_val, emotion = self.generate_demo_data()

        # 更新当前情绪
        self.current_emotion = emotion
        self.emotion_confidence = 0.7 + 0.2 * np.random.random()  # 模拟置信度

        # 存储数据
        self.emg_data.append(emg_val)
        self.gsr_data.append(gsr_val)
        self.emotion_history.append(emotion)
        self.time_stamps.append(current_time)

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 更新数据
        self.update_data()

        # 更新EMG图
        self.ax_emg.clear()
        self.ax_emg.set_title('EMG信号')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)

        if len(self.emg_data) > 0:
            times = list(self.time_stamps)
            emg_values = list(self.emg_data)
            self.ax_emg.plot(times, emg_values,
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_emg.set_ylim(-1, 1)

        # 更新GSR图
        self.ax_gsr.clear()
        self.ax_gsr.set_title('GSR信号')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        if len(self.gsr_data) > 0:
            times = list(self.time_stamps)
            gsr_values = list(self.gsr_data)
            self.ax_gsr.plot(times, gsr_values,
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_gsr.set_ylim(0, 5)

        # 更新情绪状态图
        self.ax_emotion.clear()
        self.ax_emotion.set_title('情绪状态时间线')
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
                else:
                    # 处理未知情绪状态
                    idx = list(self.emotion_states.keys()).index('Neutral')
                    emotion_values.append(idx)
                    emotion_colors.append(self.emotion_states['Neutral']['color'])

            self.ax_emotion.scatter(times, emotion_values, c=emotion_colors, s=20, alpha=0.6)

        # 更新状态标签
        emotion_info = self.emotion_states.get(self.current_emotion, self.emotion_states['Neutral'])
        self.emotion_label.config(
            text=f"{emotion_info['emoji']} {self.current_emotion} - 置信度: {self.emotion_confidence:.2f}"
        )

        # 刷新画布
        self.canvas.draw()

    def start_monitoring(self):
        """开始监测"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # 创建动画 - 从matplotlib.animation导入
            from matplotlib.animation import FuncAnimation
            self.animation = FuncAnimation(self.fig, self.update_plots,
                                         interval=100, blit=False)
            self.canvas.draw()

            print("✅ 开始实时监测")

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

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_monitoring()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 实时情绪可视化器启动")
        print(f"📊 当前模式: {'演示模式' if self.demo_mode else '实时模式'}")
        print("📋 使用说明:")
        print("   • 点击'开始监测'开始实时可视化")
        print("   • 观察EMG/GSR信号和情绪状态变化")
        if self.demo_mode:
            print("   • 演示模式会自动生成模拟数据")

        self.root.mainloop()

if __name__ == "__main__":
    # 默认使用演示模式
    visualizer = RealtimeEmotionVisualizer(demo_mode=True)
    visualizer.run()