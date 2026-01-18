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
- **催单强提醒**：订单卡片集成 `⚠️ 对方已催单` 红色动态标签，视觉冲击力极强。
- **置顶悬浮**：默认开启窗口置顶，一边刷网页一边看单，两不误。

### 🎙️ 自动化全能语音 (TTS)
- **多维度播报**：新订单到达时自动朗读：`金额` + `支付方式` + `收款人` + `付款人`。
- **动态循环**：对未处理订单每 30 秒进行一次催单语音预警。
- **核销反馈**：核销成功即刻语音确认，无需反复查看屏幕。

### 🛡️ 隐私与安全
- **数据混淆**：利润、原始返点采用 Hacker 风格的乱码滚动动画显示。
- **点击查阅**：敏感数据仅在点击后显示 5 秒，随后自动加密，有效防止旁人窥屏。

### 📊 资产对账
- **自动对账单**：每日自动生成 `utf-8-sig` 编码的 CSV 报表，Excel 打开即看。
- **利润计算**：根据动态费率自动计算每笔净利润，实时汇总今日总收成。

---

## 🛠️ 技术栈

- **GUI**: PyQt6 (高性能异步 UI 框架)
- **Data**: Pandas (用于高效 CSV 数据处理)
- **Voice**: Windows PowerShell System.Speech (原生驱动，无需第三方 API)
- **Architecture**: 多线程异步架构 (主线程 UI + 语音线程 + 轮询线程)

---

## 🏃 快速开始

### 1. 克隆仓库
```bash
git clone [https://github.com/your-username/colorwin-monitor.git](https://github.com/your-username/colorwin-monitor.git)
