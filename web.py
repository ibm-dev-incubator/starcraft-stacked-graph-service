
import os
import hashlib
from flask import Flask, send_from_directory, jsonify, render_template
from flask import request, redirect, url_for
from werkzeug.utils import secure_filename

from stacked_supply_graph import process

UPLOAD_FOLDER = os.environ.get("HOME") + "stacked_supply_graph/uploads"
ALLOWED_EXTENSIONS = set(['txt', 'sc2replay'])

app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# This is plainly from the flask docs
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unix_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(unix_filename)
            hasher = hashlib.sha1()
            with open(unix_filename, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            hashed_name = hasher.hexdigest() + ".SC2Replay"
            target_name = os.path.join(app.config['UPLOAD_FOLDER'], hashed_name)
            os.rename(unix_filename, target_name)
            return redirect(url_for('processing',
                                    filename=hashed_name))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/processing/<filename>')
def processing(filename):
    return render_template('graphing.html', filename=filename)

@app.route('/api/1.0/army_supply/<filename>')
def army_supply(filename):
    d = process(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify(d)

@app.route('/')
def root():
    print("hello")
    return app.send_static_file('index.html')

@app.route('/vendor/<path:path>')
def send_js(path):
    return send_from_directory('vendor', path)

@app.route('/data.json')
def data():
    return app.send_static_file('data.json')


@app.route('/data2.json')
def data2():
    return app.send_static_file('data2.json')

if __name__ == "__main__":
    app.run(debug=True)
