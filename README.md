# ⚡ ColorWin Monitor Pro 
> **Standard Version: ColorWin_Monitor_Final.py**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)](https://www.microsoft.com/windows)
[![Status](https://img.shields.io/badge/status-stable-00ff41.svg)](https://github.com/)

**ColorWin Monitor Pro** 是一款专为高频交易设计的实时订单监控与自动化对账系统。它不仅拥有黑客风格的 UI，还深度集成了 Telegram 机器人指令、语音合成播报及敏感数据隐私保护逻辑。

---

## 📸 界面特性 (UI Features)

| 核心组件 | 功能描述 |
| :--- | :--- |
| **实时订单卡片** | 动态显示金额、付款方式，支持点击复制付款人末位字符。 |
| **⚠️ 催单高亮** | **[NEW]** 自动检测 `state=1` 状态，实时点亮红色催单标签并同步语音提醒。 |
| **Hacker Spoiler** | 原始返点与净利润默认以乱码加密显示，点击后限时 5 秒解锁。 |
| **战报控制台** | 点击首页统计框可直接向 Telegram 推送今日经营实时战报。 |

---

## ✨ 核心特性 (Key Features)

### 🚀 自动化通知体系
- **Telegram 全量推送**：新订单到达时，自动发送包含金额、收款、付款、方式、返点、利润及订单 ID 的格式化消息。
- **智能语音调度**：采用 PowerShell 原生 TTS 引擎，支持新单播报、核销确认及 30 秒周期性待处理提醒。
- **订单 ID 追踪**：所有推送消息均包含 `<code>` 格式订单 ID，支持移动端一键点击复制。

### 📊 精准对账系统
- **自动对账单**：每日自动生成 `对账单_yyyy_mm_dd.csv`，兼容 Excel 直接开启。
- **实时费率同步**：自动监听服务器 `rebate` 费率变动，实时重算净利润。
- **历史中心**：内置数据中心弹窗，支持追溯今日最近 150 笔全量流水。

---

## 📦 Telegram 推送预览

```text
💰 新订单到达
━━━━━━━━━━━━
💵 金额：¥100.00
👤 收款：张三
👤 付款：李四
📑 方式：支付宝
🎁 原始返点：¥2.50
💹 净利：¥1.80
📑 ID：ORD12345678
