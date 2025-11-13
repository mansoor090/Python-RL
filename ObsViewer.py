import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QTimer


class ObsViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Obs Viewer (PyQt5)")
        self.setGeometry(100, 100, 600, 800)

        self.layout = QVBoxLayout()

        self.scroll = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)

        self.labels = {}
        self.last_obs = {}
        self.reward_history = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_obs)
        self.timer.start(100)  # Update every 1 second

    def update_obs(self):
        if not os.path.exists("latest_obs.json"):
            return

        try:
            with open("latest_obs.json", "r+") as f:
                data = f.read()
                if not data.strip():
                    return  # File empty, skip

                parsed = json.loads(data)

            obs = parsed.get("observation", {})
            reward = parsed.get("reward", None)

            # Update reward separately
            if reward is not None:
                reward_key = "__CURRENT_REWARD__"
                if reward_key not in self.labels:
                    label = QLabel()
                    label.setText(f"Reward: {reward:.4f}")
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    self.scroll_layout.addWidget(label)
                    self.labels[reward_key] = label
                else:
                    self.labels[reward_key].setText(f"Reward: {reward:.4f}")

                # Save last 10 rewards
                self.reward_history.append(reward)
                if len(self.reward_history) > 10:
                    self.reward_history.pop(0)

                # Show reward history
                history_key = "__REWARD_HISTORY__"
                history_text = ", ".join([f"{r:.2f}" for r in self.reward_history])
                if history_key not in self.labels:
                    label = QLabel()
                    label.setText(f"Last 10 Rewards: [{history_text}]")
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    self.scroll_layout.addWidget(label)
                    self.labels[history_key] = label
                else:
                    self.labels[history_key].setText(f"Last 10 Rewards: [{history_text}]")

            # Update observations
            for key, value in obs.items():
                display_value = str(value)

                if key not in self.labels:
                    label = QLabel()
                    label.setText(f"{key}: {display_value}")
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    self.scroll_layout.addWidget(label)
                    self.labels[key] = label
                else:
                    last_value = self.last_obs.get(key)
                    current_value = value

                    if last_value is not None:
                        try:
                            last_sum = sum(flatten(last_value))
                            current_sum = sum(flatten(current_value))
                            if current_sum > last_sum:
                                self.labels[key].setStyleSheet("color: green")
                            elif current_sum < last_sum:
                                self.labels[key].setStyleSheet("color: red")
                            else:
                                self.labels[key].setStyleSheet("color: black")
                        except:
                            self.labels[key].setStyleSheet("color: black")

                    self.labels[key].setText(f"{key}: {display_value}")

            self.last_obs = obs

        except Exception as e:
            print(f"Error reading obs: {e}")

def flatten(x):
    """Helper to flatten nested lists."""
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ObsViewer()
    viewer.show()
    sys.exit(app.exec_())
