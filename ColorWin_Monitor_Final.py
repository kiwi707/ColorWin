import sys, json, os, subprocess, threading, time, queue, random, re, requests
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFrame,
    QHBoxLayout,
    QDialog,
)
from PyQt6.QtCore import QTimer, Qt, QObject
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. 配置系统 ---
CONFIG_FILE = "config.json"


def load_local_config():
    default_cfg = {
        "tg_enable": True,
        "tg_token": "84724pItVbI",
        "tg_chat_id": "858749",
        "default_rate": 0.018,
        "report_interval_hour": 1,
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_cfg, f, indent=4, ensure_ascii=False)
        return default_cfg
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default_cfg


_cfg = load_local_config()
TG_ENABLE = _cfg.get("tg_enable", True)
TG_TOKEN = _cfg.get("tg_token", "")
TG_CHAT_ID = _cfg.get("tg_chat_id", "")
DEFAULT_RATE = _cfg.get("default_rate", 0.018)
REPORT_HOUR = _cfg.get("report_interval_hour", 1)

O_FILE = "C:/Users/Public/clash_orders.json"
C_FILE = "C:/Users/Public/clash_confirm.json"
B_FILE = "C:/Users/Public/clash_balance.json"
H_FILE = "C:/Users/Public/clash_history.json"


def get_today_log_name():
    return f"对账单_{datetime.now().strftime('%Y_%m_%d')}.csv"


def send_tg_msg(msg):
    if not TG_ENABLE or not TG_TOKEN:
        return

    def _do_send():
        try:
            url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
            payload = {
                "chat_id": TG_CHAT_ID,
                "text": msg,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            requests.post(url, json=payload, timeout=15, verify=False)
        except:
            pass

    threading.Thread(target=_do_send, daemon=True).start()


# --- 2. 语音播报 ---
class VoiceWorker(QObject):
    def __init__(self):
        super().__init__()
        self.q = queue.Queue()
        threading.Thread(target=self._run, daemon=True).start()

    def say(self, text):
        self.q.put(text)

    def _run(self):
        while True:
            t = self.q.get()
            clean_t = str(t).replace("'", "").replace('"', "")
            cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_t}')"
            subprocess.run(
                ["powershell", "-Command", cmd], shell=True, creationflags=0x08000000
            )
            time.sleep(0.1)


# --- 3. UI 组件 ---
class BreathingLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.opacity, self.dir = 1.0, -1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.breath)
        self.timer.start(50)

    def breath(self):
        self.opacity += self.dir * 0.05
        if self.opacity <= 0.3:
            self.dir = 1
        elif self.opacity >= 1.0:
            self.dir = -1
        self.setStyleSheet(
            f"color: rgba(0, 255, 65, {self.opacity}); font-weight: bold;"
        )


class ClickRevealLabel(QLabel):
    def __init__(self, prefix="费率"):
        super().__init__()
        self.prefix, self.real_value, self.is_revealed = prefix, "0.0%", False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_display()

    def set_value(self, val):
        self.real_value = val
        if not self.is_revealed:
            self.update_display()

    def mousePressEvent(self, event):
        if not self.is_revealed:
            self.is_revealed = True
            self.setText(f"{self.prefix}: {self.real_value}")
            self.setStyleSheet(
                "color: #00ff41; font-weight: bold; background: #002200; border: 1px solid #00ff41; padding: 2px 8px; border-radius: 4px;"
            )
            QTimer.singleShot(5000, self.hide_value)

    def hide_value(self):
        self.is_revealed = False
        self.update_display()

    def update_display(self):
        if not self.is_revealed:
            self.setText(f"🔒 {self.prefix}隐藏")
            self.setStyleSheet(
                "color: #00ccff; font-style: italic; background: #001122; padding: 2px 8px; border-radius: 4px;"
            )


