import sys, json, os, subprocess, threading, time, queue, random, re
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
from PyQt6.QtCore import QTimer, Qt, QObject, QPropertyAnimation, QEasingCurve

# --- 系统配置 ---
O_FILE = "C:/Users/Public/clash_orders.json"
C_FILE = "C:/Users/Public/clash_confirm.json"
B_FILE = "C:/Users/Public/clash_balance.json"
H_FILE = "C:/Users/Public/clash_history.json"
DEFAULT_RATE = 0.018


def get_today_log_name():
    return f"对账单_{datetime.now().strftime('%Y_%m_%d')}.csv"


# --- 1. 语音播报组件 ---
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
            # 优化：移除特殊字符避免 PowerShell 报错
            clean_t = str(t).replace("'", "").replace('"', "")
            cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_t}')"
            subprocess.run(
                ["powershell", "-Command", cmd], shell=True, creationflags=0x08000000
            )
            time.sleep(0.1)


# --- 2. 状态呼吸灯 ---
class BreathingLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.opacity = 1.0
        self.dir = -1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.breath)
        self.timer.start(50)

    def breath(self):
        self.opacity += self.dir * 0.05
        if self.opacity <= 0.3:
            self.dir = 1
        if self.opacity >= 1.0:
            self.dir = -1
        self.setStyleSheet(
            f"color: rgba(0, 255, 65, {self.opacity}); font-weight: bold; font-family: 'Microsoft YaHei';"
        )


# --- 3. 费率加密显示 ---
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


# --- 4. 剧透按钮组件 ---
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
                f"DATA ENCRYPTED: {''.join(random.choice('0123456789$#@&%') for _ in range(8))}"
            )

    def reveal(self):
        if self.is_revealed:
            return
        self.is_revealed = True
        rate_p = (self.raw_comm / self.score * 100) if self.score > 0 else 0
        raw_str = f"¥{self.raw_comm:.2f} ({rate_p:.1f}%)" if self.raw_comm > 0 else "-"
        self.btn.setText(f"原始返点: {raw_str}  |  净利润: ¥{self.my_profit:.2f}")
        self.btn.setStyleSheet(
            "background-color: #00ff41; color: #000000; font-weight: bold; padding: 8px; border-radius: 6px;"
        )
        QTimer.singleShot(5000, self.set_masked_style)


# --- 5. 历史记录窗口 ---
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
            for _, row in df.tail(100)[::-1].iterrows():
                st = str(row["状态"])
                comm_v = float(row.get("commission", 0))
                prof_v = float(row.get("净利润", 0))
                item_str = f"● [{st}] {row['时间']} | {row.get('方式','-')}\n金额: ¥{row['score']} (返:¥{comm_v:.2f} 净:¥{prof_v:.2f})\n收款方: {row['userName']} | 付款方: {row['payUserName']}\nID: {row.get('订单编号','-')}"
                item = QListWidgetItem(item_str)
                if st == "已核销":
                    item.setForeground(Qt.GlobalColor.green)
                elif st == "已超时":
                    item.setForeground(Qt.GlobalColor.red)
                self.hist_list.addItem(item)
        except:
            pass


