#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 生产版快速启动脚本
"""

import sys
import os

def main():
    print("🎯 EmotionHand 生产版启动器")
    print("=" * 50)

    # 检查zcf项目路径
    zcf_path = "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub"
    if not os.path.exists(zcf_path):
        print(f"❌ 找不到zcf项目路径: {zcf_path}")
        return

    print(f"✅ 找到zcf项目: {zcf_path}")

    # 添加到Python路径
    sys.path.insert(0, zcf_path)

    # 检查核心模块
    modules = [
        ('signal_processing_engine', 'RealTimeSignalProcessor'),
        ('emotion_state_detector', 'EnsembleDetector'),
        ('calibration_system', 'CalibrationSystem'),
        ('data_collector', 'RealDataCollector')
    ]

    print("\n🔍 检查核心模块:")
    all_available = True
    for module_name, class_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"❌ {module_name}.{class_name}: {e}")
            all_available = False

    if not all_available:
        print("\n⚠️ 部分模块不可用，但仍可运行基础功能")

    print("\n🚀 启动生产版系统...")
    print("📋 功能特性:")
    print("   • 8通道EMG信号处理")
    print("   • GSR信号分析")
    print("   • 6种情绪状态识别")
    print("   • 3种手势识别")
    print("   • 实时质量监测")
    print("   • 数据采集和训练")

    try:
        # 导入并启动生产版
        from emotionhand_production import ProductionEmotionHand
        app = ProductionEmotionHand()
        app.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔄 尝试启动简化版...")
        try:
            from realtime_emotion_visualizer import RealtimeEmotionVisualizer
            visualizer = RealtimeEmotionVisualizer(demo_mode=True)
            visualizer.run()
        except Exception as e2:
            print(f"❌ 简化版启动也失败: {e2}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")