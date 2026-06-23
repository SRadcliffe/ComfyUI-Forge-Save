import json
import os
import re
from datetime import datetime

import numpy as np
from PIL import Image

try:
    import folder_paths
except Exception:
    folder_paths = None


def sanitize_filename(value: str, fallback: str = "untitled") -> str:
    if value is None:
        value = fallback

    value = str(value).strip()

    if not value:
        value = fallback

    value = value.replace(" ", "_")
    value = re.sub(r"[^a-zA-Z0-9_\-\.]", "", value)
    value = re.sub(r"_+", "_", value)

    return value or fallback


def get_comfy_output_dir() -> str:
    if folder_paths is not None:
        return folder_paths.get_output_directory()

    return os.path.join(os.getcwd(), "output")


def tensor_to_numpy_frame(image_tensor):
    image = 255.0 * image_tensor.cpu().numpy()
    image = np.clip(image, 0, 255).astype(np.uint8)

    if image.shape[-1] == 4:
        image = image[:, :, :3]

    return image


def get_next_version(save_dir: str, shot_number: int, shot_label: str, extensions) -> int:
    if not os.path.isdir(save_dir):
        return 1

    safe_shot_label = re.escape(shot_label)
    shot_prefix = f"shot_{shot_number:02d}"
    escaped_extensions = "|".join([re.escape(ext.lower()) for ext in extensions])

    pattern = re.compile(
        rf"^{shot_prefix}_{safe_shot_label}_v(\d{{3}})(?:_\d{{3}})?\.({escaped_extensions})$",
        re.IGNORECASE,
    )

    highest_version = 0

    for filename in os.listdir(save_dir):
        match = pattern.match(filename)
        if match:
            try:
                found_version = int(match.group(1))
                highest_version = max(highest_version, found_version)
            except ValueError:
                pass

    return highest_version + 1


def write_video_recipe_json(
    recipe_path,
    project_name,
    folder_name,
    shot_number,
    shot_label,
    version_number,
    filename,
    video_format,
    fps,
    quality,
    frame_count,
    width,
    height,
    preview_images,
):
    metadata = {
        "forge_save": {
            "tool": "ComfyUI Forge Save",
            "node": "Save Video",
            "recipe_version": "1.0",
        },
        "output": {
            "project_name": project_name,
            "folder_name": folder_name,
            "shot_number": int(shot_number),
            "shot_label": shot_label,
            "version": int(version_number),
            "file_name": filename,
            "video_format": video_format,
            "created": datetime.now().isoformat(timespec="seconds"),
        },
        "video_recipe": {
            "fps": float(fps),
            "quality": int(quality),
            "frame_count": int(frame_count),
            "width": int(width),
            "height": int(height),
            "preview_images": int(preview_images),
        },
        "notes": {
            "reproduction_warning": (
                "Video reproduction depends on matching source frames, frame order, "
                "codec support, encoder behaviour, and local environment."
            )
        },
    }

    with open(recipe_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)


