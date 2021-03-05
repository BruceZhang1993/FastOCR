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

                    backend.yd_appid = yd_appid_input.text
                    backend.yd_seckey = yd_seckey_input.text

                    backend.face_apikey = face_apikey_input.text
                    backend.face_apisec = face_apisec_input.text

                    // Languages
                    var lang_checkboxes = language_flow.children
                    var checked = []
                    for (var i=0; i < lang_checkboxes.length; i++)
                        if (lang_checkboxes[i].checked)
                            checked.push(lang_checkboxes[i].value)
                    backend.languages = checked

                    // General
                    backend.icon_theme = icon_theme_select.currentValue
                    var radios = select_flow.children
                    for (var i=0; i < radios.length; i++)
                        if (radios[i].checked)
                            backend.default_backend = radios[i].value

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

    ScrollView
    {
        anchors.fill: parent
        width: setting.width
        clip: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 2

            GroupBox {
                title: qsTr("Default backend")
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                Flow {
                    id: select_flow
                    anchors.fill: parent

                    RadioButton {
                        property string value

                        id: baidu_select
                        value: 'baidu'
                        checked: backend ? backend.default_backend == value : false
                        text: qsTr("BaiduOCR")
                    }

                    RadioButton {
                        property string value

                        id: youdao_select
                        value: 'youdao'
                        checked: backend ? backend.default_backend == value : false
                        text: qsTr("YoudaoOCR")
                    }

                    RadioButton {
                        property string value

                        id: face_select
                        value: 'face'
                        checked: backend ? backend.default_backend == value : false
                        text: qsTr("Face++OCR")
                    }
                }
            }

            GroupBox {
                title: qsTr("Icon theme")
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop

                Flow {
                    ComboBox {
                        id: icon_theme_select
                        textRole: 'text'
                        valueRole: 'value'
                        Component.onCompleted: currentIndex = indexOfValue(backend ? backend.icon_theme : 'auto')
                        model: [
                            { value: 'auto', text: qsTr('Auto Select') },
                            { value: 'light', text: qsTr("Light") },
                            { value: 'dark', text: qsTr("Dark") }
                        ]
                    }
                }
            }

            GroupBox {
                id: group1
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
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
                        id: language_flow
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

            GroupBox {
                id: group2
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                title: qsTr("YoudaoOCR")

                GridLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    columns: 4

                    Label {
                        id: yd_appid_label
                        text: qsTr("APP_ID")
                    }

                    TextField {
                        id: yd_appid_input
                        text: backend ? backend.yd_appid : ''
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                    }

                    Label {
                        id: yd_seckey_label
                        text: qsTr("SEC_KEY")
                    }

                    TextField {
                        id: yd_seckey_input
                        text: backend ? backend.yd_seckey : ''
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                    }
                }
            }

            GroupBox {
                id: group3
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                title: qsTr("Face++OCR")

                GridLayout {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    columns: 4

                    Label {
                        id: face_apikey_label
                        text: qsTr("API_KEY")
                    }

                    TextField {
                        id: face_apikey_input
                        text: backend ? backend.face_apikey : ''
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                    }

                    Label {
                        id: face_apisec_label
                        text: qsTr("API_SEC")
                    }

                    TextField {
                        id: face_apisec_input
                        text: backend ? backend.face_apisec : ''
                        Layout.columnSpan: 3
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
}
