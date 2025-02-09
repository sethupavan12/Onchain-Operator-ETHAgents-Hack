.PHONY: install server chatbot

# Install all necessary packages
install:
	poetry install --no-root
	poetry run pip install browser_use

# Run the server with auto-reload
server:
	poetry run uvicorn api:app --reload

# Run the chatbot in the terminal
chatbot:
	poetry run python chatbot.py

