import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ScrollView
{
    anchors.fill: parent
    width: setting.width
    contentWidth: availableWidth
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    contentHeight: clayout.height
    clip: true

    Flickable {
        boundsBehavior: Flickable.StopAtBounds
        anchors.fill: parent

        GridLayout {
            id: clayout
            width: parent.width
            Layout.fillWidth: true
            columns: 2
            rowSpacing: 4
            columnSpacing: 4

            Label {
                Layout.minimumWidth: width + 10
                text: "FastOCR"
                font.pixelSize: 18
                font.bold: true
            }

            Label {
                Layout.fillWidth: true
                text: backend.appver
                font.pixelSize: 18
                font.bold: true
            }
        }
    }
}
