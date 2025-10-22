#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试版本 - 验证核心功能
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import warnings
warnings.filterwarnings('ignore')

# 设置字体
plt.rcParams['font.family'] = 'DejaVu Sans'

def test_3d_hand():
    """测试3D手部可视化"""
    print("🧪 测试3D手部可视化...")

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # 手部基础参数
    palm_width = 0.08
    palm_length = 0.12

    # 创建手掌
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi/4, 8)

    x_palm = palm_width * np.outer(np.cos(u), np.sin(v))
    y_palm = palm_length * np.outer(np.sin(u), np.sin(v)) * 0.5
    z_palm = palm_width * np.outer(np.ones(np.size(u)), np.cos(v)) * 0.3

    ax.plot_surface(x_palm, y_palm, z_palm,
                   alpha=0.4, color='blue',
                   linewidth=0, antialiased=True)

    # 绘制手指
    finger_positions = [
        [-0.04, 0.06, 0.02],
        [-0.02, 0.08, 0.025],
        [0, 0.09, 0.03],
        [0.02, 0.08, 0.025],
        [0.04, 0.06, 0.02]
    ]

    for i, pos in enumerate(finger_positions):
        finger_x = [pos[0], pos[0]]
        finger_y = [pos[1], pos[1] + 0.04]
        finger_z = [pos[2], pos[2] + 0.01]

        ax.plot(finger_x, finger_y, finger_z,
               color='red', linewidth=4, alpha=0.8)

        ax.scatter([finger_x[1]], [finger_y[1]], [finger_z[1]],
                  color='red', s=50, alpha=1.0)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D手部模型测试')

    # 设置视角
    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.savefig('/Users/wujiajun/Downloads/emotionhand-main/test_hand_3d.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ 3D手部模型测试完成，图像已保存")

def test_animation():
    """测试动画功能"""
    print("🧪 测试动画功能...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # 测试数据
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    line1, = ax1.plot(x, y)
    ax1.set_title('信号波形测试')
    ax1.set_xlabel('时间')
    ax1.set_ylabel('幅值')
    ax1.grid(True, alpha=0.3)

    # 情绪状态测试
    emotions = ['Neutral', 'Happy', 'Stress', 'Focus', 'Excited']
    colors = ['#808080', '#FFD700', '#FF6B6B', '#4ECDC4', '#FF1744']

    emotion_idx = 0

    def update(frame):
        nonlocal emotion_idx

        # 更新信号
        phase = frame * 0.1
        y_new = np.sin(x + phase)
        line1.set_ydata(y_new)

        # 更新情绪
        emotion_idx = (emotion_idx + 1) % len(emotions)
        ax2.clear()
        ax2.bar([0], [1], color=colors[emotion_idx], alpha=0.7)
        ax2.set_title(f'情绪状态: {emotions[emotion_idx]}')
        ax2.set_ylim(0, 1.2)
        ax2.set_xticks([])

        return line1,

    # 创建动画
    anim = FuncAnimation(fig, update, frames=50, interval=100, blit=False)

    plt.tight_layout()
    plt.savefig('/Users/wujiajun/Downloads/emotionhand-main/test_animation.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("✅ 动画功能测试完成，图像已保存")

def main():
    """主测试函数"""
    print("🚀 开始核心功能测试...")
    print()

    # 测试3D可视化
    test_3d_hand()
    print()

    # 测试动画
    test_animation()
    print()

    print("✅ 所有核心功能测试完成!")
    print("📁 测试图像已保存到项目目录")
    print()
    print("📋 测试结果:")
    print("   • test_hand_3d.png - 3D手部模型")
    print("   • test_animation.png - 动画功能")
    print()
    print("🎯 如果图像正常显示，说明核心功能工作正常")

if __name__ == "__main__":
    main()