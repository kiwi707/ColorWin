# 🧠 ColorWin Monitor Pro  
> 实时订单监听 · 自动对账 · 语音播报 · Telegram 推送 · 可视化监控面板

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

---

## 📌 项目简介

**ColorWin Monitor Pro** 是一套基于 **Python + PyQt6** 开发的  
👉 **本地实时订单监听与收益监控系统**

它通过监听指定 JSON 文件（订单 / 核销 / 余额 / 历史数据），实现：

- 实时订单捕获
- 自动利润计算
- 语音播报提醒
- Telegram 机器人推送
- CSV 对账单自动生成
- 可视化 GUI 监控面板

适合 **高频订单处理 / 人工核销 / 对账场景**，强调 **低延迟、强提醒、不漏单**。

---

## ✨ 核心特性一览

### 🔴 实时监听
- 监听订单文件变化（新订单 / 催单 / 超时 / 核销）
- 1 秒级 UI 刷新
- 自动去重、防重复处理

### 💰 自动利润计算
- 支持动态费率（从余额文件实时读取）
- 自动计算：
  - 原始返点
  - 净利润
  - 今日累计利润

### 🗣️ 语音播报（Windows）
- 新订单语音提醒
- 催单语音提示
- 核销成功播报
- 定时未处理订单提醒

> 使用 `System.Speech.Synthesis`，无需第三方 TTS 服务

---

### 📲 Telegram 推送
- 新订单推送
- 催单提醒
- 核销成功通知
- 订单超时告警
- **整点 / 手动经营战报**

支持 HTML 格式，美观易读。

---

### 📊 经营战报系统
- 实时统计：
  - 今日总业绩
  - 各收款人笔数 & 金额
  - 总净利润
- 支持：
  - 点击手动推送
  - 定时自动推送（可配置）

---

### 🧾 自动对账 & 历史记录
- 每日自动生成 CSV 对账单  
  📁 `对账单_YYYY_MM_DD.csv`
- 自动补录历史订单
- 图形化「今日全量流水」弹窗查看

---

### 🖥️ 高可视化 UI
- 黑客风界面（深色 + 荧光绿）
- 呼吸灯状态指示
- 核心数据加密展示（点击解锁）
- 催单高亮标识
- 一键复制付款人末位字符

---

## 🧱 系统架构

├── ColorWin_Monitor_Final.py # 主程序

├── config.json # 配置文件（自动生成）

├── 对账单_YYYY_MM_DD.csv # 每日对账单

├── clash_orders.json # 实时订单数据

├── clash_confirm.json # 核销信号

├── clash_balance.json # 余额 / 费率数据

└── clash_history.json # 历史订单数据

---

## ⚙️ 配置说明（config.json）

程序首次运行会自动生成：

```json
{
  "tg_enable": true,
  "tg_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "tg_chat_id": "YOUR_CHAT_ID",
  "default_rate": 0.018,
  "report_interval_hour": 1
}
| 字段                   | 说明                   |
| -------------------- | -------------------- |
| tg_enable            | 是否启用 Telegram 推送     |
| tg_token             | Telegram Bot Token   |
| tg_chat_id           | 接收消息的 Chat ID        |
| default_rate         | 默认费率（如 1.8% = 0.018） |
| report_interval_hour | 自动战报间隔（小时）           |
🚀 运行方式
1️⃣ 环境要求

Windows 10 / 11

Python ≥ 3.9

2️⃣ 安装依赖
pip install pyqt6 pandas requests urllib3
3️⃣ 启动程序
python ColorWin_Monitor_Final.py
程序启动后将 置顶显示，并自动进入监听状态。
🔐 安全与设计说明

纯本地运行

不主动请求任何外部业务接口

Telegram 推送可完全关闭

JSON 文件监听机制，解耦业务系统

异常全面 try/except，保证长期稳定运行

📌 适用场景

高频人工核销订单

实时资金流监控

对账 & 收益统计

需要强提醒、不允许漏单的业务环境

🧠 设计理念

不是“看数据”，而是“被提醒”

人可以走神，系统不能

界面不是装饰，是“警觉工具”

所有关键状态必须 可视 + 可听 + 可推送

📜 License

仅供学习与内部使用
请遵守当地法律法规
