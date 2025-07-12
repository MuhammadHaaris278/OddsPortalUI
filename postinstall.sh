#!/bin/bash
# Set the Playwright browser installation path to a writable directory
PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright python3 -m playwright install --with-deps
