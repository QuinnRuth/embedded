// 传感器引脚
const int sensorLeftPin = 6;
const int sensorRightPin = 7;

// 电机引脚
const int motorLeftPin = 8;
const int motorRightPin = 9;

void setup() {
    // 设置传感器引脚为输入模式
    pinMode(sensorLeftPin, INPUT);
    pinMode(sensorRightPin, INPUT);

    // 设置电机引脚为输出模式
    pinMode(motorLeftPin, OUTPUT);
    pinMode(motorRightPin, OUTPUT);

    // 确保启动时电机是停止的
    stopMotors();
}

void loop() {
    // 读取传感器的数字状态 (0代表在白底上, 1代表在黑线上)
    bool isLeftOnBlack = (digitalRead(sensorLeftPin) == 1);
    bool isRightOnBlack = (digitalRead(sensorRightPin) == 1);

    // 根据传感器状态执行对应动作
    if (!isLeftOnBlack && !isRightOnBlack) {
        // 状态: [白, 白] -> 前进
        goForward();
    }
    else if (isLeftOnBlack && !isRightOnBlack) {
        // 状态: [黑, 白] -> 平滑左转
        turnLeftGently();
    }
    else if (!isLeftOnBlack && isRightOnBlack) {
        // 状态: [白, 黑] -> 平滑右转
        turnRightGently();
    }
    else {
        // 状态: [黑, 黑] -> 停止
        stopMotors();
    }
}

// 小车前进
void goForward() {
    digitalWrite(motorLeftPin, HIGH);
    digitalWrite(motorRightPin, HIGH);
}

// 平滑左转 (左轮停, 右轮前进)
void turnLeftGently() {
    digitalWrite(motorLeftPin, LOW);
    digitalWrite(motorRightPin, HIGH);
}

// 平滑右转 (左轮前进, 右轮停)
void turnRightGently() {
    digitalWrite(motorLeftPin, HIGH);
    digitalWrite(motorRightPin, LOW);
}

// 电机停止
void stopMotors() {
    digitalWrite(motorLeftPin, LOW);
    digitalWrite(motorRightPin, LOW);
}