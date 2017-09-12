from flask import Flask
from flask import jsonify
from flask import request
from werkzeug import secure_filename
from azure.storage.blob import BlockBlobService
import os


app = Flask(__name__, static_folder='static', static_url_path='')

app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024    # 1 Mb limit
app.config['AZURE_STORAGE_ACCOUNT'] = "flasktest"
app.config['AZURE_STORAGE_CONTAINER'] = "doc"
app.config['AZURE_STORAGE_KEY'] = os.environ['AZURE_STORAGE_KEY']
try:
    os.environ['FLASK_DEBUG']
    app.debug = True
except KeyError:
    app.debug = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def root():
    return app.send_static_file('index.html')


# basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/uploadajax', methods=['POST'])
def upldfile():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app.logger.info('FileName: ' + filename)
            
            block_blob_service = BlockBlobService(account_name=app.config['AZURE_STORAGE_ACCOUNT'], account_key=app.config['AZURE_STORAGE_KEY'])
            block_blob_service.create_blob_from_bytes(
                'doc',
                filename,
                file.read())
            
#             updir = os.path.join(basedir, 'upload/')
#             file.save(os.path.join(updir, filename))
#             file_size = os.path.getsize(os.path.join(updir, filename))
            return jsonify(name=filename, url='https://'+app.config['AZURE_STORAGE_ACCOUNT']+'.blob.core.windows.net/' \
                           +app.config['AZURE_STORAGE_CONTAINER']+'/'+filename)



if __name__ == '__main__':
 app.run()