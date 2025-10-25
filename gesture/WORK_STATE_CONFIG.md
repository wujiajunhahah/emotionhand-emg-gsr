# 🔧 工作状态感知配置指南

## 📋 配置概述

本文档详细说明如何将EchoWrist手势识别系统配置为工作状态感知系统。

## 🎯 工作状态定义

### 1. 状态分类标准

```python
WORK_STATES = {
    'focused_work': {
        'code': 'FW',
        'name': '专注工作',
        'description': '高度专注，手部稳定，手指有规律的轻微活动',
        'characteristics': {
            'hand_movement': 'minimal',
            'finger_activity': 'rhythmic',
            'gesture_speed': 'slow',
            'consistency': 'high'
        },
        'duration_range': (15, 120),  # 分钟
        'confidence_threshold': 0.85
    },
    'stress_state': {
        'code': 'SS',
        'name': '压力状态',
        'description': '焦虑或紧张，手部快速微动，握拳或手指抖动',
        'characteristics': {
            'hand_movement': 'tremor',
            'finger_activity': 'erratic',
            'gesture_speed': 'fast',
            'consistency': 'low'
        },
        'duration_range': (5, 30),
        'confidence_threshold': 0.80
    },
    'fatigue_state': {
        'code': 'FS',
        'name': '疲劳状态',
        'description': '身体疲劳，手部下垂，动作缓慢无力',
        'characteristics': {
            'hand_movement': 'declining',
            'finger_activity': 'minimal',
            'gesture_speed': 'very_slow',
            'consistency': 'medium'
        },
        'duration_range': (10, 60),
        'confidence_threshold': 0.75
    },
    'relaxed_state': {
        'code': 'RS',
        'name': '放松状态',
        'description': '身心放松，手部自然舒展，动作平滑',
        'characteristics': {
            'hand_movement': 'natural',
            'finger_activity': 'casual',
            'gesture_speed': 'medium',
            'consistency': 'high'
        },
        'duration_range': (5, 45),
        'confidence_threshold': 0.80
    },
    'creative_thinking': {
        'code': 'CT',
        'name': '创意思考',
        'description': '思考创新，手部多样化动作，频繁变化姿势',
        'characteristics': {
            'hand_movement': 'varied',
            'finger_activity': 'dynamic',
            'gesture_speed': 'variable',
            'consistency': 'low'
        },
        'duration_range': (10, 90),
        'confidence_threshold': 0.75
    }
}
```

## 🎛️ 手势映射配置

### 1. 手势到状态的映射

```python
GESTURE_TO_STATE_MAPPING = {
    # 专注工作手势
    'typing_steady': {
        'target_state': 'focused_work',
        'weight': 0.9,
        'duration_threshold': 30  # 秒
    },
    'mouse_steady': {
        'target_state': 'focused_work',
        'weight': 0.8,
        'duration_threshold': 45
    },
    'writing_steady': {
        'target_state': 'focused_work',
        'weight': 0.85,
        'duration_threshold': 30
    },

    # 压力状态手势
    'finger_tapping': {
        'target_state': 'stress_state',
        'weight': 0.8,
        'duration_threshold': 15
    },
    'hand_wringing': {
        'target_state': 'stress_state',
        'weight': 0.95,
        'duration_threshold': 10
    },
    'fist_clenching': {
        'target_state': 'stress_state',
        'weight': 0.9,
        'duration_threshold': 20
    },

    # 疲劳状态手势
    'hand_dropping': {
        'target_state': 'fatigue_state',
        'weight': 0.85,
        'duration_threshold': 25
    },
    'slow_movements': {
        'target_state': 'fatigue_state',
        'weight': 0.7,
        'duration_threshold': 30
    },

    # 放松状态手势
    'open_palm': {
        'target_state': 'relaxed_state',
        'weight': 0.8,
        'duration_threshold': 20
    },
    'gentle_stretching': {
        'target_state': 'relaxed_state',
        'weight': 0.85,
        'duration_threshold': 15
    },

    # 创意思考手势
    'varied_gestures': {
        'target_state': 'creative_thinking',
        'weight': 0.75,
        'duration_threshold': 25
    },
    'hand_chin_support': {
        'target_state': 'creative_thinking',
        'weight': 0.8,
        'duration_threshold': 20
    }
}
```

