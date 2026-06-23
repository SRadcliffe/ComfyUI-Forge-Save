# ComfyUI Forge Save

Production-focused save nodes for ComfyUI with structured image and video output, automatic versioning, contact sheet generation, preview generation, and organised project folders.

Forge Save is designed for creators, studios, and production teams who need predictable output paths instead of dumping every render into a single output directory.

---

## Features

* Save images to PNG, JPG, or WEBP
* Save videos to MP4, WEBM, or GIF
* Automatic version numbering
* Clean project-based folder structure
* Optional contact sheet generation
* Smart preview behaviour for contact sheets
* Preview image generation for videos
* Open Image Folder button
* Open Video Folder button
* Shot-based naming system
* No manual version management required

---

## Nodes

Forge Save adds two nodes:

### Save Image

Saves generated images into organised project folders with automatic versioning.

Optional contact sheet generation can be enabled directly on the image save node.

### Save Video

Encodes image frame batches into MP4, WEBM, or GIF files with optional preview images.

Nodes appear under:

```text
Forge Save
```

---

## Screenshots

### Forge Save Image

![Forge Save Image](assets/forge-save-image-node.png)

### Contact Sheet Generation

![Contact Sheet Generation](assets/forge-save-contact-sheet.png)

### Forge Save Video

![Forge Save Video](assets/forge-save-video-node.png)

---

## Example Output Structure

### Images

```text
ComfyUI/output/
└── Demo_Project/
    └── Product_Shoot/
        ├── shot_01_hero_render_v001.png
        ├── shot_01_hero_render_v002.png
        ├── shot_01_hero_render_v003.png
        └── contact_sheet_shot_01_hero_render_v003.jpg
```

### Videos

```text
ComfyUI/output/
└── Demo_Project/
    └── Product_Shoot/
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

## Save Image

### Inputs

```text
images
project_name
folder_name
shot_number
shot_label
image_format
jpg_quality
generate_contact_sheet
contact_sheet_columns
```

### Example Settings

```text
project_name: Demo_Project
folder_name: Product_Shoot
shot_number: 1
shot_label: hero_render
image_format: png
jpg_quality: 95
generate_contact_sheet: true
contact_sheet_columns: 4
```

### Example Output

```text
ComfyUI/output/Demo_Project/Product_Shoot/shot_01_hero_render_v001.png
ComfyUI/output/Demo_Project/Product_Shoot/contact_sheet_shot_01_hero_render_v001.jpg
```

---

## Contact Sheet Generation

Forge Save Image can automatically generate a contact sheet from the images being saved.

When `generate_contact_sheet` is enabled, Forge Save will:

* Save all generated images normally
* Create a review contact sheet in the same project folder
* Display only the contact sheet in the ComfyUI preview panel
* Keep the original images available on disk

When `generate_contact_sheet` is disabled, Forge Save displays the individual saved images as normal.

This is useful for:

* Client reviews
* Comparing image variations
* Product photography workflows
* Fashion campaign selection
* Batch generation review
* AI art direction and selection

---

## Save Video

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
folder_name: Product_Shoot
shot_number: 1
shot_label: hero_animation
fps: 30
video_format: mp4
quality: 8
preview_images: 3
```

### Example Output

```text
ComfyUI/output/Demo_Project/Product_Shoot/shot_01_hero_animation_v001.mp4
```

Preview images:

```text
ComfyUI/output/Demo_Project/Product_Shoot/_previews/
```

---

## Video Quality

The video quality slider ranges from:

```text
1  = Smaller file size
10 = Higher quality
```

Recommended values:

```text
8–10
```

for most production workflows.

---

## Installation

Clone the repository into your ComfyUI `custom_nodes` folder:

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

Depending on your ComfyUI setup, some of these may already be installed.

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
│   ├── forge-save-contact-sheet.png
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

These automatically open the relevant output directory on the machine running ComfyUI.

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
* Contact sheet review workflows

---

## Roadmap

Planned additions:

* Metadata export
* Render manifest export
* Review video generation
* Project presets
* Wider ForgeFlow production toolkit modules

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
