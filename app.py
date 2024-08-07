from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import io
import numpy as np
import pandas as pd
import svgwrite
from skimage import measure, io as skio
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'svg', 'png', 'xlsx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to read CSV and convert to SVG
def csv_to_svg(file_path, svg_path):
    try:
        # Attempt to read the CSV file
        df = pd.read_csv(file_path)
        print("CSV DataFrame Columns:", df.columns)
        print("CSV DataFrame Head:\n", df.head())
        
        # Check if required columns exist
        if 'x' not in df.columns or 'y' not in df.columns:
            return None, f"CSV file does not contain required columns 'x' and 'y'. Available columns: {df.columns.tolist()}"
        
        # Create the SVG drawing
        dwg = svgwrite.Drawing(svg_path, profile='tiny', shape_rendering='crispEdges')

        # Add circles for each (x, y) pair in the CSV
        for _, row in df.iterrows():
            x, y = row['x'], row['y']
            dwg.add(dwg.circle(center=(x, y), r=5, fill='red'))

        # Save the SVG file
        dwg.save()
        return svg_path, None
    except Exception as e:
        return None, f"Error processing CSV: {e}"

# Function to identify shapes from an image
def identify_shapes_from_image(image_path):
    image = skio.imread(image_path, as_gray=True)
    contours = measure.find_contours(image, 0.8)
    shapes = set()
    for contour in contours:
        approx = measure.approximate_polygon(contour, tolerance=2.5)
        if len(approx) == 4:
            shapes.add('rectangle')
        elif len(approx) > 4:
            shapes.add('circle')
        else:
            shapes.add('triangle')
    return shapes

# Function to read CSV
def read_csv(csv_path):
    try:
        np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
        path_XYs = []
        for i in np.unique(np_path_XYs[:, 0]):
            npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
            XYs = []
            for j in np.unique(npXYs[:, 0]):
                XY = npXYs[npXYs[:, 0] == j][:, 1:]
                XYs.append(XY)
            path_XYs.append(XYs)
        return path_XYs
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

# Function to plot transformed data
def plot_transformed(paths_XYs):
    try:
        fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
        colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        
        for i, XYs in enumerate(paths_XYs):
            c = colours[i % len(colours)]
            for XY in XYs:
                # Flip sidewise (mirror horizontally)
                XY_flipped = XY.copy()
                XY_flipped[:, 0] = -XY_flipped[:, 0]
                
                # Rotate 180 degrees
                XY_rotated = -XY_flipped
                
                ax.plot(XY_rotated[:, 0], XY_rotated[:, 1], c=c, linewidth=2)
        
        ax.set_aspect('equal')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)
        return buffer
    except Exception as e:
        print(f"Error plotting data: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/task1', methods=['GET', 'POST'])
def task1():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if filename.endswith('.csv'):
                svg_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.svg")
                svg_file, error_message = csv_to_svg(file_path, svg_path)
                if error_message:
                    return error_message
                shapes = identify_shapes_from_image(svg_file)
            else:
                shapes = identify_shapes_from_image(file_path)
            return f"Shapes identified: {', '.join(shapes)}"
    return render_template('upload.html', task='Task 1: Regularize Curves')

@app.route('/task2', methods=['GET', 'POST'])
def task2():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return f"File {filename} uploaded successfully for Task 2."
    return render_template('upload.html', task='Task 2: Exploring Symmetry')

@app.route('/task3', methods=['GET', 'POST'])
def task3():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return f"File {filename} uploaded successfully for Task 3."
    return render_template('upload.html', task='Task 3: Completing Incomplete Curves')

@app.route('/task4', methods=['GET', 'POST'])
def task4():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if filename.endswith('.csv'):
                data = read_csv(file_path)
                if data is None:
                    return "Error processing file", 400
                img = plot_transformed(data)
                if img is None:
                    return "Error generating plot", 400
                return send_file(img, mimetype='image/png')
            else:
                return "File type not supported", 400
    return render_template('upload.html', task='Task 4: Handling and Visualization')

if __name__ == '__main__':
    app.run(debug=True)