class ForgeSaveVideo:
    def __init__(self):
        self.output_dir = get_comfy_output_dir()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": ("IMAGE",),
                "project_name": ("STRING", {"default": "ProjectName", "multiline": False}),
                "folder_name": ("STRING", {"default": "Scene_Or_Episode_Name", "multiline": False}),
                "shot_number": ("INT", {"default": 1, "min": 1, "max": 999, "step": 1}),
                "shot_label": ("STRING", {"default": "location_label", "multiline": False}),
                "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 120.0, "step": 1.0}),
                "video_format": (["mp4", "webm", "gif"], {"default": "mp4"}),
                "quality": ("INT", {"default": 8, "min": 1, "max": 10, "step": 1}),
                "preview_images": ("INT", {"default": 3, "min": 0, "max": 12, "step": 1}),
                "video_recipe": (["Off", "On"], {"default": "Off"}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_video"
    OUTPUT_NODE = True
    CATEGORY = "Forge Save"

    def save_video(
        self,
        frames,
        project_name,
        folder_name,
        shot_number,
        shot_label,
        fps,
        video_format,
        quality,
        preview_images,
        video_recipe,
    ):
        safe_project_name = sanitize_filename(project_name, "Project")
        safe_folder_name = sanitize_filename(folder_name, "Folder")
        safe_shot_label = sanitize_filename(shot_label, "shot")

        save_dir = os.path.join(
            self.output_dir,
            safe_project_name,
            safe_folder_name,
        )

        preview_dir = os.path.join(save_dir, "_previews")

        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(preview_dir, exist_ok=True)

        auto_version_number = get_next_version(
            save_dir=save_dir,
            shot_number=shot_number,
            shot_label=safe_shot_label,
            extensions=["mp4", "webm", "gif"],
        )

        filename = (
            f"shot_{shot_number:02d}_"
            f"{safe_shot_label}_"
            f"v{auto_version_number:03d}."
            f"{video_format}"
        )

        file_path = os.path.join(save_dir, filename)

        while os.path.exists(file_path):
            auto_version_number += 1
            filename = (
                f"shot_{shot_number:02d}_"
                f"{safe_shot_label}_"
                f"v{auto_version_number:03d}."
                f"{video_format}"
            )
            file_path = os.path.join(save_dir, filename)

        frame_list = [tensor_to_numpy_frame(frame) for frame in frames]

        if not frame_list:
            raise RuntimeError("Forge Save Video received no frames.")

        frame_count = len(frame_list)
        height, width = frame_list[0].shape[:2]

        preview_results = []

        preview_count = int(preview_images)
        preview_count = max(0, min(preview_count, frame_count))

        if preview_count > 0:
            if preview_count == 1:
                preview_indices = [0]
            else:
                preview_indices = np.linspace(
                    0,
                    frame_count - 1,
                    preview_count,
                    dtype=int,
                ).tolist()

            relative_preview_subfolder = os.path.join(
                safe_project_name,
                safe_folder_name,
                "_previews",
            )

            for preview_index, frame_index in enumerate(preview_indices):
                preview_filename = (
                    f"preview_"
                    f"shot_{shot_number:02d}_"
                    f"{safe_shot_label}_"
                    f"v{auto_version_number:03d}_"
                    f"frame_{preview_index + 1:03d}.png"
                )

                preview_path = os.path.join(preview_dir, preview_filename)

                Image.fromarray(frame_list[frame_index]).save(
                    preview_path,
                    compress_level=4,
                )

                preview_results.append(
                    {
                        "filename": preview_filename,
                        "subfolder": relative_preview_subfolder,
                        "type": "output",
                    }
                )

        if video_recipe == "On":
            recipe_filename = filename.rsplit(".", 1)[0] + ".json"
            recipe_path = os.path.join(save_dir, recipe_filename)

            write_video_recipe_json(
                recipe_path=recipe_path,
                project_name=safe_project_name,
                folder_name=safe_folder_name,
                shot_number=shot_number,
                shot_label=safe_shot_label,
                version_number=auto_version_number,
                filename=filename,
                video_format=video_format,
                fps=fps,
                quality=quality,
                frame_count=frame_count,
                width=width,
                height=height,
                preview_images=preview_count,
            )

        if video_format == "gif":
            duration_ms = int(1000 / float(fps))

            pil_frames = [
                Image.fromarray(frame).convert("P", palette=Image.ADAPTIVE)
                for frame in frame_list
            ]

            pil_frames[0].save(
                file_path,
                save_all=True,
                append_images=pil_frames[1:],
                duration=duration_ms,
                loop=0,
                optimize=True,
            )

            return {"ui": {"images": preview_results}}

        try:
            import imageio.v3 as iio
        except Exception as error:
            raise RuntimeError(
                "Forge Save Video needs imageio and imageio-ffmpeg. "
                "Install them inside your ComfyUI Python environment with:\n\n"
                "pip install imageio imageio-ffmpeg"
            ) from error

        quality = int(quality)
        quality = max(1, min(10, quality))

        crf = int(round(34 - ((quality - 1) / 9) * 18))
        crf = max(16, min(34, crf))

        if video_format == "mp4":
            iio.imwrite(
                file_path,
                frame_list,
                fps=float(fps),
                codec="libx264",
                quality=None,
                output_params=[
                    "-crf",
                    str(crf),
                    "-pix_fmt",
                    "yuv420p",
                ],
            )

        elif video_format == "webm":
            iio.imwrite(
                file_path,
                frame_list,
                fps=float(fps),
                codec="libvpx-vp9",
                quality=None,
                output_params=[
                    "-crf",
                    str(crf),
                    "-b:v",
                    "0",
                ],
            )

        return {"ui": {"images": preview_results}}