# ⚡ ColorWin Monitor Pro 
> **Standard Version: ColorWin_Monitor_Final.py**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-PyQt6-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/platform-Windows-0078d7.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-important.svg)](https://opensource.org/licenses/MIT)

**ColorWin Monitor Pro** 是一款专为高频订单处理设计的实时监控与资产管理系统。它不仅拥有极客风的 UI 界面，还集成了自动化语音调度、动态催单提醒及隐私保护逻辑。

---

## 📸 界面预览 (UI Gallery)

| 实时监控主界面 | 历史流水数据中心 |
| :---: | :---: |
| ![Main UI](https://via.placeholder.com/300x500?text=Order+Card+With+Urge+Tag) | ![History UI](https://via.placeholder.com/300x500?text=History+Data+Center) |
| *支持催单高亮显示与呼吸灯监听状态* | *支持今日累计净利润统计与全量导出* |

---

## ✨ 核心特性

### 🚀 智能监控逻辑
- **实时同步**：每秒毫秒级轮询系统 JSON 数据，确保订单 0 延迟显示。
- **催单强提醒**：**[NEW]** 自动捕获 `state=1` 信号，首页卡片即刻点亮 `⚠️ 催单` 标签并追加红色标注。
- **状态感知**：自动处理“待处理、已核销、已超时”三种业务状态，UI 自动增删。

### 🎙️ 自动化全能语音 (TTS)
- **多维度播报**：新订单到达自动朗读金额、收款人及付款人详情。
- **动态循环**：针对未核销订单，每 30 秒进行一次周期性语音催单预警。
- **核销确认**：订单核销成功后，即刻同步语音反馈，无需反复确认屏幕。

### 🛡️ 隐私与安全 (Hacker Style)
- **数据混淆**：利润、原始返点采用随机滚动的 `DATA ENCRYPTED` 动画覆盖。
- **限时查阅**：敏感数据点击后仅显示 5 秒，随后自动归于加密状态，防止窥屏。
- **一键脱敏**：付款人姓名支持点击快速复制末位字符，兼顾便捷与隐私。

### 📊 资产对账与推送
- **全字段推送**：Telegram 机器人实时推送新单，包含金额、收款、付款、方式、原始返点、净利润及订单 ID。
- **自动对账单**：每日自动生成 `utf-8-sig` 编码的 CSV 报表，完美兼容 Excel 统计。
- **整点战报**：支持手动或定时向 Telegram 频道发送今日经营业绩汇总。

---

## 🛠️ 技术栈

- **GUI**: PyQt6 (高性能异步 UI 框架，支持自定义 QObject 通讯)
- **Data**: Pandas (用于高效 CSV 数据读写与流水分析)
- **Network**: Requests (异步集成 Telegram Bot API)
- **Voice**: Windows PowerShell System.Speech (原生驱动，无延迟语音合成)

---

## ⚙️ 配置文件说明 (config.json)

脚本首次运行将自动生成配置文件，您可以根据需求调整参数：

```json
{
    "tg_enable": true,            // 是否开启 Telegram 推送
    "tg_token": "YOUR_BOT_TOKEN", // TG 机器人令牌
    "tg_chat_id": "YOUR_CHAT_ID", // 接收推送的 ID
    "default_rate": 0.018,        // 默认利润费率
    "report_interval_hour": 1     // 自动推送战报的时间间隔
}
---

## ⚙️ 配置文件说明 (config.json)

脚本首次运行将自动生成配置文件，您可以根据需求调整参数。请注意，系统会自动识别 JSON 格式：

```json
{
    "tg_enable": true,            // 是否开启 Telegram 推送
    "tg_token": "YOUR_BOT_TOKEN", // TG 机器人令牌
    "tg_chat_id": "YOUR_CHAT_ID", // 接收推送的 ID
    "default_rate": 0.018,        // 默认利润费率 (0.018 = 1.8%)
    "report_interval_hour": 1     // 自动推送战报的时间间隔 (小时)
}