class HackerSpoiler(QWidget):
    def __init__(self, raw_comm, my_profit, score):
        super().__init__()
        self.is_revealed, self.raw_comm, self.my_profit, self.score = (
            False,
            raw_comm,
            my_profit,
            score,
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        self.btn = QPushButton()
        self.btn.clicked.connect(self.reveal)
        layout.addWidget(self.btn)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.anim)
        self.timer.start(100)
        self.set_masked_style()

    def set_masked_style(self):
        self.is_revealed = False
        self.btn.setStyleSheet(
            "background-color: #0a0a0a; color: #00ff41; border: 1px solid #1a331a; padding: 8px; border-radius: 6px; font-family: Consolas;"
        )

    def anim(self):
        if not self.is_revealed:
            self.btn.setText(
                f"核心数据已加密: {''.join(random.choice('0123456789$#@&%') for _ in range(8))}"
            )

    def reveal(self):
        if self.is_revealed:
            return
        self.is_revealed = True
        rate_p = (self.raw_comm / self.score * 100) if self.score > 0 else 0
        self.btn.setText(
            f"原始返点: ¥{self.raw_comm:.2f} ({rate_p:.1f}%) | 净利润: ¥{self.my_profit:.2f}"
        )
        self.btn.setStyleSheet(
            "background-color: #00ff41; color: #000000; font-weight: bold; padding: 8px; border-radius: 6px;"
        )
        QTimer.singleShot(5000, self.set_masked_style)


# --- 4. 历史记录弹窗 ---
class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据中心 - 今日全量流水")
        self.setMinimumSize(600, 700)
        self.setStyleSheet(
            "background-color: #050505; color: #00ff41; font-family: 'Consolas', 'Microsoft YaHei';"
        )
        layout = QVBoxLayout(self)
        self.hist_list = QListWidget()
        self.hist_list.setStyleSheet(
            "QListWidget { background: #000a00; border: 1px solid #1a331a; border-radius: 10px; padding: 5px; } QListWidget::item { border-bottom: 1px solid #001a00; padding: 12px; }"
        )
        layout.addWidget(self.hist_list)
        self.load_data()

    def load_data(self):
        log_f = get_today_log_name()
        if not os.path.exists(log_f):
            return
        try:
            df = pd.read_csv(log_f, encoding="utf-8-sig")
            for _, row in df.tail(150)[::-1].iterrows():
                st = str(row["状态"])
                comm_v = float(row.get("commission", 0))
                prof_v = float(row.get("净利润", 0))
                item_str = f"● [{st}] {row['时间']} | {row.get('方式','-')}\n金额: ¥{row['score']} (返:¥{comm_v:.2f} 净:¥{prof_v:.2f})\n收款: {row['userName']} | 付款: {row['payUserName']}\nID: {row.get('订单ID','-')}"
                item = QListWidgetItem(item_str)
                if st == "已核销":
                    item.setForeground(Qt.GlobalColor.green)
                elif st == "已超时":
                    item.setForeground(Qt.GlobalColor.red)
                self.hist_list.addItem(item)
        except:
            pass


