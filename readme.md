# Local Development Run
- Open Terminal and execute the following command to create the virtual environment "python -m venv .myapp"
- Enter into the virtual environment using command: ".\.myapp\Scripts\activate"
- Install the required python libraries usind command: "pip install -r requirements.txt"
- Run the command "python main.py" to start the application

# Folder Structure

- `db_directory` has the sqlite DB. We need to adjust the path in ``application/config.py` as I have done in config.py file. 
- `application` is where our application code is placed
- `static` - default `static` files folder. It serves at '/static' path and it is used to store images, css files. 
- `templates` - Default flask templates folder


.
└── Project
    ├── application
    │   ├── blog_html.py
    │   ├── config.py
    │   ├── controllers.py
    │   ├── database.py
    │   ├── input_html.py
    │   └── models.py
    ├── db_directory
    │   └── blogdb.sqlite3
    ├── docs
    │   └── report.pdf
    ├── static (contains images and css files)
    ├── templates (contains all html files)
    ├── main.py
    ├── readme.md
    └── requirements.txt





