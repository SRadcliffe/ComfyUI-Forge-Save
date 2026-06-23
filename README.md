# ComfyUI ForgeSave

**ComfyUI ForgeSave** is a small production-focused custom node pack for ComfyUI.

It adds clean, organised save nodes for image and video workflows, with automatic version numbering and a project-based folder structure.

ForgeSave is designed for users who want predictable production output paths instead of dumping every render into one large output folder.

---

## Nodes

ForgeSave adds two nodes:

- **Save Image**
- **Save Video**

They appear in ComfyUI under:

```text
Forge Save
```

---

## Output Structure

ForgeSave saves files into a clean project/folder structure inside your ComfyUI output directory.

### Images

```text
ComfyUI/output/
└── ProjectName/
    └── Scene_Or_Episode_Name/
        └── shots/
            └── shot_01_location_label_v001.png
```

Example:

```text
ComfyUI/output/
└── BadlyRunByAnimals/
    └── EP002_Seagull_And_Sons_Fish_Bar/
        └── shots/
            └── shot_01_exterior_fish_bar_v001.png
```

### Videos

```text
ComfyUI/output/
└── ProjectName/
    └── Scene_Or_Episode_Name/
        └── videos/
            ├── shot_01_location_label_v001.mp4
            └── _previews/
                ├── preview_shot_01_location_label_v001_frame_001.png
                ├── preview_shot_01_location_label_v001_frame_002.png
                └── preview_shot_01_location_label_v001_frame_003.png
```

---

## Features

- Organised project-based save structure
- Automatic version numbering
- Separate folders for images and videos
- Image saving to PNG, JPG, or WEBP
- Video saving to MP4, WEBM, or GIF
- Preview images for video outputs
- Open Image Folder button
- Open Video Folder button
- No manual version number input required
- Useful for production, batch renders, client work, episode workflows, shot-based workflows, and AI video pipelines

---

## Auto Versioning

ForgeSave automatically checks the output folder and increments the version number.

For example, if this file already exists:

```text
shot_01_location_label_v001.png
```

The next generation will save as:

```text
shot_01_location_label_v002.png
```

Then:

```text
shot_01_location_label_v003.png
```

This prevents accidental overwriting and keeps render history clean.

---

## Save Image Node

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
project_name: BadlyRunByAnimals
folder_name: EP002_Seagull_And_Sons_Fish_Bar
shot_number: 1
shot_label: exterior_fish_bar
image_format: png
jpg_quality: 95
```

### Example Output

```text
ComfyUI/output/BadlyRunByAnimals/EP002_Seagull_And_Sons_Fish_Bar/shots/shot_01_exterior_fish_bar_v001.png
```

---

## Save Video Node

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

**Save Video expects an IMAGE frame batch, not a VIDEO object.**

Connect it before your final video combine/output node.

In other words, connect the node to the frames/images that make up the animation, not to an already encoded MP4/video output.

### Example Settings

```text
project_name: BadlyRunByAnimals
folder_name: EP002_Seagull_And_Sons_Fish_Bar
shot_number: 1
shot_label: exterior_fish_bar
fps: 30
video_format: mp4
quality: 8
preview_images: 3
```

### Example Output

```text
ComfyUI/output/BadlyRunByAnimals/EP002_Seagull_And_Sons_Fish_Bar/videos/shot_01_exterior_fish_bar_v001.mp4
```

Preview images are saved here:

```text
ComfyUI/output/BadlyRunByAnimals/EP002_Seagull_And_Sons_Fish_Bar/videos/_previews/
```

---

## Video Quality

The video node uses a simple `quality` value from 1 to 10.

```text
1  = smaller file, lower quality
10 = larger file, higher quality
```

For most workflows, a value between `8` and `10` is recommended.

---

## Installation

Clone or download this repository into your ComfyUI custom nodes folder.

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/YOUR_USERNAME/ComfyUI-ForgeSave.git
```

Then restart ComfyUI.

---

## Requirements

ForgeSave uses:

```text
numpy
pillow
imageio
imageio-ffmpeg
```

Install requirements with:

```bash
pip install -r requirements.txt
```

Depending on your ComfyUI setup, some of these may already be installed.

---

## Recommended Folder Structure

The repository should look like this:

```text
ComfyUI-ForgeSave/
├── __init__.py
├── README.md
├── LICENSE
├── requirements.txt
└── web/
    └── forge_save.js
```

Installed inside ComfyUI, it should look like this:

```text
ComfyUI/custom_nodes/ComfyUI-ForgeSave/
├── __init__.py
├── README.md
├── LICENSE
├── requirements.txt
└── web/
    └── forge_save.js
```

---

## Open Folder Buttons

ForgeSave includes frontend buttons for quickly opening output folders.

The image node includes:

```text
Open Image Folder
```

The video node includes:

```text
Open Video Folder
```

These buttons open the relevant output folder on the machine running ComfyUI.

---

## Example Workflow Use Cases

ForgeSave is useful for:

- AI video production
- Batch image generation
- Shot-based workflows
- Episode-based workflows
- Client-facing production renders
- Versioned render output
- Organised ComfyUI project folders
- Archviz, product, automotive, social video, and creative production pipelines

---

## Notes

The video node does not copy an existing encoded video file.

It encodes an IMAGE frame batch into a new video file.

If your workflow outputs a `VIDEO` object and not an image frame batch, connect ForgeSave before the final video output/combine node.

---

## License

MIT License.

---

## Author

Created by **ForgeWorks Studio**.
