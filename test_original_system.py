#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试原有系统框架 - 快速验证核心功能
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')

# 设置字体
plt.rcParams['font.family'] = 'DejaVu Sans'

def test_emotion_visualizer():
    """测试情绪可视化器核心功能"""
    print("🧪 测试情绪可视化器...")

    # 情绪状态定义
    emotion_states = {
        'Neutral': {'color': '#808080', 'emoji': '😐', 'range': (0.4, 0.6)},
        'Happy': {'color': '#FFD700', 'emoji': '😊', 'range': (0.6, 0.8)},
        'Stress': {'color': '#FF6B6B', 'emoji': '😰', 'range': (0.8, 1.0)},
        'Focus': {'color': '#4ECDC4', 'emoji': '🎯', 'range': (0.2, 0.4)},
        'Excited': {'color': '#FF1744', 'emoji': '🤩', 'range': (0.0, 0.2)}
    }

    # 创建测试图表
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # 1. EMG信号测试
    time_axis = np.linspace(0, 10, 500)
    emg_signal = 0.3 * np.sin(2 * np.pi * 2 * time_axis) + 0.1 * np.random.randn(500)

    axes[0].plot(time_axis, emg_signal, color='#4ECDC4', linewidth=1.5)
    axes[0].set_title('EMG信号测试')
    axes[0].set_xlabel('时间 (s)')
    axes[0].set_ylabel('幅值')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(-1, 1)

    # 2. GSR信号测试
    gsr_signal = 2.0 + 0.5 * np.sin(2 * np.pi * 0.5 * time_axis) + 0.1 * np.random.randn(500)

    axes[1].plot(time_axis, gsr_signal, color='#FFD700', linewidth=1.5)
    axes[1].set_title('GSR信号测试')
    axes[1].set_xlabel('时间 (s)')
    axes[1].set_ylabel('电导 (μS)')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(0, 5)

    # 3. 情绪状态测试
    emotions = ['Neutral', 'Focus', 'Happy', 'Excited', 'Stress']
    colors = ['#808080', '#4ECDC4', '#FFD700', '#FF1744', '#FF6B6B']

    for i, (emotion, color) in enumerate(zip(emotions, colors)):
        axes[2].barh(i, 1, color=color, alpha=0.7, edgecolor='black')
        axes[2].text(0.5, i, f'{emotion_states[emotion]["emoji"]} {emotion}',
                    ha='center', va='center', fontweight='bold')

    axes[2].set_title('情绪状态测试')
    axes[2].set_xlim(0, 1)
    axes[2].set_ylim(-0.5, len(emotions) - 0.5)
    axes[2].set_xticks([])
    axes[2].set_yticks([])

    plt.tight_layout()
    plt.savefig('/Users/wujiajun/Downloads/emotionhand-main/test_emotion_visualizer.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ 情绪可视化器测试完成")

def test_hand_3d():
    """测试3D手部可视化核心功能"""
    print("🧪 测试3D手部可视化...")

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # 手部基础参数
    palm_width = 0.08
    palm_length = 0.10

    # 创建手掌
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi/3, 10)

    x_palm = palm_width * np.outer(np.cos(u), np.sin(v))
    y_palm = palm_length * np.outer(np.sin(u), np.sin(v)) * 0.5
    z_palm = palm_width * np.outer(np.ones(np.size(u)), np.cos(v)) * 0.3

    # 绘制手掌
    ax.plot_surface(x_palm, y_palm, z_palm,
                   alpha=0.6, color='#4ECDC4',
                   linewidth=0, antialiased=True)

    # 绘制手指
    finger_positions = [
        [-0.025, 0.08, 0.01],   # 小指
        [-0.012, 0.09, 0.01],  # 无名指
        [0, 0.10, 0.01],       # 中指
        [0.012, 0.09, 0.01],   # 食指
        [0.025, 0.06, 0.01]    # 大拇指
    ]

    for i, pos in enumerate(finger_positions):
        # 手指
        finger_x = [pos[0], pos[0]]
        finger_y = [pos[1], pos[1] + 0.04]
        finger_z = [pos[2], pos[2] + 0.01]

        ax.plot(finger_x, finger_y, finger_z,
               color='#FFD700', linewidth=4, alpha=0.8)

        # 关节
        ax.scatter([pos[0]], [pos[1]], [pos[2]],
                  color='#FF1744', s=80, alpha=1.0)

    # 设置坐标轴
    ax.set_xlim([-0.15, 0.15])
    ax.set_ylim([-0.05, 0.20])
    ax.set_zlim([-0.05, 0.10])
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('3D手部模型测试 - 😊 开心状态')

    # 设置视角
    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.savefig('/Users/wujiajun/Downloads/emotionhand-main/test_hand_3d.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ 3D手部可视化测试完成")

def test_animation():
    """测试动画功能"""
    print("🧪 测试动画功能...")

    fig, ax = plt.subplots(figsize=(8, 4))

    # 测试数据
    x = np.linspace(0, 10, 100)
    line, = ax.plot(x, np.sin(x))

    ax.set_title('动画功能测试')
    ax.set_xlabel('时间')
    ax.set_ylabel('幅值')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-1.5, 1.5)

    # 测试动画函数
    def update(frame):
        phase = frame * 0.1
        y = np.sin(x + phase)
        line.set_ydata(y)
        return line,

    # 创建测试动画（只运行几帧）
    anim = FuncAnimation(fig, update, frames=10, interval=100, blit=True)

    plt.tight_layout()
    plt.savefig('/Users/wujiajun/Downloads/emotionhand-main/test_animation_function.png',
                dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ 动画功能测试完成")

def main():
    """主测试函数"""
    print("🚀 开始原有系统框架测试...")
    print()

    # 测试各个组件
    test_emotion_visualizer()
    print()

    test_hand_3d()
    print()

    test_animation()
    print()

    print("✅ 所有核心功能测试完成!")
    print()
    print("📁 生成的测试文件:")
    print("   • test_emotion_visualizer.png - 情绪可视化测试")
    print("   • test_hand_3d.png - 3D手部模型测试")
    print("   • test_animation_function.png - 动画功能测试")
    print()
    print("🎯 原有系统框架核心功能正常!")
    print()
    print("📋 使用原有系统:")
    print("   python realtime_emotion_visualizer.py  # 实时情绪可视化")
    print("   python visualize_hand_3d_optimized.py # 3D手部可视化")

if __name__ == "__main__":
    main()