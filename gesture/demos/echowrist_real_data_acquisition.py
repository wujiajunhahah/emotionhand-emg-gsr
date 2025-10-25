#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EchoWrist 真实数据采集和处理系统
支持多种传感器输入，实时数据可视化
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import time
import threading
import queue
import platform
from collections import deque
import struct

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

class SensorDataAcquirer:
    """传感器数据采集器"""

    def __init__(self, sensor_type='simulated'):
        self.sensor_type = sensor_type
        self.data_queue = queue.Queue(maxsize=1000)
        self.is_running = False
        self.sample_rate = 40000  # 40kHz

        # 模拟数据参数
        self.sim_time = 0
        self.current_gesture = '专注工作'
        self.gesture_params = {
            '专注工作': {'freq': 40, 'amp': 0.8, 'noise': 0.05},
            '压力状态': {'freq': 40, 'amp': 1.0, 'noise': 0.15},
            '疲劳状态': {'freq': 35, 'amp': 0.5, 'noise': 0.08},
            '放松状态': {'freq': 38, 'amp': 0.6, 'noise': 0.05},
            '创意思考': {'freq': 42, 'amp': 0.7, 'noise': 0.1}
        }

        if sensor_type == 'serial':
            self.serial_port = None
            self.setup_serial()

    def setup_serial(self):
        """设置串口连接"""
        try:
            # 尝试不同的串口
            possible_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/tty.usbserial-*',
                              'COM3', 'COM4', 'COM5']

            for port in possible_ports:
                try:
                    self.serial_port = serial.Serial(port, 115200, timeout=1)
                    print(f"✅ 成功连接串口: {port}")
                    return True
                except:
                    continue

            print("⚠️ 未找到可用串口，使用模拟数据")
            return False

        except Exception as e:
            print(f"❌ 串口连接失败: {e}")
            return False

    def start_acquisition(self):
        """开始数据采集"""
        self.is_running = True

        if self.sensor_type == 'serial':
            self.serial_thread = threading.Thread(target=self.serial_read_thread)
            self.serial_thread.daemon = True
            self.serial_thread.start()
        else:
            self.simulation_thread = threading.Thread(target=self.simulation_thread)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

        print("🔄 数据采集已启动")

    def stop_acquisition(self):
        """停止数据采集"""
        self.is_running = False
        if hasattr(self, 'serial_port') and self.serial_port:
            self.serial_port.close()
        print("⏹️ 数据采集已停止")

    def simulation_thread(self):
        """模拟数据生成线程"""
        gestures = list(self.gesture_params.keys())
        gesture_index = 0

        while self.is_running:
            # 每隔一段时间切换手势
            if self.sim_time % 200 == 0:  # 每2秒切换
                gesture_index = (gesture_index + 1) % len(gestures)
                self.current_gesture = gestures[gesture_index]

            # 生成模拟信号
            params = self.gesture_params[self.current_gesture]
            t = np.linspace(0, 0.1, 500)

            # 主频信号
            signal = params['amp'] * np.sin(2 * np.pi * params['freq'] * t)

            # 添加其他频率成分
            if self.current_gesture == '压力状态':
                signal += 0.3 * np.sin(2 * np.pi * 80 * t)
                signal += 0.2 * np.sin(2 * np.pi * 120 * t)

            # 添加噪声
            signal += params['noise'] * np.random.randn(len(t))

            # 添加时间戳
            timestamp = time.time()

            # 放入队列
            data_point = {
                'timestamp': timestamp,
                'signal': signal,
                'gesture': self.current_gesture,
                'sample_rate': self.sample_rate
            }

            try:
                self.data_queue.put(data_point, timeout=0.1)
            except queue.Full:
                pass  # 队列满时丢弃旧数据

            self.sim_time += 1
            time.sleep(0.1)  # 100ms间隔

    def serial_read_thread(self):
        """串口读取线程"""
        if not self.serial_port:
            return

        print("📡 开始从串口读取数据...")

        while self.is_running:
            try:
                # 读取串口数据
                if self.serial_port.in_waiting() > 0:
                    # 假设Arduino发送的是ADC值 (0-1023)
                    raw_data = self.serial_port.readline().decode('utf-8').strip()

                    if raw_data:
                        try:
                            # 解析数据，格式: "value1,value2,value3,..."
                            values = [float(x) for x in raw_data.split(',')]

                            if len(values) >= 1:
                                # 转换为电压值 (假设0-1023对应0-3.3V)
                                voltage = values[0] / 1023.0 * 3.3

                                # 生成对应的信号
                                t = np.linspace(0, 0.1, len(values))
                                signal = voltage + 0.1 * np.random.randn(len(values))

                                data_point = {
                                    'timestamp': time.time(),
                                    'signal': signal,
                                    'raw_values': values,
                                    'sample_rate': len(values) * 10  # 估算采样率
                                }

                                self.data_queue.put(data_point, timeout=0.1)
                        except ValueError as e:
                            print(f"⚠️ 数据解析错误: {e}")

            except Exception as e:
                print(f"❌ 串口读取错误: {e}")
                time.sleep(0.1)

    def get_latest_data(self):
        """获取最新数据"""
        data_list = []

        # 获取队列中所有数据
        while not self.data_queue.empty():
            try:
                data_list.append(self.data_queue.get_nowait())
            except queue.Empty:
                break

        return data_list

