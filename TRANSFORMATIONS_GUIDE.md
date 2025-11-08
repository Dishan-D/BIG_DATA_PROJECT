# Image Transformation Guide

## 🎨 Available Transformations

Your distributed image processing system now supports **15 different transformations** that can be applied individually or combined!

### Blur & Smoothing
- **🌫️ Gaussian Blur** - Smooth blur effect (kernel size: 31x31)
- **🎯 Bilateral Filter** - Edge-preserving smoothing
- **🧹 Denoise** - Remove noise while preserving details

### Edge Detection
- **🔍 Canny Edges** - Classic Canny edge detection algorithm
- **📐 Sobel Edges** - Sobel operator for edge detection

### Enhancement
- **✨ Sharpen** - Enhance image sharpness
- **☀️ Brighten** - Increase brightness (1.3x)
- **🎚️ Contrast** - Boost contrast (1.5x)
- **🌈 Saturation** - Enhance color saturation (1.5x)

### Artistic Effects
- **⚫ Grayscale** - Convert to black and white
- **🟤 Sepia** - Vintage sepia tone effect
- **🔄 Invert** - Invert all colors
- **🗿 Emboss** - 3D embossing effect
- **🎨 Cartoon** - Cartoon-style effect with edge detection
- **✏️ Sketch** - Pencil sketch effect

## 💡 Combination Examples

### Photo Enhancement
```
Denoise → Sharpen → Saturation → Contrast
```
Best for: Improving photo quality

### Vintage Look
```
Sepia → Brightness
```
Best for: Old-photo effect

### Artistic
```
Grayscale → Contrast → Sketch
```
Best for: Pencil drawing effect

### Edge Analysis
```
Denoise → Edge_Canny
```
Best for: Computer vision preprocessing

### HDR Effect
```
Bilateral → Contrast → Saturation
```
Best for: Dramatic photos

## 🔧 Technical Details

### Processing Flow
1. User selects transformations on frontend
2. Image split into 512×512 tiles
3. Each tile distributed to workers via Kafka
4. Workers apply transformations **in sequence**
5. Processed tiles collected and reassembled
6. Final image saved and displayed

### Performance
- **Single transformation**: ~2-5 seconds for 2200×1650 image
- **Multiple transformations**: Time increases linearly
- **Load balanced**: 2 workers = ~50% faster processing

### Implementation
- **Backend**: OpenCV (cv2) with NumPy
- **Frontend**: Checkbox-based multi-select UI
- **Message format**: JSON with `transformations` array
- **Worker processing**: Sequential application of effects

## 📊 Transformation Categories

| Category | Count | Examples |
|----------|-------|----------|
| Blur & Smooth | 3 | Gaussian, Bilateral, Denoise |
| Edge Detection | 2 | Canny, Sobel |
| Enhancement | 4 | Sharpen, Brightness, Contrast, Saturation |
| Artistic | 6 | Grayscale, Sepia, Cartoon, Sketch, Emboss, Invert |
| **Total** | **15** | |

## 🚀 Usage

### Via Web UI
1. Upload image
2. Select one or more transformations
3. Click "🚀 Process Image"
4. Download result when complete

### Via API
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "image=@photo.jpg" \
  -F 'transformations=["blur","sharpen","saturation"]'
```

## 🎯 Use Cases

### Photography
- Portrait enhancement: `denoise → sharpen → brightness`
- Landscape: `saturation → contrast`
- Low-light fix: `denoise → brightness → contrast`

### Computer Vision
- Preprocessing: `denoise → grayscale`
- Feature extraction: `bilateral → edge_canny`
- Object detection: `sharpen → contrast`

### Art & Design
- Vintage poster: `sepia → contrast`
- Comic book: `cartoon`
- Technical drawing: `grayscale → edge_sobel → invert`

### Social Media
- Instagram-style: `saturation → brightness`
- Black & white art: `grayscale → contrast → sharpen`
- Dreamy effect: `blur → brightness`

## 🔬 Algorithm Details

### Gaussian Blur
- Kernel: 31×31 (medium)
- Algorithm: cv2.GaussianBlur()
- Use: General smoothing

### Canny Edge Detection
- Thresholds: 100, 200
- Algorithm: cv2.Canny()
- Use: Precise edge detection

### Bilateral Filter
- d=9, sigmaColor=75, sigmaSpace=75
- Algorithm: cv2.bilateralFilter()
- Use: Smoothing with edge preservation

### Denoise
- h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
- Algorithm: cv2.fastNlMeansDenoisingColored()
- Use: Advanced noise reduction

### Cartoon Effect
1. Median blur + adaptive threshold (edges)
2. Bilateral filter (color quantization)
3. Combine edges with color

### Sketch Effect
1. Grayscale conversion
2. Invert
3. Gaussian blur
4. Color dodge blend

---

**Note**: Processing time depends on:
- Image size
- Number of transformations
- Number of active workers
- Transformation complexity (e.g., denoise is slower than grayscale)
