.PHONY: uv setup clean

uv:
	@echo "Installing uv..."
	curl -LsSf https://astral.sh/uv/install.sh | sh

setup:
	@echo "Setting up environment..."
	uv venv
	@echo "Virtual environment created. To activate: source .venv/bin/activate"
	uv pip install -e .
	# uv pip install pre-commit && pre-commit install # Uncomment if pre-commit config is added

clean:
	rm -rf .venv
	rm -rf build dist
	rm -rf **/__pycache__
