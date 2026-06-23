import json
import math
import os
import re
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFont

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
                highest_version = max(highest_version, int(match.group(1)))
            except ValueError:
                pass

    return highest_version + 1


def find_first_node_by_class(prompt, class_type):
    if not isinstance(prompt, dict):
        return None

    for node in prompt.values():
        if isinstance(node, dict) and node.get("class_type") == class_type:
            return node

    return None


def find_nodes_by_class(prompt, class_type):
    if not isinstance(prompt, dict):
        return []

    return [
        node for node in prompt.values()
        if isinstance(node, dict) and node.get("class_type") == class_type
    ]


def extract_reproduction_summary(prompt=None):
    summary = {
        "prompt": None,
        "negative_prompt": None,
        "seed": None,
        "steps": None,
        "cfg": None,
        "sampler": None,
        "scheduler": None,
        "denoise": None,
        "model": None,
        "clip": None,
        "vae": None,
        "width": None,
        "height": None,
        "batch_size": None,
    }

    if not isinstance(prompt, dict):
        return summary

    sampler_node = find_first_node_by_class(prompt, "KSampler")
    if sampler_node:
        inputs = sampler_node.get("inputs", {})
        summary["seed"] = inputs.get("seed")
        summary["steps"] = inputs.get("steps")
        summary["cfg"] = inputs.get("cfg")
        summary["sampler"] = inputs.get("sampler_name")
        summary["scheduler"] = inputs.get("scheduler")
        summary["denoise"] = inputs.get("denoise")

    text_nodes = find_nodes_by_class(prompt, "CLIPTextEncode")
    if text_nodes:
        summary["prompt"] = text_nodes[0].get("inputs", {}).get("text")

        if len(text_nodes) > 1:
            summary["negative_prompt"] = text_nodes[1].get("inputs", {}).get("text")

    unet_node = find_first_node_by_class(prompt, "UNETLoader")
    if unet_node:
        summary["model"] = unet_node.get("inputs", {}).get("unet_name")

    clip_node = find_first_node_by_class(prompt, "CLIPLoader")
    if clip_node:
        summary["clip"] = clip_node.get("inputs", {}).get("clip_name")

    vae_node = find_first_node_by_class(prompt, "VAELoader")
    if vae_node:
        summary["vae"] = vae_node.get("inputs", {}).get("vae_name")

    latent_node = (
        find_first_node_by_class(prompt, "EmptySD3LatentImage")
        or find_first_node_by_class(prompt, "EmptyLatentImage")
    )

    if latent_node:
        inputs = latent_node.get("inputs", {})
        summary["width"] = inputs.get("width")
        summary["height"] = inputs.get("height")
        summary["batch_size"] = inputs.get("batch_size")

    return summary


def write_image_recipe_json(
    metadata_path,
    project_name,
    folder_name,
    shot_number,
    shot_label,
    version_number,
    filename,
    image_format,
    jpg_quality,
    batch_index,
    batch_count,
    prompt=None,
):
    metadata = {
        "forge_save": {
            "tool": "ComfyUI Forge Save",
            "node": "Save Image",
            "metadata_version": "1.0",
        },
        "output": {
            "project_name": project_name,
            "folder_name": folder_name,
            "shot_number": int(shot_number),
            "shot_label": shot_label,
            "version": int(version_number),
            "file_name": filename,
            "image_format": image_format,
            "jpg_quality": int(jpg_quality),
            "batch_index": int(batch_index),
            "batch_count": int(batch_count),
            "created": datetime.now().isoformat(timespec="seconds"),
        },
        "image_recipe": extract_reproduction_summary(prompt=prompt),
        "notes": {
            "reproduction_warning": (
                "Exact 1:1 reproduction depends on matching models, LoRAs, "
                "custom nodes, ComfyUI version, sampler behaviour, and local environment."
            )
        },
    }

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)


