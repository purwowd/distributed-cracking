#!/bin/bash
# Script to run test_api.py with proper setup
# Resolving the cmd module conflict with Python standard library

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR=$(pwd)
ORIGINAL_CMD_PATH="$PROJECT_DIR/cmd"
TEMP_CMD_PATH="$PROJECT_DIR/_cmd_temp"

# Check for pytest-asyncio
echo -e "${BLUE}=== Checking for pytest-asyncio plugin ===${NC}"
pip list | grep pytest-asyncio > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing pytest-asyncio plugin...${NC}"
    pip install pytest-asyncio
else
    echo -e "${GREEN}pytest-asyncio already installed.${NC}"
fi

# Temporarily rename cmd folder to avoid conflict
echo -e "${BLUE}\n=== Running test_api.py with pytest ===${NC}\n"
echo -e "${YELLOW}Temporarily renaming cmd folder to _cmd_temp...${NC}"
if [ -d "$TEMP_CMD_PATH" ]; then
    rm -rf "$TEMP_CMD_PATH"
fi
mv "$ORIGINAL_CMD_PATH" "$TEMP_CMD_PATH"

# Run test_api.py with pytest
echo -e "${BLUE}\nRunning test_api.py...${NC}"
PYTHONPATH=$PROJECT_DIR python -m pytest -v test/test_api.py --asyncio-mode=auto
API_TEST_RESULT=$?

# Restore cmd folder name
echo -e "\n${YELLOW}Restoring cmd folder name...${NC}"
if [ -d "$ORIGINAL_CMD_PATH" ]; then
    rm -rf "$ORIGINAL_CMD_PATH"
fi
mv "$TEMP_CMD_PATH" "$ORIGINAL_CMD_PATH"

# Display results
echo -e "\n${BLUE}=== Test Results ===${NC}"
if [ $API_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ test_api.py passed successfully!${NC}"
else
    echo -e "${RED}❌ test_api.py failed.${NC}"
fi

# Set executable permission
chmod +x "$PROJECT_DIR/run_api_test.sh"

# Exit with test result
exit $API_TEST_RESULT
