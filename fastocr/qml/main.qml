import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./component" as CustomComponent

ApplicationWindow {
    id: setting
    visible: false
    width: 600
    height: 720
    title: qsTr('FastOCR Setting')

    onClosing: {
        close.accepted = false
        setting.visible = false
    }

    Column {
        anchors.fill: parent

        TabBar {
            id: bar
            width: parent.width
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            TabButton {
                text: qsTr("Setting")
            }
            TabButton {
                text: qsTr("About")
            }
        }

        StackLayout {
            anchors.topMargin: bar.height
            width: parent.width
            anchors.fill: parent
            currentIndex: bar.currentIndex
            CustomComponent.Setting {}
            CustomComponent.About {}
        }
    }

}
