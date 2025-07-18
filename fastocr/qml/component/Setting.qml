import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Column {
    anchors.fill: parent

    ScrollView
    {
        anchors.fill: parent
        width: setting.width
        contentWidth: availableWidth
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        contentHeight: clayout.height
        bottomPadding: bottom_toolbar.height + 10
        clip: true

        Flickable {
            boundsBehavior: Flickable.StopAtBounds

            ColumnLayout {
                id: clayout
                width: parent.width
                Layout.fillWidth: true
                spacing: 2

                GroupBox {
                    title: qsTr("General")
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop

                    GridLayout {
                        Layout.fillWidth: true
                        anchors.top: parent.top
                        Layout.alignment: Qt.AlignTop
                        columns: 4

                        CheckBox {
                            id: autostart_input
                            text: qsTr('Run at system start')
                            checked: backend.autostart
                            checkable: backend.autostart_supported
                            enabled: backend.autostart_supported
                            Layout.columnSpan: 4
                            Layout.fillWidth: true
                        }

                        Label {
                            id: icontheme_label
                            text: qsTr("Icon theme")
                        }

                        ComboBox {
                            id: icon_theme_select
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                            textRole: 'text'
                            valueRole: 'value'
                            Component.onCompleted: currentIndex = indexOfValue(backend.icon_theme)
                            model: [
                                { value: 'auto', text: qsTr('Auto Select') },
                                { value: 'light', text: qsTr("Light") },
                                { value: 'dark', text: qsTr("Dark") }
                            ]
                        }

                        Label {
                            id: working_mode_label
                            text: qsTr("Working mode")
                        }

                        ComboBox {
                            id: working_mode_select
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                            textRole: 'text'
                            valueRole: 'value'
                            Component.onCompleted: currentIndex = indexOfValue(backend.mode)
                            model: [
                                { value: 0, text: qsTr('Copy to clipboard automatic') },
                                { value: 1, text: qsTr("Show notification to copy (Cannot click on notifications on some platforms)") }
                            ]
                        }
                    }
                }

                GroupBox {
                    title: qsTr("Default text backend")
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop

                    Flow {
                        id: select_flow
                        anchors.fill: parent
                        spacing: 2

                        RadioButton {
                            property string value

                            id: baidu_select
                            value: 'baidu'
                            checked: backend.default_backend == value
                            text: qsTr("BaiduOCR")
                        }

                        RadioButton {
                            property string value

                            id: youdao_select
                            value: 'youdao'
                            checked: backend.default_backend == value
                            text: qsTr("YoudaoOCR")
                        }

                        RadioButton {
                            property string value

                            id: face_select
                            value: 'face'
                            checked: backend.default_backend == value
                            text: qsTr("Face++OCR")
                        }

                        RadioButton {
                            property string value

                            id: paddle_select
                            value: 'paddle'
                            checked: backend.default_backend == value
                            text: qsTr("PaddleOCR")
                        }
                    }
                }

                GroupBox {
                    title: qsTr("Default formula backend")
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop

                    Flow {
                        id: select_formula_flow
                        anchors.fill: parent
                        spacing: 2

                        RadioButton {
                            property string value

                            id: mathpix_select
                            value: 'mathpix'
                            checked: true
                            text: qsTr("Mathpix")
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

                        Text {
                            id: link_free_resource
                            Layout.columnSpan: 4
                            text: '<a href="https://console.bce.baidu.com/ai/#/ai/ocr/overview/resource/getFree">Get free quota</a>'
                            onLinkActivated: Qt.openUrlExternally(link)
                            MouseArea {
                                id: freeLinkMouseArea
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                enabled: false
                            }
                        }

                        Label {
                            id: appid_label
                            text: qsTr("APP_ID")
                        }

                        TextField {
                            id: appid_input
                            text: backend.appid
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }

                        Label {
                            id: apikey_label
                            text: qsTr("API_KEY")
                        }

                        TextField {
                            id: apikey_input
                            text: backend.apikey
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }

                        Label {
                            id: seckey_label
                            text: qsTr("SECRET_KEY")
                        }

                        TextField {
                            id: seckey_input
                            text: backend.seckey
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
                            spacing: 2

                            Repeater {
                                model: backend.all_language_tags
                                CheckBox {
                                    property string value

                                    text: qsTr(backend.all_language_names[index])
                                    checked: backend.languages.includes(this.value)
                                    value: modelData
                                }
                            }
                        }

                        Label {
                            id: default_lang_label
                            text: qsTr("Default language")
                        }

                        TextField {
                            id: default_lang_input
                            text: backend.default_language
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }

                        Row {
                            CheckBox {
                                id: accurate_input
                                text: qsTr('Use accurate mode')
                                checked: backend.accurate
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
                            text: backend.yd_appid
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }

                        Label {
                            id: yd_seckey_label
                            text: qsTr("SEC_KEY")
                        }

                        TextField {
                            id: yd_seckey_input
                            text: backend.yd_seckey
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
                            text: backend.face_apikey
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

                GroupBox {
                    id: group4
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop
                    title: qsTr("Mathpix OCR")

                    GridLayout {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.topMargin: 0
                        anchors.rightMargin: 0
                        anchors.leftMargin: 0
                        columns: 4

                        Label {
                            id: mathpix_appid_label
                            text: qsTr("App ID")
                        }

                        TextField {
                            id: mathpix_appid_input
                            text: backend.mathpix_appid
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }

                        Label {
                            id: mathpix_appkey_label
                            text: qsTr("App Key")
                        }

                        TextField {
                            id: mathpix_appkey_input
                            text: backend ? backend.mathpix_appkey : ''
                            Layout.columnSpan: 3
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }

    ToolBar {
        id: bottom_toolbar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        ButtonGroup {
            id: button_group
            buttons: buttons.children
        }

        Row {
            id: buttons
            anchors.fill: parent
            layoutDirection: Qt.RightToLeft

            function saveAll() {
                backend.autostart = autostart_input.checked
                backend.appid = appid_input.text
                backend.apikey = apikey_input.text
                backend.seckey = seckey_input.text
                backend.accurate = accurate_input.checked
                backend.default_language = default_lang_input.text

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
                backend.mode = working_mode_select.currentValue
                var radios = select_flow.children
                for (var i=0; i < radios.length; i++)
                    if (radios[i].checked)
                        backend.default_backend = radios[i].value

                backend.save()
            }

            Button {
                id: save_button
                text: qsTr('Save')
                enabled: true
                onClicked: {
                    parent.saveAll()
                    setting.visible = false
                }
            }

            Button {
                id: apply_button
                text: qsTr('Apply')
                enabled: true
                onClicked: {
                    parent.saveAll()
                }
            }

            Button {
                text: qsTr('Close')
                onClicked: setting.visible = false
            }

            Button {
                text: qsTr('Open in editor')
                onClicked: {
                    backend.open_setting_file()
                }
            }
        }
    }
}
