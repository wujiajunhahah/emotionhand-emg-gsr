#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 演示版 - 无需传感器的情绪识别可视化演示
包含自动状态转换和完整的3D手部可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
import threading
import time
from collections import deque
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class DemoEmotionHand:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EmotionHand 演示版 - 情绪识别可视化系统")
        self.root.geometry("1400x800")

        # 情绪状态定义
        self.emotion_states = {
            'Neutral': {'color': '#808080', 'emoji': '😐', 'description': '平静'},
            'Happy': {'color': '#FFD700', 'emoji': '😊', 'description': '开心'},
            'Stress': {'color': '#FF6B6B', 'emoji': '😰', 'description': '压力'},
            'Focus': {'color': '#4ECDC4', 'emoji': '🎯', 'description': '专注'},
            'Excited': {'color': '#FF1744', 'emoji': '🤩', 'description': '兴奋'}
        }

        self.current_emotion = 'Neutral'
        self.emotion_confidence = 0.5

        # 演示数据
        self.demo_time = 0
        self.emotion_schedule = [
            (0, 30, 'Neutral'),      # 0-30秒: 平静
            (30, 60, 'Focus'),       # 30-60秒: 专注
            (60, 90, 'Happy'),       # 60-90秒: 开心
            (90, 120, 'Excited'),    # 90-120秒: 兴奋
            (120, 150, 'Stress'),    # 120-150秒: 压力
            (150, 180, 'Neutral')    # 150-180秒: 平静
        ]

        # 信号数据
        self.signal_history = deque(maxlen=500)
        self.emotion_history = deque(maxlen=100)

        # 动画相关
        self.animation = None
        self.is_running = True

        self.setup_ui()
        self.start_demo()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="EmotionHand 演示版",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=5)

        # 状态信息框架
        info_frame = ttk.LabelFrame(main_frame, text="当前状态", padding="10")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 状态显示
        self.status_text = tk.Text(info_frame, height=4, width=50)
        self.status_text.grid(row=0, column=0, padx=5)

        # 创建图表框架
        self.create_plots(main_frame)

        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(control_frame, text="开始演示",
                                   command=self.start_demo)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="停止演示",
                                  command=self.stop_demo)
        self.stop_btn.grid(row=0, column=1, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, length=400,
                                          variable=self.progress_var)
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=5)

    def create_plots(self, parent):
        """创建图表"""
        # 创建图形
        self.fig = plt.Figure(figsize=(14, 6), facecolor='white')

        # 子图1: 信号波形
        self.ax1 = self.fig.add_subplot(131)
        self.ax1.set_title('模拟信号波形', fontsize=12)
        self.ax1.set_xlabel('时间 (s)')
        self.ax1.set_ylabel('幅值')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_ylim(-1, 1)

        # 子图2: 情绪状态时间线
        self.ax2 = self.fig.add_subplot(132)
        self.ax2.set_title('情绪状态时间线', fontsize=12)
        self.ax2.set_xlabel('时间 (s)')
        self.ax2.set_ylabel('情绪状态')
        self.ax2.set_ylim(-0.5, len(self.emotion_states) - 0.5)

        # 子图3: 3D手部可视化
        self.ax3 = self.fig.add_subplot(133, projection='3d')
        self.ax3.set_title('3D手部模型', fontsize=12)

        # 设置3D视图
        self.setup_3d_hand()

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, pady=10)

        self.fig.tight_layout()

    def setup_3d_hand(self):
        """设置3D手部模型"""
        # 清除3D图形
        self.ax3.clear()

        # 手部基础参数
        palm_width = 0.08
        palm_length = 0.12
        finger_length = 0.04

        # 创建手掌（半透明椭圆）
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi/4, 10)

        x_palm = palm_width * np.outer(np.cos(u), np.sin(v))
        y_palm = palm_length * np.outer(np.sin(u), np.sin(v)) * 0.5
        z_palm = palm_width * np.outer(np.ones(np.size(u)), np.cos(v)) * 0.3

        # 获取当前情绪颜色
        emotion_color = self.emotion_states[self.current_emotion]['color']
        rgb_color = self.hex_to_rgb(emotion_color)

        # 绘制手掌
        self.ax3.plot_surface(x_palm, y_palm, z_palm,
                             alpha=0.4, color=rgb_color,
                             linewidth=0, antialiased=True)

        # 绘制手指（简化表示）
        finger_positions = [
            [-0.04, 0.06, 0.02],  # 小指
            [-0.02, 0.08, 0.025], # 无名指
            [0, 0.09, 0.03],      # 中指
            [0.02, 0.08, 0.025],  # 食指
            [0.04, 0.06, 0.02]    # 大拇指
        ]

        for i, pos in enumerate(finger_positions):
            # 手指基座到指尖
            finger_x = [pos[0], pos[0]]
            finger_y = [pos[1], pos[1] + finger_length * (1 + 0.2 * np.sin(self.demo_time + i))]
            finger_z = [pos[2], pos[2] + 0.01]

            self.ax3.plot(finger_x, finger_y, finger_z,
                         color=rgb_color, linewidth=4,
                         alpha=0.8 + 0.2 * np.sin(self.demo_time + i))

            # 指尖
            self.ax3.scatter([finger_x[1]], [finger_y[1]], [finger_z[1]],
                           color=rgb_color, s=50, alpha=1.0)

        # 设置坐标轴
        self.ax3.set_xlim([-0.1, 0.1])
        self.ax3.set_ylim([-0.05, 0.15])
        self.ax3.set_zlim([-0.02, 0.08])
        self.ax3.set_xlabel('X')
        self.ax3.set_ylabel('Y')
        self.ax3.set_zlabel('Z')

        # 设置视角
        self.ax3.view_init(elev=20, azim=45)

        # 添加情绪标签
        emoji = self.emotion_states[self.current_emotion]['emoji']
        description = self.emotion_states[self.current_emotion]['description']
        self.ax3.text2D(0.5, 0.95, f'{emoji} {description}',
                       transform=self.ax3.transAxes,
                       fontsize=14, ha='center', weight='bold')

    def hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    def get_current_emotion(self):
        """根据时间获取当前情绪状态"""
        for start, end, emotion in self.emotion_schedule:
            if start <= self.demo_time < end:
                return emotion
        return 'Neutral'

    def generate_demo_signal(self):
        """生成模拟信号数据"""
        t = self.demo_time

        # 基础信号
        base_signal = 0.1 * np.sin(2 * np.pi * 10 * t)

        # 根据情绪状态添加特征
        if self.current_emotion == 'Stress':
            # 压力状态：高频成分增加
            base_signal += 0.3 * np.sin(2 * np.pi * 50 * t) + 0.1 * np.random.randn()
        elif self.current_emotion == 'Happy':
            # 开心状态：中等频率，规律性
            base_signal += 0.2 * np.sin(2 * np.pi * 20 * t)
        elif self.current_emotion == 'Focus':
            # 专注状态：低频，稳定
            base_signal += 0.15 * np.sin(2 * np.pi * 5 * t)
        elif self.current_emotion == 'Excited':
            # 兴奋状态：高频+低频混合
            base_signal += 0.25 * np.sin(2 * np.pi * 30 * t) + 0.15 * np.sin(2 * np.pi * 80 * t)

        # 添加噪声
        base_signal += 0.05 * np.random.randn()

        return np.clip(base_signal, -1, 1)

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 更新时间
        self.demo_time += 0.1

        # 获取当前情绪
        self.current_emotion = self.get_current_emotion()

        # 生成模拟信号
        signal = self.generate_demo_signal()
        self.signal_history.append(signal)

        # 更新情绪历史
        self.emotion_history.append(self.current_emotion)

        # 清除并重绘信号图
        self.ax1.clear()
        self.ax1.set_title('模拟信号波形', fontsize=12)
        self.ax1.set_xlabel('时间 (s)')
        self.ax1.set_ylabel('幅值')
        self.ax1.grid(True, alpha=0.3)

        if len(self.signal_history) > 0:
            time_axis = np.arange(len(self.signal_history)) * 0.1
            self.ax1.plot(time_axis, list(self.signal_history),
                         color=self.emotion_states[self.current_emotion]['color'],
                         linewidth=1.5, alpha=0.8)
            self.ax1.set_ylim(-1, 1)

        # 清除并重绘情绪时间线
        self.ax2.clear()
        self.ax2.set_title('情绪状态时间线', fontsize=12)
        self.ax2.set_xlabel('时间 (s)')
        self.ax2.set_ylabel('情绪状态')

        # 绘制情绪时间线
        if len(self.emotion_history) > 0:
            emotion_values = []
            emotion_colors = []
            for emotion in self.emotion_history:
                idx = list(self.emotion_states.keys()).index(emotion)
                emotion_values.append(idx)
                emotion_colors.append(self.emotion_states[emotion]['color'])

            time_axis = np.arange(len(emotion_values)) * 0.1
            self.ax2.scatter(time_axis, emotion_values,
                           c=emotion_colors, s=20, alpha=0.6)

            # 设置y轴标签
            self.ax2.set_yticks(range(len(self.emotion_states)))
            self.ax2.set_yticklabels(list(self.emotion_states.keys()))

        # 更新3D手部模型
        self.setup_3d_hand()

        # 更新状态文本
        self.update_status()

        # 更新进度条
        total_demo_time = 180  # 3分钟演示
        progress = min((self.demo_time / total_demo_time) * 100, 100)
        self.progress_var.set(progress)

        # 重置演示
        if self.demo_time >= total_demo_time:
            self.demo_time = 0
            self.emotion_history.clear()
            self.signal_history.clear()

        self.canvas.draw()

    def update_status(self):
        """更新状态信息"""
        self.status_text.delete(1.0, tk.END)

        emotion_info = self.emotion_states[self.current_emotion]
        status_info = f"""当前情绪: {emotion_info['emoji']} {emotion_info['description']}
置信度: {self.emotion_confidence:.2f}
演示时间: {self.demo_time:.1f}秒 / 180秒
状态: 演示运行中..."""

        self.status_text.insert(1.0, status_info)

    def start_demo(self):
        """开始演示"""
        if self.animation is None:
            self.is_running = True
            self.animation = FuncAnimation(self.fig, self.update_plots,
                                        interval=100, blit=False)
            self.canvas.draw()
            print("✅ 演示已开始")

    def stop_demo(self):
        """停止演示"""
        self.is_running = False
        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None
        print("⏸️ 演示已停止")

    def run(self):
        """运行应用"""
        def on_closing():
            self.stop_demo()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 演示版启动成功!")
        print("📋 功能说明:")
        print("   • 自动情绪状态转换 (平静→专注→开心→兴奋→压力)")
        print("   • 实时信号波形模拟")
        print("   • 3D手部模型可视化")
        print("   • 情绪状态时间线追踪")
        print("\n🎮 演示时长: 3分钟 (自动循环)")
        print("⏯️  使用控制按钮开始/停止演示")

        self.root.mainloop()

if __name__ == "__main__":
    app = DemoEmotionHand()
    app.run()