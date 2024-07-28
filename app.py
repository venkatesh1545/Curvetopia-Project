from flask import Flask, request, send_file, render_template
import numpy as np
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

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

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Create a temporary directory if it doesn't exist
            temp_dir = 'tmp'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            print(f"File saved to {file_path}")
            data = read_csv(file_path)
            if data is None:
                return "Error processing file", 400
            img = plot_transformed(data)
            if img is None:
                return "Error generating plot", 400
            return send_file(img, mimetype='image/png')
        else:
            return "File type not supported", 400
    except Exception as e:
        print(f"Error during file upload: {e}")
        return "File upload failed", 500

if __name__ == '__main__':
    app.run(debug=True)