# --- 6. 主监控程序 ---
class HackerMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active, self.confirmed, self.today_p, self.current_rate = (
            {},
            set(),
            0.0,
            DEFAULT_RATE,
        )
        self.all_known_ids, self.last_urge_voice = set(), {}
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

    def check_log_file(self):
        log_n = get_today_log_name()
        if not os.path.exists(log_n):
            pd.DataFrame(columns=self.cols).to_csv(
                log_n, index=False, encoding="utf-8-sig"
            )
        else:
            try:
                df = pd.read_csv(log_n, encoding="utf-8-sig")
                self.all_known_ids = set(df["订单ID"].astype(str).tolist())
                self.today_p = df[df["状态"] == "已核销"]["净利润"].sum()
            except:
                self.today_p = 0.0
        self.p_btn.setText(f"今日累计净利润: ¥{self.today_p:.2f}")

    def init_ui(self):
        self.setWindowTitle("ColorWin 聚宝实时监控 Pro")
        self.setMinimumSize(480, 800)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        c = QWidget()
        self.setCentralWidget(c)
        self.main_lay = QVBoxLayout(c)
        self.main_lay.setSpacing(15)

        self.p_btn = QPushButton("今日累计净利润: ¥0.00")
        self.p_btn.setStyleSheet(
            """
            QPushButton { 
                font-size: 26px; font-weight: bold; color: #00ff41; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #001a00, stop:1 #000000); 
                border: 2px solid #00ff41; border-radius: 15px; padding: 25px;
            }
            QPushButton:hover { background: #002200; border: 2px solid #ffffff; }
        """
        )
        self.p_btn.clicked.connect(self.show_history)
        self.main_lay.addWidget(self.p_btn)

        self.list = QListWidget()
        self.list.setStyleSheet(
            "QListWidget { background:transparent; border:none; outline:none; }"
        )
        self.main_lay.addWidget(self.list)

        self.status_bar = QFrame()
        self.status_bar.setStyleSheet(
            "background: #050505; border-top: 1px solid #1a331a; min-height: 50px;"
        )
        status_lay = QHBoxLayout(self.status_bar)
        self.state_lbl = BreathingLabel("● 正在监听系统")
        self.balance_lbl = QLabel("余额: ¥0.00 | 冻结: ¥0.00")
        self.balance_lbl.setStyleSheet(
            "color: #ffd700; font-weight: bold; font-size: 13px;"
        )
        self.rate_lbl = ClickRevealLabel(prefix="费率")
        status_lay.addWidget(self.state_lbl)
        status_lay.addStretch()
        status_lay.addWidget(self.balance_lbl)
        status_lay.addStretch()
        status_lay.addWidget(self.rate_lbl)
        self.main_lay.addWidget(self.status_bar)

    def show_history(self):
        HistoryDialog(self).exec()

    def copy_last_char(self, text):
        if text and text != "-":
            last_char = text.strip()[-1]
            QApplication.clipboard().setText(last_char)
            self.voice.say(f"已复制{last_char}")

    def log_to_csv(self, oid, info, st="待处理", p=0, skip_if_exists=False):
        log_n = get_today_log_name()
        oid = str(oid)
        if skip_if_exists and oid in self.all_known_ids:
            return
        try:
            df = pd.read_csv(log_n, encoding="utf-8-sig")
            t_str = info.get("t") or datetime.now().strftime("%H:%M:%S")
            raw_rc = float(info.get("rc", 0))
            if oid in df["订单ID"].astype(str).values:
                mask = df["订单ID"].astype(str) == oid
                df.loc[mask, "状态"] = st
                df.loc[mask, "净利润"] = round(float(p), 2)
                df.loc[mask, "commission"] = raw_rc
                df.loc[mask, "userName"] = info["u"]
                df.loc[mask, "payUserName"] = info["p"]
                df.loc[mask, "订单编号"] = info.get("no", "-")
            else:
                row = [
                    oid,
                    t_str,
                    info["u"],
                    info["p"],
                    info["s"],
                    raw_rc,
                    round(float(p), 2),
                    st,
                    info.get("m", "-"),
                    info.get("no", "-"),
                ]
                df = pd.concat([df, pd.DataFrame([row], columns=self.cols)])
                self.all_known_ids.add(oid)
            df.to_csv(log_n, index=False, encoding="utf-8-sig")
        except:
            pass

    def extract_info(self, o):
        u_val = o.get("cUserName") or o.get("userName", "-")
        p_val = (
            o.get("payUserName")
            if "payUserName" in o
            else (o.get("userName", "-") if "cUserName" in o else "-")
        )
        return {
            "s": float(o.get("score", 0)),
            "u": u_val,
            "p": p_val,
            "rc": float(o.get("commission", 0)),
            "m": o.get("cBankName") or o.get("bankName", "支付宝"),
            "no": o.get("orderNo", "-"),
            "state": o.get("state"),
            "t": (
                (o.get("created") or "").replace("T", " ").split(" ")[-1][:8]
                if o.get("created")
                else datetime.now().strftime("%H:%M:%S")
            ),
        }

    def sync(self):
        if os.path.exists(B_FILE):
            try:
                with open(B_FILE, "r", encoding="utf-16") as f:
                    d = json.load(f).get("data", {})
                    self.balance_lbl.setText(
                        f"余额: ¥{float(d.get('quota',0)):.2f} | 冻结: ¥{float(d.get('frozen',0)):.2f}"
                    )
                    reb_val = float(d.get("rebate", 1.8))
                    self.current_rate = reb_val / 100 if reb_val > 0.5 else DEFAULT_RATE
                    self.rate_lbl.set_value(f"{reb_val:.1f}%")
            except:
                pass

        if os.path.exists(C_FILE):
            try:
                with open(C_FILE, "r", encoding="utf-16") as f:
                    cid = f.read().strip().replace('"', "")
                    if cid in self.active:
                        info = self.active[cid]
                        self.confirmed.add(cid)
                        self.log_to_csv(
                            cid, info, "已核销", info["s"] * self.current_rate
                        )
                        self.voice.say("核销成功")
                        self.rm_item(cid)
                        self.check_log_file()
                os.remove(C_FILE)
            except:
                pass

        if os.path.exists(O_FILE):
            try:
                with open(O_FILE, "r", encoding="utf-16") as f:
                    orders = json.load(f).get("data") or []
                    cur_ids = [str(o.get("id")) for o in orders]
                    for o in orders:
                        oid = str(o.get("id"))
                        info = self.extract_info(o)
                        # 催单语音播报
                        if info["state"] == 1:
                            now = time.time()
                            if oid not in self.last_urge_voice or (
                                now - self.last_urge_voice[oid] > 30
                            ):
                                self.voice.say(
                                    f"收款人{info['u']}，对方已催单，请及时处理"
                                )
                                self.last_urge_voice[oid] = now

                        if oid not in self.active and oid not in self.confirmed:
                            self.active[oid] = info
                            self.log_to_csv(oid, info)
                            self.add_item(oid, info)
                            # 新订单完整播报
                            self.voice.say(
                                f"新订单{info['s']}元，方式{info['m']}，收款人{info['u']}，付款人{info['p']}"
                            )

                    for i in range(self.list.count()):
                        it = self.list.item(i)
                        oid_in_list = it.data(Qt.ItemDataRole.UserRole)
                        for o in orders:
                            if str(o.get("id")) == oid_in_list:
                                widget = self.list.itemWidget(it)
                                urge_label = widget.findChild(QLabel, "urge_tag")
                                if urge_label:
                                    urge_label.setVisible(o.get("state") == 1)

                    for oid in list(self.active.keys()):
                        if oid not in cur_ids and oid not in self.confirmed:
                            self.log_to_csv(oid, self.active[oid], "已超时", 0)
                            self.rm_item(oid)
            except:
                pass

    def loop_speak(self):
        while True:
            time.sleep(30)
            for oid, info in list(self.active.items()):
                if oid not in self.confirmed:
                    # 循环播报：保持简洁，只报金额
                    self.voice.say(f"待处理订单{info['s']}元")

    def add_item(self, oid, info):
        container = QWidget()
        v_lay = QVBoxLayout(container)
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a0a, stop:1 #111111); 
                border: 1px solid #1a331a; border-radius: 12px;
            }
            QFrame:hover { border: 1px solid #00ff41; background: #000800; }
        """
        )
        card_lay = QVBoxLayout(card)
        card_lay.setSpacing(8)
        header_lay = QHBoxLayout()
        amt_lbl = QLabel(f"¥{info['s']}")
        amt_lbl.setStyleSheet(
            "color: #ffffff; font-size: 28px; font-weight: bold; font-family: Arial;"
        )
        urge_tag = QLabel("⚠️ 对方已催单")
        urge_tag.setObjectName("urge_tag")
        urge_tag.setStyleSheet(
            "color: #ff3131; font-weight: bold; font-size: 14px; background: #330000; padding: 2px 6px; border-radius: 4px;"
        )
        urge_tag.setVisible(info.get("state") == 1)
        st_lbl = QLabel("[ 待核销 ]")
        st_lbl.setStyleSheet("color: #00ff41; font-size: 14px; font-weight: bold;")
        header_lay.addWidget(amt_lbl)
        header_lay.addStretch()
        header_lay.addWidget(urge_tag)
        header_lay.addWidget(st_lbl)
        card_lay.addLayout(header_lay)
        detail_txt = f"<b>方式：</b>{info['m']} | <b>时间：</b>{info['t']}<br/><b>收款方：</b>{info['u']}<br/><b>订单号：</b>{info['no']}"
        detail_lbl = QLabel(detail_txt)
        detail_lbl.setStyleSheet("color: #bbbbbb; font-size: 13px; line-height: 1.5;")
        card_lay.addWidget(detail_lbl)
        lbl_p = QLabel(f"👤 付款方(点击复制末位): {info['p']}")
        lbl_p.setStyleSheet(
            "color: #00ccff; font-size: 13px; text-decoration: underline;"
        )
        lbl_p.setCursor(Qt.CursorShape.PointingHandCursor)
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
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it and it.data(Qt.ItemDataRole.UserRole) == oid:
                self.list.takeItem(i)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = HackerMonitor()
    win.show()
    sys.exit(app.exec())
