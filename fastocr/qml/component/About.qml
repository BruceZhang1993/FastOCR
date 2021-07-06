import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.qmlmodels 1.0

ScrollView
{
    anchors.fill: parent
    contentWidth: availableWidth
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    clip: true

    Flickable {
        boundsBehavior: Flickable.StopAtBounds
        anchors.fill: parent

        ColumnLayout {
            id: clayout
            width: parent.width
            Layout.fillWidth: true
            spacing: 2

            Item { height: 40 }

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "FastOCR"
                font.pixelSize: 22
                font.bold: true
            }

            Label {
                Layout.alignment: Qt.AlignHCenter
                text: backend.appver
                font.pixelSize: 14
                font.bold: false
                color: '#888';
            }

            Item { height: 40 }

            TableView {
                id: tableView
                columnSpacing: 1
                rowSpacing: 1
                Layout.fillWidth: true
                clip: true
                contentHeight: 40 * rows
                height: 40 * rows
                boundsBehavior: Flickable.StopAtBounds

                property var columnWidths: [width / 3, width / 3 * 2]

                columnWidthProvider: function (column) { return columnWidths[column] }

                model: TableModel {
                    TableModelColumn { display: 'name' }
                    TableModelColumn { display: 'value' }
                    rows: backend.about_data
                }

                delegate: Rectangle {
                    implicitHeight: 40
                    border.width: 0

                    TextEdit {
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: 6
                        clip: true
                        text: display
                        readOnly: true
                        wrapMode: Text.WordWrap
                        selectByMouse: true
                    }
                }
            }

        }
    }
}
