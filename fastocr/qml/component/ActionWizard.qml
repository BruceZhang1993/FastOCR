import QtQuick 2.3
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    property int step

    signal actionGenerated(var action)

    id: actionDialog
    visible: false
    title: 'Create new action'
    modal: true

    Component.onCompleted: {
        this.step = 0
    }

    contentItem: StackLayout {
        width: parent.width
        anchors.fill: parent
        currentIndex: actionDialog.step

        Rectangle {
            color: 'lightskyblue'
            implicitWidth: 400
            implicitHeight: 100
        }

        Rectangle {
            color: 'skyblue'
            implicitWidth: 400
            implicitHeight: 100
        }

        Rectangle {
            color: 'blue'
            implicitWidth: 400
            implicitHeight: 100
        }
    }

    footer: DialogButtonBox {
        Button {
            enabled: false
            id: backButton
            objectName: 'backButton'
            text: qsTr("Back")
            DialogButtonBox.buttonRole: DialogButtonBox.ActionRole
        }

        Button {
            id: nextButton
            objectName: 'nextButton'
            text: qsTr("Next")
            DialogButtonBox.buttonRole: DialogButtonBox.ActionRole
        }

        onClicked: {
            switch (button.objectName) {
                case 'nextButton':
                    actionDialog.step ++
                    backButton.enabled = true
                    if (actionDialog.step >= 3) {
                        actionDialog.actionGenerated('test')
                        actionDialog.close()
                    } else if (actionDialog.step >= 2) {
                        nextButton.text = qsTr("Ok")
                    }
                    break;
                case 'backButton':
                    actionDialog.step --
                    nextButton.text = qsTr("Next")
                    if (actionDialog.step <= 0) {
                        backButton.enabled = false
                    }
                    break;
            }

        }
    }
}
