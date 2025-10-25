#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoWrist手势识别可视化演示
实时显示手势状态识别效果
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.gridspec import GridSpec
import time
import random
from datetime import datetime

class EchoWristGestureDemo:
    def __init__(self):
        # 初始化图形界面
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('EchoWrist 手势识别实时演示', fontsize=20, fontweight='bold')

        # 创建网格布局
        gs = GridSpec(3, 4, figure=self.fig, hspace=0.3, wspace=0.3)

        # 子图布局
        self.ax_waveform = self.fig.add_subplot(gs[0, :2])  # 原始波形
        self.ax_spectrum = self.fig.add_subplot(gs[1, :2])  # 频谱分析
        self.ax_range_doppler = self.fig.add_subplot(gs[2, :2])  # Range-Doppler图
        self.ax_hand_3d = self.fig.add_subplot(gs[0, 2:])  # 3D手部模型
        self.ax_gesture = self.fig.add_subplot(gs[1, 2:])  # 手势分类
        self.ax_confidence = self.fig.add_subplot(gs[2, 2:])  # 置信度

        # 初始化数据
        self.time_data = np.linspace(0, 1, 1000)
        self.sampling_rate = 40000  # 40kHz
        self.current_time = 0

        # 手势状态定义
        self.gesture_states = [
            '专注工作', '压力状态', '疲劳状态', '放松状态',
            '创意思考', '会议状态', '休息状态', '准备工作'
        ]

        self.current_gesture = '专注工作'
        self.current_confidence = 0.0
        self.target_confidence = 0.0

        # 历史数据
        self.gesture_history = []
        self.confidence_history = []
        self.max_history = 100

        # 手部3D模型点
        self.hand_joints = self.generate_hand_joints()

        # 初始化所有图形元素
        self.setup_plots()

    def generate_hand_joints(self):
        """生成手部3D关节点"""
        # 简化的手部模型 (主要关节)
        joints = np.array([
            [0, 0, 0],      # 手腕
            [2, 1, 0],      # 食指根部
            [4, 2, 0],      # 食指中段
            [5, 3, 0],      # 食指指尖
            [2, -1, 0],     # 中指根部
            [4, -2, 0],     # 中指中段
            [5, -3, 0],     # 中指指尖
            [-2, -1, 0],    # 无名指根部
            [-4, -2, 0],    # 无名指中段
            [-5, -3, 0],    # 无名指指尖
            [-2, 1, 0],     # 小指根部
            [-3, 2, 0],     # 小指中段
            [-4, 3, 0],     # 小指指尖
            [-3, 0, 1],     # 拇指根部
            [-2, 0, 2],     # 拇指中段
            [-1, 0, 3],     # 拇指指尖
        ])
        return joints

    def setup_plots(self):
        """设置所有子图"""
        # 波形图
        self.ax_waveform.set_title('声纳信号波形', fontsize=14, fontweight='bold')
        self.ax_waveform.set_xlabel('时间 (ms)')
        self.ax_waveform.set_ylabel('幅度')
        self.ax_waveform.grid(True, alpha=0.3)
        self.ax_waveform.set_ylim(-2, 2)

        # 频谱图
        self.ax_spectrum.set_title('频谱分析 (FFT)', fontsize=14, fontweight='bold')
        self.ax_spectrum.set_xlabel('频率 (kHz)')
        self.ax_spectrum.set_ylabel('幅度')
        self.ax_spectrum.grid(True, alpha=0.3)
        self.ax_spectrum.set_xlim(0, 20)

        # Range-Doppler图
        self.ax_range_doppler.set_title('Range-Doppler 回波图', fontsize=14, fontweight='bold')
        self.ax_range_doppler.set_xlabel('多普勒频率')
        self.ax_range_doppler.set_ylabel('距离')

        # 3D手部模型
        self.ax_hand_3d.set_title('3D手部姿态', fontsize=14, fontweight='bold')
        self.ax_hand_3d.set_xlim(-6, 6)
        self.ax_hand_3d.set_ylim(-4, 4)
        self.ax_hand_3d.set_aspect('equal')
        self.ax_hand_3d.grid(True, alpha=0.3)

        # 手势分类结果
        self.ax_gesture.set_title('手势识别结果', fontsize=14, fontweight='bold')
        self.ax_gesture.axis('off')

        # 置信度显示
        self.ax_confidence.set_title('识别置信度', fontsize=14, fontweight='bold')
        self.ax_confidence.set_xlim(0, 1)
        self.ax_confidence.set_ylim(0, 1)
        self.ax_confidence.set_xlabel('置信度')
        self.ax_confidence.set_xticks([0, 0.25, 0.5, 0.75, 1])
        self.ax_confidence.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])

    def generate_acoustic_signal(self, gesture):
        """根据手势状态生成模拟声纳信号"""
        t = self.time_data

        if gesture == '专注工作':
            # 专注: 稳定的低频信号
            signal = 0.8 * np.sin(2 * np.pi * 40 * t) + \
                    0.2 * np.sin(2 * np.pi * 120 * t) + \
                    0.05 * np.random.randn(len(t))

        elif gesture == '压力状态':
            # 压力: 高频不稳定信号
            signal = 1.0 * np.sin(2 * np.pi * 40 * t) + \
                    0.5 * np.sin(2 * np.pi * 200 * t) + \
                    0.3 * np.sin(2 * np.pi * 500 * t) + \
                    0.2 * np.random.randn(len(t))

        elif gesture == '疲劳状态':
            # 疲劳: 低频缓慢变化
            envelope = 1.0 - 0.3 * np.sin(2 * np.pi * 0.5 * t)
            signal = envelope * np.sin(2 * np.pi * 40 * t) + \
                    0.1 * np.random.randn(len(t))

        elif gesture == '放松状态':
            # 放松: 平滑的低频信号
            signal = 0.6 * np.sin(2 * np.pi * 40 * t) + \
                    0.1 * np.sin(2 * np.pi * 80 * t) + \
                    0.05 * np.random.randn(len(t))

        elif gesture == '创意思考':
            # 创意: 复杂多频信号
            signal = 0.7 * np.sin(2 * np.pi * 40 * t) + \
                    0.3 * np.sin(2 * np.pi * 60 * t) + \
                    0.2 * np.sin(2 * np.pi * 100 * t) + \
                    0.1 * np.random.randn(len(t))

        else:
            # 默认状态
            signal = 0.5 * np.sin(2 * np.pi * 40 * t) + \
                    0.1 * np.random.randn(len(t))

        return signal

    def generate_spectrum(self, signal):
        """生成频谱数据"""
        fft_result = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/self.sampling_rate)

        # 只取正频率部分
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = np.abs(fft_result[:len(fft_result)//2])

        # 转换为kHz
        freqs_khz = positive_freqs / 1000

        return freqs_khz[:2000], positive_fft[:2000]  # 只显示前20kHz

    def generate_range_doppler(self, gesture):
        """生成Range-Doppler图"""
        size = 50

        if gesture == '专注工作':
            # 专注: 集中的回波
            rd_map = np.zeros((size, size))
            rd_map[20:30, 20:30] = 0.8
            rd_map[15:35, 15:35] = 0.4

        elif gesture == '压力状态':
            # 压力: 分散的回波
            rd_map = np.random.rand(size, size) * 0.3
            rd_map[10:20, 10:40] = 0.6
            rd_map[30:40, 10:40] = 0.6

        elif gesture == '疲劳状态':
            # 疲劳: 微弱的回波
            rd_map = np.random.rand(size, size) * 0.2
            rd_map[22:28, 22:28] = 0.4

        else:
            # 其他状态
            rd_map = np.random.rand(size, size) * 0.3
            rd_map[size//2-5:size//2+5, size//2-5:size//2+5] = 0.6

        return rd_map

    def update_hand_pose(self, gesture):
        """根据手势更新手部姿态"""
        base_joints = self.hand_joints.copy()

        if gesture == '专注工作':
            # 专注: 手部稳定，手指微曲
            base_joints[1:4, 1] -= 0.5  # 食指弯曲
            base_joints[4:7, 1] -= 0.3  # 中指弯曲
            base_joints += np.random.randn(*base_joints.shape) * 0.05

        elif gesture == '压力状态':
            # 压力: 握拳姿态
            base_joints[1:13, 0] *= 0.7  # 手指收缩
            base_joints[1:13, 1] *= 0.5
            base_joints += np.random.randn(*base_joints.shape) * 0.1

        elif gesture == '疲劳状态':
            # 疲劳: 手部下垂
            base_joints[:, 1] -= 1.0
            base_joints += np.random.randn(*base_joints.shape) * 0.15

        elif gesture == '放松状态':
            # 放松: 手部张开
            base_joints[1:13, 0] *= 1.2  # 手指伸展
            base_joints[13:16, 2] += 1.0  # 拇指展开
            base_joints += np.random.randn(*base_joints.shape) * 0.08

        elif gesture == '创意思考':
            # 创意: 手部活动频繁
            movement = np.sin(self.current_time * 2) * 0.3
            base_joints[:, 0] += movement
            base_joints[:, 2] += np.cos(self.current_time * 3) * 0.2
            base_joints += np.random.randn(*base_joints.shape) * 0.12

        return base_joints

    def update_gesture_probability(self):
        """更新手势识别概率"""
        # 模拟识别过程
        if random.random() < 0.02:  # 2%概率切换手势
            self.current_gesture = random.choice(self.gesture_states)
            self.target_confidence = random.uniform(0.7, 0.95)

        # 平滑置信度变化
        self.current_confidence += (self.target_confidence - self.current_confidence) * 0.1

        # 生成所有手势的概率分布
        probabilities = np.random.rand(len(self.gesture_states))
        probabilities /= probabilities.sum()

        # 提高当前手势的概率
        current_idx = self.gesture_states.index(self.current_gesture)
        probabilities[current_idx] = self.current_confidence
        probabilities /= probabilities.sum()

        return probabilities

    def animate(self, frame):
        """动画更新函数"""
        self.current_time += 0.05

        # 清除所有子图
        self.ax_waveform.clear()
        self.ax_spectrum.clear()
        self.ax_range_doppler.clear()
        self.ax_hand_3d.clear()
        self.ax_gesture.clear()
        self.ax_confidence.clear()

        # 重新设置标题和标签
        self.setup_plots()

        # 生成当前手势的信号
        signal = self.generate_acoustic_signal(self.current_gesture)

        # 绘制波形图
        time_ms = self.time_data * 1000  # 转换为毫秒
        self.ax_waveform.plot(time_ms[:200], signal[:200], 'b-', linewidth=1.5)
        self.ax_waveform.fill_between(time_ms[:200], 0, signal[:200], alpha=0.3)

        # 绘制频谱图
        freqs, spectrum = self.generate_spectrum(signal)
        self.ax_spectrum.plot(freqs, spectrum, 'r-', linewidth=1.5)
        self.ax_spectrum.fill_between(freqs, 0, spectrum, alpha=0.3, color='red')

        # 绘制Range-Doppler图
        rd_map = self.generate_range_doppler(self.current_gesture)
        im = self.ax_range_doppler.imshow(rd_map, cmap='viridis', aspect='auto',
                                         extent=[-25, 25, 0, 50], vmin=0, vmax=1)

        # 绘制3D手部姿态
        hand_pose = self.update_hand_pose(self.current_gesture)

        # 绘制手部连接线
        connections = [
            [0, 1], [1, 2], [2, 3],  # 食指
            [0, 4], [4, 5], [5, 6],  # 中指
            [0, 7], [7, 8], [8, 9],  # 无名指
            [0, 10], [10, 11], [11, 12],  # 小指
            [0, 13], [13, 14], [14, 15],  # 拇指
            [1, 4], [4, 7], [7, 10]  # 手掌
        ]

        for connection in connections:
            start = hand_pose[connection[0]]
            end = hand_pose[connection[1]]
            self.ax_hand_3d.plot([start[0], end[0]], [start[1], end[1]],
                               [start[2], end[2]], 'b-', linewidth=2)

        # 绘制关节点
        colors = ['red'] + ['blue'] * 15  # 手腕红色，其他蓝色
        for i, (joint, color) in enumerate(zip(hand_pose, colors)):
            self.ax_hand_3d.scatter(joint[0], joint[1], joint[2],
                                  c=color, s=50, alpha=0.8)

        # 更新手势识别结果
        probabilities = self.update_gesture_probability()

        # 绘制手势概率条形图
        y_pos = np.arange(len(self.gesture_states))
        bars = self.ax_gesture.barh(y_pos, probabilities, color='skyblue', alpha=0.7)

        # 高亮当前识别的手势
        current_idx = self.gesture_states.index(self.current_gesture)
        bars[current_idx].set_color('orange')
        bars[current_idx].set_alpha(0.9)

        self.ax_gesture.set_yticks(y_pos)
        self.ax_gesture.set_yticklabels(self.gesture_states)
        self.ax_gesture.set_xlabel('概率')
        self.ax_gesture.set_xlim(0, 1)

        # 添加当前识别结果文本
        result_text = f"识别结果: {self.current_gesture}\n置信度: {self.current_confidence:.1%}"
        self.ax_gesture.text(0.5, 0.95, result_text, transform=self.ax_gesture.transAxes,
                          fontsize=12, fontweight='bold', ha='center', va='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # 绘制置信度条
        self.ax_confidence.barh(0.5, self.current_confidence, height=0.3,
                               color='green', alpha=0.7)
        self.ax_confidence.barh(0.5, 1.0, height=0.3, color='lightgray', alpha=0.3)

        # 添加置信度文本
        conf_text = f"{self.current_confidence:.1%}"
        self.ax_confidence.text(0.5, 0.5, conf_text, transform=self.ax_confidence.transAxes,
                              fontsize=16, fontweight='bold', ha='center', va='center')

        # 添加时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.fig.text(0.02, 0.02, f"更新时间: {timestamp}", fontsize=10,
                     transform=self.fig.transFigure)

        return []

    def run(self):
        """运行动画"""
        print("🚀 EchoWrist 手势识别演示启动!")
        print("=" * 50)
        print("📊 实时显示内容:")
        print("  • 声纳信号波形")
        print("  • 频谱分析 (FFT)")
        print("  • Range-Doppler 回波图")
        print("  • 3D手部姿态")
        print("  • 手势分类结果")
        print("  • 识别置信度")
        print("=" * 50)
        print("⚡ 每50毫秒更新一次")
        print("🔄 手势状态自动切换演示")
        print("=" * 50)
        print("按 Ctrl+C 停止演示")
        print()

        # 创建动画
        ani = animation.FuncAnimation(self.fig, self.animate, interval=50,
                                    blit=False, cache_frame_data=False)

        plt.show()

def main():
    """主函数"""
    print("🎯 启动 EchoWrist 手势识别可视化演示")
    print("正在初始化...")

    # 创建演示实例
    demo = EchoWristGestureDemo()

    # 运行演示
    try:
        demo.run()
    except KeyboardInterrupt:
        print("\n👋 演示已停止")
    except Exception as e:
        print(f"❌ 运行出错: {e}")

if __name__ == "__main__":
    main()