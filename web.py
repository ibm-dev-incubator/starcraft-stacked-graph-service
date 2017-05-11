
import os
import io
import hashlib
import tempfile

from flask import Flask, send_from_directory, jsonify, render_template
from flask import request, redirect, url_for
import swiftclient
from werkzeug.utils import secure_filename

from stacked_supply_graph import process

SWIFT_AUTH_URL = os.environ.get("SWIFT_AUTH_URL")
SWIFT_USERNAME = os.environ.get("SWIFT_USERNAME")
SWIFT_API_KEY = os.environ.get("SWIFT_API_KEY")

UPLOAD_FOLDER = str(tempfile.mkdtemp()) + "/"
ALLOWED_EXTENSIONS = set(['txt', 'sc2replay'])

app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

port = int(os.getenv("PORT"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# This is plainly from the flask docs
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # collect and save the uploaded file to a temporary directory
            filename = secure_filename(file.filename)
            unix_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(unix_filename)
            # Get the sha1 hash of the file
            hasher = hashlib.sha1()
            with open(unix_filename, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            hashed_name = hasher.hexdigest() + ".SC2Replay"
            # Save the file renamed to its sha1 hash to swift
            # in the 'replays' container
            with open(unix_filename, 'rb') as f:
                swift.put_object('replays', hashed_name, f.read())

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
    headers, file = swift.get_object('replays', filename)
    readable_file = io.BytesIO(file)
    d = process(readable_file)
    return jsonify(d)

@app.route('/vendor/<path:path>')
def send_js(path):
    return send_from_directory('vendor', path)


if __name__ == "__main__":
    swift = swiftclient.client.Connection(auth_version='1',
                                          user=SWIFT_USERNAME,
                                          key=SWIFT_API_KEY,
                                          authurl=SWIFT_AUTH_URL)
    app.run(host='0.0.0.0', port=port, debug=True)
