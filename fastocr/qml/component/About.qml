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

        ColumnLayout {
            id: clayout
            width: parent.width
            Layout.fillWidth: true
            spacing: 2

            Label {
                text: "FastOCR - Version " + (backend ? backend.appver : 'Unknown')
                font.pixelSize: 22
                font.bold: true
            }
        }
    }
}
