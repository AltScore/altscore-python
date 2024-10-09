#!/bin/bash

# 0. determine the project root, which is ./../../.. relative to this script
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/.."
# 0.1 modify setup.py to increase minor version
cd "$PROJECT_ROOT" || exit

# Use grep to extract the version number. The version part is like version="a.b.c"
# macOS doesn't support the -P option in grep, so use a POSIX-compatible regex
CURRENT_VERSION=$(grep -oE 'version="[0-9]+\.[0-9]+\.[0-9]+"' setup.py | head -n 1)
CURRENT_MAJOR=$(echo "$CURRENT_VERSION" | cut -d. -f1 | grep -oE '[0-9]+')
CURRENT_SECONDARY=$(echo "$CURRENT_VERSION" | cut -d. -f2 | grep -oE '[0-9]+')
CURRENT_MINOR=$(echo "$CURRENT_VERSION" | cut -d. -f3 | grep -oE '[0-9]+')

# Increment the minor version
NEW_MINOR=$((CURRENT_MINOR+1))
NEW_MAJOR=$CURRENT_MAJOR
NEW_SECONDARY=$CURRENT_SECONDARY

# Replace the version, keeping the original a and b parts
# Using the appropriate `sed` syntax for macOS and Linux
# macOS's sed requires an explicit '' after -i
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/version=\"${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR}\"/version=\"${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}\"/g" setup.py
else
  sed -i "s/version=\"${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR}\"/version=\"${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}\"/g" setup.py
fi

# 1. do git add and git commit
git add .
NEW_VERSION="${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"
git commit -m "fix: minor change -> v$NEW_VERSION"

# Tag the new version
git tag "v${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"

# 2. Push changes and tags to the repository
git push
git push --tags

# Output the old and new versions
echo "v${CURRENT_MAJOR}.${CURRENT_SECONDARY}.${CURRENT_MINOR} -> v${NEW_MAJOR}.${NEW_SECONDARY}.${NEW_MINOR}"