class RealTimeEchoWristDemo:
    def __init__(self):
        # 创建数据采集器
        self.acquirer = SensorDataAcquisition('simulated')  # 可以改为 'serial'

        # 数据缓存
        self.data_buffer = deque(maxlen=500)
        self.gesture_history = deque(maxlen=100)
        self.confidence_history = deque(maxlen=100)

        # 手势状态
        self.gestures = ['专注工作', '压力状态', '疲劳状态', '放松状态', '创意思考']
        self.current_gesture = '专注工作'
        self.current_confidence = 0.0

        # 创建图形
        self.fig = plt.figure(figsize=(16, 12))
        self.fig.suptitle('EchoWrist 真实数据采集与识别系统', fontsize=18, fontweight='bold')

        # 创建子图
        self.ax_signal = self.fig.add_subplot(3, 3, 1)
        self.ax_spectrum = self.fig.add_subplot(3, 3, 2)
        self.ax_spectrogram = self.fig.add_subplot(3, 3, 3)
        self.ax_stats = self.fig.add_subplot(3, 3, 4)
        self.ax_gesture_prob = self.fig.add_subplot(3, 3, 5)
        self.ax_confidence = self.fig.add_subplot(3, 3, 6)
        self.ax_hand_3d = self.fig.add_subplot(3, 3, 7)
        self.ax_timeline = self.ax_3d = self.fig.add_subplot(3, 3, 8, projection='3d')
        self.ax_controls = self.fig.add_subplot(3, 3, 9)

        # 控制按钮
        self.setup_controls()

        # 初始化3D数据
        self.spectrogram_data = np.zeros((50, 100))
        self.hand_3d_data = self.create_initial_hand_data()

        # 动画
        self.animation = None

    def create_initial_hand_data(self):
        """创建初始3D手部数据"""
        return {
            'thumb': np.array([[0, 0, 0], [-1.5, 0, 2], [-2, 0, 3.5], [-1, 0, 4.5]]),
            'index': np.array([[0, 0, 0], [2, 1, 0], [3.5, 2, 0], [4.5, 3, 0]]),
            'middle': np.array([[0, 0, 0], [2, -1, 0], [3.5, -2.5, 0], [4.5, -3.5, 0]]),
            'ring': np.array([[0, 0, 0], [1.5, -2, 0], [2.5, -3, 0], [3, -4, 0]]),
            'pinky': np.array([[0, 0, 0], [1, -2.5, 0], [1.5, -3.5, 0], [2, -4.5, 0]])
        }

    def setup_controls(self):
        """设置控制面板"""
        self.ax_controls.axis('off')
        self.ax_controls.set_title('控制面板', fontsize=14, fontweight='bold')

        # 显示当前状态
        self.status_text = self.ax_controls.text(0.5, 0.8, '数据源: 模拟',
                                                  transform=self.ax_controls.transAxes,
                                                  fontsize=12, ha='center',
                                                  bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

        self.gesture_text = self.ax_controls.text(0.5, 0.6, '状态: 准备中',
                                                  transform=self.ax_controls.transAxes,
                                                  fontsize=12, ha='center')

        self.data_rate_text = self.ax_controls.text(0.5, 0.4, '采样率: 0 Hz',
                                                    transform=self.ax_controls.transAxes,
                                                    fontsize=12, ha='center')

        self.buffer_text = self.ax_controls.text(0.5, 0.2, '缓冲区: 0 样本',
                                                   transform=self.ax_controls.transAxes,
                                                   fontsize=12, ha='center')

        # 添加模拟按钮
        button_box = plt.Rectangle((0.2, 0.05), (0.6, 0.1),
                                 transform=self.ax_controls.transAxes,
                                 facecolor='green', alpha=0.3, edgecolor='green')
        self.ax_controls.add_patch(button_box)

        self.ax_controls.text(0.5, 0.1, '点击开始采集',
                            transform=self.ax_controls.transAxes,
                            fontsize=10, ha='center', va='center')

    def on_click(self, event):
        """处理鼠标点击事件"""
        if event.inaxes == self.ax_controls:
            # 检查是否点击了开始按钮
            if 0.2 <= event.xdata <= 0.8 and 0.05 <= event.ydata <= 0.15:
                if self.acquirer.is_running:
                    self.stop_demo()
                else:
                    self.start_demo()

    def start_demo(self):
        """开始演示"""
        print("🚀 开始数据采集")
        self.acquirer.start_acquisition()

        if self.animation is None:
            self.animation = FuncAnimation(self.fig, self.update_display,
                                        interval=100, blit=False)

        plt.show()

    def stop_demo(self):
        """停止演示"""
        print("⏹️ 停止数据采集")
        self.acquirer.stop_acquisition()

    def analyze_signal(self, signal):
        """分析信号特征"""
        # 基本统计
        mean_val = np.mean(signal)
        std_val = np.std(signal)
        rms_val = np.sqrt(np.mean(signal**2))

        # 频域分析
        fft_data = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/40000)

        # 找到主频
        pos_freqs = freqs[:len(freqs)//2]
        pos_fft = np.abs(fft_data[:len(fft_data)//2])
        main_freq_idx = np.argmax(pos_fft)
        main_freq = pos_freqs[main_freq_idx]
        main_freq_strength = pos_fft[main_freq_idx]

        # 能量分布
        total_energy = np.sum(pos_fft)
        low_freq_energy = np.sum(pos_fft[:50])  # 0-2kHz
        high_freq_energy = np.sum(pos_fft[100:])  # 4kHz+

        # 频谱重心
        spectral_centroid = np.sum(pos_freqs * pos_fft) / total_energy

        return {
            'mean': mean_val,
            'std': std_val,
            'rms': rms_val,
            'main_freq': main_freq,
            'main_freq_strength': main_freq_strength,
            'total_energy': total_energy,
            'low_freq_ratio': low_freq_energy / total_energy,
            'high_freq_ratio': high_freq_total_energy / total_energy,
            'spectral_centroid': spectral_centroid
        }

    def classify_gesture(self, features):
        """基于特征分类手势"""
        # 简单的基于特征的分类器
        main_freq = features['main_freq']
        rms = features['rms']
        std_val = features['std']

        if main_freq < 37 and rms > 0.6:
            return '专注工作', 0.85
        elif main_freq > 42 and std_val > 0.15:
            return '压力状态', 0.80
        elif rms < 0.4 and std_val < 0.08:
            return '疲劳状态', 0.75
        elif 37 <= main_freq <= 39 and std_val < 0.06:
            return '放松状态', 0.82
        else:
            return '创意思考', 0.70

    def update_3d_hand(self, gesture):
        """根据手势更新3D手部模型"""
        if gesture == '专注工作':
            # 稳定姿态
            for finger in self.hand_3d_data:
                self.hand_3d_data[finger][:, 1] *= 0.9
                self.hand_3d_data[finger][:, 2] *= 0.9
        elif gesture == '压力状态':
            # 握拳
            for finger in self.hand_3d_data:
                self.hand_3d_data[finger][1:, 0] *= 0.6
                self.hand_3d_data[finger][1:, 1] *= 0.4
        elif gesture == '疲劳状态':
            # 下垂
            for finger in self.hand_3d_data:
                self.hand_3d_data[finger][:, 1] -= 1.2
        elif gesture == '放松状态':
            # 伸展
            for finger in self.hand_3d_data:
                self.hand_3d_data[finger][1:, 0] *= 1.2
                self.hand_3d_data[finger][1:, 1] *= 1.1
        elif gesture == '创意思考':
            # 动态
            for finger in self.hand_3d_data:
                for i in range(len(self.hand_3d_data[finger])):
                    self.hand_3d_data[finger][i, 0] += np.sin(time.time() * 2 + i) * 0.1
                    self.hand_3d_data[finger][i, 1] += np.cos(time.time() * 3 + i) * 0.1

    def update_display(self, frame):
        """更新显示"""
        # 获取最新数据
        data_points = self.acquirer.get_latest_data()

        if not data_points:
            return

        # 处理最新数据点
        latest_data = data_points[-1]
        signal = latest_data['signal']
        current_gesture = latest_data.get('gesture', '未知')

        # 更新数据缓冲
        self.data_buffer.extend(signal)
        if len(self.data_buffer) > 500:
            self.data_buffer = list(self.data_buffer)[-500:]

        # 分析信号
        features = self.analyze_signal(signal)

        # 分类手势
        predicted_gesture, confidence = self.classify_gesture(features)
        self.current_gesture = predicted_gesture
        self.current_confidence = confidence

        # 更新历史
        self.gesture_history.append(self.current_gesture)
        self.confidence_history.append(self.current_confidence)

        if len(self.gesture_history) > 100:
            self.gesture_history = list(self.gesture_history)[-100:]
            self.confidence_history = list(self.confidence_history)[-100:]

        # 清除并重新绘制所有子图
        for ax in [self.ax_signal, self.ax_spectrum, self.ax_spectrogram, self.ax_stats,
                  self.ax_gesture_prob, self.ax_confidence, self.ax_hand_3d, self.ax_timeline,
                  self.ax_3d]:
            ax.clear()

        # 1. 实时信号波形
        t = np.linspace(0, len(signal)/40000, len(signal)) * 1000
        self.ax_signal.plot(t, signal, 'b-', linewidth=1)
        self.ax_signal.fill_between(t, 0, signal, alpha=0.3)
        self.ax_signal.set_title('实时信号波形', fontsize=12, fontweight='bold')
        self.ax_signal.set_xlabel('时间 (ms)')
        self.ax_signal.set_ylabel('幅度')
        self.ax_signal.grid(True, alpha=0.3)

        # 2. 频谱图
        fft_data = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/40000)
        pos_freqs = freqs[:len(freqs)//2] / 1000
        pos_fft = np.abs(fft_data[:len(fft_data)//2])

        self.ax_spectrum.plot(pos_freqs[:200], pos_fft[:200], 'r-', linewidth=1)
        self.ax_spectrum.fill_between(pos_freqs[:200], 0, pos_fft[:200], alpha=0.3, color='red')
        self.ax_spectrum.set_title('频谱分析', fontsize=12, fontweight='bold')
        self.ax_spectrum.set_xlabel('频率 (kHz)')
        self.ax_spectrum.set_ylabel('幅度')
        self.ax_spectrum.grid(True, alpha=0.3)

        # 3. 频谱图
        if len(self.data_buffer) >= 500:
            # 创建频谱图
            segment_length = 100
            n_segments = len(self.data_buffer) // segment_length

            for i in range(min(n_segments, 50)):
                start_idx = i * segment_length
                end_idx = start_idx + segment_length
                segment = self.data_buffer[start_idx:end_idx]

                if len(segment) == segment_length:
                    fft_segment = np.fft.fft(segment)
                    freqs_segment = np.fft.fftfreq(len(segment), 1/40000)

                    # 只保留正频率部分
                    pos_freqs_segment = freqs_segment[:len(freqs_segment)//2]
                    pos_fft_segment = np.abs(fft_segment[:len(fft_segment)//2])

                    # 更新频谱图
                    self.spectrogram_data[i] = pos_fft_segment[:50]

            # 绘制频谱图
            im = self.ax_spectrogram.imshow(self.spectrogram_data.T, aspect='auto',
                                              cmap='viridis', vmin=0, extent=[0, 50, 0, 20],
                                              origin='lower')
            self.ax_spectrogram.set_title('频谱图 (时间vs频率)', fontsize=12, fontweight='bold')
            self.ax_spectrogram.set_xlabel('时间')
            self.ax_spectrogram.set_ylabel('频率 (kHz)')

        # 4. 统计信息
        self.ax_stats.text(0.1, 0.9, f'主频: {features["main_freq"]:.1f} kHz', transform=self.ax_stats.transAxes, fontsize=10)
        self.ax_stats.text(0.1, 0.8, f'RMS: {features["rms"]:.3f}', transform=self.ax_stats.transAxes, fontsize=10)
        self.ax_stats.text(0.1, 0.7, f'标准差: {features["std"]:.3f}', transform=self.ax_stats.transAxes, fontsize=10)
        self.ax_stats.text(0.1, 0.6, f'低频比: {features["low_freq_ratio"]:.2f}', transform=self.ax_stats.transAxes, fontsize=10)
        self.ax_stats.text(0.1, 0.5, f'总能量: {features["total_energy"]:.1f}', transform=self.ax_stats.transAxes, fontsize=10)
        self.ax_stats.set_title('信号统计', fontsize=12, fontweight='bold')
        self.ax_stats.axis('off')

        # 5. 手势概率分布
        gesture_probs = np.random.rand(len(self.gestures))
        current_idx = self.gestures.index(self.current_gesture)
        gesture_probs[current_idx] = self.current_confidence
        gesture_probs /= gesture_probs.sum()

        bars = self.ax_gesture_bar.barh(self.gestures, gesture_probs,
                                        color='skyblue', alpha=0.7)
        bars[current_idx].set_color('orange')
        bars[current_idx].set_alpha(0.9)
        self.ax_gesture_bar.set_title('手势识别概率', fontsize=12, fontweight='bold')
        self.ax_gesture_bar.set_xlabel('概率')
        self.ax_gesture_bar.set_xlim(0, 1)

        # 6. 置信度显示
        self.ax_confidence.set_title(f'识别置信度: {self.current_confidence:.1%}', fontsize=12, fontweight='bold')

        # 绘制仪表
        theta = np.linspace(0, np.pi, 100)
        self.ax_confidence.fill_between(theta, 0.3, 1.0, color='lightgray', alpha=0.3)
        confidence_theta = np.linspace(0, self.current_confidence * np.pi, 100)

        color = 'green' if self.current_confidence > 0.7 else 'orange'
        self.ax_confidence.fill_between(confidence_theta, 0.3, 1.0, color=color, alpha=0.8)
        self.ax_confidence.set_ylim(0, 1)
        self.ax_confidence.set_xlim(0, np.pi)
        self.ax_confidence.set_xticks([0, np.pi/2, np.pi])
        self.ax_confidence.set_xticklabels(['0%', '50%', '100%'])
        self.ax_confidence.set_yticks([0.3, 1.0])
        self.ax_confidence.set_yticklabels(['0%', '100%'])

        # 7. 3D手部模型
        self.update_3d_hand(self.current_gesture)

        # 绘制手部
        finger_colors = ['red', 'blue', 'green', 'orange', 'purple']
        for i, (finger_name, color) in enumerate(['拇指', '食指', '中指', '无名指', '小指']):
            points = self.hand_3d_data[finger_name]
            self.ax_hand_3d.plot(points[:, 0], points[:, 1], points[:, 2],
                               color=color, linewidth=2, alpha=0.8)
            self.ax_hand_3d.scatter(points[:, 0], points[:, 1], points[:, 2],
                                   c=color, s=50, alpha=0.9)

        self.ax_hand_3d.set_title('3D手部模型', fontsize=12, fontshape='bold')
        self.ax_hand_3d.set_xlim(-3, 5)
        self.ax_hand_3d.set_ylim(-6, 2)
        self.ax_hand_3d.set_zlim(-1, 5)
        self.ax_hand_3d.grid(True, alpha=0.3)

        # 8. 时间线
        if len(self.gesture_history) > 1:
            time_points = list(range(len(self.gesture_history)))
            confidence_line = self.ax_timeline.plot(time_points, self.confidence_history,
                                                 'b-', linewidth=1, alpha=0.5)

            # 标记关键状态
            for i, gesture in enumerate(self.gesture_history):
                if i == 0 or gesture != self.gesture_history[i-1]:
                    color = 'red' if gesture == '压力状态' else 'green'
                    self.ax_timeline.scatter(i, self.confidence_history[i],
                                            c=color, s=30, alpha=0.8)

        self.ax_timeline.set_title('状态时间线', fontsize=12, fontweight='bold')
        self.ax_timeline.set_xlabel('时间')
        self.ax_timeline.set_ylabel('置信度')
        self.ax_timeline.set_ylim(0, 1)
        self.ax_timeline.grid(True, alpha=0.3)

        # 9. 3D轨迹图
        if len(self.hand_3d_data['index']) > 0:
            # 绘制指尖轨迹
            for finger_name, color in [('thumb', 'red'), ('index', 'blue')]:
                points = self.hand_3d_data[finger_name]
                self.ax_3d.plot(points[:, 0], points[:, 1], points[:, 2],
                               color=color, alpha=0.5, linewidth=1)

            # 绘制手掌轨迹
            palm_center = np.mean([self.hand_3d_data[finger][:1] for finger in self.hand_3d_data.values()], axis=0)
            self.ax_3d.scatter(palm_center[0], palm_center[1], palm_center[2],
                            c='black', s=100, marker='o')

        self.ax_3d.set_title('3D轨迹图', fontsize=12, fontweight='bold')
        self.ax_3d.set_xlabel('X')
        self.ax_3d.set_ylabel('Y')
        self.ax_3d.set_zlabel('Z')
        self.ax_3d.grid(True, alpha=0.3)

        # 更新控制面板
        self.update_controls()

        plt.tight_layout()

    def update_controls(self):
        """更新控制面板"""
        self.status_text.set_text(f'数据源: {self.acquirer.sensor_type}')
        self.gesture_text.set_text(f'当前状态: {self.current_gesture}')
        self.data_rate_text.set_text(f'采样率: {self.acquirer.sample_rate} Hz')
        self.buffer_text.set_text(f'缓冲区: {len(self.data_buffer)} 样本')

        if self.acquirer.is_running:
            button_color = 'orange'
            button_text = '停止采集'
        else:
            button_color = 'green'
            button_text = '开始采集'

        # 更新按钮
        for patch in self.ax_controls.patches:
            if isinstance(patch, plt.Rectangle):
                patch.set_facecolor(button_color)
                break

        # 更新按钮文字
        for text in self.ax_control.texts:
            if '开始采集' in text.get_text() or '停止采集' in text.get_text():
                text.set_text(button_text)
                break

    def run(self):
        """运行主程序"""
        print("🎯 EchoWrist 真实数据采集系统")
        print("=" * 60)
        print("📊 功能特性:")
        print("  • 实时信号采集 (模拟/串口)")
        print("  • 频谱分析")
        print("  • 频谱图显示")
        print("  • 手势状态识别")
        print("  • 3D手部模型")
        print("  • 实时统计分析")
        print("  • 历史数据追踪")
        print("  • 3D轨迹可视化")
        print("=" * 60)
        print("🔌 连接鼠标点击控制面板上的按钮")
        print("⚙️ 支持串口数据输入")
        print("⚙️ 支持多传感器数据融合")
        print("=" * 60)

        # 连接鼠标事件
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

        # 开始动画
        self.animation = FuncAnimation(self.fig, self.update_display,
                                        interval=100, blit=False,
                                        cache_frame_data=False)

        plt.show()

def main():
    print("🎯 启动 EchoWrist 实时数据采集系统")
    demo = RealTimeEchoWristDemo()
    demo.run()

if __name__ == "__main__":
    main()