def create_contact_sheet_image(
    saved_image_paths,
    output_path,
    columns=3,
    thumb_width=384,
    padding=24,
):
    if not saved_image_paths:
        return

    columns = max(1, int(columns))
    padding = max(0, int(padding))
    thumb_width = max(128, int(thumb_width))

    source_images = []

    for path in saved_image_paths:
        try:
            img = Image.open(path).convert("RGB")
            source_images.append((path, img.copy()))
            img.close()
        except Exception:
            pass

    if not source_images:
        return

    resized_images = []
    thumb_heights = []

    for path, image in source_images:
        ratio = thumb_width / image.width
        thumb_height = int(image.height * ratio)
        resized = image.resize((thumb_width, thumb_height), Image.LANCZOS)
        resized_images.append((path, resized))
        thumb_heights.append(thumb_height)

    rows = math.ceil(len(resized_images) / columns)
    label_height = 34
    cell_width = thumb_width
    cell_height = max(thumb_heights) + label_height

    sheet_width = (columns * cell_width) + ((columns + 1) * padding)
    sheet_height = (rows * cell_height) + ((rows + 1) * padding)

    sheet = Image.new("RGB", (sheet_width, sheet_height), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    for index, (path, image) in enumerate(resized_images):
        row = index // columns
        col = index % columns

        x = padding + col * (cell_width + padding)
        y = padding + row * (cell_height + padding)

        sheet.paste(image, (x, y))

        label = f"{index + 1:03d}"
        label_y = y + max(thumb_heights) + 8
        draw.text((x, label_y), label, fill=(220, 220, 220), font=font)

    sheet.save(output_path, quality=92, optimize=True)


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
                "contact_sheet": ("BOOLEAN", {"default": False}),
                "sheet_columns": ("INT", {"default": 4, "min": 1, "max": 12, "step": 1}),
                "image_recipe": (["Off", "On"], {"default": "Off"}),
            },
            "hidden": {
                "prompt": "PROMPT",
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
        contact_sheet,
        sheet_columns,
        image_recipe,
        prompt=None,
    ):
        safe_project_name = sanitize_filename(project_name, "Project")
        safe_folder_name = sanitize_filename(folder_name, "Folder")
        safe_shot_label = sanitize_filename(shot_label, "shot")

        save_dir = os.path.join(
            self.output_dir,
            safe_project_name,
            safe_folder_name,
        )

        os.makedirs(save_dir, exist_ok=True)

        auto_version_number = get_next_version(
            save_dir=save_dir,
            shot_number=shot_number,
            shot_label=safe_shot_label,
            extensions=["png", "jpg", "webp"],
        )

        results = []
        saved_image_paths = []
        relative_subfolder = os.path.join(safe_project_name, safe_folder_name)
        batch_count = len(images)

        for batch_index, image_tensor in enumerate(images):
            pil_image = tensor_to_pil(image_tensor)

            batch_suffix = ""
            if batch_count > 1:
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

            saved_image_paths.append(file_path)

            if image_recipe == "On":
                base_name = filename.rsplit(".", 1)[0]
                metadata_path = os.path.join(save_dir, f"{base_name}.json")

                write_image_recipe_json(
                    metadata_path=metadata_path,
                    project_name=safe_project_name,
                    folder_name=safe_folder_name,
                    shot_number=shot_number,
                    shot_label=safe_shot_label,
                    version_number=auto_version_number,
                    filename=filename,
                    image_format=image_format,
                    jpg_quality=jpg_quality,
                    batch_index=batch_index + 1,
                    batch_count=batch_count,
                    prompt=prompt,
                )

            results.append(
                {
                    "filename": filename,
                    "subfolder": relative_subfolder,
                    "type": "output",
                }
            )

        if contact_sheet and saved_image_paths:
            contact_sheet_filename = (
                f"contact_sheet_"
                f"shot_{shot_number:02d}_"
                f"{safe_shot_label}_"
                f"v{auto_version_number:03d}.jpg"
            )

            contact_sheet_path = os.path.join(save_dir, contact_sheet_filename)

            create_contact_sheet_image(
                saved_image_paths=saved_image_paths,
                output_path=contact_sheet_path,
                columns=sheet_columns,
            )

            return {
                "ui": {
                    "images": [
                        {
                            "filename": contact_sheet_filename,
                            "subfolder": relative_subfolder,
                            "type": "output",
                        }
                    ]
                }
            }

        return {"ui": {"images": results}}