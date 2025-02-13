# Semi-automatic Feature Point Annotator
> A tool for annotating and matching points between RGB images and depth maps, designed for obesity analysis.

## Features

### Dataset Management
- Load and navigate through image datasets
- Automatic dataset directory scanning
- Dataset navigation controls (Previous/Next)
- Point storage per image
- Persistence of labeled points across sessions

### Point Mapping Tool
- Load and display RGB images and depth maps side by side
- Semi-automatic point annotation with synchronized mapping
- Adjustable offset controls for precise depth map alignment
- Real-time visualization of point correspondences
- Point-to-point line connections for better visualization
- Scrollable point list with coordinates
- Clear points functionality
- JSON-based point storage and retrieval

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
**Note**: The project was created using python 3.11.0

### Using the Point Mapping Tool

1. Click "Load Dataset" to select a directory containing your images
2. Navigate through the dataset using Previous/Next buttons
3. Adjust X/Y offsets to align the depth map with the RGB image
4. Click points on the RGB image to automatically map them to the depth map
5. Points are automatically saved to labeled_points.json
6. Use "Clear Points" to restart the annotation for the current image

### Using the Image Overlay Tool

1. Click "Load Dataset" to select your image directory
2. Use navigation buttons to move through the dataset
3. Use the transparency slider to adjust the overlay visibility
4. Fine-tune the alignment using X/Y offset controls
5. Click to add points on the overlaid image
6. Points are stored per image and persisted between sessions

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

### Data Storage
- Points are stored in labeled_points.json
- Each image maintains its own point collection
- Automatic saving on point updates
- Point data persists between sessions