# --- 5. 主监控程序 ---
class HackerMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active, self.confirmed, self.today_p, self.current_rate = (
            {},
            set(),
            0.0,
            DEFAULT_RATE,
        )
        self.all_known_ids, self.last_urge_voice, self.urged_ids = set(), {}, set()
        self.last_report_time = time.time()
        self.voice = VoiceWorker()
        self.cols = [
            "订单ID",
            "时间",
            "userName",
            "payUserName",
            "score",
            "commission",
            "净利润",
            "状态",
            "方式",
            "订单编号",
        ]
        self.init_ui()
        self.check_log_file()
        threading.Thread(target=self.loop_speak, daemon=True).start()
        self.tm = QTimer()
        self.tm.timeout.connect(self.sync)
        self.tm.start(1000)
        send_tg_msg("🚀 **系统启动成功**\nColorWin_Monitor_Final.py 正在运行")

    def init_ui(self):
        self.setWindowTitle("ColorWin 聚宝实时监控 Pro")
        self.setMinimumSize(480, 800)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        c = QWidget()
        self.setCentralWidget(c)
        self.main_lay = QVBoxLayout(c)

        self.p_btn = QPushButton("今日累计净利润: ¥0.00")
        self.p_btn.setStyleSheet(
            "QPushButton { font-size: 24px; font-weight: bold; color: #00ff41; background: #001a00; border: 2px solid #00ff41; border-radius: 12px; padding: 20px; }"
        )
        self.p_btn.clicked.connect(self.show_history)
        self.main_lay.addWidget(self.p_btn)

        self.report_box = QLabel("等待数据统计...")
        self.report_box.setWordWrap(True)
        self.report_box.setCursor(Qt.CursorShape.PointingHandCursor)
        self.report_box.setStyleSheet(
            "QLabel { background: #050505; border: 1px solid #1a331a; border-radius: 8px; color: #00ccff; font-size: 13px; font-family: 'Consolas', 'Microsoft YaHei'; padding: 12px; } QLabel:hover { border: 1px solid #00ccff; background: #001111; }"
        )
        self.report_box.mousePressEvent = self.manual_push_report_event
        self.main_lay.addWidget(self.report_box)

        self.list = QListWidget()
        self.list.setStyleSheet("background:transparent; border:none;")
        self.main_lay.addWidget(self.list)

        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(
            "background: #050505; border-top: 1px solid #1a331a; min-height: 50px;"
        )
        status_lay = QHBoxLayout(self.status_bar)
        self.state_lbl = BreathingLabel("● 正在监听系统")
        self.balance_lbl = QLabel("余额: ¥0.00 | 冻结: ¥0.00")
        self.balance_lbl.setStyleSheet("color: #ffd700; font-weight: bold;")
        self.rate_lbl = ClickRevealLabel(prefix="费率")
        status_lay.addWidget(self.state_lbl)
        status_lay.addStretch()
        status_lay.addWidget(self.balance_lbl)
        status_lay.addStretch()
        status_lay.addWidget(self.rate_lbl)
        self.main_lay.addWidget(self.status_bar)

    def manual_push_report_event(self, event):
        self.push_hourly_report()
        self.voice.say("战报已手动推送")

    def update_report_ui(self, df):
        if df.empty:
            return
        valid_df = df[df["状态"] == "已核销"]
        if valid_df.empty:
            self.report_box.setText("今日暂无核销记录 (点击可推送战报)")
            return
        counts = valid_df["userName"].value_counts()
        sums = valid_df.groupby("userName")["score"].sum()
        total_score = valid_df["score"].sum()
        header = f"<span style='color:#ffd700; font-weight:bold; font-size:15px;'>[今日总业绩: ¥{total_score:.2f}]</span><br/>"
        items = [
            f"{name}[{count}笔/¥{sums[name]:.0f}]" for name, count in counts.items()
        ]
        self.report_box.setText(header + "📊 战报: " + " | ".join(items))

    def push_hourly_report(self):
        log_n = get_today_log_name()
        if not os.path.exists(log_n):
            return
        try:
            df = pd.read_csv(log_n, encoding="utf-8-sig")
            valid_df = df[df["状态"] == "已核销"]
            if valid_df.empty:
                return
            counts = valid_df["userName"].value_counts()
            sums = valid_df.groupby("userName")["score"].sum()
            total_score, total_p = valid_df["score"].sum(), valid_df["净利润"].sum()
            msg = f"<b>📊 今日经营实时战报</b>\n━━━━━━━━━━━━\n💰 <b>总业绩：¥{total_score:.2f}</b>\n━━━━━━━━━━━━\n"
            for name, count in counts.items():
                msg += f"👤 {name}：<code>{count}</code> 笔 (¥{sums[name]:.2f})\n"
            msg += f"━━━━━━━━━━━━\n💹 总利润：<b>¥{total_p:.2f}</b>\n⏰ 触发时间：{datetime.now().strftime('%H:%M:%S')}"
            send_tg_msg(msg)
        except:
            pass

    def show_history(self):
        self.check_log_file()
        HistoryDialog(self).exec()

    def extract_info(self, o, mode="realtime"):
        if mode == "realtime":
            shoukuan, fukuan = (
                o.get("userName") or "未知收款",
                o.get("payUserName") or "未知付款",
            )
        else:
            shoukuan, fukuan = (
                o.get("cUserName") or "未知收款",
                o.get("userName") or "未知付款",
            )
        oid = str(o.get("id", "")).strip().upper()
        raw_t = o.get("created", "")
        t_display = (
            raw_t.split("T")[-1][:8]
            if "T" in raw_t
            else datetime.now().strftime("%H:%M:%S")
        )
        return {
            "s": float(o.get("score", 0)),
            "u": shoukuan,
            "p": fukuan,
            "rc": float(o.get("commission", 0)),
            "m": o.get("cBankName") or o.get("bankName") or "支付宝",
            "no": o.get("orderNo", "-"),
            "state": o.get("state"),
            "id": oid,
            "t": t_display,
        }

    def update_urged_status_ui(self, oid, is_urged):
        """实时刷新 UI 列表中特定订单的催单标签"""
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == oid:
                container = self.list.itemWidget(item)
                urge_tag = container.findChild(QLabel, "urge_tag")
                if urge_tag and urge_tag.isVisible() != is_urged:
                    urge_tag.setVisible(is_urged)
                    detail_lbl = container.findChild(QLabel, "detail_lbl")
                    if detail_lbl and is_urged:
                        base_text = detail_lbl.text().split("<font")[0]
                        detail_lbl.setText(
                            f"{base_text} <font color='#ff3131'>[已催单]</font>"
                        )
                break

    def check_log_file(self):
        log_n = get_today_log_name()
        if not os.path.exists(log_n):
            pd.DataFrame(columns=self.cols).to_csv(
                log_n, index=False, encoding="utf-8-sig"
            )
        try:
            df = pd.read_csv(log_n, encoding="utf-8-sig")
            df["订单ID"] = df["订单ID"].astype(str).str.strip().str.upper()
            self.all_known_ids = set(df["订单ID"].tolist())
            if os.path.exists(H_FILE):
                with open(H_FILE, "r", encoding="utf-16") as f:
                    h_data = json.load(f).get("data") or []
                    new_rows = []
                    for o in h_data:
                        info = self.extract_info(o, mode="history")
                        if info["id"] and info["id"] not in self.all_known_ids:
                            st_map = {1: "待处理", 2: "已核销", 3: "已超时"}
                            st_str = st_map.get(info["state"], "已完成")
                            p_val = (
                                info["s"] * self.current_rate
                                if st_str == "已核销"
                                else 0
                            )
                            new_rows.append(
                                [
                                    info["id"],
                                    info["t"],
                                    info["u"],
                                    info["p"],
                                    info["s"],
                                    info["rc"],
                                    round(p_val, 2),
                                    st_str,
                                    info["m"],
                                    info["no"],
                                ]
                            )
                    if new_rows:
                        df = pd.concat(
                            [df, pd.DataFrame(new_rows, columns=self.cols)],
                            ignore_index=True,
                        )
                        df.drop_duplicates(
                            subset=["订单ID"], keep="first", inplace=True
                        )
                        df.to_csv(log_n, index=False, encoding="utf-8-sig")
                        self.all_known_ids = set(df["订单ID"].tolist())
            self.today_p = df[df["状态"] == "已核销"]["净利润"].sum()
            self.p_btn.setText(f"今日累计净利润: ¥{self.today_p:.2f}")
            self.update_report_ui(df)
        except:
            pass

    def log_to_csv(self, oid, info, st="待处理", p=0):
        log_n = get_today_log_name()
        oid = str(oid).strip().upper()
        try:
            df = pd.read_csv(log_n, encoding="utf-8-sig")
            df["订单ID"] = df["订单ID"].astype(str).str.strip().str.upper()
            if oid in df["订单ID"].values:
                df.loc[df["订单ID"] == oid, ["状态", "净利润"]] = [
                    st,
                    round(float(p), 2),
                ]
            else:
                row = [
                    oid,
                    info["t"],
                    info["u"],
                    info["p"],
                    info["s"],
                    info["rc"],
                    round(float(p), 2),
                    st,
                    info["m"],
                    info["no"],
                ]
                df = pd.concat(
                    [df, pd.DataFrame([row], columns=self.cols)], ignore_index=True
                )
                self.all_known_ids.add(oid)
            df.to_csv(log_n, index=False, encoding="utf-8-sig")
            self.update_report_ui(df)
        except:
            pass

    def copy_last_char(self, name):
        if name and isinstance(name, str) and len(name.strip()) > 0:
            last_char = name.strip()[-1]
            QApplication.clipboard().setText(last_char)
            self.voice.say(f"已复制{last_char}")

    def sync(self):
        if time.time() - self.last_report_time > (REPORT_HOUR * 3600):
            self.push_hourly_report()
            self.last_report_time = time.time()

        if os.path.exists(B_FILE):
            try:
                with open(B_FILE, "r", encoding="utf-16") as f:
                    d = json.load(f).get("data", {})
                    self.balance_lbl.setText(
                        f"余额: ¥{float(d.get('quota',0)):.2f} | 冻结: ¥{float(d.get('frozen',0)):.2f}"
                    )
                    reb = float(d.get("rebate", 1.8))
                    self.current_rate = reb / 100 if reb > 0.5 else DEFAULT_RATE
                    self.rate_lbl.set_value(f"{reb:.1f}%")
            except:
                pass

        if os.path.exists(C_FILE):
            try:
                with open(C_FILE, "r", encoding="utf-16") as f:
                    cid = f.read().strip().replace('"', "").upper()
                    if cid in self.active:
                        info = self.active[cid]
                        self.confirmed.add(cid)
                        p_val = info["s"] * self.current_rate
                        self.log_to_csv(cid, info, "已核销", p_val)
                        self.voice.say("核销成功")
                        send_tg_msg(
                            f"✅ <b>订单核销成功</b>\n━━━━━━━━━━━━\n💵 金额：<code>¥{info['s']}</code>\n👤 收款：{info['u']}\n💹 净利：<b>¥{p_val:.2f}</b>\n📑 ID：<code>{cid}</code>"
                        )
                        self.rm_item(cid)
                        self.check_log_file()
                os.remove(C_FILE)
            except:
                pass

        if os.path.exists(O_FILE):
            try:
                with open(O_FILE, "r", encoding="utf-16") as f:
                    orders = json.load(f).get("data") or []
                    cur_ids = [str(o.get("id")).strip().upper() for o in orders]
                    for o in orders:
                        info = self.extract_info(o, mode="realtime")
                        oid = info["id"]

                        if info["state"] == 1:
                            now = time.time()
                            if oid not in self.last_urge_voice or (
                                now - self.last_urge_voice[oid] > 30
                            ):
                                self.voice.say(f"收款人{info['u']}，对方已催单，请核实是否到账")
                                self.last_urge_voice[oid] = now
                            if oid not in self.urged_ids:
                                send_tg_msg(
                                    f"⚠️ <b>对方已催单</b>\n━━━━━━━━━━━━\n💵 金额：¥{info['s']}\n👤 收款：{info['u']}\n👤 付款：{info['p']}\n📑 ID：<code>{oid}</code>"
                                )
                                self.urged_ids.add(oid)
                            self.update_urged_status_ui(oid, True)

                        if oid not in self.active and oid not in self.confirmed:
                            self.active[oid] = info
                            self.log_to_csv(oid, info)
                            self.add_item(oid, info)
                            self.voice.say(f"新订单{info['s']}元，方式{info['m']}，收款人{info['u']}，付款人{info['p']}")

                            # --- 按照您要求的格式推送新订单 ---
                            my_p = info["s"] * self.current_rate
                            new_order_msg = (
                                f"💰 <b>新订单到达</b>\n"
                                f"━━━━━━━━━━━━\n"
                                f"💵 金额：<code>¥{info['s']}</code>\n"
                                f"👤 收款：{info['u']}\n"
                                f"👤 付款：{info['p']}\n"
                                f"📑 方式：{info['m']}\n"
                                f"🎁 原始返点：¥{info['rc']:.2f}\n"
                                f"💹 净利：<b>¥{my_p:.2f}</b>\n"
                                f"📑 ID：<code>{oid}</code>"
                            )
                            send_tg_msg(new_order_msg)

                    for oid in list(self.active.keys()):
                        if oid not in cur_ids and oid not in self.confirmed:
                            info = self.active[oid]
                            self.log_to_csv(oid, info, "已超时", 0)
                            send_tg_msg(
                                f"❌ <b>订单已超时/消失</b>\n━━━━━━━━━━━━\n💵 金额：<code>¥{info['s']}</code>\n📑 ID：<code>{oid}</code>"
                            )
                            self.rm_item(oid)
                            self.check_log_file()
            except:
                pass

    def loop_speak(self):
        while True:
            time.sleep(30)
            for _, info in list(self.active.items()):
                self.voice.say(f"待处理订单{info['s']}元，请及时处理")

    def add_item(self, oid, info):
        container = QWidget()
        v_lay = QVBoxLayout(container)
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #0a0a0a; border: 1px solid #1a331a; border-radius: 12px; }"
        )
        card_lay = QVBoxLayout(card)
        header_lay = QHBoxLayout()
        amt_lbl = QLabel(f"¥{info['s']}")
        amt_lbl.setStyleSheet("color: #ffffff; font-size: 28px; font-weight: bold;")
        tag_lay = QHBoxLayout()
        wait_tag = QLabel("● 待处理")
        wait_tag.setStyleSheet(
            "color: #00ccff; font-weight: bold; background: #001122; padding: 2px 8px; border-radius: 4px; font-size: 11px;"
        )
        urge_tag = QLabel("⚠️ 催单")
        urge_tag.setObjectName("urge_tag")
        urge_tag.setStyleSheet(
            "color: #ff3131; font-weight: bold; background: #330000; padding: 2px 8px; border-radius: 4px; font-size: 11px;"
        )
        is_urged = info.get("state") == 1
        urge_tag.setVisible(is_urged)
        tag_lay.addWidget(wait_tag)
        tag_lay.addWidget(urge_tag)
        header_lay.addWidget(amt_lbl)
        header_lay.addStretch()
        header_lay.addLayout(tag_lay)
        card_lay.addLayout(header_lay)
        urge_text = " <font color='#ff3131'>[已催单]</font>" if is_urged else ""
        detail_lbl = QLabel(
            f"<b>方式：</b>{info['m']} | <b>时间：</b>{info['t']}{urge_text}<br/><b>收款：</b>{info['u']}<br/><b>ID：</b>{oid}"
        )
        detail_lbl.setObjectName("detail_lbl")
        detail_lbl.setStyleSheet("color: #bbbbbb; font-size: 13px;")
        card_lay.addWidget(detail_lbl)
        lbl_p = QLabel(f"👤 付款: {info['p']} (点击复制末位)")
        lbl_p.setStyleSheet(
            "color: #00ccff; text-decoration: underline; cursor: pointer;"
        )
        lbl_p.mousePressEvent = lambda e: self.copy_last_char(info["p"])
        card_lay.addWidget(lbl_p)
        card_lay.addWidget(
            HackerSpoiler(info["rc"], info["s"] * self.current_rate, info["s"])
        )
        v_lay.addWidget(card)
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, oid)
        item.setSizeHint(container.sizeHint())
        self.list.insertItem(0, item)
        self.list.setItemWidget(item, container)

    def rm_item(self, oid):
        if oid in self.active:
            del self.active[oid]
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.ItemDataRole.UserRole) == oid:
                self.list.takeItem(i)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HackerMonitor()
    win.show()
    sys.exit(app.exec())
