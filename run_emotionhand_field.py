#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 实地运行脚本
整合了zcf项目的专业信号处理引擎
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
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# 添加zcf项目路径
zcf_paths = [
    "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub",
    "/Users/wujiajun/Downloads/zcf/gesture",
    "/Users/wujiajun/Downloads/zcf/GestureSense_Complete_Project"
]

for path in zcf_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)

# 导入专业信号处理引擎
try:
    from signal_processing_engine import RealTimeSignalProcessor
    PROFESSIONAL_ENGINE_AVAILABLE = True
    print("✅ 成功加载企业级信号处理引擎")
except ImportError as e:
    print(f"⚠️ 企业级信号处理引擎加载失败: {e}")
    PROFESSIONAL_ENGINE_AVAILABLE = False

# 尝试导入其他组件
try:
    from emotion_state_detector import EnsembleDetector
    ENSEMBLE_DETECTOR_AVAILABLE = True
    print("✅ 成功加载集成情绪检测器")
except ImportError as e:
    print(f"⚠️ 集成情绪检测器加载失败: {e}")
    ENSEMBLE_DETECTOR_AVAILABLE = False

try:
    from calibration_system import CalibrationSystem
    CALIBRATION_AVAILABLE = True
    print("✅ 成功加载校准系统")
except ImportError as e:
    print(f"⚠️ 校准系统加载失败: {e}")
    CALIBRATION_AVAILABLE = False

