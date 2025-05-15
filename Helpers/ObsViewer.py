# obs_viewer.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt

def flatten(x):
    """Helper to flatten nested lists."""
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

class ObsViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Obs Viewer (Push-Based)")
        self.setGeometry(100, 100, 600, 800)

        # set up scrollable area
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll)

        # state
        self.labels = {}          # maps keys -> QLabel
        self.last_obs = {}        # maps keys -> last value
        self.reward_history = []  # stores last 10 rewards

        # **SHOW THE WINDOW**
        self.show()


    def update(self, obs: dict, reward: float):
        """
        Call this on every env.step:
          obs    = your observation dict
          reward = the reward returned that step
        """
        # ——— current reward ———
        key_cur = "__CURRENT_REWARD__"
        txt = f"Reward: {reward:.4f}"
        if key_cur not in self.labels:
            lbl = QLabel(txt)
            lbl.setWordWrap(True); lbl.setAlignment(Qt.AlignLeft)
            self.scroll_layout.addWidget(lbl)
            self.labels[key_cur] = lbl
        else:
            self.labels[key_cur].setText(txt)

        # ——— reward history ———
        self.reward_history.append(reward)
        if len(self.reward_history) > 10:
            self.reward_history.pop(0)
        key_hist = "__REWARD_HISTORY__"
        hist_txt = ", ".join(f"{r:.2f}" for r in self.reward_history)
        full = f"Last 10 Rewards: [{hist_txt}]"
        if key_hist not in self.labels:
            lbl = QLabel(full)
            lbl.setWordWrap(True); lbl.setAlignment(Qt.AlignLeft)
            self.scroll_layout.addWidget(lbl)
            self.labels[key_hist] = lbl
        else:
            self.labels[key_hist].setText(full)

        # ——— observations ———
        for k, v in obs.items():
            disp = str(v)
            if k not in self.labels:
                lbl = QLabel(f"{k}: {disp}")
                lbl.setWordWrap(True); lbl.setAlignment(Qt.AlignLeft)
                self.scroll_layout.addWidget(lbl)
                self.labels[k] = lbl
            else:
                # color-code based on sum comparison
                prev = self.last_obs.get(k)
                if prev is not None:
                    try:
                        prev_sum = sum(flatten(prev))
                        cur_sum  = sum(flatten(v))
                        color = "green" if cur_sum>prev_sum else "red" if cur_sum<prev_sum else "black"
                        self.labels[k].setStyleSheet(f"color: {color}")
                    except:
                        self.labels[k].setStyleSheet("color: black")
                self.labels[k].setText(f"{k}: {disp}")
            self.last_obs[k] = v

        # force immediate repaint
        QApplication.processEvents()