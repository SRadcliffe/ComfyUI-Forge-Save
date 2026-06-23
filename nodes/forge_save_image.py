import os
import re
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


def tensor_to_pil(image_tensor):
    image = 255.0 * image_tensor.cpu().numpy()
    image = np.clip(image, 0, 255).astype(np.uint8)

    if image.shape[-1] == 4:
        return Image.fromarray(image, "RGBA")

    return Image.fromarray(image, "RGB")


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


class ForgeSaveImage:
    def __init__(self):
        self.output_dir = get_comfy_output_dir()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "project_name": ("STRING", {"default": "ProjectName", "multiline": False}),
                "folder_name": ("STRING", {"default": "Scene_Or_Episode_Name", "multiline": False}),
                "shot_number": ("INT", {"default": 1, "min": 1, "max": 999, "step": 1}),
                "shot_label": ("STRING", {"default": "location_label", "multiline": False}),
                "image_format": (["png", "jpg", "webp"], {"default": "png"}),
                "jpg_quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "Forge Save"

    def save_images(
        self,
        images,
        project_name,
        folder_name,
        shot_number,
        shot_label,
        image_format,
        jpg_quality,
    ):
        safe_project_name = sanitize_filename(project_name, "Project")
        safe_folder_name = sanitize_filename(folder_name, "Folder")
        safe_shot_label = sanitize_filename(shot_label, "shot")

        save_dir = os.path.join(
            self.output_dir,
            safe_project_name,
            safe_folder_name,
            "shots",
        )

        os.makedirs(save_dir, exist_ok=True)

        auto_version_number = get_next_version(
            save_dir=save_dir,
            shot_number=shot_number,
            shot_label=safe_shot_label,
            extensions=["png", "jpg", "webp"],
        )

        results = []

        for batch_index, image_tensor in enumerate(images):
            pil_image = tensor_to_pil(image_tensor)

            batch_suffix = ""
            if len(images) > 1:
                batch_suffix = f"_{batch_index + 1:03d}"

            filename = (
                f"shot_{shot_number:02d}_"
                f"{safe_shot_label}_"
                f"v{auto_version_number:03d}"
                f"{batch_suffix}."
                f"{image_format}"
            )

            file_path = os.path.join(save_dir, filename)

            while os.path.exists(file_path):
                auto_version_number += 1
                filename = (
                    f"shot_{shot_number:02d}_"
                    f"{safe_shot_label}_"
                    f"v{auto_version_number:03d}"
                    f"{batch_suffix}."
                    f"{image_format}"
                )
                file_path = os.path.join(save_dir, filename)

            if image_format == "jpg":
                if pil_image.mode == "RGBA":
                    pil_image = pil_image.convert("RGB")
                pil_image.save(file_path, quality=jpg_quality, optimize=True)

            elif image_format == "webp":
                pil_image.save(file_path, quality=jpg_quality, method=6)

            else:
                pil_image.save(file_path, compress_level=4)

            relative_subfolder = os.path.join(
                safe_project_name,
                safe_folder_name,
                "shots",
            )

            results.append(
                {
                    "filename": filename,
                    "subfolder": relative_subfolder,
                    "type": "output",
                }
            )

        return {"ui": {"images": results}}