#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoWrist简化版手势识别演示
轻量级版本，运行更快
"""

import numpy as np
import matplotlib.pyplot as plt
import random
import time

class SimpleEchoWristDemo:
    def __init__(self):
        # 手势状态
        self.gestures = ['专注工作', '压力状态', '疲劳状态', '放松状态', '创意思考']
        self.current_gesture = '专注工作'
        self.confidence = 0.0

        # 创建图形
        plt.figure(figsize=(14, 8))
        plt.suptitle('EchoWrist 手势识别演示', fontsize=16, fontweight='bold')

        # 创建子图
        self.ax1 = plt.subplot(2, 3, 1)  # 波形
        self.ax2 = plt.subplot(2, 3, 2)  # 频谱
        self.ax3 = plt.subplot(2, 3, 3)  # 手部姿态
        self.ax4 = plt.subplot(2, 3, 4)  # 手势分类
        self.ax5 = plt.subplot(2, 3, 5)  # 置信度
        self.ax6 = plt.subplot(2, 3, 6)  # 状态指示

    def generate_signal(self, gesture):
        """生成模拟信号"""
        t = np.linspace(0, 0.1, 500)

        if gesture == '专注工作':
            signal = 0.8 * np.sin(2*np.pi*40*t) + 0.1 * np.random.randn(500)
        elif gesture == '压力状态':
            signal = 1.0 * np.sin(2*np.pi*40*t) + 0.3 * np.sin(2*np.pi*200*t) + 0.2 * np.random.randn(500)
        elif gesture == '疲劳状态':
            signal = 0.5 * np.sin(2*np.pi*40*t) * (1 - 0.3*np.sin(2*np.pi*5*t)) + 0.1 * np.random.randn(500)
        elif gesture == '放松状态':
            signal = 0.6 * np.sin(2*np.pi*40*t) + 0.05 * np.random.randn(500)
        else:  # 创意思考
            signal = 0.7 * np.sin(2*np.pi*40*t) + 0.2 * np.sin(2*np.pi*80*t) + 0.1 * np.random.randn(500)

        return t, signal

    def update_display(self):
        """更新显示"""
        # 随机切换手势
        if random.random() < 0.1:
            self.current_gesture = random.choice(self.gestures)
            self.confidence = random.uniform(0.7, 0.95)

        # 清除所有子图
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.clear()

        # 1. 波形图
        t, signal = self.generate_signal(self.current_gesture)
        self.ax1.plot(t*1000, signal, 'b-', linewidth=1)
        self.ax1.set_title('声纳信号波形', fontweight='bold')
        self.ax1.set_xlabel('时间 (ms)')
        self.ax1.set_ylabel('幅度')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.fill_between(t*1000, 0, signal, alpha=0.3)

        # 2. 频谱图
        fft_data = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/40000)
        pos_freqs = freqs[:len(freqs)//2] / 1000  # kHz
        pos_fft = np.abs(fft_data[:len(fft_data)//2])

        self.ax2.plot(pos_freqs[:100], pos_fft[:100], 'r-', linewidth=1)
        self.ax2.set_title('频谱分析', fontweight='bold')
        self.ax2.set_xlabel('频率 (kHz)')
        self.ax2.set_ylabel('幅度')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.fill_between(pos_freqs[:100], 0, pos_fft[:100], alpha=0.3, color='red')

        # 3. 手部姿态 (简化2D表示)
        hand_x = [0, 2, 4, 5, 2, 4, 5, -2, -4, -5, -2, -3, -4, -3, -2, -1]
        hand_y = [0, 1, 2, 3, -1, -2, -3, -1, -2, -3, 1, 2, 3, 0, 0, 0]

        # 根据手势调整手部姿态
        if self.current_gesture == '专注工作':
            hand_y = [y * 0.7 for y in hand_y]
        elif self.current_gesture == '压力状态':
            hand_x = [x * 0.6 for x in hand_x]
            hand_y = [y * 0.5 for y in hand_y]
        elif self.current_gesture == '疲劳状态':
            hand_y = [y - 1 for y in hand_y]
        elif self.current_gesture == '放松状态':
            hand_x = [x * 1.2 for x in hand_x]

        self.ax3.scatter(hand_x, hand_y, c='blue', s=50, alpha=0.8)
        self.ax3.plot([0, 2, 4, 5], [0, 1, 2, 3], 'b-', linewidth=2)  # 食指
        self.ax3.plot([0, 2, 4, 5], [0, -1, -2, -3], 'b-', linewidth=2)  # 中指
        self.ax3.plot([0, -2, -4, -5], [0, -1, -2, -3], 'b-', linewidth=2)  # 无名指
        self.ax3.plot([0, -2, -3, -4], [0, 1, 2, 3], 'b-', linewidth=2)  # 小指
        self.ax3.scatter([0], [0], c='red', s=100)  # 手腕

        self.ax3.set_title('手部姿态', fontweight='bold')
        self.ax3.set_xlim(-6, 6)
        self.ax3.set_ylim(-5, 5)
        self.ax3.set_aspect('equal')
        self.ax3.grid(True, alpha=0.3)

        # 4. 手势分类结果
        probs = np.random.rand(len(self.gestures))
        current_idx = self.gestures.index(self.current_gesture)
        probs[current_idx] = self.confidence
        probs /= probs.sum()

        bars = self.ax4.barh(self.gestures, probs, color='skyblue', alpha=0.7)
        bars[current_idx].set_color('orange')
        self.ax4.set_title('手势识别结果', fontweight='bold')
        self.ax4.set_xlabel('概率')
        self.ax4.set_xlim(0, 1)

        # 5. 置信度显示
        self.ax5.barh(0.5, self.confidence, height=0.4, color='green', alpha=0.7)
        self.ax5.barh(0.5, 1.0, height=0.4, color='lightgray', alpha=0.3)
        self.ax5.set_title(f'置信度: {self.confidence:.1%}', fontweight='bold')
        self.ax5.set_xlim(0, 1)
        self.ax5.set_xticks([0, 0.25, 0.5, 0.75, 1])
        self.ax5.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        self.ax5.set_yticks([])

        # 6. 状态指示器
        colors = {'专注工作': 'green', '压力状态': 'red', '疲劳状态': 'orange',
                 '放松状态': 'blue', '创意思考': 'purple'}

        self.ax6.text(0.5, 0.7, '当前状态:', transform=self.ax6.transAxes,
                     fontsize=14, ha='center', fontweight='bold')
        self.ax6.text(0.5, 0.4, self.current_gesture, transform=self.ax6.transAxes,
                     fontsize=16, ha='center', color=colors.get(self.current_gesture, 'black'),
                     fontweight='bold',
                     bbox=dict(boxstyle='round', facecolor=colors.get(self.current_gesture, 'lightgray'),
                               alpha=0.3))
        self.ax6.set_xlim(0, 1)
        self.ax6.set_ylim(0, 1)
        self.ax6.axis('off')

        plt.tight_layout()

    def run(self):
        """运行演示"""
        print("🚀 EchoWrist 简化版手势识别演示启动!")
        print("=" * 60)
        print("📊 实时显示内容:")
        print("  • 声纳信号波形")
        print("  • 频谱分析")
        print("  • 2D手部姿态")
        print("  • 手势分类概率")
        print("  • 识别置信度")
        print("  • 状态指示器")
        print("=" * 60)
        print("🔄 每100毫秒更新一次")
        print("🎯 手势状态自动切换")
        print("⏹️  按Ctrl+C停止演示")
        print("=" * 60)
        print()

        try:
            for i in range(1000):  # 运行1000次或直到中断
                self.update_display()
                plt.pause(0.1)  # 每100ms更新
                if i % 20 == 0:  # 每2秒打印一次状态
                    print(f"📍 当前状态: {self.current_gesture} | 置信度: {self.confidence:.1%}")

        except KeyboardInterrupt:
            print("\n👋 演示已停止")
        except Exception as e:
            print(f"❌ 运行出错: {e}")

        plt.show()

def main():
    print("🎯 启动 EchoWrist 手势识别演示")
    demo = SimpleEchoWristDemo()
    demo.run()

if __name__ == "__main__":
    main()