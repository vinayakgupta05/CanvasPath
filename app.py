from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
app = Flask(__name__)

host = 'http://127.0.0.1:5000/'
app.secret_key = 'jumanji'


@app.route('/', methods=['POST', 'GET'])
def login():
    error = None
    session['current'] = ''
    session['password'] = ''
    if request.method == 'POST':
        result = validloginStudent(request.form['email'], request.form['password'])
        if result:

            session['current'] = request.form['email']
            session['password'] = request.form['password']
            return redirect(url_for("student"))
        else:
            result = validloginProfessor(request.form['email'], request.form['password'])
            if result:
                session['current'] = request.form['email']
                session['password'] = request.form['password']
                return redirect(url_for("professor"))
            else:
                result = validloginAdmin(request.form['email'], request.form['password'])
                if result:
                    session['current'] = request.form['email']
                    session['password'] = request.form['password']
                    return redirect(url_for("admin"))
                else:
                    error = 'invalid login'
                    return render_template('ErrorScreen.html', error=error, url=host, result=result)
    return render_template('LoginScreen.html', error=error)


@app.route('/professor')
def professor():
    error = None
    email = str(session.get('current', None))
    password = str(session.get('password', None))
    result = validloginProfessor(email, password)
    result2 = ProfCourseList(email)
    if result:
        return render_template('ProfessorDashboard.html', name=result[0][0], email=email,
                               password=password, error=error, result=result, result2=result2)


@app.route('/student')
def student():
    error = None
    email = str(session.get('current', None))
    password = str(session.get('password', None))
    result = validloginStudent(email, password)
    result2 = getCourselist(email)
    if result:
        return render_template('StudentDashboard.html', name=result[0][0], email=email,
                               password=password, error=error, result=result, result2=result2)


@app.route('/admin')
def admin():
    error = None
    email = str(session.get('current', None))
    password = str(session.get('password', None))
    result = validloginAdmin(email, password)
    if result:
        return render_template('AdminDashboard.html', email=email, password=password, error=error, result=result)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    error = None
    return render_template('LoginScreen.html', error=error, url=host)


@app.route('/home', methods=['POST', 'GET'])
def home():
    email = str(session.get('current', None))
    password = str(session.get('password', None))
    if request.method == 'POST':
        result = validloginStudent(email, password)
        if result:
            return redirect(url_for("student"))
        else:
            result = validloginProfessor(email, password)
            if result:
                return redirect(url_for("professor"))
            else:
                result = validloginAdmin(email, password)
                if result:
                    return redirect(url_for("admin"))


@app.route('/resetPassword', methods=['POST', 'GET'])
def resetPassword():
    error = None
    if request.method == 'POST':
        resetPass(request.form['email'], request.form['NewPassword'], request.form['ConfirmPassword'])
        result = validloginStudent(request.form['email'], request.form['NewPassword'])
        if result:
            return render_template('StudentDashboard.html', name=result[0][0], error=error, result=result)
        else:
            result = validloginProfessor(request.form['email'], request.form['password'])
            if result:
                return render_template('ProfessorDashboard.html', name=result[0][0], error=error, result=result)
            else:
                result = validloginAdmin(request.form['email'], request.form['password'])
                if result:
                    return render_template('AdminDashboard.html', error=error, result=result)


@app.route('/professor/<string:section>', methods=['POST', 'GET'])
def fetchSectioninfo(section):
    error = None
    email = str(session.get('current', None))
    session['section']=section
    result2 = getSectioninfo(email, section)
    result3 = getHomeworkinfo(email, section)
    result4 = getExaminfo(email, section)
    result = ProfCourseList(email)
    session['course'] = result[0][0]
    return render_template('PCourseScreen.html', error=error, result2=result2, result3=result3, result4=result4)


@app.route('/student/<string:course>', methods=['POST', 'GET'])
def fetchCourseInfo(course):
    error = None
    email = str(session.get('current', None))
    session['course'] = course
    result2 = getCourseInfo(email, course)
    result3 = getHomeworkSInfo(email, course)
    result4 = getExamSInfo(email, course)
    result1 = result2[0][0]
    result5 = result2[0][1]
    print(result3)
    return render_template('SCourseScreen.html', error=error, result1=result1, result5=result5,result2=result2, result3=result3, result4=result4)


