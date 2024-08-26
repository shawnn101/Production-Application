# IMPORTANT
This project is still under development. Additions and changes are to be made regularly. 

# Production-Application
The productivity tracker monitors the specified running processes on a computer, categorizes them as productive or unproductive, and provides real-time feedback to the user using a GUI built with PyQt5. Based on the user's past and present productivity, an ML algorithm will make sure to send daily reminders and recommendations that reflect the users' actions. Additional files are made for tracking and troubleshooting purposes. Sample documents are provided in the repository.

## Libraries
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following libraries:
```bash
pip install pandas
pip install psutil
pip install PyQt5
pip install scikit-learn
```

# Versions
## v0.0.1
- Code implements most above libraries to achieve functions
- The program tracks the stated programs respective to its class and prints out each process and its class when the program is terminated
- Program percentage breakdown is printed out when the program is terminated
- Widget is created when the file is executed; process listed and message based on productivity is posted
- Nessacry logs are created a filled with necessary information
- **Message to send daily reminders and recommendations that reflect the users' actions to be made (implement ML algorithm with appropriate library such as OpenCV or Tensorflow)**






