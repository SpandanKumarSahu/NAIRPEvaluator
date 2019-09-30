from flask import Flask, jsonify, abort, request, make_response, redirect, send_file
from werkzeug.utils import secure_filename
import sys, os
import random
import time

app = Flask(__name__, static_url_path = "")
app.config['TEMP_FOLDER'] = 'TEMP_FOLDER'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', '.csv'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def eval(sfile, courseID, exerciseID, data=None):
    # TODO: Implement different eval techniques
    truth = open(os.path.join("LABELS", str(courseID), str(exerciseID), "test_labels.txt"), "r").readlines()
    predictions = open(sfile, "r").readlines()
    if(len(truth) != len(predictions)):
        return make_response(jsonify({'message': 'Please send correct labels file', 'status': 'Failed'}))
    else:
        return float(sum([x.strip()==y.strip() for x,y in list(zip(truth, predictions))]))/ len(truth)

@app.errorhandler(400)
def not_found1(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found2(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/', methods = ['GET'])
def getInfo():
    return redirect('/index.html')

@app.route('/index.html', methods=['GET', 'POST'])
def getIndex():
    return send_file('index.html', mimetype='text/html', cache_timeout=-1)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'labels' not in request.files:
        return make_response(jsonify({'message': 'Please don\'t modify the submission function', 'status': 'Failed'}))
    file = request.files['labels']
    if file.filename == '':
        return make_response(jsonify({'message': 'Please don\'t modify the submission function', 'status': 'Failed'}))
    if sum([1 for x in ["courseID", "exerciseID", "userID"] if x not in request.args]) > 0:
        return make_response(jsonify({'message': 'Please don\'t modify the submission function', 'status': 'Failed'}))
    courseID, exerciseID, userID = request.args.get('courseID'), request.args.get('exerciseID'), request.args.get('userID')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        sfile = os.path.join(app.config['TEMP_FOLDER'], str(courseID)+"_"+str(exerciseID)+"_"+str(userID)+"_"+filename)
        file.save(sfile)
        score = eval(sfile, int(courseID), int(exerciseID))
        if type(score) != float:
            return score
        return make_response(jsonify({'accuracy': str(score), 'status': 'Success'}))
    else:
        return make_response(jsonify({'status': 'Failed'}))


if  __name__=="__main__":
    app.run(debug = True)
