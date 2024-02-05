from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')

# Directory to store uploaded text files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dictionary to store user information and uploaded text files (simulating a database)
users = {}

def count_words(text):
    words = text.split()
    return len(words)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        # Check if username is already taken
        if username in users:
            error_message = "Username already exists. Choose a different one."
        else:
            # Store user information in the dictionary
            users[username] = {
                'password': password,
                'firstname': firstname,
                'lastname': lastname,
                'email': email
            }

            # Handle file upload
            file = request.files['file']
            if file:
                # Save the file with a secure filename
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Read the content of the uploaded text file
                with open(file_path, 'r') as file_content:
                    text_content = file_content.read()

                # Store the text content in the user dictionary
                users[username]['text_content'] = text_content
                # Calculate and store the word count
                users[username]['word_count'] = count_words(text_content)

            # Redirect to success_register page
            return redirect(url_for('success_register', username=username, firstname=firstname, lastname=lastname, email=email))

    return render_template('register.html', error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match
        user_info = users.get(username, None)
        if user_info and user_info['password'] == password:
            return render_template('success.html', user_info=user_info)
        else:
            error_message = "Username or password incorrect."

    return render_template('login.html', error_message=error_message)

@app.route('/success_register')
def success_register():
    username = request.args.get('username')
    firstname = request.args.get('firstname')
    lastname = request.args.get('lastname')
    email = request.args.get('email')

    user_info = users.get(username, None)
    word_count = user_info.get('word_count', 0)

    return render_template('success_register.html', username=username, firstname=firstname, lastname=lastname, email=email, word_count=word_count)

@app.route('/download/<username>')
def download(username):
    user_info = users.get(username, None)
    text_content = user_info.get('text_content', '')
    
    # Save the text content to a file
    filename = f"{username}_text_file.txt"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'w') as file:
        file.write(text_content)

    # Provide the file for download
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Create the 'uploads' directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=80, debug=True)
