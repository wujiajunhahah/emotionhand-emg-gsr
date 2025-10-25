#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoWrist 3D手势识别可视化演示 (修复版)
带中文字体支持和生动3D手部模型
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.animation import FuncAnimation
import random
import platform

# 设置中文字体
def set_chinese_font():
    system = platform.system()
    if system == 'Darwin':  # macOS
        plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Arial Unicode MS', 'SimHei']
    elif system == 'Windows':
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False

set_chinese_font()

class EchoWrist3DDemo:
    def __init__(self):
        # 手势状态
        self.gestures = ['专注工作', '压力状态', '疲劳状态', '放松状态', '创意思考']
        self.current_gesture = '专注工作'
        self.confidence = 0.0
        self.time_step = 0

        # 创建图形
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('EchoWrist 3D手势识别实时演示', fontsize=18, fontweight='bold')

        # 创建子图
        self.ax_signal = self.fig.add_subplot(2, 4, 1)  # 信号波形
        self.ax_spectrum = self.fig.add_subplot(2, 4, 2)  # 频谱
        self.ax_hand_3d = self.fig.add_subplot(2, 4, 3)  # 3D手部
        self.ax_radar = self.fig.add_subplot(2, 4, 4, projection='polar')  # 雷达图
        self.ax_gesture_bar = self.fig.add_subplot(2, 4, 5)  # 手势概率条
        self.ax_confidence = self.fig.add_subplot(2, 4, 6)  # 置信度仪表
        self.ax_status = self.fig.add_subplot(2, 4, 7)  # 状态指示
        self.ax_timeline = self.fig.add_subplot(2, 4, 8)  # 时间线

    def create_3d_hand_model(self, gesture):
        """创建详细的3D手部模型"""
        # 手指关节定义
        fingers = {
            'thumb': [
                [0, 0, 0],      # 拇指根部
                [-1.5, 0, 2],    # 拇指第一关节
                [-2, 0, 3.5],    # 拇指第二关节
                [-1, 0, 4.5]     # 拇指指尖
            ],
            'index': [
                [0, 0, 0],      # 食指根部
                [2, 1, 0],      # 食指第一关节
                [3.5, 2, 0],    # 食指第二关节
                [4.5, 3, 0]     # 食指指尖
            ],
            'middle': [
                [0, 0, 0],      # 中指根部
                [2, -1, 0],     # 中指第一关节
                [3.5, -2.5, 0],  # 中指第二关节
                [4.5, -3.5, 0]   # 中指指尖
            ],
            'ring': [
                [0, 0, 0],      # 无名指根部
                [1.5, -2, 0],   # 无名指第一关节
                [2.5, -3, 0],   # 无名指第二关节
                [3, -4, 0]      # 无名指指尖
            ],
            'pinky': [
                [0, 0, 0],      # 小指根部
                [1, -2.5, 0],   # 小指第一关节
                [1.5, -3.5, 0], # 小指第二关节
                [2, -4.5, 0]    # 小指指尖
            ]
        }

        # 根据手势调整手部姿态
        if gesture == '专注工作':
            # 专注: 手指微曲，稳定
            for finger_name in fingers:
                finger = fingers[finger_name]
                for i in range(1, len(finger)):
                    finger[i][1] *= 0.7
                    finger[i][2] *= 0.8

        elif gesture == '压力状态':
            # 压力: 握拳
            for finger_name in fingers:
                finger = fingers[finger_name]
                for i in range(1, len(finger)):
                    finger[i][0] *= 0.6
                    finger[i][1] *= 0.4
                    finger[i][2] *= 0.5

        elif gesture == '疲劳状态':
            # 疲劳: 手部下垂
            for finger_name in fingers:
                finger = fingers[finger_name]
                for i in range(len(finger)):
                    finger[i][1] -= 1.5

        elif gesture == '放松状态':
            # 放松: 手指伸展
            for finger_name in fingers:
                finger = fingers[finger_name]
                for i in range(1, len(finger)):
                    finger[i][0] *= 1.3
                    finger[i][1] *= 1.1

        elif gesture == '创意思考':
            # 创意: 手部有活力
            for finger_name in fingers:
                finger = fingers[finger_name]
                for i in range(len(finger)):
                    finger[i][0] += np.sin(self.time_step * 0.1 + i) * 0.2
                    finger[i][1] += np.cos(self.time_step * 0.15 + i) * 0.15

        return fingers

    def draw_3d_hand(self, ax, fingers):
        """绘制3D手部模型"""
        # 手掌连接点
        palm_points = [
            fingers['thumb'][0],
            fingers['index'][0],
            fingers['middle'][0],
            fingers['ring'][0],
            fingers['pinky'][0]
        ]

        # 绘制手掌
        palm_x = [p[0] for p in palm_points]
        palm_y = [p[1] for p in palm_points]

        # 绘制手掌轮廓 (五边形)
        palm_polygon = plt.Polygon(list(zip(palm_x + [palm_x[0]], palm_y + [palm_y[0]])),
                                 fill=True, alpha=0.3, color='pink',
                                 edgecolor='red', linewidth=2)
        ax.add_patch(palm_polygon)

        # 绘制手指
        finger_colors = ['red', 'blue', 'green', 'orange', 'purple']

        finger_data = [
            (fingers['thumb'], finger_colors[0]),
            (fingers['index'], finger_colors[1]),
            (fingers['middle'], finger_colors[2]),
            (fingers['ring'], finger_colors[3]),
            (fingers['pinky'], finger_colors[4])
        ]

        for finger_points, color in finger_data:
            # 绘制手指线条
            x_coords = [p[0] for p in finger_points]
            y_coords = [p[1] for p in finger_points]
            ax.plot(x_coords, y_coords, color=color, linewidth=3, alpha=0.8)

            # 绘制关节点
            ax.scatter(x_coords, y_coords, c=color, s=80, alpha=0.9,
                      edgecolors='black', linewidth=1, zorder=5)

            # 指尖特殊标记
            ax.scatter(x_coords[-1], y_coords[-1], c=color, s=120,
                      marker='*', edgecolors='black', linewidth=1, zorder=6)

    def generate_acoustic_signal(self, gesture):
        """生成声纳信号"""
        t = np.linspace(0, 0.1, 500)

        if gesture == '专注工作':
            signal = 0.8 * np.sin(2 * np.pi * 40 * t) + \
                    0.1 * np.sin(2 * np.pi * 80 * t) + \
                    0.05 * np.random.randn(500)

        elif gesture == '压力状态':
            signal = 1.0 * np.sin(2 * np.pi * 40 * t) + \
                    0.4 * np.sin(2 * np.pi * 120 * t) + \
                    0.3 * np.sin(2 * np.pi * 200 * t) + \
                    0.15 * np.random.randn(500)

        elif gesture == '疲劳状态':
            envelope = 1.0 - 0.4 * np.sin(2 * np.pi * 2 * t)
            signal = envelope * np.sin(2 * np.pi * 40 * t) + \
                    0.08 * np.random.randn(500)

        elif gesture == '放松状态':
            signal = 0.6 * np.sin(2 * np.pi * 40 * t) + \
                    0.15 * np.sin(2 * np.pi * 60 * t) + \
                    0.05 * np.random.randn(500)

        elif gesture == '创意思考':
            signal = 0.7 * np.sin(2 * np.pi * 40 * t) + \
                    0.25 * np.sin(2 * np.pi * 80 * t) + \
                    0.15 * np.sin(2 * np.pi * 120 * t) + \
                    0.08 * np.random.randn(500)

        return t, signal

    def update_display(self, frame):
        """更新所有显示"""
        self.time_step += 1

        # 随机切换手势
        if random.random() < 0.02:
            self.current_gesture = random.choice(self.gestures)
            self.confidence = random.uniform(0.75, 0.95)

        # 平滑置信度
        target_conf = self.confidence
        self.confidence += (target_conf - self.confidence) * 0.1

        # 清除所有子图
        for ax in [self.ax_signal, self.ax_spectrum, self.ax_hand_3d, self.ax_radar,
                  self.ax_gesture_bar, self.ax_confidence, self.ax_status, self.ax_timeline]:
            ax.clear()

        # 1. 信号波形图
        t, signal = self.generate_acoustic_signal(self.current_gesture)
        self.ax_signal.plot(t * 1000, signal, 'b-', linewidth=1.5, alpha=0.8)
        self.ax_signal.fill_between(t * 1000, 0, signal, alpha=0.3, color='blue')
        self.ax_signal.set_title('声纳信号波形', fontsize=12, fontweight='bold')
        self.ax_signal.set_xlabel('时间 (ms)')
        self.ax_signal.set_ylabel('幅度')
        self.ax_signal.grid(True, alpha=0.3)
        self.ax_signal.set_ylim(-2, 2)

        # 2. 频谱图
        fft_data = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/40000)
        pos_freqs = freqs[:len(freqs)//2] / 1000
        pos_fft = np.abs(fft_data[:len(fft_data)//2])

        self.ax_spectrum.plot(pos_freqs[:200], pos_fft[:200], 'r-', linewidth=1.5, alpha=0.8)
        self.ax_spectrum.fill_between(pos_freqs[:200], 0, pos_fft[:200], alpha=0.3, color='red')
        self.ax_spectrum.set_title('频谱分析', fontsize=12, fontweight='bold')
        self.ax_spectrum.set_xlabel('频率 (kHz)')
        self.ax_spectrum.set_ylabel('幅度')
        self.ax_spectrum.grid(True, alpha=0.3)

        # 3. 3D手部模型
        fingers = self.create_3d_hand_model(self.current_gesture)
        self.draw_3d_hand(self.ax_hand_3d, fingers)
        self.ax_hand_3d.set_title('3D手部姿态', fontsize=12, fontweight='bold')
        self.ax_hand_3d.set_xlim(-3, 5)
        self.ax_hand_3d.set_ylim(-6, 2)
        self.ax_hand_3d.set_aspect('equal')
        self.ax_hand_3d.grid(True, alpha=0.3)

        # 4. 雷达图 (状态分布)
        angles = np.linspace(0, 2 * np.pi, len(self.gestures), endpoint=False)
        values = np.random.rand(len(self.gestures))
        current_idx = self.gestures.index(self.current_gesture)
        values[current_idx] = self.confidence
        values /= values.sum()

        self.ax_radar.plot(angles, values, 'o-', linewidth=2, markersize=8)
        self.ax_radar.fill(angles, values, alpha=0.25)
        self.ax_radar.set_xticks(angles)
        self.ax_radar.set_xticklabels(self.gestures, fontsize=8)
        self.ax_radar.set_ylim(0, 1)
        self.ax_radar.set_title('状态分布', fontsize=12, fontweight='bold')
        self.ax_radar.grid(True)

        # 5. 手势概率条
        probabilities = np.random.rand(len(self.gestures))
        probabilities[current_idx] = self.confidence
        probabilities /= probabilities.sum()

        bars = self.ax_gesture_bar.barh(self.gestures, probabilities,
                                        color='skyblue', alpha=0.7, edgecolor='black')
        bars[current_idx].set_color('orange')
        bars[current_idx].set_alpha(0.9)

        self.ax_gesture_bar.set_title('识别概率', fontsize=12, fontweight='bold')
        self.ax_gesture_bar.set_xlabel('概率')
        self.ax_gesture_bar.set_xlim(0, 1)

        # 6. 置信度仪表
        self.ax_confidence.set_title(f'置信度: {self.confidence:.1%}', fontsize=12, fontweight='bold')

        # 绘制仪表背景
        theta = np.linspace(0, np.pi, 100)
        r_inner = 0.3
        r_outer = 1.0
        self.ax_confidence.fill_between(theta, r_inner, r_outer, color='lightgray', alpha=0.3)

        # 绘制置信度弧
        confidence_theta = np.linspace(0, self.confidence * np.pi, 100)
        color = 'green' if self.confidence > 0.7 else 'orange'
        self.ax_confidence.fill_between(confidence_theta, r_inner, r_outer,
                                       color=color, alpha=0.8)

        self.ax_confidence.set_ylim(0, 1)
        self.ax_confidence.set_yticks([0.3, 1.0])
        self.ax_confidence.set_yticklabels(['0%', '100%'])
        self.ax_confidence.set_xticks([0, np.pi/2, np.pi])
        self.ax_confidence.set_xticklabels(['0%', '50%', '100%'])

        # 7. 状态指示器
        colors = {'专注工作': '#2ECC71', '压力状态': '#E74C3C', '疲劳状态': '#F39C12',
                 '放松状态': '#3498DB', '创意思考': '#9B59B6'}

        # 创建状态框
        status_box = FancyBboxPatch((0.1, 0.3), 0.8, 0.4,
                                  boxstyle="round,pad=0.1",
                                  facecolor=colors.get(self.current_gesture, 'gray'),
                                  alpha=0.3,
                                  edgecolor=colors.get(self.current_gesture, 'black'),
                                  linewidth=3,
                                  transform=self.ax_status.transAxes)
        self.ax_status.add_patch(status_box)

        self.ax_status.text(0.5, 0.7, '当前状态', transform=self.ax_status.transAxes,
                          fontsize=14, fontweight='bold', ha='center')
        self.ax_status.text(0.5, 0.5, self.current_gesture, transform=self.ax_status.transAxes,
                          fontsize=16, fontweight='bold', ha='center',
                          color=colors.get(self.current_gesture, 'black'))
        self.ax_status.text(0.5, 0.3, f'置信度: {self.confidence:.1%}', transform=self.ax_status.transAxes,
                          fontsize=12, ha='center')
        self.ax_status.set_xlim(0, 1)
        self.ax_status.set_ylim(0, 1)
        self.ax_status.axis('off')

        # 8. 时间线
        if not hasattr(self, 'timeline_gestures'):
            self.timeline_gestures = []
            self.timeline_confidences = []

        self.timeline_gestures.append(self.current_gesture)
        self.timeline_confidences.append(self.confidence)

        # 保持最近50个数据点
        if len(self.timeline_gestures) > 50:
            self.timeline_gestures = self.timeline_gestures[-50:]
            self.timeline_confidences = self.timeline_confidences[-50:]

        time_points = list(range(len(self.timeline_gestures)))
        colors_timeline = [colors.get(g, 'gray') for g in self.timeline_gestures]

        for i in range(len(time_points) - 1):
            if i < len(time_points) - 1:
                self.ax_timeline.plot(time_points[i:i+2], self.timeline_confidences[i:i+2],
                                   color=colors_timeline[i], linewidth=2, alpha=0.7)
            self.ax_timeline.scatter(time_points[i], self.timeline_confidences[i],
                                   c=colors_timeline[i], s=30, alpha=0.8)

        self.ax_timeline.set_title('状态时间线', fontsize=12, fontweight='bold')
        self.ax_timeline.set_xlabel('时间')
        self.ax_timeline.set_ylabel('置信度')
        self.ax_timeline.set_ylim(0, 1)
        self.ax_timeline.grid(True, alpha=0.3)

        plt.tight_layout()

    def run(self):
        """运行演示"""
        print("🚀 EchoWrist 3D手势识别演示启动!")
        print("=" * 60)
        print("📊 实时显示内容:")
        print("  • 声纳信号波形")
        print("  • 频谱分析")
        print("  • 3D手部模型 (详细手指关节)")
        print("  • 状态分布雷达图")
        print("  • 识别概率条形图")
        print("  • 置信度仪表盘")
        print("  • 彩色状态指示器")
        print("  • 历史时间线")
        print("=" * 60)
        print("🔄 每100毫秒更新")
        print("🎯 手势状态自动切换")
        print("⏹️  按Ctrl+C停止演示")
        print("=" * 60)

        # 创建动画
        anim = FuncAnimation(self.fig, self.update_display, interval=100,
                            blit=False, cache_frame_data=False)

        try:
            plt.show()
        except KeyboardInterrupt:
            print("\n👋 演示已停止")

def main():
    print("🎯 启动 EchoWrist 3D手势识别演示")
    demo = EchoWrist3DDemo()
    demo.run()

if __name__ == "__main__":
    main()