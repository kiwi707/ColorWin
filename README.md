<div align="center">

# 🧠 ColorWin Monitor Pro

### 实时订单监听 · 自动对账 · 语音播报 · Telegram 推送 · 可视化监控面板

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

</div>

---

## 🚀 项目简介

**ColorWin Monitor Pro** 是一套基于 **Python + PyQt6** 的  
**本地实时订单监听与收益监控系统**。

系统通过监听本地 JSON 数据源，实现对订单生命周期的全流程监控，并以  
**可视化界面 + 语音提醒 + Telegram 推送** 的方式，确保关键事件不被遗漏。

> 设计目标：**低延迟 · 不漏单 · 强提醒 · 长时间稳定运行**

---

## ✨ 核心功能

### 🔴 实时订单监听
- 监听订单 / 核销 / 余额 / 历史数据文件
- 1 秒级 UI 刷新
- 订单去重与状态追踪
- 自动识别催单、超时、消失订单

---

### 💰 利润与费率引擎
- 动态费率（实时读取余额文件）
- 自动计算：
  - 原始返点
  - 单笔净利润
  - 今日累计净利润
- 核心数据加密显示（点击解锁）

---

### 🗣️ 语音播报系统（Windows）
- 新订单到达提醒
- 催单语音提示
- 核销成功播报
- 定时未处理订单提醒

> 基于 Windows `System.Speech.Synthesis`  
> 无需第三方 TTS 服务

---

### 📲 Telegram 推送通知
- 新订单推送
- 催单预警
- 核销成功通知
- 订单超时提醒
- 整点 / 手动经营战报

支持 HTML 格式，信息清晰、阅读友好。

---

### 📊 经营战报面板
- 实时统计：
  - 今日总业绩
  - 各收款人交易笔数
  - 累计交易金额
  - 总净利润
- 支持一键推送 Telegram
- 支持定时自动推送

---

### 🧾 自动对账与历史记录
- 每日自动生成 CSV 对账单  
  `对账单_YYYY_MM_DD.csv`
- 自动补录历史订单
- GUI 查看「今日全量流水」

---

### 🖥️ 高可视化 UI 设计
- 深色黑客风界面
- 呼吸灯运行状态指示
- 催单高亮标识
- 核心信息遮罩保护
- 一键复制辅助操作

---

## 🧱 项目结构

```text
.
├── ColorWin_Monitor_Final.py   # 主程序
├── config.json                # 配置文件（自动生成）
├── 对账单_YYYY_MM_DD.csv       # 每日对账单
├── clash_orders.json          # 实时订单数据源
├── clash_confirm.json         # 核销信号文件
├── clash_balance.json         # 余额 / 费率数据
└── clash_history.json         # 历史订单数据

{
  "tg_enable": true,
  "tg_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "tg_chat_id": "YOUR_CHAT_ID",
  "default_rate": 0.018,
  "report_interval_hour": 1
}

