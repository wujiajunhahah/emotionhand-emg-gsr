#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 真实版 - 基于EMG+GSR信号的实时情绪识别系统
修复了字体、动画和状态映射问题
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from collections import deque
import queue
import serial
import serial.tools.list_ports
from scipy import signal as scipy_signal
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体和后端
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

from signal_processing_engine import SignalProcessingEngine
from emotion_state_detector import EmotionStateDetector
from calibration_system import CalibrationSystem

class RealtimeEmotionHand:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EmotionHand 真实版 - EMG+GSR情绪识别系统")
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

        # 数据队列
        self.data_queue = queue.Queue()
        self.emotion_history = deque(maxlen=100)
        self.emg_history = deque(maxlen=500)
        self.gsr_history = deque(maxlen=500)

        # 系统组件
        self.signal_engine = SignalProcessingEngine()
        self.emotion_detector = EmotionStateDetector()
        self.calibration_system = CalibrationSystem()

        # 串口连接
        self.serial_port = None
        self.is_connected = False

        # 动画控制
        self.animation = None
        self.is_running = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="EmotionHand 真实版",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=5)

        # 连接状态框架
        connection_frame = ttk.LabelFrame(main_frame, text="设备连接", padding="10")
        connection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # 串口选择
        ttk.Label(connection_frame, text="串口:").grid(row=0, column=0, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var,
                                       state="readonly", width=15)
        self.port_combo.grid(row=0, column=1, padx=5)

        self.refresh_ports_btn = ttk.Button(connection_frame, text="刷新端口",
                                           command=self.refresh_ports)
        self.refresh_ports_btn.grid(row=0, column=2, padx=5)

        self.connect_btn = ttk.Button(connection_frame, text="连接设备",
                                     command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=3, padx=5)

        self.connection_status = ttk.Label(connection_frame, text="未连接",
                                          foreground="red")
        self.connection_status.grid(row=0, column=4, padx=10)

        # 校准框架
        calibration_frame = ttk.LabelFrame(main_frame, text="校准状态", padding="10")
        calibration_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.calib_status = ttk.Label(calibration_frame, text="未校准")
        self.calib_status.grid(row=0, column=0, padx=5)

        self.calib_btn = ttk.Button(calibration_frame, text="开始校准",
                                   command=self.start_calibration)
        self.calib_btn.grid(row=0, column=1, padx=5)

        # 状态信息框架
        info_frame = ttk.LabelFrame(main_frame, text="当前状态", padding="10")
        info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        self.status_text = tk.Text(info_frame, height=4, width=80)
        self.status_text.grid(row=0, column=0, padx=5)

        # 创建图表
        self.create_plots(main_frame)

        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.start_btn = ttk.Button(control_frame, text="开始监测",
                                   command=self.start_monitoring, state="disabled")
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="停止监测",
                                  command=self.stop_monitoring, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)

    def create_plots(self, parent):
        """创建图表"""
        # 创建图形
        self.fig = plt.Figure(figsize=(14, 6), facecolor='white')

        # 子图1: EMG信号
        self.ax1 = self.fig.add_subplot(131)
        self.ax1.set_title('EMG信号', fontsize=12)
        self.ax1.set_xlabel('时间 (s)')
        self.ax1.set_ylabel('幅值')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_ylim(-1, 1)

        # 子图2: GSR信号
        self.ax2 = self.fig.add_subplot(132)
        self.ax2.set_title('GSR信号', fontsize=12)
        self.ax2.set_xlabel('时间 (s)')
        self.ax2.set_ylabel('电导 (μS)')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_ylim(0, 10)

        # 子图3: 3D手部可视化
        self.ax3 = self.fig.add_subplot(133, projection='3d')
        self.ax3.set_title('3D手部模型', fontsize=12)

        # 设置3D视图
        self.setup_3d_hand()

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=3, pady=10)

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

        # 绘制手指（根据情绪状态调整）
        finger_positions = [
            [-0.04, 0.06, 0.02],  # 小指
            [-0.02, 0.08, 0.025], # 无名指
            [0, 0.09, 0.03],      # 中指
            [0.02, 0.08, 0.025],  # 食指
            [0.04, 0.06, 0.02]    # 大拇指
        ]

        # 根据情绪状态调整手指
        emotion_multiplier = self.get_emotion_multiplier()

        for i, pos in enumerate(finger_positions):
            # 手指基座到指尖
            finger_extension = emotion_multiplier * finger_length
            finger_x = [pos[0], pos[0]]
            finger_y = [pos[1], pos[1] + finger_extension]
            finger_z = [pos[2], pos[2] + 0.01]

            self.ax3.plot(finger_x, finger_y, finger_z,
                         color=rgb_color, linewidth=4, alpha=0.8)

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

    def get_emotion_multiplier(self):
        """根据情绪状态获取手指伸展倍数"""
        multipliers = {
            'Neutral': 1.0,
            'Happy': 1.2,
            'Stress': 0.8,
            'Focus': 1.1,
            'Excited': 1.3
        }
        return multipliers.get(self.current_emotion, 1.0)

    def refresh_ports(self):
        """刷新可用串口"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
        print(f"🔍 发现串口: {ports}")

    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            self.connect_device()
        else:
            self.disconnect_device()

    def connect_device(self):
        """连接设备"""
        if not self.port_var.get():
            messagebox.showerror("错误", "请选择串口")
            return

        try:
            self.serial_port = serial.Serial(
                port=self.port_var.get(),
                baudrate=115200,
                timeout=1
            )
            self.is_connected = True
            self.connection_status.config(text="已连接", foreground="green")
            self.connect_btn.config(text="断开连接")
            self.start_btn.config(state="normal")
            print(f"✅ 设备连接成功: {self.port_var.get()}")
        except Exception as e:
            messagebox.showerror("连接失败", f"无法连接设备: {e}")
            print(f"❌ 连接失败: {e}")

    def disconnect_device(self):
        """断开设备连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.connection_status.config(text="未连接", foreground="red")
        self.connect_btn.config(text="连接设备")
        self.start_btn.config(state="disabled")
        print("🔌 设备已断开")

    def start_calibration(self):
        """开始校准"""
        if not self.is_connected:
            messagebox.showerror("错误", "请先连接设备")
            return

        self.calib_btn.config(state="disabled")
        self.calib_status.config(text="校准中...")

        def calibrate():
            try:
                result = self.calibration_system.run_calibration(self.serial_port)
                if result:
                    self.calib_status.config(text="校准完成", foreground="green")
                    print("✅ 校准完成")
                else:
                    self.calib_status.config(text="校准失败", foreground="red")
                    print("❌ 校准失败")
            except Exception as e:
                print(f"❌ 校准错误: {e}")
                self.calib_status.config(text="校准错误", foreground="red")
            finally:
                self.calib_btn.config(state="normal")

        threading.Thread(target=calibrate, daemon=True).start()

    def start_monitoring(self):
        """开始监测"""
        if not self.is_connected:
            messagebox.showerror("错误", "请先连接设备")
            return

        if not self.calibration_system.is_calibrated:
            messagebox.showerror("错误", "请先完成校准")
            return

        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        # 启动数据读取线程
        self.data_thread = threading.Thread(target=self.read_data, daemon=True)
        self.data_thread.start()

        # 启动动画
        self.animation = FuncAnimation(self.fig, self.update_plots,
                                     interval=100, blit=False)
        self.canvas.draw()

        print("🚀 开始实时监测")

    def stop_monitoring(self):
        """停止监测"""
        self.is_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None

        print("⏹️ 监测已停止")

    def read_data(self):
        """读取传感器数据"""
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        data = self.parse_sensor_data(line)
                        if data:
                            self.data_queue.put(data)
                time.sleep(0.01)
            except Exception as e:
                print(f"❌ 数据读取错误: {e}")
                break

    def parse_sensor_data(self, line):
        """解析传感器数据"""
        try:
            # 假设数据格式: EMG1,EMG2,EMG3,EMG4,GSR
            values = [float(x) for x in line.split(',')]
            if len(values) >= 5:
                return {
                    'emg': values[:4],
                    'gsr': values[4],
                    'timestamp': time.time()
                }
        except Exception:
            pass
        return None

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 处理数据队列
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                self.process_data(data)
            except queue.Empty:
                break

        # 更新EMG信号图
        self.ax1.clear()
        self.ax1.set_title('EMG信号', fontsize=12)
        self.ax1.set_xlabel('时间 (s)')
        self.ax1.set_ylabel('幅值')
        self.ax1.grid(True, alpha=0.3)

        if len(self.emg_history) > 0:
            time_axis = np.arange(len(self.emg_history)) * 0.1
            self.ax1.plot(time_axis, list(self.emg_history),
                         color=self.emotion_states[self.current_emotion]['color'],
                         linewidth=1.5, alpha=0.8)
            self.ax1.set_ylim(-1, 1)

        # 更新GSR信号图
        self.ax2.clear()
        self.ax2.set_title('GSR信号', fontsize=12)
        self.ax2.set_xlabel('时间 (s)')
        self.ax2.set_ylabel('电导 (μS)')
        self.ax2.grid(True, alpha=0.3)

        if len(self.gsr_history) > 0:
            time_axis = np.arange(len(self.gsr_history)) * 0.1
            self.ax2.plot(time_axis, list(self.gsr_history),
                         color=self.emotion_states[self.current_emotion]['color'],
                         linewidth=1.5, alpha=0.8)
            self.ax2.set_ylim(0, 10)

        # 更新3D手部模型
        self.setup_3d_hand()

        # 更新状态信息
        self.update_status()

        self.canvas.draw()

    def process_data(self, data):
        """处理传感器数据"""
        try:
            # 信号处理
            processed_emg = self.signal_engine.process_emg(data['emg'])
            processed_gsr = self.signal_engine.process_gsr(data['gsr'])

            # 情绪检测
            emotion_result = self.emotion_detector.detect_emotion(
                processed_emg, processed_gsr
            )

            if emotion_result:
                self.current_emotion = emotion_result['emotion']
                self.emotion_confidence = emotion_result['confidence']

            # 保存历史数据
            self.emg_history.append(np.mean(processed_emg))
            self.gsr_history.append(processed_gsr)
            self.emotion_history.append(self.current_emotion)

        except Exception as e:
            print(f"❌ 数据处理错误: {e}")

    def update_status(self):
        """更新状态信息"""
        self.status_text.delete(1.0, tk.END)

        emotion_info = self.emotion_states[self.current_emotion]
        status_info = f"""当前情绪: {emotion_info['emoji']} {emotion_info['description']}
置信度: {self.emotion_confidence:.2f}
连接状态: {'已连接' if self.is_connected else '未连接'}
校准状态: {'已完成' if self.calibration_system.is_calibrated else '未校准'}
监测状态: {'运行中' if self.is_running else '已停止'}"""

        self.status_text.insert(1.0, status_info)

    def setup_connections(self):
        """设置连接"""
        self.refresh_ports()

        # 绑定关闭事件
        def on_closing():
            if self.is_running:
                self.stop_monitoring()
            if self.is_connected:
                self.disconnect_device()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def run(self):
        """运行应用"""
        print("🚀 EmotionHand 真实版启动成功!")
        print("📋 使用说明:")
        print("   1. 选择串口并连接设备")
        print("   2. 进行60秒校准 (30秒静止 + 30秒轻握)")
        print("   3. 开始实时情绪监测")
        print("   4. 观察3D手部模型和信号变化")
        print("\n⚠️  确保传感器正确佩戴")

        self.root.mainloop()

if __name__ == "__main__":
    app = RealtimeEmotionHand()
    app.run()