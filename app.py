from canvasapi import Canvas
from flask import Flask, request, redirect, Response
from flask_cors import CORS
import requests
import json
# from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Canvas API URL
API_URL = "https://ecornell.beta.instructure.com"
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
CODE = 0
TOKEN_LINK = 'https://ecornell.beta.instructure.com/login/oauth2/token'
REDIRECT_LINK = 'https://ecornell.beta.instructure.com/login/oauth2/auth?client_id='+CLIENT_ID+'&response_type=code&state=YYY&redirect_uri=https://dreamworthie-populate-canvas.herokuapp.com/oauth2response'

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

def createPage(course, module, pgtype, pgname):
    if pgtype == 'watch':
        page_content = "<h2 class='watch'>"+pgname+"</h2><p>Context</p><div id='kaltura1' class='kaltura_video resp2' style='margin: auto; width: 640px; height: 390px; margin-bottom: 1em; background: #ccc;'><span class='entryId' style='display: none;'>KALTURACODE</span></div>"
    elif pgtype == 'tool':
        page_content = "<h2 class='tool'>"+pgname+"</h2><div class='tip-box float-right' style='width: 300px;'><h3 class='download'>&nbsp;</h3><p>Use this helpful <a href='https://s3.amazonaws.com/ecornell/content/CIPA/CIPA541/cipa541_skills-inventory.pdf'>Tool_Title_Here</a> to yada yada....</p></div><p>Paragraph text here.</p><p>&nbsp;</p><h3>Important instructions for saving your work:</h3><p>When you open the linked PDF, it may open in a new browser window. Save it to your desktop or preferred storage location, then open it with Adobe Reader, and save a copy with a new name. This will give you a working copy that you can review, print, or add content to without losing your work. It will also enable you to retain a clean copy of the original document for future use.</p>"
    elif pgtype == 'activity':
        page_content = "<h2 class='activity'>"+pgname+"</h2><p>Content</p>"
    elif pgtype == 'read':
        page_content = "<h2 class='read'>"+pgname+"</h2><p>Content</p>"
    else: 
        page_content = "<h2>"+pgname+"</h2><p>Content</p>"
    page = course.create_page({"title": pgtype+': '+pgname, 'body': page_content})
    page_id = page.page_id
    module.create_module_item({'content_id': page_id, 'type': 'page'})
    return page

def createQuiz(course, module, pgtype, pgname):
    description = "<p>[quiz prompt]</p><p><strong>You must achieve a score of 100% on this quiz to complete the course. You may take the quiz as many times as you need to achieve that score.</strong></p>"
    quiz = course.create_quiz({'title': pgname, 'description': description, 'allowed_attempts': -1})
    quiz_id = quiz.id
    module.create_module_item({'content_id': quiz_id, 'type': pgtype})
    return quiz

def createDiscussion(course, module, pgtype):
    # description = "<p>(Fill in topic here.)</p><h3>Instructions:</h3><ul><li>You are required to participate meaningfully in course discussions.</li><li>You must post to the board before seeing other students' posts. You are encouraged to respond and engage meaningfully with your peers.&nbsp;</li><li>Your responses will be reviewed according to the following criteria:<ul><li class='ql-indent-1'>Comprehension: Demonstrates an understanding of course content.</li><li class='ql-indent-1'>Synthesis: Demonstrates ability to synthesize course content within the project topic.&nbsp;</li><li class='ql-indent-1'>Originality: Utilizes your own original thinking.</li><li class='ql-indent-1'>Development: Clearly articulates and fully addresses all required questions/topics.&nbsp;</li></ul></li></ul><h3>To participate in this discussion:</h3><p>Click <strong>Reply</strong> to post a comment or reply to another comment. Please consider that this is a professional forum; courtesy and professional language and tone are expected. Before posting, please review <a href='https://s3.amazonaws.com/ecornell/global/eCornellPlagiarismPolicy.pdf' target='_blank' rel='noopener'>eCornell's policy regarding plagiarism</a> (the presentation of someone else's work as your own without source credit).</p><h3>Please note:</h3><p>While discussion board postings will be accepted through the end of the course, we strongly encourage everyone to move through this course as a group. As such, postings that are made to this board after 5 p.m. ET on the due date will be read and graded but may not receive a response on the board from your facilitator and/or your peers. Please let your facilitator know if you have any questions.</p>"
    discussion = course.create_discussion_topic()
    discussion_id = discussion.id
    module.create_module_item({'content_id': discussion_id, 'type': pgtype})
    return discussion

def createAssignment(course, module, pgtype, pgname):
    assignment = course.create_assignment({'name': pgname})
    assignment_id = assignment.id
    module.create_module_item({'content_id': assignment_id, 'type': pgtype})
    return assignment

def createProject(course, module, pgname):
    description = "<p>In this part of the course project, you will ....</p><p><em>Completion of this project is a course requirement.</em></p><p>&nbsp;</p><h3><strong>Instructions:</strong></h3><ol><li>Download the <a class='inline_disabled' href='http://%22%22/' target='_blank' rel='noopener'>course project document</a>.</li><li>Complete Part One.</li><li>Save your work as one of these file types: .<span>doc, .docx, .txt, .pdf, .xls, .xlsx.</span> No other file types will be accepted for submission.</li><li>You will not submit your course project for grading and credit now. At the end of the course, you will submit your completed project for facilitator review and grading.</li></ol><h3><strong>Before you begin:</strong></h3><p>Please review&nbsp;<a class='inline_disabled' href='https://s3.amazonaws.com/ecornell/global/eCornellPlagiarismPolicy.pdf' target='_blank' rel='noopener'>eCornell's policy regarding&nbsp;plagiarism</a>&nbsp;(the presentation of someone else's work as your own without source credit).</p>"
    project = course.create_assignment({'name': pgname, 'description': description})
    project_id = project.id
    module.create_module_item({'content_id': project_id, 'type': 'assignment'})
    return project

def populateCanvas(formdata, course):
    for [pgtype, pgname] in formdata.values():
        if pgtype == "module":
            module = course.create_module({'name': pgname})
        elif pgtype == "assignment":
            _ = createAssignment(course, module, pgtype, pgname)
        elif pgtype == "quiz":
            _ = createQuiz(course, module, pgtype, pgname)
        elif pgtype == "discussion":
            _ = createDiscussion(course, module, pgtype)
        elif pgtype == "project":
            _ = createProject(course, module, pgname)
        else:
            _ = createPage(course, module, pgtype, pgname)

@app.route('/oauth2response', methods=['GET', 'POST'])
def oauth():
    global CODE
    CODE = request.args.get('code', None)
    # socketio.emit('my response', {'code': code, 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET})
    return redirect('https://dreamworthie.com/wait')

@app.route('/home', methods=['POST'])
def createCourse():
    data = request.json
    API_KEY = data['token']
    coursecode = data['classcode']

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(int(coursecode))

    formdata = data['data']
    populateCanvas(formdata, course)
    return success_response(formdata)

@app.route('/redirect', methods=['POST'])
def proxy():
    resp = requests.post(TOKEN_LINK, json=request.get_json())
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/getcode', methods=['GET'])
def getcode():
    return success_response({'code': CODE, 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET})

@app.route('/geturl', methods=['GET'])
def geturl():
    return success_response({'url': REDIRECT_LINK})

if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app, port=5000, debug=True)