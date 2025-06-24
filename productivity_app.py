import time
import psutil
import pandas as pd
import sys
import os
import atexit
import joblib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# === Load ML Classifier for Apps ===
try:
    classifier_model = joblib.load("program_learn/app_classifier_model.pkl")
except:
    print("Warning: app_classifier_model.pkl not found. Classifier fallback to manual lists.")
    classifier_model = None

#If pkl. fails to load...
manual_productive_apps = ["Word", "Excel", "PyCharm", "CLion", "Opera.exe", "Obsidian", "msedge.exe", "Python", "Slack"]
manual_unproductive_apps = ["Steam.exe", "Fallout", "Minecraft", "EpicGamesLauncher.exe", "Valorant", "RiotClient", "osu"]


def is_process_in_list(process_name, app_list):
    return any(app.lower() in process_name.lower() for app in app_list)

def auto_classify_process(process_name):
    if classifier_model:
        try:
            # Extract text features
            df = pd.DataFrame([{'app': process_name}])
            df['app'] = df['app'].str.lower().str.replace(".exe", "", regex=False)
            return classifier_model.predict(df['app'].values.reshape(-1, 1))[0]
        except:
            pass

    # Fallback to manual
    if is_process_in_list(process_name, manual_productive_apps):
        return "Productive"
    elif is_process_in_list(process_name, manual_unproductive_apps):
        return "Unproductive"
    return "Unknown"

def get_process_list():
    seen = set()
    process_list = []
    for proc in psutil.process_iter(['name', 'username']):
        try:
            name = proc.info['name']
            if proc.info['username'] == psutil.Process().username():
                name_lower = name.lower()
                if name_lower not in seen:
                    seen.add(name_lower)
                    category = auto_classify_process(name)
                    process_list.append((name, category))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
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

    df = pd.DataFrame([{
        'Timestamp': current_time,
        'Feedback': feedback,
        'Productive_Count': productive_count,
        'Unproductive_Count': unproductive_count
    }])

    with open("Productivity-Generated Documents/productivity_log.csv", "a") as f:
        df.to_csv(f, header=f.tell() == 0, index=False)

def train_model():
    if not os.path.exists("Productivity-Generated Documents/productivity_log.csv"):
        df = pd.DataFrame([{
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Feedback': 'Productive',
            'Productive_Count': 1,
            'Unproductive_Count': 0
        }])
        df.to_csv("productivity_log.csv", index=False)

    df = pd.read_csv("Productivity-Generated Documents/productivity_log.csv")

    if 'Feedback' not in df.columns:
        print("Missing 'Feedback' column")
        return None

    def map_feedback(fb):
        if "Productive" in fb:
            return "Productive"
        elif "Unproductive" in fb:
            return "Unproductive"
        return "Balanced"

    df['Category'] = df['Feedback'].apply(map_feedback)

    if df['Category'].nunique() < 2:
        print("Need both Productive and Unproductive data")
        return None

    df['Productivity'] = df['Productive_Count'] - df['Unproductive_Count']
    X = df[['Productive_Count', 'Unproductive_Count']]
    y = df['Productivity']

    model = RandomForestClassifier()
    model.fit(X, y)
    return model

def provide_feedback(model):
    if not model:
        return "Model not available", [], []

    processes = get_process_list()
    productive = [p for p in processes if p[1] == "Productive"]
    unproductive = [p for p in processes if p[1] == "Unproductive"]

    X = pd.DataFrame([[len(productive), len(unproductive)]],
                     columns=['Productive_Count', 'Unproductive_Count'])
    score = model.predict(X)[0]

    if score > 0:
        feedback = "Productive"
    elif score < 0:
        feedback = "Unproductive"
    else:
        feedback = "Balanced"

    with open("Productivity-Generated Documents/feedback.txt", "w") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {feedback}\n")

    log_productivity_status(score, productive, unproductive)
    return feedback, productive, unproductive

def cleanup_and_print_summary():
    print("Exiting. Final summary:")
    summary = {'Productive': 0, 'Unproductive': 0, 'Unknown': 0}
    for _, cat in get_process_list():
        summary[cat] += 1
    print(summary)

atexit.register(cleanup_and_print_summary)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productivity Feedback")
        self.resize(400, 200)
        self.label = QLabel("Feedback will appear here")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.model = train_model()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_feedback)
        self.timer.start(2000)

    def update_feedback(self):
        feedback, productive, unproductive = provide_feedback(self.model)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        p_names = "\n".join(f"- {p[0]}" for p in productive)
        u_names = "\n".join(f"- {u[0]}" for u in unproductive)

        text = f"{now}: {feedback}\n\nProductive Apps:\n{p_names}\n\nUnproductive Apps:\n{u_names}"
        self.label.setText(text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
