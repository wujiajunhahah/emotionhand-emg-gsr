#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmotionHand 启动器 - 简化版启动脚本
实地运行专用
"""

import sys
import os
import time
import argparse
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    required_modules = ['numpy', 'matplotlib', 'scipy', 'tkinter']
    missing_modules = []

    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ 缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行: pip install numpy matplotlib scipy")
        return False

    return True

def check_zcf_projects():
    """检查zcf项目"""
    zcf_paths = [
        "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub",
        "/Users/wujiajun/Downloads/zcf/gesture",
        "/Users/wujiajun/Downloads/zcf/GestureSense_Complete_Project"
    ]

    found_projects = []
    for path in zcf_paths:
        if os.path.exists(path):
            found_projects.append(path)

    if found_projects:
        print(f"✅ 发现zcf项目: {len(found_projects)}个")
        for path in found_projects:
            print(f"   📁 {path}")
        return True
    else:
        print("⚠️ 未找到zcf项目，将使用简化版功能")
        return False

def start_integrated_version(demo_mode=True):
    """启动集成版"""
    try:
        print("🚀 启动EmotionHand集成版...")

        # 添加zcf项目路径
        zcf_paths = [
            "/Users/wujiajun/Downloads/zcf/EmotionHand_GitHub",
            "/Users/wujiajun/Downloads/zcf/gesture",
            "/Users/wujiajun/Downloads/zcf/GestureSense_Complete_Project"
        ]

        for path in zcf_paths:
            if os.path.exists(path):
                sys.path.insert(0, path)

        # 导入并启动集成版
        from emotionhand_integrated import EmotionHandIntegrated

        mode_text = "演示模式" if demo_mode else "实时模式"
        print(f"📊 运行模式: {mode_text}")

        app = EmotionHandIntegrated(demo_mode=demo_mode)
        app.run()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("🔄 尝试启动简化版...")
        start_simple_version(demo_mode)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

    return True

def start_simple_version(demo_mode=True):
    """启动简化版"""
    try:
        print("🚀 启动EmotionHand简化版...")

        from realtime_emotion_visualizer import RealtimeEmotionVisualizer

        mode_text = "演示模式" if demo_mode else "实时模式"
        print(f"📊 运行模式: {mode_text}")

        visualizer = RealtimeEmotionVisualizer(demo_mode=demo_mode)
        visualizer.run()

    except Exception as e:
        print(f"❌ 简化版启动失败: {e}")
        return False

    return True

def start_3d_visualization():
    """启动3D可视化"""
    try:
        print("🚀 启动3D手部可视化...")

        from visualize_hand_3d_optimized import Hand3DVisualizer

        visualizer = Hand3DVisualizer(demo_mode=True)
        visualizer.run()

    except Exception as e:
        print(f"❌ 3D可视化启动失败: {e}")
        return False

    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='EmotionHand 启动器')
    parser.add_argument('--mode', choices=['demo', 'real', '3d'], default='demo',
                       help='运行模式: demo(演示), real(实时), 3d(3D可视化)')
    parser.add_argument('--check', action='store_true',
                       help='只检查依赖和项目，不启动')

    args = parser.parse_args()

    print("=" * 60)
    print("🎯 EmotionHand 启动器 v1.0")
    print("=" * 60)

    # 检查依赖
    print("\n🔍 检查依赖...")
    if not check_dependencies():
        input("按回车键退出...")
        return

    # 检查zcf项目
    print("\n🔍 检查zcf项目...")
    has_zcf = check_zcf_projects()

    if args.check:
        print("\n✅ 检查完成")
        input("按回车键退出...")
        return

    # 根据模式启动
    print(f"\n🚀 启动模式: {args.mode}")

    if args.mode == '3d':
        success = start_3d_visualization()
    elif args.mode == 'demo':
        success = start_integrated_version(demo_mode=True)
    elif args.mode == 'real':
        success = start_integrated_version(demo_mode=False)
    else:
        print("❌ 未知模式")
        success = False

    if not success:
        print("\n❌ 启动失败，请检查错误信息")
        input("按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        input("按回车键退出...")