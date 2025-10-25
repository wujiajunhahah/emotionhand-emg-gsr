/*
  EmotionHand Arduino 代码
  硬件: Seeed Studio XIAO ESP32C3

  传感器连接:
  1. EMG模块: Advancer Technologies Muscle Sensor v3
     - +Vs → XIAO 3V3
     - GND → XIAO GND
     - -Vs → XIAO GND
     - SIG → XIAO D2 (GPIO2)

  2. GSR模块: Grove GSR v1.2
     - VCC → XIAO 3V3
     - GND → XIAO GND
     - SIG → XIAO D3 (GPIO3)

  输出格式: "EMG,GSR"
  波特率: 115200
  采样率: ~1000Hz
*/

// 引脚定义
const int EMG_PIN = 2;  // D2 (GPIO2)
const int GSR_PIN = 3;  // D3 (GPIO3)

// 采样参数
const int SAMPLE_RATE_US = 1000;  // 1000Hz采样率 (1ms)
const unsigned long BAUD_RATE = 115200;

// 滤波参数
const int EMG_FILTER_SIZE = 5;    // EMG移动平均滤波
const int GSR_FILTER_SIZE = 10;   // GSR移动平均滤波

// 数据缓冲区
float emgBuffer[EMG_FILTER_SIZE];
float gsrBuffer[GSR_FILTER_SIZE];
int emgIndex = 0;
int gsrIndex = 0;

// 校准参数
float emgBaseline = 0.0;
float gsrBaseline = 0.0;
bool calibrated = false;
const int CALIBRATION_SAMPLES = 1000;  // 1秒校准

// 统计参数
unsigned long sampleCount = 0;
unsigned long lastOutputTime = 0;
const unsigned long OUTPUT_INTERVAL_MS = 10;  // 每10ms输出一次 (100Hz显示)

void setup() {
  // 初始化串口
  Serial.begin(BAUD_RATE);
  delay(2000);

  Serial.println("EmotionHand Sensor System");
  Serial.println("Hardware: XIAO ESP32C3");
  Serial.println("EMG: Muscle Sensor v3 (Pin D2)");
  Serial.println("GSR: Grove GSR v1.2 (Pin D3)");
  Serial.println("Sample Rate: 1000Hz");
  Serial.println("Output Format: EMG,GSR");
  Serial.println("========================");

  // 初始化引脚
  pinMode(EMG_PIN, INPUT);
  pinMode(GSR_PIN, INPUT);

  // 初始化缓冲区
  for(int i = 0; i < EMG_FILTER_SIZE; i++) {
    emgBuffer[i] = 0.0;
  }
  for(int i = 0; i < GSR_FILTER_SIZE; i++) {
    gsrBuffer[i] = 0.0;
  }

  // 校准基线
  Serial.println("Calibrating sensors... Keep muscles relaxed!");
  calibrateSensors();

  Serial.println("System ready!");
  Serial.println("Output format: EMG(0-3.3V),GSR_Conductance(μS)");
  Serial.println("=====================================");

  lastOutputTime = millis();
}

void loop() {
  // 高频采样
  sampleSensors();

  // 低频输出 (100Hz显示)
  if (millis() - lastOutputTime >= OUTPUT_INTERVAL_MS) {
    outputData();
    lastOutputTime = millis();
  }
}

void calibrateSensors() {
  float emgSum = 0.0;
  float gsrSum = 0.0;

  Serial.println("Calibrating...");

  for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
    // 读取EMG (原始ADC值)
    int emgRaw = analogRead(EMG_PIN);
    float emgVoltage = emgRaw * (3.3 / 4095.0);  // 转换为电压 (12位ADC)
    emgSum += emgVoltage;

    // 读取GSR
    int gsrRaw = analogRead(GSR_PIN);
    float gsrResistance = calculateGSRResistance(gsrRaw);
    float gsrConductance = 1.0 / gsrResistance * 1000000.0;  // 转换为微西门子
    gsrSum += gsrConductance;

    // 延迟以维持采样率
    delayMicroseconds(SAMPLE_RATE_US);

    // 进度显示
    if (i % 100 == 0) {
      Serial.print(".");
    }
  }

  emgBaseline = emgSum / CALIBRATION_SAMPLES;
  gsrBaseline = gsrSum / CALIBRATION_SAMPLES;

  Serial.println();
  Serial.print("EMG Baseline: ");
  Serial.print(emgBaseline, 3);
  Serial.println("V");
  Serial.print("GSR Baseline: ");
  Serial.print(gsrBaseline, 1);
  Serial.println(" μS");

  calibrated = true;
}

void sampleSensors() {
  // 读取EMG信号
  int emgRaw = analogRead(EMG_PIN);
  float emgVoltage = emgRaw * (3.3 / 4095.0);  // 12位ADC，3.3V参考电压

  // EMG滤波 (移动平均)
  emgBuffer[emgIndex] = emgVoltage;
  emgIndex = (emgIndex + 1) % EMG_FILTER_SIZE;
  float emgFiltered = getAverage(emgBuffer, EMG_FILTER_SIZE);

  // 读取GSR信号
  int gsrRaw = analogRead(GSR_PIN);
  float gsrResistance = calculateGSRResistance(gsrRaw);
  float gsrConductance = 1.0 / gsrResistance * 1000000.0;  // 微西门子

  // GSR滤波 (移动平均)
  gsrBuffer[gsrIndex] = gsrConductance;
  gsrIndex = (gsrIndex + 1) % GSR_FILTER_SIZE;
  float gsrFiltered = getAverage(gsrBuffer, GSR_FILTER_SIZE);

  // 存储当前值
  currentEMG = emgFiltered;
  currentGSR = gsrFiltered;

  sampleCount++;
}

void outputData() {
  // 输出CSV格式: EMG,GSR
  Serial.print(currentEMG, 4);  // EMG电压，4位小数
  Serial.print(",");
  Serial.println(currentGSR, 2);  // GSR电导，2位小数
}

float calculateGSRResistance(int rawValue) {
  // 根据Grove GSR v1.2的公式计算电阻
  // R = ((1024 + 2 × ADC) × 10000) / (512 - ADC)
  float numerator = (1024.0 + 2.0 * rawValue) * 10000.0;
  float denominator = 512.0 - rawValue;

  if (denominator <= 0) {
    return 500000.0;  // 防止除零，返回最大电阻
  }

  float resistance = numerator / denominator;

  // 限制在合理范围内 (50KΩ - 500KΩ)
  if (resistance < 50000.0) {
    resistance = 50000.0;
  } else if (resistance > 500000.0) {
    resistance = 500000.0;
  }

  return resistance;
}

float getAverage(float buffer[], int size) {
  float sum = 0.0;
  for (int i = 0; i < size; i++) {
    sum += buffer[i];
  }
  return sum / size;
}

// 全局变量 (用于在函数间共享)
float currentEMG = 0.0;
float currentGSR = 0.0;

// 可选：添加一些诊断信息输出
void printDiagnostics() {
  static unsigned long lastDiagTime = 0;

  if (millis() - lastDiagTime >= 5000) {  // 每5秒输出一次诊断信息
    lastDiagTime = millis();

    Serial.print("DIAG: EMG=");
    Serial.print(currentEMG, 3);
    Serial.print("V, GSR=");
    Serial.print(currentGSR, 1);
    Serial.print("μS, Samples=");
    Serial.println(sampleCount);
  }
}