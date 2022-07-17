from website import create_app

app = create_app()

# Only if we run this file are we going to execute app.run...
if __name__ == '__main__':
    # Run flask application and start a web server
    app.run(debug=True)