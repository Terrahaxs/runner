setup:
	@virtualenv venv && \
		. venv/bin/activate && \
		pip install -r features/requirements.txt && \
		pip install -e .