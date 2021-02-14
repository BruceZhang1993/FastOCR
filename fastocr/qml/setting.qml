import QtQuick 2.11
import QtQuick.Window 2.2
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.4

ApplicationWindow {
    id: setting
    visible: false
    width: 480
    height: 640
    title: 'FastOCR Setting'
    flags: Qt.Window | Qt.WindowMinMaxButtonsHint

    footer: ToolBar {
        ButtonGroup {
            id: button_group
            buttons: buttons.children
        }

        Row {
            id: buttons
            anchors.fill: parent
            layoutDirection: Qt.RightToLeft

            Button {
                text: 'Save'
                onClicked: {
                    backend.appid = appid_input.text
                    backend.apikey = apikey_input.text
                    backend.seckey = seckey_input.text
                    backend.save()
                    setting.visible = false
                }
            }

            Button {
                text: 'Cancel'
                onClicked: setting.visible = false
            }
        }
    }

    Column {
        anchors.fill: parent
        padding: 0
        anchors.bottomMargin: 50
    }

    GroupBox {
        id: group1
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        font.weight: Font.Bold
        font.bold: false
        anchors.rightMargin: 10
        anchors.leftMargin: 10
        anchors.topMargin: 7
        title: qsTr("BaiduOCR")

        GridLayout {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            rows: 3
            columns: 2

            Label {
                id: appid_label
                text: qsTr("APP_ID")
            }

            TextField {
                id: appid_input
                text: backend.appid ?? ''
            }

            Label {
                id: apikey_label
                text: qsTr("API_KEY")
            }

            TextField {
                id: apikey_input
                text: backend.apikey ?? ''
            }

            Label {
                id: seckey_label
                text: qsTr("SECRET_KEY")
            }

            TextField {
                id: seckey_input
                text: backend.seckey ?? ''
            }
        }
    }
}
