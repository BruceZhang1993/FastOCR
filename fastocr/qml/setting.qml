import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: setting
    visible: false
    width: 860
    height: 640
    title: qsTr('FastOCR Setting')

    onClosing: {
        close.accepted = false
        setting.visible = false
    }

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
                text: qsTr('Save')
                onClicked: {
                    backend.appid = appid_input.text
                    backend.apikey = apikey_input.text
                    backend.seckey = seckey_input.text
                    backend.accurate = accurate_input.checked

                    // Languages
                    var lang_checkboxes = [japanese, korean, french, spanish, germany, russian]
                    var checked = []
                    for (var i=0; i < lang_checkboxes.length; i++)
                        if (lang_checkboxes[i].checked)
                            checked.push(lang_checkboxes[i].value)
                    backend.languages = checked

                    backend.save()
                    setting.visible = false
                }
            }

            Button {
                text: qsTr('Close')
                onClicked: setting.visible = false
            }
        }
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
            columns: 4

            Label {
                id: appid_label
                text: qsTr("APP_ID")
            }

            TextField {
                id: appid_input
                text: backend ? backend.appid : ''
                Layout.columnSpan: 3
                Layout.fillWidth: true
            }

            Label {
                id: apikey_label
                text: qsTr("API_KEY")
            }

            TextField {
                id: apikey_input
                text: backend ? backend.apikey : ''
                Layout.columnSpan: 3
                Layout.fillWidth: true
            }

            Label {
                id: seckey_label
                text: qsTr("SECRET_KEY")
            }

            TextField {
                id: seckey_input
                text: backend ? backend.seckey : ''
                Layout.columnSpan: 3
                Layout.fillWidth: true
            }

            Label {
                id: lang_label
                text: qsTr("Languages")
            }

            Flow {
                Layout.columnSpan: 3
                Layout.fillWidth: true

                CheckBox {
                    property string value

                    id: japanese
                    text: qsTr('Japanese')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'JAP'
                }

                CheckBox {
                    property string value

                    id: korean
                    text: qsTr('Korean')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'KOR'
                }

                CheckBox {
                    property string value

                    id: french
                    text: qsTr('French')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'FRE'
                }

                CheckBox {
                    property string value

                    id: spanish
                    text: qsTr('Spanish')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'SPA'
                }

                CheckBox {
                    property string value

                    id: germany
                    text: qsTr('Germany')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'GER'
                }

                CheckBox {
                    property string value

                    id: russian
                    text: qsTr('Russian')
                    checked: backend ? backend.languages.includes(this.value): false
                    value: 'RUS'
                }
            }

            Row {
                CheckBox {
                    id: accurate_input
                    text: qsTr('Use accurate mode')
                    checked: backend ? backend.accurate : false
                    Layout.columnSpan: 4
                    Layout.fillWidth: true
                }
            }
        }
    }
}
