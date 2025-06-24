import time
import psutil
import pandas as pd
import sys
import os
import atexit
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# === Configuration ===
productive_apps = ["Word", "Excel", "PyCharm", "CLion", "Opera.exe", "Obsidian", "msedge.exe", "Python", "Slack"]
unproductive_apps = ["Steam.exe", "Fallout", "Minecraft", "EpicGamesLauncher.exe", "Valorant", "RiotClient", "osu"]

# === Utility Functions ===
def is_process_in_list(process_name, app_list):
    return any(app.lower() in process_name.lower() for app in app_list)

def categorize_process(process_name):
    if is_process_in_list(process_name, productive_apps):
        return "Productive"
    elif is_process_in_list(process_name, unproductive_apps):
        return "Unproductive"
    return "Unknown"

def get_process_list():
    process_list = []
    for proc in psutil.process_iter(['name', 'username']):
        try:
            if proc.info['username'] == psutil.Process().username():
                category = categorize_process(proc.info['name'])
                process_list.append((proc.info['name'], category))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_list

def log_productivity_status(predicted_productivity, productive_processes, unproductive_processes):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    productive_count = len(productive_processes)
    unproductive_count = len(unproductive_processes)

    if predicted_productivity > 0:
        feedback = "Productive"
    elif predicted_productivity < 0:
        feedback = "Unproductive"
    else:
        feedback = "Balanced"

    log_data = {
        'Timestamp': [current_time],
        'Feedback': [feedback],
        'Productive_Count': [productive_count],
        'Unproductive_Count': [unproductive_count]
    }

    df = pd.DataFrame(log_data)
    with open("productivity_log.csv", "a") as f:
        df.to_csv(f, header=f.tell() == 0, index=False)

def train_model():
    if not os.path.exists("productivity_log.csv"):
        print("Creating default productivity_log.csv")
        df = pd.DataFrame({
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Feedback': ['Productive'],
            'Productive_Count': [1],
            'Unproductive_Count': [0]
        })
        df.to_csv("productivity_log.csv", index=False)

    try:
        df = pd.read_csv("productivity_log.csv")

        if 'Feedback' not in df.columns:
            print("Missing 'Feedback' column in productivity_log.csv")
            return None

        # Flexible mapping from feedback to categories
        def map_feedback(fb):
            fb = fb.lower()
            if "productive" in fb and "unproductive" not in fb:
                return "Productive"
            elif "unproductive" in fb or "consider focusing" in fb:
                return "Unproductive"
            return "Balanced"

        df['Category'] = df['Feedback'].apply(map_feedback)

        if df['Category'].nunique() < 2:
            print("Need both Productive and Unproductive data to train model")
            return None

        df['Productivity'] = df['Productive_Count'] - df['Unproductive_Count']
        features = df[['Productive_Count', 'Unproductive_Count']]
        target = df['Productivity']

        model = RandomForestClassifier()
        model.fit(features, target)

        print("Model trained successfully.")
        return model

    except Exception as e:
        print(f"Failed to train model: {e}")
        return None

def provide_feedback(model):
    if model is None:
        return "Model not available.", [], []

    running_processes = get_process_list()
    productive = [p for p in running_processes if p[1] == "Productive"]
    unproductive = [p for p in running_processes if p[1] == "Unproductive"]

    features = pd.DataFrame([[len(productive), len(unproductive)]],
                            columns=['Productive_Count', 'Unproductive_Count'])

    score = model.predict(features)[0]

    if score > 0:
        feedback = "Productive"
    elif score < 0:
        feedback = "Unproductive"
    else:
        feedback = "Balanced"

    with open("feedback.txt", "w") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {feedback}\n")

    log_productivity_status(score, productive, unproductive)

    return feedback, productive, unproductive

def print_process_summary():
    summary = {'Productive': 0, 'Unproductive': 0, 'Unknown': 0}
    for _, category in get_process_list():
        summary[category] = summary.get(category, 0) + 1

    total = sum(summary.values())
    if total == 0: total = 1  # prevent div by zero

    print("\nSummary:")
    for k, v in summary.items():
        print(f"{k}: {v} ({v/total:.2%})")

def cleanup_and_print_summary():
    print("\nExiting... Printing final process summary:")
    print_process_summary()

atexit.register(cleanup_and_print_summary)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity Feedback")
        self.resize(400, 200)
        self.label = QLabel("Feedback will appear here", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.model = train_model()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_feedback)
        self.timer.start(30000)

        self.update_feedback()

    def update_feedback(self):
        feedback, productive, unproductive = provide_feedback(self.model)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        productive_names = set(proc[0] for proc in productive)
        unproductive_names = set(proc[0] for proc in unproductive)

        text = f"{timestamp}: {feedback}\n\nProductive Processes:\n"
        text += "\n".join(f"- {p}" for p in productive_names)
        text += "\n\nUnproductive Processes:\n"
        text += "\n".join(f"- {u}" for u in unproductive_names)

        self.label.setText(text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