@app.route('/professor/section/<string:email>', methods=['POST', 'GET'])
def fetchStudentCourseInfo(email):
    error = None
    session['studentemail'] = email
    course = str(session.get('course', None))
    result2 = getCourseInfo(email, course)
    result3 = getHomeworkSInfo(email, course)
    result4 = getExamSInfo(email, course)
    result1 = result2[0][0]
    result5 = result2[0][1]
    return render_template('PSCourseScreen.html', error=error, result2=result2, result3=result3, result4=result4,
                           result1=result1, result5=result5)


@app.route('/professor/section/email/<string:HwID>', methods=['POST', 'GET'])
def updatehwGrade(HwID):
    error = None
    email = str(session.get('studentemail', None))
    course = str(session.get('course', None))
    insertHWGrade(email, HwID, int(request.form['HwGrade']))
    result2 = getCourseInfo(email, course)
    result3 = getHomeworkSInfo(email, course)
    result4 = getExamSInfo(email, course)
    result1 = result2[0][0]
    result5 = result2[0][1]
    return render_template('PSCourseScreen.html', error=error, result2=result2, result1=result1, result5=result5, result4=result4, result3=result3)


@app.route('/student/course/<string:HwID>', methods=['POST', 'GET'])
def updatehwsubmission(HwID):
    error = None
    email = str(session.get('current', None))
    course = str(session.get('course', None))
    insertHWsub(email, HwID, str(request.form['Hsubmission']))
    result2 = getCourseInfo(email, course)
    result3 = getHomeworkSInfo(email, course)
    result4 = getExamSInfo(email, course)
    result1 = result2[0][0]
    result5 = result2[0][1]
    return render_template('SCourseScreen.html', error=error, result1=result1, result5=result5, result2=result2,
                           result3=result3, result4=result4)


@app.route('/professor/section/email/ExamID/<string:ExamID>', methods=['POST', 'GET'])
def updateexamGrade(ExamID):
    error = None
    email = str(session.get('studentemail', None))
    course = str(session.get('course', None))
    insertExamGrade(email, ExamID, request.form["ExamGrade"])
    result2 = getCourseInfo(email, course)
    return render_template('PSCourseScreen.html', error=error, result2=result2)


@app.route('/professor/section/homework', methods=['Post', 'Get'])
def CreateHomework():
    error = None
    email = str(session.get('current', None))
    section = session.get('section', None)
    course = str(session.get('course', None))
    insertHomework(course, section, request.form['HwID'], request.form['Hdetail'])
    insertSHomework(course, section, request.form['HwID'], request.form['Hdetail'])
    result2 = getSectioninfo(email, section)
    result3 = getHomeworkinfo(email, section)
    result4 = getExaminfo(email, section)
    return render_template('PCourseScreen.html', error=error,  result2=result2, result3=result3, result4=result4)


@app.route('/professor/section/exam', methods=['Post', 'Get'])
def CreateExam():
    error = None
    email = str(session.get('current', None))
    section = session.get('section', None)
    course = str(session.get('course', None))
    insertExam(course, section, request.form['ExamID'], request.form['Edetail'])
    insertSExam(course, section, request.form['ExamID'], request.form['Edetail'])
    result2 = getSectioninfo(email, section)
    result3 = getHomeworkinfo(email, section)
    result4 = getExaminfo(email, section)
    return render_template('PCourseScreen.html', error=error,  result2=result2, result3=result3, result4=result4)


@app.route('/professor/deletehomework/<string:HwID>', methods=['Post', 'Get'])
def deleteHomework(HwID):
    error = None
    course = str(session.get('course', None))
    email = str(session.get('current', None))
    section = session.get('section', None)
    deleteHW(course, HwID)
    deleteSHW(course, HwID)
    result2 = getSectioninfo(email, section)
    result3 = getHomeworkinfo(email, section)
    result4 = getExaminfo(email, section)
    return render_template('PCourseScreen.html', error=error, result2=result2, result3=result3, result4=result4)


