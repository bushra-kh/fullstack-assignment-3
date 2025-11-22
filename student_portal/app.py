import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Path to students.json
STUDENTS_FILE = os.path.join(os.path.dirname(__file__), '..', 'students.json')

class Student:
    def __init__(self):
        pass

    def display_info(self):
        return display_all()

    def update_email(self, roll, new_email):
        details = json_data()
        found = False
        for student in details:
            if student["rollno"] == roll:
                try:
                    validate_email(new_email)
                    student["email"] = new_email
                    found = True
                except InvalidEmailFormat as e:
                    return {"success": False, "message": str(e)}
                break
        
        if found:
            with open(STUDENTS_FILE, "w") as f:
                json.dump(details, f, indent=4)
            return {"success": True, "message": "Student email updated."}
        else:
            return {"success": False, "message": "Student not found"}


class InvalidEmailFormat(Exception):
    #Custom exception for invalid email format
    pass

def validate_email(email):
    #Validation function for email
    if not "@" in email or not ".com" in email:
        raise InvalidEmailFormat("Invalid email format.")
    return True

def json_data():#function to read json data
    with open(STUDENTS_FILE) as file:
        data = file.read()
        details = json.loads(data)
    return details

def add_record(name, roll, dep, email): #add student record
    try:
        roll = int(roll)
    except ValueError as ve:
        return {"success": False, "message": f"Error: Roll number must be an integer"}
    
    try:
        validate_email(email)
        data={
            "name": name,
            "rollno":roll,
            "department":dep,
            "email":email
        }
    except InvalidEmailFormat as e:
        return {"success": False, "message": str(e)}
    
    # Read existing data
    with open(STUDENTS_FILE, "r") as f:
        students = json.load(f)
    
    students.append(data)
    
    # Write back to file
    with open(STUDENTS_FILE, "w") as f:
        json.dump(students, f, indent=4)
    
    return {"success": True, "message": "Student record added."}

def searchby_roll(roll):
    try:
        roll = int(roll)
    except ValueError:
        return None
    
    details = json_data()
    for student in details:
        if student["rollno"] == roll:
            return student
    return None

def display_all():
    details = json_data()
    return details

                                                            #ROUTES

@app.route('/')         #HOMEPAGE
def index():
    return render_template('index.html')

@app.route('/students')  #DISPLAY ALL
def students():
    all_students = display_all() #data from json
    return render_template('students.html', students=all_students)

@app.route('/add', methods=['GET', 'POST'])     # ADD NEW STD 
def add():              
    if request.method == 'POST':
        name = request.form.get('name')
        roll = request.form.get('roll')
        department = request.form.get('department')
        email = request.form.get('email')
        
        result = add_record(name, roll, department, email)
        
        if result['success']:
            return redirect(url_for('students'))
        else:
            return render_template('add.html', error=result['message'])
    
    return render_template('add.html')

@app.route('/search', methods=['GET', 'POST'])  # SEARCH STD BY ROLLNO
def search():
    student = None
    error = None
    
    if request.method == 'POST':
        roll = request.form.get('roll')
        student = searchby_roll(roll)
        if not student:
            error = "Student not found"
    
    return render_template('search.html', student=student, error=error)

@app.route('/update/<int:roll>', methods=['GET', 'POST']) #UPDATE EXISTING STD EMAIL
def update(roll):
    student = searchby_roll(roll)
    error = None
    success = None
    
    if not student:
        error = "Student not found"
    
    if request.method == 'POST':
        new_email = request.form.get('email')
        obj = Student()
        result = obj.update_email(roll, new_email)
        
        if result['success']:
            success = result['message']
            student = searchby_roll(roll)
        else:
            error = result['message']
    
    return render_template('update.html', student=student, error=error, success=success)

if __name__ == '__main__':
    app.run(debug=True)
