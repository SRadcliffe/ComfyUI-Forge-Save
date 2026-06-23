import os
import sys
import subprocess

try:
    from aiohttp import web
    from server import PromptServer
except Exception:
    web = None
    PromptServer = None

from .nodes.forge_save_image import (
    ForgeSaveImage,
    sanitize_filename,
    get_comfy_output_dir,
)

from .nodes.forge_save_video import ForgeSaveVideo


WEB_DIRECTORY = "./web"


def open_folder_in_os(folder_path: str):
    folder_path = os.path.abspath(folder_path)

    if not os.path.isdir(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    if sys.platform.startswith("win"):
        os.startfile(folder_path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", folder_path])
    else:
        subprocess.Popen(["xdg-open", folder_path])


if PromptServer is not None and web is not None:
    @PromptServer.instance.routes.post("/forge_save/open_output_folder")
    async def forge_save_open_output_folder(request):
        try:
            data = await request.json()

            project_name = sanitize_filename(
                data.get("project_name", "ProjectName"),
                "Project",
            )

            folder_name = sanitize_filename(
                data.get("folder_name", "Scene_Or_Episode_Name"),
                "Folder",
            )

            output_type = sanitize_filename(
                data.get("output_type", "shots"),
                "shots",
            )

            if output_type not in ["shots", "videos"]:
                output_type = "shots"

            output_dir = get_comfy_output_dir()

            target_dir = os.path.join(
                output_dir,
                project_name,
                folder_name,
                output_type,
            )

            open_folder_in_os(target_dir)

            return web.json_response(
                {
                    "success": True,
                    "path": target_dir,
                }
            )

        except Exception as error:
            return web.json_response(
                {
                    "success": False,
                    "error": str(error),
                },
                status=500,
            )


NODE_CLASS_MAPPINGS = {
    "ForgeSaveImage": ForgeSaveImage,
    "ForgeSaveVideo": ForgeSaveVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ForgeSaveImage": "Save Image",
    "ForgeSaveVideo": "Save Video",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]