@app.route('/professor/deleteexam/<string:ExamID>', methods=['Post', 'Get'])
def deleteExam(ExamID):
    error = None
    course = str(session.get('course', None))
    email = str(session.get('current', None))
    section = session.get('section', None)
    deleteEx(course, ExamID)
    deleteSEx(course, ExamID)
    result2 = getSectioninfo(email, section)
    result3 = getHomeworkinfo(email, section)
    result4 = getExaminfo(email, section)
    return render_template('PCourseScreen.html', error=error, result2=result2, result3=result3, result4=result4)


@app.route('/admin/course')
def fetchCourselist():
    error = None
    result1 = getallcourselist()
    result2 = GetpAssignment()
    return render_template('CourseDash.html', error=error, result1=result1, result2 = result2)


@app.route('/admin/professor')
def fetchProflist():
    error = None
    result1 = getallcourselist()
    result2 = GetpAssignment()
    result3 = fetchProflist()
    result4 = fetchTeamlist()
    return render_template('ProfDash.html', error=error, result1=result1, result2=result2, result3=result3, result4=result4)


@app.route('/admin/student')
def fetchStudentlist():
    error = None
    result1 = fetchSenrollment()
    result2 = fetchCourseList()
    result4 = fetchSectionList()
    return render_template('StudDash.html', error=error, result1=result1, result2=result2, result4=result4)


@app.route('/admin/course/createcourse', methods=["POST", "GET"])
def CreateCourse():
    error = None
    CourseID = request.form['CourseID']
    Cname = request.form['CName']
    Cdetail = request.form['Cdetail']
    SectionNo = request.form['SectionNo']
    Stype = request.form['Stype']
    Slimit = request.form['Slimit']
    teachingID = request.form['teachingID']
    insertSection(CourseID, SectionNo, Stype, Slimit, teachingID)
    insertCourse(CourseID, Cname, Cdetail)
    result1 = getallcourselist()
    result2 = GetpAssignment()
    return render_template('CourseDash.html', error=error, result1=result1, result2=result2)


@app.route('/professor/deletecourse/<string:CourseID>/<string:SectionNo>', methods=['Post', 'Get'])
def deleteCourse(CourseID, SectionNo):
    error=None
    deleteSec(CourseID, SectionNo)
    if checkcourselist(CourseID)==True:
        deleteCOU(CourseID)
    result1 = getallcourselist()
    result2 = GetpAssignment()
    return render_template('CourseDash.html', error=error, result1=result1, result2=result2)


@app.route('/admin/professor/AssignTeam', methods=["POST", "GET"])
def AssignTeam():
    error = None
    email = request.form.get('email')
    teamid = request.form.get('teachingID')
    updateAssignTeam(email, teamid)
    result1 = getallcourselist()
    result2 = GetpAssignment()
    result3 = fetchProflist()
    result4 = fetchTeamlist()
    return render_template('ProfDash.html', error=error, result1=result1, result2=result2, result3=result3,
                           result4=result4)


@app.route('/professor/deleteteamid/<string:email>/<string:teachingID>', methods=['Post', 'Get'])
def deleteteamid(email, teachingID):
    error = None
    deleteTID(email, teachingID)
    result1 = getallcourselist()
    result2 = GetpAssignment()
    result3 = fetchProflist()
    result4 = fetchTeamlist()
    return render_template('ProfDash.html', error=error, result1=result1, result2=result2, result3=result3,
                           result4=result4)


@app.route('/admin/student/EnrollStud', methods=["POST", "GET"])
def EnrollStud():
    error = None
    email = request.form.get('email')
    course = request.form.get('CourseID')
    section = request.form.get('SectionNo')
    updateStudEnroll(email, course, section)
    result1 = fetchSenrollment()
    return render_template('StudDash.html', error=error, result1=result1)


@app.route('/admin/student/EnrollStud/<string:email>', methods=['POST', 'GET'])
def fetchStudentEnrollmentInfo(email):
    error = None
    result1 = getstudenroll(email)
    return render_template('StudentEnroll.html', error=error, result1=result1, email=email)


@app.route('/admin/student/EnrollStud/<string:email>/<string:CourseID>/<string:SectionNo>', methods=['Post', 'Get'])
def deleteenroll(email, CourseID, SectionNo):
    error=None
    deleteSEnroll(email, CourseID, SectionNo)
    result1 = getstudenroll(email)
    return render_template('StudentEnroll.html', error=error, result1=result1, email=email)


