# Semi-automatic Feature Point Annotator
> A tool for annotating and matching points between RGB images and depth maps, designed for obesity analysis.

## Features

### Point Mapping Tool
- Load and display RGB images and depth maps side by side
- Semi-automatic point annotation with synchronized mapping
- Adjustable offset controls for precise depth map alignment
- Real-time visualization of point correspondences
- Point-to-point line connections for better visualization
- Scrollable point list with coordinates
- Clear points functionality

![image](https://github.com/user-attachments/assets/77c152a0-a728-4ecf-9828-3e61ec870964)


### Image Overlay Tool
- Load RGB images and depth maps
- Interactive transparency control for depth map visualization
- Precise X/Y offset adjustments with slider and numeric input
- Point annotation capabilities
- Connected point visualization
- Scrollable point list
- Clear points functionality

![image](https://github.com/user-attachments/assets/ce5fc3d1-6364-4d99-9a3d-fefeecd16d36)


## Project Structure

```
code/
├── pointer_tool.py       # Main application integrating both tools
├── point_matching_tool.py # Point mapping implementation
└── image_matching_tool.py # Image overlay implementation
```

## Usage

### Running the Application

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main application:
```bash
python pointer_tool.py
```

### Using the Point Mapping Tool

1. Click "Load RGB Image" to load your source image
2. Click "Load Depth Map" to load the corresponding depth map
3. Adjust X/Y offsets to align the depth map with the RGB image
4. Click points on the RGB image to automatically map them to the depth map
5. Use "Clear Points" to restart the annotation process

### Using the Image Overlay Tool

1. Load both RGB and depth images using the respective buttons
2. Use the transparency slider to adjust the overlay visibility
3. Fine-tune the alignment using X/Y offset controls
4. Click to add points on the overlaid image
5. Points will be automatically connected in sequence
6. View point coordinates in the scrollable list

## Technical Details

### Default Offset Values
- X Offset: -36 pixels
- Y Offset: 8 pixels

### Supported Image Formats
- PNG
- JPG/JPEG

### Display Features
- Automatic image scaling
- Scrollable interface for large images
- Point labels with sequential numbering
- Yellow connection lines between points
- White point markers with black outline

