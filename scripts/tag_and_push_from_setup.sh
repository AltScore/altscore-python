#!/bin/bash

# 0. determine the project root, which is ./../../.. relative to this script
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
# 0.1 modify setup.py to increase minor version
cd "$PROJECT_ROOT" || exit

# Use grep to extract the version number. The version part is like version="a.b.c"
# macOS doesn't support the -P option in grep, so use a POSIX-compatible regex
CURRENT_VERSION=$(grep -oE 'version="[0-9]+\.[0-9]+\.[0-9]+"' setup.py | head -n 1)
CURRENT_MAJOR=$(echo "$CURRENT_VERSION" | cut -d'"' -f2 | cut -d. -f1)
CURRENT_SECONDARY=$(echo "$CURRENT_VERSION" | cut -d'"' -f2 | cut -d. -f2)
CURRENT_MINOR=$(echo "$CURRENT_VERSION" | cut -d'"' -f2 | cut -d. -f3)

# Tag the new version
git tag "v${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR}"

# 2. Push changes and tags to the repository
git push --tags

echo "v${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR}"