// OpenBruma Calamares sidebar slideshow — intentionally minimal and
// dependency-free so it renders on software QML backends.
import QtQuick 2.15

Item {
    width: 320
    height: 240

    Rectangle {
        anchors.fill: parent
        color: "#0a0c0f"
    }

    Rectangle {
        anchors.centerIn: parent
        width: parent.width * 0.55
        height: parent.height * 0.55
        color: "transparent"
        border.color: "#00ff9d"
        border.width: 2
        opacity: 0.55
    }

    Text {
        anchors.centerIn: parent
        text: "OpenBruma"
        color: "#00ff9d"
        font.pixelSize: 20
        font.bold: true
    }
}
