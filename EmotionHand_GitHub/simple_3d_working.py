#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 最简单的3D手势演示
"""

import numpy as np
import matplotlib.pyplot as plt
import time

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei', 'PingFang SC', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def simple_3d_demo():
    """简单3D演示"""
    print("🎭 EmotionHand 3D手势演示")
    print("=" * 40)

    # 创建3D图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 手掌顶点
    palm_x = np.array([[-0.3, 0.3, 0.3, -0.3, -0.3, 0.3]])
    palm_y = np.array([[0.3, -0.3, -0.3], [-0.3, 0.3], [-0.3, -0.3]])
    palm_z = np.array([[0.2, 0.2, 0.2], [0.2, 0.2], [0.2, 0.2]])

    # 绘制手掌
    for i in range(len(palm_x)):
        for j in range(len(palm_x[i])):
            ax.plot([palm_x[i][j], palm_x[(i+1)%4][j]],
                   [palm_y[i][j], palm_y[(i+1)%4][j]],
                   [palm_z[i][j], palm_z[(i+1)%4][j]],
                   'b-', color='lightblue', linewidth=2)

    # 手指线
    finger_x = np.array([0, 0, 0, 0])
    finger_y = np.array([0, 0.2, 0.4, 0.5])
    finger_z = np.array([0.2, 0.4, 0.6, 0.8, 1.0])

    # 绘制手指
    for i in range(len(finger_x)):
        ax.plot(finger_x, finger_y, finger_z, 'ro-', linewidth=3, color='red', markersize=10)

    # 设置坐标轴
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.set_zlim([0, 1.5])

    # 设置标题和标签
    ax.set_title('EmotionHand 3D手势演示', fontsize=14, fontweight='bold')
    ax.set_xlabel('X轴', fontsize=12)
    ax.set_ylabel('Y轴', fontsize=12)
    ax.set_zlabel('Z轴', fontsize=12)

    # 设置视角
    ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simple_3d_demo()