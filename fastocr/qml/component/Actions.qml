import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ColumnLayout {
    id: actions
    anchors.fill: parent

    Button {
        text: "Test"
        onClicked: {
            actionWizard.open()
        }
    }

    ActionWizard {
        id: actionWizard
        Layout.fillWidth: true

        Component.onCompleted: {
            this.actionGenerated.connect(actions.actionAdd)
        }
    }

    function actionAdd(data) {
        console.log(data)
    }
}
