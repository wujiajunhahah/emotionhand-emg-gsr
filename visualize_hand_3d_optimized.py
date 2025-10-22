#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D手部可视化优化版 - 根据情绪状态显示动态手部模型
修复了坐标轴和显示问题
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
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

class Hand3DVisualizer:
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EmotionHand - 3D手部可视化")
        self.root.geometry("1000x800")

        # 情绪状态定义
        self.emotion_states = {
            'Neutral': {'color': '#808080', 'emoji': '😐', 'description': '平静'},
            'Happy': {'color': '#FFD700', 'emoji': '😊', 'description': '开心'},
            'Stress': {'color': '#FF6B6B', 'emoji': '😰', 'description': '压力'},
            'Focus': {'color': '#4ECDC4', 'emoji': '🎯', 'description': '专注'},
            'Excited': {'color': '#FF1744', 'emoji': '🤩', 'description': '兴奋'}
        }

        # 当前状态
        self.current_emotion = 'Neutral'
        self.emotion_confidence = 0.5

        # 动画相关
        self.animation = None
        self.is_running = False
        self.start_time = time.time()
        self.frame_count = 0

        # 设置界面
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame, text="EmotionHand 3D手部可视化",
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

        # 创建3D图形
        self.setup_3d_plot(main_frame)

        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(control_frame, text="开始可视化",
                                   command=self.start_visualization)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="停止可视化",
                                  command=self.stop_visualization,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 信息显示
        info_frame = ttk.LabelFrame(main_frame, text="手部状态说明", padding=10)
        info_frame.pack(fill=tk.X, pady=5)

        info_text = """🖐️ 手部动作说明：
• 平静: 手指自然伸展
• 开心: 手指微微弯曲，手掌放松
• 压力: 手指蜷缩，手掌紧张
• 专注: 食指伸展，其他手指微曲
• 兴奋: 手指完全伸展，动作幅度大"""

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack()

    def setup_3d_plot(self, parent):
        """设置3D图形"""
        # 创建matplotlib图形
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')

        # 设置初始视角
        self.ax.view_init(elev=20, azim=45)

        # 嵌入到tkinter
        self.canvas = plt.get_current_fig_manager().canvas
        self.canvas.get_tk_widget = lambda: self.canvas.get_tk_widget()

        # 使用FigureCanvasTkAgg正确嵌入
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_hand_model(self, emotion, frame_count):
        """创建手部模型"""
        # 清除之前的图形
        self.ax.clear()

        # 手部基础参数 (单位：米)
        palm_width = 0.08
        palm_length = 0.10
        palm_thickness = 0.02

        # 获取情绪颜色
        emotion_info = self.emotion_states.get(emotion, self.emotion_states['Neutral'])
        base_color = emotion_info['color']
        rgb_color = self.hex_to_rgb(base_color)

        # 绘制手掌
        self.draw_palm(palm_width, palm_length, palm_thickness, rgb_color, emotion, frame_count)

        # 绘制手指
        self.draw_fingers(emotion, frame_count, rgb_color)

        # 设置坐标轴
        self.ax.set_xlim([-0.15, 0.15])
        self.ax.set_ylim([-0.05, 0.20])
        self.ax.set_zlim([-0.05, 0.10])
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_zlabel('Z (m)')

        # 设置标题
        self.ax.set_title(f'3D手部模型 - {emotion_info["emoji"]} {emotion_info["description"]}',
                         fontsize=14, fontweight='bold')

        # 添加情绪标签
        self.ax.text2D(0.5, 0.95, f'{emotion_info["emoji"]} {emotion}',
                      transform=self.ax.transAxes,
                      fontsize=16, ha='center', weight='bold',
                      color=base_color)

    def draw_palm(self, width, length, thickness, color, emotion, frame_count):
        """绘制手掌"""
        # 创建手掌网格
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi/3, 10)

        # 根据情绪调整手掌形状
        emotion_factor = self.get_emotion_factor(emotion)

        # 手掌表面
        x_palm = width * np.outer(np.cos(u), np.sin(v)) * emotion_factor['palm_width']
        y_palm = length * np.outer(np.sin(u), np.sin(v)) * 0.5
        z_palm = thickness * np.outer(np.ones(np.size(u)), np.cos(v))

        # 添加动态效果
        z_offset = 0.002 * np.sin(frame_count * 0.1)
        z_palm += z_offset

        # 绘制手掌
        self.ax.plot_surface(x_palm, y_palm, z_palm,
                            alpha=0.6, color=color,
                            linewidth=0, antialiased=True,
                            shade=True)

    def draw_fingers(self, emotion, frame_count, color):
        """绘制手指"""
        # 手指基础参数
        finger_length = 0.04
        finger_spacing = 0.015

        # 获取情绪因子
        emotion_factor = self.get_emotion_factor(emotion)

        # 手指位置和状态
        fingers_config = [
            {'name': '小指', 'x': -0.025, 'y': 0.08, 'base_angle': -30},
            {'name': '无名指', 'x': -0.012, 'y': 0.09, 'base_angle': -15},
            {'name': '中指', 'x': 0, 'y': 0.10, 'base_angle': 0},
            {'name': '食指', 'x': 0.012, 'y': 0.09, 'base_angle': 15},
            {'name': '大拇指', 'x': 0.025, 'y': 0.06, 'base_angle': 45}
        ]

        for i, finger in enumerate(fingers_config):
            # 根据情绪调整手指状态
            if emotion == 'Stress':
                # 压力：手指蜷缩
                extension = finger_length * 0.3
                angle = finger['base_angle'] + 45
            elif emotion == 'Excited':
                # 兴奋：手指伸展
                extension = finger_length * 1.2
                angle = finger['base_angle'] + np.sin(frame_count * 0.1 + i) * 10
            elif emotion == 'Focus':
                # 专注：食指伸展，其他微曲
                if finger['name'] == '食指':
                    extension = finger_length * 1.1
                else:
                    extension = finger_length * 0.6
                angle = finger['base_angle']
            elif emotion == 'Happy':
                # 开心：自然微曲
                extension = finger_length * 0.9
                angle = finger['base_angle'] + 10
            else:  # Neutral
                # 平静：自然伸展
                extension = finger_length * 0.8
                angle = finger['base_angle']

            # 计算手指位置
            angle_rad = np.radians(angle)
            finger_end_x = finger['x'] + extension * np.sin(angle_rad) * 0.3
            finger_end_y = finger['y'] + extension * np.cos(angle_rad)
            finger_end_z = 0.01 + 0.005 * np.sin(frame_count * 0.1 + i)

            # 绘制手指
            finger_x = [finger['x'], finger_end_x]
            finger_y = [finger['y'], finger_end_y]
            finger_z = [0.01, finger_end_z]

            self.ax.plot(finger_x, finger_y, finger_z,
                        color=color, linewidth=6,
                        alpha=0.9, solid_capstyle='round')

            # 绘制关节
            self.ax.scatter([finger['x']], [finger['y']], [0.01],
                          color=color, s=80, alpha=1.0)
            self.ax.scatter([finger_end_x], [finger_end_y], [finger_end_z],
                          color=color, s=60, alpha=1.0)

    def get_emotion_factor(self, emotion):
        """获取情绪相关的调整因子"""
        factors = {
            'Neutral': {'palm_width': 1.0, 'finger_extension': 0.8},
            'Happy': {'palm_width': 1.1, 'finger_extension': 0.9},
            'Stress': {'palm_width': 0.8, 'finger_extension': 0.3},
            'Focus': {'palm_width': 0.95, 'finger_extension': 0.7},
            'Excited': {'palm_width': 1.2, 'finger_extension': 1.2}
        }
        return factors.get(emotion, factors['Neutral'])

    def hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    def get_demo_emotion(self):
        """获取演示模式的情绪状态"""
        current_time = time.time() - self.start_time
        emotion_cycle_time = 25  # 25秒一个周期
        phase = (current_time % emotion_cycle_time) / emotion_cycle_time

        if phase < 0.2:
            return 'Neutral'
        elif phase < 0.4:
            return 'Focus'
        elif phase < 0.6:
            return 'Happy'
        elif phase < 0.8:
            return 'Excited'
        else:
            return 'Stress'

    def update_visualization(self, frame):
        """更新可视化"""
        if not self.is_running:
            return

        self.frame_count += 1

        # 获取当前情绪
        if self.demo_mode:
            self.current_emotion = self.get_demo_emotion()
        else:
            # 这里应该从情绪检测器获取情绪
            self.current_emotion = self.get_demo_emotion()

        # 更新置信度（模拟）
        self.emotion_confidence = 0.7 + 0.2 * np.random.random()

        # 更新手部模型
        self.create_hand_model(self.current_emotion, self.frame_count)

        # 更新状态标签
        emotion_info = self.emotion_states.get(self.current_emotion, self.emotion_states['Neutral'])
        self.emotion_label.config(
            text=f"{emotion_info['emoji']} {self.current_emotion} - 置信度: {self.emotion_confidence:.2f}"
        )

        # 刷新画布
        self.canvas.draw()

    def start_visualization(self):
        """开始可视化"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.frame_count = 0
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # 创建动画 - 从matplotlib.animation导入
            from matplotlib.animation import FuncAnimation
            self.animation = FuncAnimation(self.fig, self.update_visualization,
                                         interval=100, blit=False)
            self.canvas.draw()

            print("✅ 开始3D手部可视化")

    def stop_visualization(self):
        """停止可视化"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            if self.animation is not None:
                self.animation.event_source.stop()
                self.animation = None

            print("⏹️ 停止3D可视化")

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_visualization()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 3D手部可视化器启动")
        print(f"🎨 当前模式: {'演示模式' if self.demo_mode else '实时模式'}")
        print("📋 使用说明:")
        print("   • 点击'开始可视化'启动3D手部动画")
        print("   • 观察不同情绪状态下的手部动作变化")
        if self.demo_mode:
            print("   • 演示模式会自动切换情绪状态")

        self.root.mainloop()

if __name__ == "__main__":
    # 默认使用演示模式
    visualizer = Hand3DVisualizer(demo_mode=True)
    visualizer.run()