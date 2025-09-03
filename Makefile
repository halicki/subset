# Makefile for subset validation library
# Provides standardized commands for development workflows

.PHONY: help test lint format typecheck quality clean install dev-install

# Default target
help:
	@echo "Available commands:"
	@echo "  make test        - Run all tests with pytest"
	@echo "  make lint        - Run ruff linting checks"
	@echo "  make format      - Format code with ruff"
	@echo "  make typecheck   - Run type checking with ty"
	@echo "  make quality     - Run all quality checks (test + lint + typecheck)"
	@echo "  make clean       - Clean up cache files and build artifacts"
	@echo "  make install     - Install the package and dependencies"
	@echo "  make dev-install - Install package with development dependencies"

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

# Run linting checks
lint:
	@echo "🔍 Running linting checks..."
	uv run ruff check .

# Format code
format:
	@echo "✨ Formatting code..."
	uv run ruff format .

# Run type checking
typecheck:
	@echo "🔎 Running type checking..."
	uv run ty check .

# Run all quality checks
quality: test lint typecheck
	@echo "✅ All quality checks completed successfully!"

# Clean up cache files and build artifacts
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf tests/__pycache__/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "✅ Cleanup completed!"

# Install package and dependencies
install:
	@echo "📦 Installing package..."
	uv sync

# Install with development dependencies
dev-install:
	@echo "🛠️ Installing with development dependencies..."
	uv sync --dev
	@echo "✅ Development environment ready!"

# Quick development workflow - format, then run quality checks
dev: format quality
	@echo "🚀 Development workflow completed!"