def getstudenroll(email):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT CourseID, SectionID FROM StudentEnrolls WHERE StudentID=%s'
    cursor.execute(query_str, (email,))
    ans = cursor.fetchall()
    return ans


def fetchSenrollment():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT name, email FROM Student'
    cursor.execute(query_str, )
    ans = cursor.fetchall()
    return ans


def deleteSEnroll(email, course, section):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM StudentEnrolls Where StudentID=%s and CourseID=%s and SectionID=%s'
    cursor.execute(query_str, (email, course, section,))
    connection.commit()
    return


def fetchCourseList():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT CourseID FROM Courses'
    cursor.execute(query_str, )
    ans = []
    for row in cursor.fetchall():
        ans.append(row[0])
    return ans


def fetchSectionList():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT SectionID FROM Sections'
    cursor.execute(query_str, )
    ans = []
    for row in cursor.fetchall():
        ans.append(row[0])
    return ans


def updateStudEnroll(email, course, section):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'INSERT INTO StudentEnrolls' \
                '(StudentID, CourseID, SectionID) Values (%s, %s, %s)'
    cursor.execute(query_str, (email, course, section))
    connection.commit()
    return


def deleteTID(email, teamid):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM ProfessorTeams Where email=%s and TeachingID=%s '
    cursor.execute(query_str, (email,teamid))
    connection.commit()
    return


def fetchProflist():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT P.email FROM Professor P'
    cursor.execute(query_str, )
    ans = []
    for row in cursor.fetchall():
        ans.append(row[0])
    return ans


def fetchTeamlist():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT S.teachingID FROM Sections S ORDER BY S.teachingID asc'
    cursor.execute(query_str, )
    ans = []
    for row in cursor.fetchall():
        ans.append(row[0])
    return ans


def updateAssignTeam(email, teamid):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'INSERT INTO ProfessorTeams' \
                '(email, TeachingID) Values (%s, %s)'
    cursor.execute(query_str, (email, teamid))
    connection.commit()
    return