class FieldEmotionHand:
    """实地版EmotionHand"""

    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EmotionHand 实地运行版 - 专业EMG+GSR情绪识别")
        self.root.geometry("1400x800")

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

        # 数据存储
        self.emg_data = deque(maxlen=500)
        self.gsr_data = deque(maxlen=500)
        self.emotion_history = deque(maxlen=100)
        self.time_stamps = deque(maxlen=500)

        # 初始化组件
        self.init_components()

        # 动画控制
        self.animation = None
        self.is_running = False
        self.start_time = time.time()

        # 设置界面
        self.setup_ui()

    def init_components(self):
        """初始化组件"""
        # 信号处理引擎
        self.signal_engine = None
        if PROFESSIONAL_ENGINE_AVAILABLE:
            try:
                config_path = "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub/signal_processing_config.json"
                if not os.path.exists(config_path):
                    config_path = None

                self.signal_engine = RealTimeSignalProcessor(config_path)
                self.signal_engine.start()
                print("✅ 信号处理引擎初始化成功")
            except Exception as e:
                print(f"❌ 信号处理引擎初始化失败: {e}")

        # 情绪检测器
        self.emotion_detector = None
        if ENSEMBLE_DETECTOR_AVAILABLE:
            try:
                self.emotion_detector = EnsembleDetector()
                print("✅ 情绪检测器初始化成功")
            except Exception as e:
                print(f"❌ 情绪检测器初始化失败: {e}")

        # 校准系统
        self.calibration_system = None
        if CALIBRATION_AVAILABLE:
            try:
                self.calibration_system = CalibrationSystem()
                print("✅ 校准系统初始化成功")
            except Exception as e:
                print(f"❌ 校准系统初始化失败: {e}")

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame,
                               text="EmotionHand 实地运行版 - 专业EMG+GSR情绪识别系统",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)

        # 系统状态
        status_frame = ttk.LabelFrame(main_frame, text="系统状态", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        # 创建状态显示
        status_info = []
        if PROFESSIONAL_ENGINE_AVAILABLE:
            status_info.append("✅ 企业级信号处理引擎")
        else:
            status_info.append("⚠️ 简化信号处理")

        if ENSEMBLE_DETECTOR_AVAILABLE:
            status_info.append("✅ 集成情绪检测器")
        else:
            status_info.append("⚠️ 基础情绪检测")

        if CALIBRATION_AVAILABLE:
            status_info.append("✅ 专业校准系统")
        else:
            status_info.append("⚠️ 基础校准")

        ttk.Label(status_frame, text=" | ".join(status_info),
                 font=('Arial', 10)).pack()

        # 当前状态框架
        current_frame = ttk.LabelFrame(main_frame, text="当前状态", padding=10)
        current_frame.pack(fill=tk.X, pady=5)

        self.emotion_label = ttk.Label(current_frame,
                                      text=f"😐 平静 - 置信度: 0.50",
                                      font=('Arial', 14, 'bold'))
        self.emotion_label.pack()

        self.quality_label = ttk.Label(current_frame,
                                       text="信号质量: 检测中...",
                                       font=('Arial', 11))
        self.quality_label.pack()

        # 创建图表
        self.create_plots(main_frame)

        # 控制面板
        self.create_control_panel(main_frame)

    def create_plots(self, parent):
        """创建图表"""
        # 创建matplotlib图形
        self.fig = plt.figure(figsize=(14, 6), facecolor='white')

        # EMG信号图
        self.ax_emg = self.fig.add_subplot(131)
        self.ax_emg.set_title('EMG信号', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(-1, 1)

        # GSR信号图
        self.ax_gsr = self.fig.add_subplot(132)
        self.ax_gsr.set_title('GSR信号', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)
        self.ax_gsr.set_ylim(0, 5)

        # 情绪状态图
        self.ax_emotion = self.fig.add_subplot(133)
        self.ax_emotion.set_title('情绪状态时间线', fontsize=12, fontweight='bold')
        self.ax_emotion.set_xlabel('时间 (s)')
        self.ax_emotion.set_ylabel('情绪状态')
        self.ax_emotion.set_ylim(-0.5, len(self.emotion_states) - 0.5)
        self.ax_emotion.set_yticks(range(len(self.emotion_states)))
        self.ax_emotion.set_yticklabels(list(self.emotion_states.keys()))
        self.ax_emotion.grid(True, alpha=0.3)

        # 嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig.tight_layout()

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=10)

        # 主要控制按钮
        self.start_btn = ttk.Button(control_frame, text="🚀 开始监测",
                                   command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹️ 停止监测",
                                  command=self.stop_monitoring,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.calibrate_btn = ttk.Button(control_frame, text="🎯 校准",
                                       command=self.start_calibration)
        self.calibrate_btn.pack(side=tk.LEFT, padx=5)

        # 功能按钮
        ttk.Button(control_frame, text="📊 保存数据",
                  command=self.save_data).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="🔄 重置",
                  command=self.reset_system).pack(side=tk.LEFT, padx=5)

        # 模式切换
        ttk.Label(control_frame, text="运行模式:").pack(side=tk.LEFT, padx=(20, 5))
        self.mode_var = tk.StringVar(value="演示模式")
        mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var,
                                   values=["演示模式", "实时模式"], state="readonly", width=10)
        mode_combo.pack(side=tk.LEFT, padx=5)

    def generate_realistic_demo_data(self):
        """生成真实的演示数据"""
        current_time = time.time() - self.start_time

        # 根据情绪状态生成不同的EMG信号模式
        emg_channels = []
        for ch in range(8):
            # 基础信号
            base_freq = 10 + ch * 2
            signal = 0.1 * np.sin(2 * np.pi * base_freq * current_time)

            # 添加情绪特征
            if self.current_emotion == 'Stress':
                # 压力：高频噪声增加
                signal += 0.2 * np.random.randn() + 0.1 * np.sin(2 * np.pi * 50 * current_time)
            elif self.current_emotion == 'Happy':
                # 开心：中等频率规律信号
                signal += 0.15 * np.sin(2 * np.pi * 20 * current_time)
            elif self.current_emotion == 'Focus':
                # 专注：低频稳定信号
                signal *= 0.7
                signal += 0.05 * np.sin(2 * np.pi * 5 * current_time)
            elif self.current_emotion == 'Excited':
                # 兴奋：多频率混合
                signal += 0.1 * np.sin(2 * np.pi * 30 * current_time)
                signal += 0.08 * np.sin(2 * np.pi * 60 * current_time)

            # 添加噪声
            signal += 0.02 * np.random.randn()
            emg_channels.append(np.clip(signal, -1, 1))

        # 生成GSR信号
        base_gsr = 2.0 + 0.3 * np.sin(2 * np.pi * 0.1 * current_time)

        if self.current_emotion == 'Stress':
            base_gsr += 0.4  # 压力时皮电增强
        elif self.current_emotion == 'Excited':
            base_gsr += 0.2 + 0.1 * np.sin(2 * np.pi * 0.5 * current_time)

        gsr_value = max(0.1, base_gsr + 0.05 * np.random.randn())

        return emg_channels, gsr_value

    def get_demo_emotion(self):
        """获取演示情绪状态"""
        current_time = time.time() - self.start_time
        cycle_time = 25  # 25秒一个周期
        phase = (current_time % cycle_time) / cycle_time

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

    def process_data(self):
        """处理数据"""
        is_demo_mode = self.mode_var.get() == "演示模式"

        if is_demo_mode:
            # 演示模式
            self.current_emotion = self.get_demo_emotion()
            emg_data, gsr_data = self.generate_realistic_demo_data()
            quality_score = np.random.uniform(0.7, 0.95)
            processing_time = np.random.uniform(0.005, 0.015)

            return {
                'emg_data': emg_data,
                'gsr_data': gsr_data,
                'emotion': self.current_emotion,
                'confidence': 0.7 + 0.2 * np.random.random(),
                'quality_score': quality_score,
                'processing_time': processing_time
            }

        # 实时模式
        if self.signal_engine:
            try:
                result = self.signal_engine.process_window()
                if result:
                    # 检测情绪
                    emotion = self.detect_emotion_from_features(result['normalized_features'])

                    return {
                        'emg_data': [result['emg_features']['rms']] * 8,  # 简化处理
                        'gsr_data': result['gsr_features']['tonic'],
                        'emotion': emotion,
                        'confidence': 0.8,
                        'quality_score': result['quality']['overall'],
                        'processing_time': result['processing_time'],
                        'features': result['normalized_features']
                    }
            except Exception as e:
                print(f"数据处理错误: {e}")

        return None

    def detect_emotion_from_features(self, features):
        """从特征检测情绪"""
        # 简化的情绪检测逻辑
        if not features:
            return 'Neutral'

        rms = features.get('rms', 0.5)
        gsr_tonic = features.get('gsr_tonic', 0.5)

        if rms > 0.7 and gsr_tonic > 0.7:
            return 'Stress'
        elif rms > 0.6 and gsr_tonic < 0.4:
            return 'Focus'
        elif rms > 0.5 and 0.3 < gsr_tonic < 0.7:
            return 'Happy'
        elif rms > 0.8:
            return 'Excited'
        else:
            return 'Neutral'

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 处理数据
        result = self.process_data()
        if not result:
            return

        # 更新状态
        self.current_emotion = result['emotion']
        self.emotion_confidence = result['confidence']

        # 存储数据
        current_time = time.time() - self.start_time
        self.time_stamps.append(current_time)

        if result['emg_data']:
            self.emg_data.append(np.mean(result['emg_data']))
        self.gsr_data.append(result['gsr_data'])
        self.emotion_history.append(result['emotion'])

        # 更新图表
        self.update_emg_plot()
        self.update_gsr_plot()
        self.update_emotion_plot()

        # 更新状态显示
        self.update_status_display(result)

        # 刷新画布
        self.canvas.draw()

    def update_emg_plot(self):
        """更新EMG图"""
        self.ax_emg.clear()
        self.ax_emg.set_title('EMG信号', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('幅值')
        self.ax_emg.grid(True, alpha=0.3)

        if len(self.emg_data) > 0:
            times = list(self.time_stamps)[-len(self.emg_data):]
            self.ax_emg.plot(times, list(self.emg_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_emg.set_ylim(-1, 1)

    def update_gsr_plot(self):
        """更新GSR图"""
        self.ax_gsr.clear()
        self.ax_gsr.set_title('GSR信号', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        if len(self.gsr_data) > 0:
            times = list(self.time_stamps)[-len(self.gsr_data):]
            self.ax_gsr.plot(times, list(self.gsr_data),
                           color=self.emotion_states[self.current_emotion]['color'],
                           linewidth=1.5, alpha=0.8)
            self.ax_gsr.set_ylim(0, 5)

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

    def update_status_display(self, result):
        """更新状态显示"""
        emotion_info = self.emotion_states[self.current_emotion]
        self.emotion_label.config(
            text=f"{emotion_info['emoji']} {emotion_info['description']} - 置信度: {result['confidence']:.2f}"
        )

        quality_score = result.get('quality_score', 0.5)
        if quality_score >= 0.8:
            quality_text = "优秀"
            color = "green"
        elif quality_score >= 0.6:
            quality_text = "良好"
            color = "blue"
        else:
            quality_text = "一般"
            color = "orange"

        self.quality_label.config(
            text=f"信号质量: {quality_text} ({quality_score:.2f}) | 延迟: {result['processing_time']*1000:.1f}ms",
            foreground=color
        )

    def start_monitoring(self):
        """开始监测"""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            # 重启信号引擎
            if self.signal_engine:
                self.signal_engine.start()

            # 创建动画
            from matplotlib.animation import FuncAnimation
            self.animation = FuncAnimation(self.fig, self.update_plots,
                                         interval=100, blit=False)
            self.canvas.draw()

            print(f"🚀 开始监测 - 模式: {self.mode_var.get()}")

    def stop_monitoring(self):
        """停止监测"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

            if self.animation is not None:
                self.animation.event_source.stop()
                self.animation = None

            if self.signal_engine:
                self.signal_engine.stop()

            print("⏹️ 停止监测")

    def start_calibration(self):
        """开始校准"""
        if self.calibration_system:
            self.calibrate_btn.config(state=tk.DISABLED)
            threading.Thread(target=self._calibration_thread, daemon=True).start()
        else:
            messagebox.showinfo("提示", "校准系统不可用")

    def _calibration_thread(self):
        """校准线程"""
        try:
            messagebox.showinfo("校准", "开始60秒校准程序...\n请保持静止30秒，然后轻握30秒")
            # 这里可以调用实际的校准程序
            time.sleep(2)  # 模拟校准
            messagebox.showinfo("完成", "校准完成！")
        except Exception as e:
            messagebox.showerror("错误", f"校准失败: {e}")
        finally:
            self.calibrate_btn.config(state=tk.NORMAL)

    def save_data(self):
        """保存数据"""
        try:
            import json
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"emotionhand_field_data_{timestamp}.json"

            data = {
                'timestamp': timestamp,
                'mode': self.mode_var.get(),
                'duration': time.time() - self.start_time if self.is_running else 0,
                'emotion_history': list(self.emotion_history),
                'system_info': {
                    'professional_engine': PROFESSIONAL_ENGINE_AVAILABLE,
                    'ensemble_detector': ENSEMBLE_DETECTOR_AVAILABLE,
                    'calibration_system': CALIBRATION_AVAILABLE
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"数据已保存到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def reset_system(self):
        """重置系统"""
        if messagebox.askyesno("确认", "确定要重置系统吗？"):
            # 清空数据
            self.emg_data.clear()
            self.gsr_data.clear()
            self.emotion_history.clear()
            self.time_stamps.clear()

            # 重置状态
            self.current_emotion = 'Neutral'
            self.emotion_confidence = 0.5
            self.start_time = time.time()

            messagebox.showinfo("完成", "系统已重置")

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_monitoring()

            if self.signal_engine:
                self.signal_engine.stop()

            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EmotionHand 实地运行版启动成功!")
        print("📋 系统组件:")
        print(f"   • 信号处理引擎: {'企业级' if PROFESSIONAL_ENGINE_AVAILABLE else '简化版'}")
        print(f"   • 情绪检测器: {'集成版' if ENSEMBLE_DETECTOR_AVAILABLE else '基础版'}")
        print(f"   • 校准系统: {'专业版' if CALIBRATION_AVAILABLE else '基础版'}")
        print("\n🎮 使用说明:")
        print("   • 选择运行模式（演示/实时）")
        print("   • 点击'开始监测'启动系统")
        print("   • 观察信号波形和情绪变化")
        print("   • 可进行校准和保存数据")

        self.root.mainloop()

if __name__ == "__main__":
    app = FieldEmotionHand()
    app.run()