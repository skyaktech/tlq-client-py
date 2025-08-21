#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2)
echo -e "${GREEN}Current version: ${CURRENT_VERSION}${NC}"

# Ask for new version
echo -n "Enter new version (or press Enter to keep ${CURRENT_VERSION}): "
read NEW_VERSION

# Use current version if no new version provided
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
else
    # Update version in pyproject.toml
    sed -i '' "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" pyproject.toml
    
    # Update version in __init__.py
    sed -i '' "s/__version__ = \".*\"/__version__ = \"${NEW_VERSION}\"/" tlq_client/__init__.py
    
    echo -e "${GREEN}Updated version to ${NEW_VERSION}${NC}"
    
    # Commit version change
    git add pyproject.toml tlq_client/__init__.py
    git commit -m "chore: bump version to ${NEW_VERSION}"
fi

# Create git tag
TAG="v${NEW_VERSION}"
echo -e "${YELLOW}Creating git tag: ${TAG}${NC}"
git tag -a $TAG -m "Release version ${NEW_VERSION}"

# Clean old builds
echo -e "${YELLOW}Cleaning old builds...${NC}"
rm -rf dist/ build/ *.egg-info tlq_client.egg-info/

# Build the package
echo -e "${YELLOW}Building package...${NC}"
python -m build

# Ask where to publish
echo -e "${YELLOW}Where do you want to publish?${NC}"
echo "1) TestPyPI (test.pypi.org)"
echo "2) PyPI (pypi.org)"
echo "3) Both (TestPyPI first, then PyPI)"
echo "4) Skip publishing"
echo -n "Enter choice [1-4]: "
read PUBLISH_CHOICE

case $PUBLISH_CHOICE in
    1)
        echo -e "${YELLOW}Uploading to TestPyPI...${NC}"
        twine upload --repository testpypi dist/*
        echo -e "${GREEN}✓ Published to TestPyPI${NC}"
        echo -e "${GREEN}Test with: pip install --index-url https://test.pypi.org/simple/ tlq-client==${NEW_VERSION}${NC}"
        ;;
    2)
        echo -e "${YELLOW}Uploading to PyPI...${NC}"
        twine upload dist/*
        echo -e "${GREEN}✓ Published to PyPI${NC}"
        echo -e "${GREEN}Install with: pip install tlq-client==${NEW_VERSION}${NC}"
        
        # Push git changes
        echo -e "${YELLOW}Pushing to git...${NC}"
        git push
        git push --tags
        ;;
    3)
        echo -e "${YELLOW}Uploading to TestPyPI first...${NC}"
        twine upload --repository testpypi dist/*
        echo -e "${GREEN}✓ Published to TestPyPI${NC}"
        
        echo -n "Test installation successful? Proceed to PyPI? [y/N]: "
        read PROCEED
        if [ "$PROCEED" = "y" ] || [ "$PROCEED" = "Y" ]; then
            echo -e "${YELLOW}Uploading to PyPI...${NC}"
            twine upload dist/*
            echo -e "${GREEN}✓ Published to PyPI${NC}"
            echo -e "${GREEN}Install with: pip install tlq-client==${NEW_VERSION}${NC}"
            
            # Push git changes
            echo -e "${YELLOW}Pushing to git...${NC}"
            git push
            git push --tags
        else
            echo -e "${YELLOW}Skipped PyPI publishing${NC}"
            echo -e "${YELLOW}To publish later, run: twine upload dist/*${NC}"
        fi
        ;;
    4)
        echo -e "${YELLOW}Skipped publishing${NC}"
        echo -e "${YELLOW}To publish later, run: twine upload dist/*${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✓ Done!${NC}"