def checkcourselist(CourseID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select S.CourseID From Sections S Where S.CourseID=%s'
    cursor.execute(query_str,(CourseID,))
    ans = cursor.fetchall()
    if len(ans) > 0:
        return False
    else:
        return True


def GetpAssignment():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT P.name, P.email, P1.TeachingID ,S.CourseID, S.SectionID  '\
                'FROM ProfessorTeams P1, Professor P, Sections S Where P.email=P1.email and S.teachingID=P1.TeachingID ' \
                'ORDER By P1.TeachingID asc'
    cursor.execute(query_str, )
    ans = cursor.fetchall()
    return ans


def deleteSec(CourseID, SectionID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM Sections Where CourseID=%s and SectionID=%s '
    cursor.execute(query_str, (CourseID,SectionID))
    connection.commit()
    return


def deleteCOU(CourseID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM Courses Where CourseID=%s'
    cursor.execute(query_str, (CourseID,))
    connection.commit()
    return


def insertSection(CourseID, SectionNo, Stype, Slimit, teachingID ):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'REPLACE INTO Sections' \
                '(CourseID, SectionID, Stype, Slimit, teachingID ) Values (%s, %s, %s, %s, %s)'
    cursor.execute(query_str, (CourseID, SectionNo, Stype, Slimit, teachingID))
    connection.commit()
    return


def insertCourse(CourseID, Cname, Cdetail):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'REPLACE INTO Courses' \
                '(CourseID, Cname, Cdetail) Values (%s, %s, %s)'
    cursor.execute(query_str, (CourseID, Cname, Cdetail))
    connection.commit()
    return


def getallcourselist():
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT  C.CourseID, C.CName, C.CDetail, S.SectionID, S.Stype, S.Slimit, S.teachingID '\
                'FROM  Courses C, Sections S Where C.CourseID=S.CourseID'
    cursor.execute(query_str, )
    ans = cursor.fetchall()
    return ans


def validloginStudent(email, password):
    connection = mysql.connector.connect(host ='localhost', user= 'root', passwd='PC1998MLv',database= 'CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT S.name , S.age, S.gender, S.major FROM Student S WHERE S.email = %s AND S.password = %s'
    cursor.execute(query_str, (email, password,))
    ans = cursor.fetchall()
    return ans


def validloginProfessor(email, password):
    connection = mysql.connector.connect(host ='localhost', user ='root', passwd ='PC1998MLv',database= 'CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT P.title, P.name, P.age, P.gender, P.office_address from Professor P ' \
                'where P.email = %s and P.password = %s'
    cursor.execute(query_str, (email, password))
    ans = cursor.fetchall()
    return ans


def validloginAdmin(email, password):
    connection = mysql.connector.connect(host ='localhost', user ='root', passwd ='PC1998MLv',database= 'CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT * from Admin A where A.AdminID = %s AND A.password = %s'
    cursor.execute(query_str, (email, password,))
    ans = cursor.fetchall()
    return ans


def getCourselist(email):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT  S1.CourseID, S1.SectionID FROM  StudentEnrolls S1 WHERE S1.StudentID=%s'
    cursor.execute(query_str, (email,))
    ans = cursor.fetchall()
    return ans


def ProfCourseList(email):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT S2.CourseID, S2.SectionID FROM  Sections S2, Professor P, ProfessorTeams P2 ' \
                'WHERE P.email=%s AND S2.teachingID=P2.TeachingID AND P.email=P2.email'
    cursor.execute(query_str, (email,))
    ans = cursor.fetchall()
    return ans


def getSectioninfo(email, section):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select Distinct S2.name, S1.StudentID From StudentEnrolls S1, ProfessorTeams P,Sections S, Student S2 ' \
                'Where P.email=%s And S.teachingID=P.TeachingID and S1.CourseID=S.CourseID and S1.SectionID=%s and ' \
                'S2.email=S1.StudentID'
    cursor.execute(query_str, (email, section,))
    ans = cursor.fetchall()
    return ans


def getHomeworkinfo(email, section):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select DISTINCT H.HwID , H.HDetail From Homework H, Sections S, ProfessorTeams P ' \
                'Where P.email=%s And H.CourseID=S.CourseID and P.TeachingID=S.teachingID and H.SectionNo=%s'
    cursor.execute(query_str, (email, int(section),))
    ans = cursor.fetchall()
    return ans


def getExaminfo(email, section):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select Distinct E.ExamID , E.EDetail From Exam E, Sections S ,ProfessorTeams P ' \
                'Where P.email=%s And E.CourseID=S.CourseID and P.TeachingID=S.teachingID and E.SectionNo=%s'
    cursor.execute(query_str, (email, int(section),))
    ans = cursor.fetchall()
    return ans


def getHomeworkSInfo(email, course):
    print(email,course)
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select H.HwID , H.HDetail, H.HSubmission, H.HGrades From HomeworkGrades H WHERE H.StudentID=%s AND H.CourseID=%s'
    cursor.execute(query_str, (email, course,))
    ans = cursor.fetchall()
    print(ans)
    return ans


def getExamSInfo(email, course):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'Select Distinct E.ExamID , E.EDetail, E.EGrade ' \
                'From ExamGrades E WHERE E.StudentID=%s And E.CourseID=%s '
    cursor.execute(query_str, (email, course, ))
    ans = cursor.fetchall()
    return ans


def getCourseInfo(email, course):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'SELECT DISTINCT S.name as Sname, S1.CourseID ,P.name as Pname, P.office_address, P.email,P.title ' \
                'From Student S, Professor P, ProfessorTeams P1, Sections S1  ' \
                'Where S.email=%s and P1.TeachingID = S1.teachingID AND S1.CourseID=%s AND P.email=P1.email'
    cursor.execute(query_str, (email, course,))
    ans = cursor.fetchall()
    return ans


def insertHomework(course, section, HwID, HwDetails):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'REPLACE INTO Homework' \
                '(CourseID, SectionNo, HwID, HDetail) Values (%s, %s, %s, %s)'
    cursor.execute(query_str, (course, section, int(HwID), HwDetails,))
    connection.commit()
    return


def insertSHomework(course, section, HwID, HwDetails):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    email = session.get('current', None)
    Studentlist = getSectioninfo(email, section)
    for i, j in Studentlist:

        query_str = 'REPLACE INTO HomeworkGrades' \
                    '(StudentID, CourseID, SectionNo, HwID, HDetail, HGrades) Values (%s ,%s, %s, %s, %s, NULL )'
        cursor.execute(query_str, (j, course, section, HwID, HwDetails,))
    connection.commit()
    return


def insertExam(course, section, ExamID, EDetail):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'REPLACE INTO Exam' \
                '(CourseID, SectionNo, ExamID, EDetail) Values (%s, %s, %s, %s)'
    cursor.execute(query_str, (course, section, ExamID, EDetail,))
    connection.commit()
    return


def insertSExam(course, section, ExamID, EDetail):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    email = session.get('current', None)
    Studentlist = getSectioninfo(email, section)
    for i, j in Studentlist:
        query_str = 'REPLACE INTO ExamGrades' \
                    '(StudentID, CourseID, SectionNo, ExamID, EDetail, EGrade) Values (%s ,%s, %s, %s, %s, NULL )'
        cursor.execute(query_str, (j, course, section, ExamID, EDetail,))
    connection.commit()
    return


def insertHWGrade(email, HwID, HwGrade):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    course = str(session.get('course', None))
    cursor = connection.cursor()
    query_str = 'Update HomeworkGrades H Set H.HGrades=%s ' \
                'Where H.HwID=%s and H.CourseID=%s and H.StudentID=%s'
    cursor.execute(query_str, (HwGrade, HwID, course, email,))
    connection.commit()
    return


def insertHWsub(email, HwID, hsubmission):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    course = str(session.get('course', None))
    print(hsubmission, HwID, course, email)
    cursor = connection.cursor()
    query_str = 'Update HomeworkGrades H Set H.HSubmission=%s ' \
                'Where H.HwID=%s and H.CourseID=%s and H.StudentID=%s'
    cursor.execute(query_str, (hsubmission, HwID, course, email,))
    connection.commit()
    return


def insertExamGrade(email, ExamID, EGrade):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    course = str(session.get('course', None))
    cursor = connection.cursor()
    query_str = 'Update ExamGrades E Set E.EGrade=%s ' \
                'Where E.ExamID=%s and E.CourseID=%s and E.StudentID=%s'
    cursor.execute(query_str, (EGrade, ExamID, course, email,))
    connection.commit()
    return


def deleteHW(course, HwID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM Homework Where HwID=%s And CourseID=%s'
    cursor.execute(query_str, (HwID, course,))
    connection.commit()
    return


def deleteSHW(course, HwID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM HomeworkGrades Where HwID=%s And CourseID=%s'
    cursor.execute(query_str, (HwID, course,))
    connection.commit()
    return


def deleteEx(course, ExamID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM Exam Where ExamID=%s And CourseID=%s'
    cursor.execute(query_str, (ExamID, course,))
    connection.commit()
    return


def deleteSEx(course, ExamID):
    connection = mysql.connector.connect(host='localhost', user='root', passwd='PC1998MLv', database='CanvasPath')
    cursor = connection.cursor()
    query_str = 'DELETE FROM ExamGrades Where ExamID=%s And CourseID=%s'
    cursor.execute(query_str, (ExamID, course,))
    connection.commit()
    return


def resetPass(email, NewPassword, ConfirmPassword):
    connection = mysql.connector.connect(host ='localhost', user='root', passwd='PC1998MLv',database='CanvasPath')
    cursor = connection.cursor()
    if NewPassword == ConfirmPassword:
        query_str = 'UPDATE Student S SET S.password = %s WHERE S.email= %s'
        cursor.execute(query_str, (NewPassword, email))
    if NewPassword == ConfirmPassword:
        query_str = 'UPDATE Professor P SET P.password = %s WHERE P.email= %s'
        cursor.execute(query_str, (NewPassword, email))
    if NewPassword == ConfirmPassword:
        query_str = 'UPDATE Admin A SET A.password = %s WHERE A.AdminID= %s'
        cursor.execute(query_str, (NewPassword, email))
    connection.commit()

    return