## 📊 信号处理配置

### 1. 声纳信号参数

```python
ACOUSTIC_CONFIG = {
    'sampling_rate': 40000,  # Hz
    'fft_size': 2048,
    'window_size': 1024,
    'hop_length': 512,
    'frequency_bands': {
        'low_freq': (20, 200),      # Hz - 手部大动作
        'mid_freq': (200, 2000),    # Hz - 手指活动
        'high_freq': (2000, 8000)   # Hz - 微动和噪声
    },
    'feature_extraction': {
        'spectral_centroid': True,
        'spectral_rolloff': True,
        'zero_crossing_rate': True,
        'mfcc': True,
        'chroma': False,
        'spectral_contrast': True
    }
}
```

### 2. 特征提取配置

```python
FEATURE_CONFIG = {
    'time_domain': {
        'mean': True,
        'std': True,
        'variance': True,
        'skewness': True,
        'kurtosis': True,
        'rms': True,
        'peak_to_peak': True
    },
    'frequency_domain': {
        'spectral_centroid': True,
        'spectral_bandwidth': True,
        'spectral_rolloff': True,
        'spectral_flux': True,
        'mfcc': 13,  # 13个MFCC系数
        'chroma': 12  # 12个色度特征
    },
    'time_frequency': {
        'cqt': True,  # Constant-Q Transform
        'stft': True,  # Short-Time Fourier Transform
        'wavelet': True  # 小波变换
    }
}
```

## 🤖 模型配置

### 1. 深度学习模型架构

```python
MODEL_CONFIG = {
    'input_shape': (30, 128),  # (时间步长, 特征维度)
    'num_classes': 5,  # 5种工作状态
    'architecture': {
        'type': 'LSTM_BiDirectional',
        'layers': [
            {
                'type': 'LSTM',
                'units': 128,
                'return_sequences': True,
                'dropout': 0.2
            },
            {
                'type': 'LSTM',
                'units': 64,
                'return_sequences': False,
                'dropout': 0.2
            },
            {
                'type': 'Dense',
                'units': 32,
                'activation': 'relu',
                'dropout': 0.3
            },
            {
                'type': 'Dense',
                'units': 5,
                'activation': 'softmax'
            }
        ]
    },
    'training': {
        'batch_size': 32,
        'epochs': 100,
        'learning_rate': 0.001,
        'optimizer': 'adam',
        'loss': 'categorical_crossentropy',
        'metrics': ['accuracy', 'precision', 'recall']
    }
}
```

### 2. 传统机器学习配置

```python
ML_CONFIG = {
    'algorithms': {
        'random_forest': {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2
        },
        'svm': {
            'kernel': 'rbf',
            'C': 1.0,
            'gamma': 'scale',
            'probability': True
        },
        'xgboost': {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8
        }
    },
    'ensemble': {
        'method': 'voting',
        'weights': [0.4, 0.3, 0.3]  # RF, SVM, XGB
    }
}
```

## 📈 数据采集配置

### 1. 采集参数设置

```python
DATA_COLLECTION_CONFIG = {
    'session_duration': 300,  # 5分钟
    'sampling_rate': 40000,   # 40kHz
    'channels': 2,           # 立体声
    'bit_depth': 16,         # 16位
    'format': 'wav',         # WAV格式

    'gesture_settings': {
        'preparation_time': 3,    # 准备时间 (秒)
        'gesture_duration': 2,    # 手势持续时间 (秒)
        'rest_duration': 1,       # 休息时间 (秒)
        'repetitions': 5,         # 重复次数
        'random_order': True      # 随机顺序
    },

    'recording': {
        'audio_device': 'default',
        'camera_device': 0,
        'save_video': True,
        'save_audio': True,
        'sync_signal': True
    }
}
```

