import time
import psutil
import pandas as pd
import sys
import atexit
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# Define lists of productive and unproductive applications
productive_apps = ["Word", "Excel", "PyCharm", "CLion",
                   "Opera.exe", "Obsidian", "msedge.exe", "Python", "Slack"]
unproductive_apps = ["Steam.exe", "Fallout", "Minecraft", "EpicGamesLauncher.exe", "Valorant", "RiotClient", "osu"]


# Function to check if a process name matches any in the given list
def is_process_in_list(process_name, app_list):
    for app in app_list:
        if app.lower() in process_name.lower():
            return True
    return False


# Function to categorize a process as productive or unproductive
def categorize_process(process_name):
    if is_process_in_list(process_name, productive_apps):
        return "Productive"
    elif is_process_in_list(process_name, unproductive_apps):
        return "Unproductive"
    else:
        return "Unknown"


# Function to get the list of running processes and their categories
def get_process_list():
    process_list = []
    for proc in psutil.process_iter(['name', 'username']):
        try:
            process_name = proc.info['name']
            username = proc.info['username']

            # Check if the process belongs to the current user and is not a system process
            if username == psutil.Process().username():
                category = categorize_process(process_name)
                process_list.append((process_name, category))

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_list


# Function to log productivity status to a CSV file
def log_productivity_status(feedback, productive_processes, unproductive_processes):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    productive_count = len(productive_processes)
    unproductive_count = len(unproductive_processes)

    log_data = {
        'Timestamp': [current_time],
        'Feedback': [feedback],
        'Productive_Count': [productive_count],
        'Unproductive_Count': [unproductive_count]
    }

    df = pd.DataFrame(log_data)

    # Append the data to a CSV file
    with open("productivity_log.csv", "a") as f:
        df.to_csv(f, header=f.tell() == 0, index=False)


# Function to print summary of productive and unproductive processes
def print_process_summary():
    productive_processes_count = 0
    unproductive_processes_count = 0
    unknown_processes_count = 0
    total_processes_count = 0

    # Calculate counts for productive, unproductive, and unknown processes
    for _, category in get_process_list():
        if category == "Productive":
            productive_processes_count += 1
        elif category == "Unproductive":
            unproductive_processes_count += 1
        elif category == "Unknown":
            unknown_processes_count += 1
        total_processes_count += 1

    # Calculate percentages
    productive_percentage = (
            productive_processes_count / total_processes_count * 100) if total_processes_count != 0 else 0
    unproductive_percentage = (
            unproductive_processes_count / total_processes_count * 100) if total_processes_count != 0 else 0
    unknown_percentage = (unknown_processes_count / total_processes_count * 100) if total_processes_count != 0 else 0

    # Print summary
    print("Productive Processes Summary:")
    for process, category in get_process_list():
        if category == "Productive":
            print(f"- {process}")

    print("\nUnproductive Processes Summary:")
    for process, category in get_process_list():
        if category == "Unproductive":
            print(f"- {process}")

    print("\nUnknown Processes Summary:")
    for process, category in get_process_list():
        if category == "Unknown":
            print(f"- {process}")

    # Print percentages
    print("\nOverall Summary:")
    print(f"Productive Percentage: {productive_percentage:.2f}%")
    print(f"Unproductive Percentage: {unproductive_percentage:.2f}%")
    print(f"Unmarked Processes: {unknown_percentage:.2f}%")


# Function to handle cleanup and print summary when the code is stopped
def cleanup_and_print_summary():
    print("Stopping code...")
    print_process_summary()


# Register cleanup function to execute when the script exits
atexit.register(cleanup_and_print_summary)


# Function to train the machine learning model
def train_model():
    # Load the activity log
    df = pd.read_csv("activity_log.csv")

    # Feature Engineering: Extract features (e.g., count of productive and unproductive activities)
    df['Productive_Count'] = (df['Category'] == 'Productive').astype(int)
    df['Unproductive_Count'] = (df['Category'] == 'Unproductive').astype(int)

    # Target variable
    df['Productivity'] = df['Productive_Count'] - df['Unproductive_Count']
    features = df[['Productive_Count', 'Unproductive_Count']]
    target = df['Productivity']

    # Train a machine learning model
    model = RandomForestClassifier()
    model.fit(features, target)

    return model


# Function to provide feedback based on model predictions
def provide_feedback(model):
    # Get currently running productive and unproductive processes
    running_processes = get_process_list()
    productive_processes = [proc for proc in running_processes if proc[1] == "Productive"]
    unproductive_processes = [proc for proc in running_processes if proc[1] == "Unproductive"]

    # Create feature set for prediction
    productive_count = len(productive_processes)
    unproductive_count = len(unproductive_processes)
    features = pd.DataFrame([[productive_count, unproductive_count]],
                            columns=['Productive_Count', 'Unproductive_Count'])

    # Predict productivity score
    predicted_productivity = model.predict(features)[0]

    # Determine feedback message based on productivity score
    if predicted_productivity > 0:
        feedback = "You're engaged in productive activities. Keep up the good work!"
    elif predicted_productivity < 0:
        feedback = "Consider focusing on more productive tasks to enhance your efficiency."
    else:
        feedback = "Your productivity level is balanced."

    # Write feedback to a file with current timestamp
    with open("feedback.txt", "w") as f:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{current_time}: {feedback}\n")

    # Log the productivity status
    log_productivity_status(feedback, productive_processes, unproductive_processes)

    return feedback, productive_processes, unproductive_processes


# Create and display Feedback widget
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
        self.timer.start(1000)

        self.update_feedback()

    # Update feedback real-time
    def update_feedback(self):
        feedback, productive_processes, unproductive_processes = provide_feedback(self.model)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')

        # Remove duplicate process names
        unique_productive_processes = set(proc[0] for proc in productive_processes)
        unique_unproductive_processes = set(proc[0] for proc in unproductive_processes)

        # Construct feedback text
        feedback_text = f"{current_time}: {feedback}\n\n"
        feedback_text += "Productive Processes:\n"
        feedback_text += "\n".join([f"- {proc}" for proc in unique_productive_processes])
        feedback_text += "\n\nUnproductive Processes:\n"
        feedback_text += "\n".join([f"- {proc}" for proc in unique_unproductive_processes])

        self.label.setText(feedback_text)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
