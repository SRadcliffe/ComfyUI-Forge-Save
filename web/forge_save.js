import { app } from "../../../scripts/app.js";

function getWidgetValue(node, widgetName, fallback = "") {
    if (!node.widgets) {
        return fallback;
    }

    const widget = node.widgets.find((w) => w.name === widgetName);

    if (!widget) {
        return fallback;
    }

    return widget.value ?? fallback;
}

function addOpenFolderButton(node, outputType) {
    const label =
        outputType === "videos"
            ? "Open Video Folder"
            : "Open Image Folder";

    node.addWidget(
        "button",
        label,
        "open",
        async () => {
            const projectName = getWidgetValue(
                node,
                "project_name",
                "ProjectName"
            );

            const folderName = getWidgetValue(
                node,
                "folder_name",
                "Scene_Or_Episode_Name"
            );

            try {
                const response = await fetch(
                    "/forge_save/open_output_folder",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            project_name: projectName,
                            folder_name: folderName,
                            output_type: outputType,
                        }),
                    }
                );

                const result = await response.json();

                if (!response.ok || !result.success) {
                    const message = result.error || "Unknown error";
                    console.error("[Forge Save]", message);
                    alert(`Could not open output folder:\n${message}`);
                    return;
                }

                console.log(
                    "[Forge Save] Opened output folder:",
                    result.path
                );
            } catch (error) {
                console.error("[Forge Save]", error);
                alert(`Could not open output folder:\n${error.message}`);
            }
        }
    );
}

app.registerExtension({
    name: "ForgeSave.OpenOutputFolder",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (
            nodeData.name !== "ForgeSaveImage" &&
            nodeData.name !== "ForgeSaveVideo"
        ) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function () {
            if (originalOnNodeCreated) {
                originalOnNodeCreated.apply(this, arguments);
            }

            if (nodeData.name === "ForgeSaveVideo") {
                addOpenFolderButton(this, "videos");
            } else {
                addOpenFolderButton(this, "shots");
            }
        };
    },
});