### 2. 标签配置

```python
LABEL_CONFIG = {
    'annotation_tool': 'label-studio',
    'label_format': 'json',
    'label_schema': {
        'work_state': {
            'type': 'classification',
            'classes': list(WORK_STATES.keys())
        },
        'gesture_type': {
            'type': 'classification',
            'classes': list(GESTURE_TO_STATE_MAPPING.keys())
        },
        'confidence': {
            'type': 'regression',
            'range': [0, 1]
        },
        'timestamp': {
            'type': 'timestamp'
        }
    }
}
```

## 🔍 实时处理配置

### 1. 流处理配置

```python
STREAMING_CONFIG = {
    'buffer_size': 1024,
    'overlap': 0.5,
    'processing_interval': 0.1,  # 100ms
    'smooth_window': 5,  # 平滑窗口大小

    'real_time_features': {
        'extract_mfcc': True,
        'extract_spectral': True,
        'extract_temporal': True,
        'feature_normalization': True
    },

    'prediction': {
        'model_update_interval': 1.0,  # 1秒更新一次
        'confidence_threshold': 0.7,
        'state_smoothing': True,
        'min_state_duration': 2.0  # 最小状态持续时间 (秒)
    }
}
```

### 2. 性能优化配置

```python
PERFORMANCE_CONFIG = {
    'gpu_acceleration': True,
    'batch_inference': True,
    'model_quantization': True,
    'feature_caching': True,

    'memory_management': {
        'max_memory_usage': '2GB',
        'cleanup_interval': 300,  # 5分钟
        'buffer_size': 1000
    },

    'threading': {
        'data_processing_threads': 2,
        'inference_threads': 1,
        'io_threads': 1
    }
}
```

## 📱 用户界面配置

### 1. 可视化配置

```python
UI_CONFIG = {
    'dashboard': {
        'refresh_rate': 1.0,  # 1秒刷新
        'chart_history': 60,  # 显示60秒历史
        'color_scheme': {
            'focused_work': '#2ECC71',
            'stress_state': '#E74C3C',
            'fatigue_state': '#F39C12',
            'relaxed_state': '#3498DB',
            'creative_thinking': '#9B59B6'
        }
    },

    'alerts': {
        'stress_threshold': 0.8,
        'fatigue_threshold': 0.7,
        'notification_types': ['popup', 'sound', 'email'],
        'alert_cooldown': 300  # 5分钟冷却时间
    }
}
```

## 📊 数据存储配置

### 1. 存储格式

```python
STORAGE_CONFIG = {
    'raw_data': {
        'format': 'hdf5',
        'compression': 'gzip',
        'chunk_size': 1024
    },
    'processed_data': {
        'format': 'parquet',
        'compression': 'snappy'
    },
    'metadata': {
        'format': 'json',
        'encryption': False
    },

    'database': {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'database': 'work_state_db',
        'table_names': {
            'sessions': 'work_sessions',
            'predictions': 'state_predictions',
            'users': 'user_profiles'
        }
    }
}
```

## 🔒 隐私和安全配置

```python
PRIVACY_CONFIG = {
    'data_anonymization': True,
    'local_processing': True,
    'encryption': {
        'at_rest': True,
        'in_transit': True,
        'algorithm': 'AES-256'
    },
    'retention_policy': {
        'raw_data_days': 7,
        'processed_data_days': 30,
        'analytics_data_days': 365
    },
    'gdpr_compliance': True
}
```

## 🧪 实验配置模板

### 1. A/B测试配置

```python
EXPERIMENT_CONFIG = {
    'ab_test': {
        'control_group': {
            'model_type': 'baseline',
            'feature_set': 'basic'
        },
        'treatment_group': {
            'model_type': 'enhanced',
            'feature_set': 'comprehensive'
        },
        'sample_size': 100,
        'duration_days': 14,
        'success_metrics': ['accuracy', 'user_satisfaction', 'engagement']
    }
}
```

---

**使用说明**: 复制相关配置到实际代码文件中，根据具体需求调整参数值。