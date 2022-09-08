// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.3
import QtQuick.Controls 1.4 as Controls1

import UM 1.3 as UM
import Cura 1.0 as Cura

Item
{
    id: widget

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    function requestConnectToPrint()
    {
        UM.ConnectToPrintManager.run();
    }

    Cura.PrimaryButton
    {
        id: connectToPrintButton
        height: parent.height

        shadowEnabled: true
        shadowColor: UM.Theme.getColor("primary_shadow")
        cornerSide: Cura.RoundedRectangle.Direction.Right

        anchors
        {
            top: parent.top
            right: parent.right
        }

        leftPadding: UM.Theme.getSize("narrow_margin").width //Need more space than usual here for wide text.
        rightPadding: UM.Theme.getSize("narrow_margin").width
        iconSource: popup.opened ? UM.Theme.getIcon("arrow_top") : UM.Theme.getIcon("arrow_bottom")
        color: UM.Theme.getColor("action_panel_secondary")
        visible: (devicesModel.deviceCount > 1)
        text: catalog.i18nc("@button", "Connect to print")

        onClicked:
        {
            forceActiveFocus()
            widget.requestConnectToPrint()
        }
    }
}