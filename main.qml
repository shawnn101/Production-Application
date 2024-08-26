import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 400
    height: 200
    title: "Productivity Feedback"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10

        Label {
            id: feedbackLabel
            text: "Feedback will appear here"
            font.pixelSize: 16
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
        }

        Label {
            id: timeLabel
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            Timer {
                interval: 1000 // Update every 1 second
                repeat: true
                running: true
                onTriggered: {
                    var now = new Date();
                    timeLabel.text = "Current Time: " + now.toLocaleTimeString();
                }
            }
        }
    }
}
