#!/bin/bash

# Test Jekyll site locally
# This script helps you test your Jekyll site locally before pushing to GitHub

set -e  # Exit on error

# Check if Ruby is installed
if ! command -v ruby &> /dev/null; then
    echo "Error: Ruby is not installed. Please install Ruby first."
    exit 1
fi

# Check if Bundler is installed
if ! command -v bundle &> /dev/null; then
    echo "Installing Bundler..."
    gem install bundler
fi

cd docs

# Install dependencies if needed
if [ ! -d "vendor/bundle" ]; then
    echo "Installing dependencies..."
    bundle install --path vendor/bundle
else
    echo "Updating dependencies..."
    bundle update
fi

# Build the site
echo "Building the site..."
bundle exec jekyll build

# Serve the site
echo "Starting local server at http://localhost:4000/my-public-notes/"
echo "Press Ctrl+C to stop the server"
bundle exec jekyll serve --baseurl "/my-public-notes" 