from flask import Flask, request, render_template, send_file, after_this_request
import os
import DataCleaning  # Import DataCleaning.py
import DataProcessing  # Import DataProcessing.py

app = Flask(__name__)

# Define the folder to save uploaded and processed files
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the uploaded file
    uploaded_file = request.files['uploadedFile']
    first_lower_bound = int(request.form['firstLowerBound'])
    upper_bounds = list(map(int, request.form['upperBounds'].split()))

    if uploaded_file:
        # Step 1: Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)

        try:
            # Step 2: Process the file using DataCleaning.py
            cleaned_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'cleaned_' + uploaded_file.filename)
            DataCleaning.main(file_path, cleaned_file_path, first_lower_bound, upper_bounds)  # Cleaning logic

            # Step 3: Process the cleaned file using DataProcessing.py
            final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'final_' + uploaded_file.filename)
            DataProcessing.main(cleaned_file_path, final_file_path)  # Processing logic

            # Step 4: Register a cleanup function to delete files after the response is sent
            @after_this_request
            def cleanup(response):
                try:
                    # Remove all files after they are processed
                    os.remove(file_path)  # Remove the original uploaded file
                    os.remove(cleaned_file_path)  # Remove the cleaned file
                    os.remove(final_file_path)  # Remove the final processed file
                except Exception as e:
                    print(f"Error cleaning up files: {e}")
                return response

            # Step 5: Send the final processed file back to the user for download
            return send_file(final_file_path, as_attachment=True)

        except Exception as e:
            # If there is any error during processing, log it and return an error message
            print(f"Error during processing: {e}")
            return "There was an error processing the file.", 500

    

    return 'No file uploaded!'

if __name__ == '__main__':
    app.run(debug=True)
