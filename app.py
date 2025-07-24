from config import create_app


app = create_app()


if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, host="127.0.0.1", port=5000)
