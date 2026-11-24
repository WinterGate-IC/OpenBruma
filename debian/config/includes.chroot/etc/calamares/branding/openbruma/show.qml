/* OpenBruma Calamares slideshow — WIC neo-noir */
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 12000
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Image {
            id: bg1
            source: "slide1.png"
            width: 520; height: 300
            fillMode: Image.PreserveAspectCrop
            anchors.centerIn: parent
        }
        Text {
            anchors.horizontalCenter: bg1.horizontalCenter
            anchors.top: bg1.bottom
            anchors.topMargin: 12
            text: qsTr("Welcome to OpenBruma\nWinterGate Intelligence Collective · OSINT Edition")
            color: "#eafff5"
            font.pixelSize: 18
            horizontalAlignment: Text.Center
            wrapMode: Text.WordWrap
            width: 600
        }
    }

    Slide {
        Rectangle {
            width: 520; height: 300
            color: "#0a0c0f"
            border.color: "#1b4a3a"
            border.width: 2
            anchors.centerIn: parent
            Column {
                anchors.centerIn: parent
                spacing: 12
                Text { text: "Built for lawful OSINT"; color: "#00ff9d"; font.pixelSize: 24; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "nmap · Wireshark · exiftool · SleuthKit"; color: "#eafff5"; font.pixelSize: 15; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "binwalk · foremost · hashcat · john"; color: "#eafff5"; font.pixelSize: 15; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "Firefox ESR · Thunderbird · LibreOffice"; color: "#eafff5"; font.pixelSize: 15; anchors.horizontalCenter: parent.horizontalCenter }
            }
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.verticalCenter
            anchors.topMargin: 165
            text: qsTr("Documented · proportional · lawful")
            color: "#00b8ff"
            font.pixelSize: 15
        }
    }

    Slide {
        Rectangle {
            width: 520; height: 300
            color: "#0a0c0f"
            border.color: "#1b4a3a"
            border.width: 2
            anchors.centerIn: parent
            Column {
                anchors.centerIn: parent
                spacing: 14
                Text { text: "Installing OpenBruma"; color: "#00ff9d"; font.pixelSize: 24; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "The guided installer will partition, install,\nand set up your system automatically."; color: "#eafff5"; font.pixelSize: 15; horizontalAlignment: Text.Center; anchors.horizontalCenter: parent.horizontalCenter }
                Text { text: "You can also choose manual partitioning\nin the Custom installer."; color: "#00b8ff"; font.pixelSize: 14; horizontalAlignment: Text.Center; anchors.horizontalCenter: parent.horizontalCenter }
            }
        }
    }
}
