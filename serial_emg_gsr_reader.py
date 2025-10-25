#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMG+GSR 串口数据接收器
配合 Arduino XIAO ESP32C3 使用
实时读取 EMG 和 GSR 信号数据

硬件配置:
- EMG: Muscle Sensor v3 (Pin D2)
- GSR: Grove GSR v1.2 (Pin D3)
- 波特率: 115200
- 输出格式: "EMG,GSR"
"""

import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from collections import deque
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置matplotlib字体
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

class SerialEMGGSRReader:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("EMG+GSR 实时数据接收器")
        self.root.geometry("1400x800")

        # 串口连接
        self.serial_port = None
        self.is_connected = False
        self.port_name = ""
        self.baud_rate = 115200

        # 数据存储
        self.emg_data = deque(maxlen=1000)
        self.gsr_data = deque(maxlen=1000)
        self.time_stamps = deque(maxlen=1000)
        self.raw_emg_data = deque(maxlen=1000)
        self.raw_gsr_data = deque(maxlen=1000)

        # 数据处理参数
        self.emg_baseline = 0.0
        self.gsr_baseline = 0.0
        self.baseline_samples = 0
        self.calibration_mode = True
        self.calibration_count = 0
        self.calibration_target = 1000  # 1秒校准数据

        # 统计信息
        self.sample_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.last_data_time = 0

        # 动画控制
        self.animation = None
        self.is_running = False

        # 设置界面
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame,
                               text="EMG+GSR 实时数据接收器 - XIAO ESP32C3",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)

        # 连接控制框架
        connection_frame = ttk.LabelFrame(main_frame, text="串口连接", padding=10)
        connection_frame.pack(fill=tk.X, pady=5)

        # 串口选择
        port_frame = ttk.Frame(connection_frame)
        port_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(port_frame, text="串口:").pack(side=tk.LEFT, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var,
                                       state="readonly", width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(port_frame, text="刷新端口",
                                     command=self.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(port_frame, text="连接",
                                     command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.connection_status = ttk.Label(connection_frame, text="未连接",
                                          foreground="red", font=('Arial', 12, 'bold'))
        self.connection_status.pack(side=tk.LEFT, padx=20)

        # 校准控制框架
        calib_frame = ttk.LabelFrame(main_frame, text="校准状态", padding=10)
        calib_frame.pack(fill=tk.X, pady=5)

        self.calib_status = ttk.Label(calib_frame, text="等待校准...",
                                     font=('Arial', 11))
        self.calib_status.pack(side=tk.LEFT, padx=10)

        self.calib_btn = ttk.Button(calib_frame, text="重新校准",
                                    command=self.start_calibration)
        self.calib_btn.pack(side=tk.LEFT, padx=10)

        self.calib_progress = ttk.Progressbar(calib_frame, length=200,
                                             mode='determinate')
        self.calib_progress.pack(side=tk.LEFT, padx=10)

        # 实时数据框架
        data_frame = ttk.LabelFrame(main_frame, text="实时数据", padding=10)
        data_frame.pack(fill=tk.X, pady=5)

        self.data_info = ttk.Label(data_frame,
                                   text="EMG: 0.000V | GSR: 0.0μS | 采样率: 0Hz | 错误率: 0%",
                                   font=('Arial', 12))
        self.data_info.pack()

        # 创建图表
        self.create_plots(main_frame)

        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(control_frame, text="🚀 开始监测",
                                   command=self.start_monitoring, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹️ 停止监测",
                                  command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="💾 保存数据",
                  command=self.save_data).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="🔄 重置",
                  command=self.reset_data).pack(side=tk.LEFT, padx=5)

        # 初始化串口列表
        self.refresh_ports()

    def create_plots(self, parent):
        """创建图表"""
        # 创建matplotlib图形
        self.fig = plt.figure(figsize=(14, 6), facecolor='white')

        # EMG信号图
        self.ax_emg = self.fig.add_subplot(121)
        self.ax_emg.set_title('EMG信号 (0-3.3V)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('电压 (V)')
        self.ax_emg.grid(True, alpha=0.3)
        self.ax_emg.set_ylim(0, 3.3)

        # GSR信号图
        self.ax_gsr = self.fig.add_subplot(122)
        self.ax_gsr.set_title('GSR信号 (电导率)', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('电导率 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)
        self.ax_gsr.set_ylim(0, 20)

        # 嵌入到tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig.tight_layout()

    def refresh_ports(self):
        """刷新串口列表"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports

        if ports:
            # 尝试自动选择XIAO设备
            xiao_ports = [p for p in ports if 'USB' in p or 'SLAB' in p or 'CP210' in p]
            if xiao_ports:
                self.port_combo.set(xiao_ports[0])
            else:
                self.port_combo.set(ports[0])

        print(f"🔍 发现串口: {ports}")

    def toggle_connection(self):
        """切换连接状态"""
        if not self.is_connected:
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        """连接串口"""
        if not self.port_var.get():
            messagebox.showerror("错误", "请选择串口")
            return

        try:
            self.serial_port = serial.Serial(
                port=self.port_var.get(),
                baudrate=self.baud_rate,
                timeout=0.1,
                write_timeout=0.1
            )
            self.is_connected = True
            self.port_name = self.port_var.get()
            self.connection_status.config(text="已连接", foreground="green")
            self.connect_btn.config(text="断开")
            self.start_btn.config(state=tk.NORMAL)

            # 启动数据读取线程
            self.data_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.data_thread.start()

            print(f"✅ 串口连接成功: {self.port_name}")

        except Exception as e:
            messagebox.showerror("连接失败", f"无法连接串口: {e}")
            print(f"❌ 连接失败: {e}")

    def disconnect_serial(self):
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.connection_status.config(text="未连接", foreground="red")
        self.connect_btn.config(text="连接")
        self.start_btn.config(state=tk.DISABLED)
        print("🔌 串口已断开")

    def start_calibration(self):
        """开始校准"""
        if not self.is_connected:
            messagebox.showwarning("提示", "请先连接串口")
            return

        self.calibration_mode = True
        self.calibration_count = 0
        self.calib_status.config(text="正在校准... 请保持肌肉放松！")
        self.calib_progress['value'] = 0
        print("🎯 开始校准，请保持肌肉放松...")

    def read_serial_data(self):
        """读取串口数据"""
        while self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()

                    if line:
                        self.process_data_line(line)

            except Exception as e:
                self.error_count += 1
                print(f"❌ 数据读取错误: {e}")

            time.sleep(0.001)  # 1ms延迟

    def process_data_line(self, line):
        """处理数据行"""
        try:
            # 解析CSV格式: EMG,GSR
            parts = line.split(',')
            if len(parts) >= 2:
                emg_value = float(parts[0])
                gsr_value = float(parts[1])

                self.last_data_time = time.time()

                # 校准处理
                if self.calibration_mode:
                    self.process_calibration_data(emg_value, gsr_value)
                else:
                    self.process_normal_data(emg_value, gsr_value)

                self.sample_count += 1

        except ValueError as e:
            self.error_count += 1
            if self.error_count % 10 == 0:  # 每10个错误显示一次
                print(f"⚠️ 数据解析错误 (累计{self.error_count}次): {e}")

    def process_calibration_data(self, emg_value, gsr_value):
        """处理校准数据"""
        self.emg_baseline += emg_value
        self.gsr_baseline += gsr_value
        self.calibration_count += 1

        # 更新进度条
        progress = (self.calibration_count / self.calibration_target) * 100
        self.calib_progress['value'] = progress

        # 校准完成
        if self.calibration_count >= self.calibration_target:
            self.emg_baseline /= self.calibration_count
            self.gsr_baseline /= self.calibration_count
            self.calibration_mode = False

            self.calib_status.config(
                text=f"校准完成 - EMG基线: {self.emg_baseline:.3f}V, GSR基线: {self.gsr_baseline:.1f}μS"
            )
            self.calib_progress['value'] = 100

            print(f"✅ 校准完成:")
            print(f"   EMG基线: {self.emg_baseline:.3f}V")
            print(f"   GSR基线: {self.gsr_baseline:.1f}μS")

    def process_normal_data(self, emg_value, gsr_value):
        """处理正常数据"""
        current_time = time.time() - self.start_time

        # 存储原始数据
        self.raw_emg_data.append(emg_value)
        self.raw_gsr_data.append(gsr_value)

        # 相对于基线的处理
        if self.emg_baseline > 0:
            # EMG标准化 (相对于基线)
            normalized_emg = (emg_value - self.emg_baseline) / 3.3  # 标准化到[-1, 1]
        else:
            normalized_emg = emg_value / 3.3

        # GSR处理
        if self.gsr_baseline > 0:
            # GSR变化率
            gsr_change = gsr_value - self.gsr_baseline
        else:
            gsr_change = gsr_value

        # 存储处理后的数据
        self.time_stamps.append(current_time)
        self.emg_data.append(normalized_emg)
        self.gsr_data.append(gsr_change)

    def update_plots(self, frame):
        """更新图表"""
        if not self.is_running:
            return

        # 更新EMG图
        self.ax_emg.clear()
        self.ax_emg.set_title('EMG信号 (标准化)', fontsize=12, fontweight='bold')
        self.ax_emg.set_xlabel('时间 (s)')
        self.ax_emg.set_ylabel('标准化值')
        self.ax_emg.grid(True, alpha=0.3)

        if len(self.emg_data) > 0:
            times = list(self.time_stamps)
            self.ax_emg.plot(times, list(self.emg_data), 'b-', linewidth=1.5, alpha=0.8)
            self.ax_emg.set_ylim(-1, 1)

            # 添加基线
            if self.emg_baseline > 0:
                self.ax_emg.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='基线')
                self.ax_emg.legend()

        # 更新GSR图
        self.ax_gsr.clear()
        self.ax_gsr.set_title('GSR信号 (相对变化)', fontsize=12, fontweight='bold')
        self.ax_gsr.set_xlabel('时间 (s)')
        self.ax_gsr.set_ylabel('变化量 (μS)')
        self.ax_gsr.grid(True, alpha=0.3)

        if len(self.gsr_data) > 0:
            times = list(self.time_stamps)
            self.ax_gsr.plot(times, list(self.gsr_data), 'r-', linewidth=1.5, alpha=0.8)

            # 自动调整y轴范围
            if len(self.gsr_data) > 0:
                gsr_min = min(self.gsr_data)
                gsr_max = max(self.gsr_data)
                margin = (gsr_max - gsr_min) * 0.1
                self.ax_gsr.set_ylim(gsr_min - margin, gsr_max + margin)

        # 更新数据信息
        self.update_data_info()

        # 刷新画布
        self.canvas.draw()

    def update_data_info(self):
        """更新数据显示"""
        current_time = time.time() - self.start_time
        sample_rate = self.sample_count / current_time if current_time > 0 else 0
        error_rate = (self.error_count / (self.sample_count + self.error_count)) * 100 if (self.sample_count + self.error_count) > 0 else 0

        emg_value = self.emg_data[-1] if len(self.emg_data) > 0 else 0
        gsr_value = self.gsr_data[-1] if len(self.gsr_data) > 0 else 0

        info_text = f"EMG: {emg_value:.3f} | GSR: {gsr_value:.1f}μS | 采样率: {sample_rate:.1f}Hz | 错误率: {error_rate:.1f}%"
        self.data_info.config(text=info_text)

    def start_monitoring(self):
        """开始监测"""
        if not self.is_connected:
            messagebox.showwarning("提示", "请先连接串口")
            return

        if self.calibration_mode:
            messagebox.showwarning("提示", "请等待校准完成")
            return

        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        # 创建动画
        from matplotlib.animation import FuncAnimation
        self.animation = FuncAnimation(self.fig, self.update_plots,
                                     interval=50, blit=False)  # 20Hz更新
        self.canvas.draw()

        print("🚀 开始实时监测")

    def stop_monitoring(self):
        """停止监测"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None

        print("⏹️ 停止监测")

    def save_data(self):
        """保存数据"""
        if len(self.emg_data) == 0:
            messagebox.showwarning("提示", "没有数据可保存")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emg_gsr_data_{timestamp}.json"

            data = {
                'timestamp': timestamp,
                'duration': time.time() - self.start_time,
                'sample_count': self.sample_count,
                'error_count': self.error_count,
                'calibration': {
                    'emg_baseline': self.emg_baseline,
                    'gsr_baseline': self.gsr_baseline,
                    'calibration_samples': self.calibration_target
                },
                'raw_data': {
                    'emg': list(self.raw_emg_data),
                    'gsr': list(self.raw_gsr_data),
                    'timestamps': list(self.time_stamps)
                },
                'processed_data': {
                    'emg_normalized': list(self.emg_data),
                    'gsr_changes': list(self.gsr_data)
                },
                'hardware_info': {
                    'port': self.port_name,
                    'baud_rate': self.baud_rate,
                    'emg_sensor': 'Muscle Sensor v3',
                    'gsr_sensor': 'Grove GSR v1.2',
                    'microcontroller': 'XIAO ESP32C3'
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"数据已保存到: {filename}")
            print(f"✅ 数据已保存到: {filename}")

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def reset_data(self):
        """重置数据"""
        result = messagebox.askyesno("确认", "确定要重置所有数据吗？")
        if result:
            # 清空数据
            self.emg_data.clear()
            self.gsr_data.clear()
            self.raw_emg_data.clear()
            self.raw_gsr_data.clear()
            self.time_stamps.clear()

            # 重置统计
            self.sample_count = 0
            self.error_count = 0
            self.start_time = time.time()

            # 重新校准
            self.start_calibration()

            messagebox.showinfo("完成", "数据已重置，开始重新校准")

    def run(self):
        """运行应用"""
        def on_closing():
            if self.is_running:
                self.stop_monitoring()
            if self.is_connected:
                self.disconnect_serial()
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        print("🚀 EMG+GSR 串口数据接收器启动成功!")
        print("📋 硬件配置:")
        print("   • 微控制器: XIAO ESP32C3")
        print("   • EMG传感器: Muscle Sensor v3 (Pin D2)")
        print("   • GSR传感器: Grove GSR v1.2 (Pin D3)")
        print("   • 波特率: 115200")
        print("   • 输出格式: EMG,GSR")
        print("\n🎮 使用说明:")
        print("   1. 选择串口并连接设备")
        print("   2. 等待自动校准完成")
        print("   3. 开始实时监测")
        print("   4. 保存数据供后续分析")

        self.root.mainloop()

if __name__ == "__main__":
    app = SerialEMGGSRReader()
    app.run()