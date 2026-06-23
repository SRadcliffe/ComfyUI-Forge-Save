# ComfyUI Forge Save

Production-focused save nodes for ComfyUI with structured image and video output, automatic versioning, preview generation, and organised project folders.

Forge Save is designed for creators, studios, and production teams who need predictable output structures instead of dumping every render into a single output directory.

---

## Features

* Save images to PNG, JPG, or WEBP
* Save videos to MP4, WEBM, or GIF
* Automatic version numbering
* Organised project-based folder structure
* Preview image generation for videos
* Open Image Folder button
* Open Video Folder button
* Shot-based naming system
* Production-friendly output organisation
* No manual version management required

---

## Nodes

Forge Save adds two nodes:

### Forge Save Image

Save generated images into organised project folders with automatic versioning.

### Forge Save Video

Encode image frame batches into MP4, WEBM, or GIF files with optional preview images.

Nodes appear under:

```text
Forge Save
```

---

## Screenshots

### Forge Save Image

![Forge Save Image](assets/forge-save-image-node.png)

### Forge Save Video

![Forge Save Video](assets/forge-save-video-node.png)

---

## Example Output Structure

### Images

```text
ComfyUI/output/
└── Demo_Project/
    └── Shot_Development/
        └── shots/
            ├── shot_01_hero_render_v001.png
            ├── shot_01_hero_render_v002.png
            └── shot_01_hero_render_v003.png
```

### Videos

```text
ComfyUI/output/
└── Demo_Project/
    └── Shot_Development/
        └── videos/
            ├── shot_01_hero_animation_v001.mp4
            └── _previews/
                ├── preview_shot_01_hero_animation_v001_frame_001.png
                ├── preview_shot_01_hero_animation_v001_frame_002.png
                └── preview_shot_01_hero_animation_v001_frame_003.png
```

---

## Automatic Versioning

Forge Save automatically checks the output directory and increments the version number.

If this file already exists:

```text
shot_01_hero_render_v001.png
```

The next render becomes:

```text
shot_01_hero_render_v002.png
```

Then:

```text
shot_01_hero_render_v003.png
```

This prevents accidental overwriting and keeps render history intact.

---

## Forge Save Image

### Inputs

```text
images
project_name
folder_name
shot_number
shot_label
image_format
jpg_quality
```

### Example Settings

```text
project_name: Demo_Project
folder_name: Shot_Development
shot_number: 1
shot_label: hero_render
image_format: png
jpg_quality: 95
```

### Example Output

```text
ComfyUI/output/Demo_Project/Shot_Development/shots/shot_01_hero_render_v001.png
```

---

## Forge Save Video

### Inputs

```text
frames
project_name
folder_name
shot_number
shot_label
fps
video_format
quality
preview_images
```

### Important

Forge Save Video expects an IMAGE frame batch, not a VIDEO object.

Connect it before your final video combine/output node.

### Example Settings

```text
project_name: Demo_Project
folder_name: Shot_Development
shot_number: 1
shot_label: hero_animation
fps: 30
video_format: mp4
quality: 8
preview_images: 3
```

### Example Output

```text
ComfyUI/output/Demo_Project/Shot_Development/videos/shot_01_hero_animation_v001.mp4
```

Preview images:

```text
ComfyUI/output/Demo_Project/Shot_Development/videos/_previews/
```

---

## Video Quality

The quality slider ranges from:

```text
1  = Smaller file size
10 = Highest quality
```

Recommended values:

```text
8–10
```

for most production workflows.

---

## Installation

Clone the repository into your ComfyUI custom_nodes folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/SRadcliffe/ComfyUI-Forge-Save.git
```

Restart ComfyUI.

---

## Requirements

```text
numpy
pillow
imageio
imageio-ffmpeg
```

Install manually if required:

```bash
pip install -r requirements.txt
```

---

## Repository Structure

```text
ComfyUI-ForgeSave/
├── __init__.py
├── README.md
├── LICENSE
├── requirements.txt
├── assets/
│   ├── forge-save-image-node.png
│   └── forge-save-video-node.png
├── nodes/
│   ├── forge_save_image.py
│   └── forge_save_video.py
└── web/
    └── forge_save.js
```

---

## Open Folder Buttons

Both nodes include quick-access buttons:

```text
Open Image Folder
Open Video Folder
```

These automatically open the correct output directory in your operating system.

---

## Typical Use Cases

* AI image generation
* AI video production
* Product visualisation
* Automotive workflows
* Architectural visualisation
* Batch rendering
* Client projects
* Shot-based production pipelines
* Version-controlled render output

---

## Roadmap

Planned additions:

* Forge Contact Sheet
* Forge Metadata Export
* Forge Review Video
* Forge Project Manager

---

## Support

If Forge Save helps your workflow, support future development:

https://buymeacoffee.com/sradcliffe

---

## License

MIT License

---

## Author

Created by ForgeWorks Studio

Simon Radcliffe
