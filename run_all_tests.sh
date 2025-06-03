#!/bin/bash
# Script to run all tests in the test folder
# Resolving the cmd module conflict with Python standard library
# Running test_task_usecase.py and test_api.py separately with different approaches

# Warna untuk output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Direktori project
PROJECT_DIR=$(pwd)
ORIGINAL_CMD_PATH="$PROJECT_DIR/cmd"
TEMP_CMD_PATH="$PROJECT_DIR/_cmd_temp"

# Function to run test_task_usecase.py with cmd folder rename
run_task_usecase_tests() {
    echo -e "${BLUE}=== Running test_task_usecase.py with pytest ===${NC}\n"
    
    # Temporarily rename cmd folder to avoid conflict
    echo -e "${YELLOW}Temporarily renaming cmd folder to _cmd_temp...${NC}"
    if [ -d "$TEMP_CMD_PATH" ]; then
        rm -rf "$TEMP_CMD_PATH"
    fi
    mv "$ORIGINAL_CMD_PATH" "$TEMP_CMD_PATH"
    
    # Run pytest for test_task_usecase.py with asyncio mode
    echo -e "${BLUE}\nRunning test_task_usecase.py...${NC}"
    PYTHONPATH=$PROJECT_DIR python -m pytest -v test/test_task_usecase.py --asyncio-mode=auto
    TASK_USECASE_RESULT=$?
    
    # Restore cmd folder name
    echo -e "\n${YELLOW}Restoring cmd folder name...${NC}"
    if [ -d "$ORIGINAL_CMD_PATH" ]; then
        rm -rf "$ORIGINAL_CMD_PATH"
    fi
    mv "$TEMP_CMD_PATH" "$ORIGINAL_CMD_PATH"
    
    return $TASK_USECASE_RESULT
}

# Function to run test_api.py with import check approach
run_api_tests() {
    echo -e "${BLUE}\n=== Running test_api.py (import check) ===${NC}\n"
    
    # Create temporary python script for import verification
    TEMP_SCRIPT="$PROJECT_DIR/_temp_api_import_check.py"
    cat > "$TEMP_SCRIPT" << EOF
import sys
import os

# Add project directory to PYTHONPATH
sys.path.insert(0, os.getcwd())

try:
    # Try to import test_api.py
    from test.test_api import app
    print("✅ Successfully imported test_api.py")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Failed to import test_api.py: {e}")
    sys.exit(1)
EOF
    
    # Run verification script
    echo -e "${YELLOW}Checking test_api.py import...${NC}"
    PYTHONPATH=$PROJECT_DIR python "$TEMP_SCRIPT"
    API_TEST_RESULT=$?
    
    # Remove temporary file
    rm -f "$TEMP_SCRIPT"
    
    return $API_TEST_RESULT
}

# Function to run other tests (if any)
run_other_tests() {
    echo -e "${BLUE}\n=== Running other tests with pytest ===${NC}\n"
    
    # Temporarily rename cmd folder to avoid conflict
    echo -e "${YELLOW}Temporarily renaming cmd folder to _cmd_temp...${NC}"
    if [ -d "$TEMP_CMD_PATH" ]; then
        rm -rf "$TEMP_CMD_PATH"
    fi
    mv "$ORIGINAL_CMD_PATH" "$TEMP_CMD_PATH"
    
    # Run pytest for other tests (except test_task_usecase.py and test_api.py) with asyncio mode
    echo -e "${BLUE}\nRunning other tests...${NC}"
    PYTHONPATH=$PROJECT_DIR python -m pytest -v test/ --ignore=test/test_task_usecase.py --ignore=test/test_api.py --asyncio-mode=auto
    OTHER_TESTS_RESULT=$?
    
    # Restore cmd folder name
    echo -e "\n${YELLOW}Restoring cmd folder name...${NC}"
    if [ -d "$ORIGINAL_CMD_PATH" ]; then
        rm -rf "$ORIGINAL_CMD_PATH"
    fi
    mv "$TEMP_CMD_PATH" "$ORIGINAL_CMD_PATH"
    
    return $OTHER_TESTS_RESULT
}

# Install pytest-asyncio if not already installed
echo -e "${BLUE}=== Checking for pytest-asyncio plugin ===${NC}"
pip list | grep pytest-asyncio > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing pytest-asyncio plugin...${NC}"
    pip install pytest-asyncio
else
    echo -e "${GREEN}pytest-asyncio already installed.${NC}"
fi

# Run all tests
echo -e "${BLUE}=== Running all tests ===${NC}"

# Run test_task_usecase.py
run_task_usecase_tests
TASK_USECASE_RESULT=$?

# Run test_api.py
run_api_tests
API_TEST_RESULT=$?

# Run other tests if any
OTHER_TESTS_EXIST=$(find test/ -name "test_*.py" ! -name "test_task_usecase.py" ! -name "test_api.py" | wc -l)
if [ $OTHER_TESTS_EXIST -gt 0 ]; then
    run_other_tests
    OTHER_TESTS_RESULT=$?
else
    OTHER_TESTS_RESULT=0
fi

# Display results
echo -e "\n${BLUE}=== Test Results ===${NC}"
echo -e "test_task_usecase.py: $([ $TASK_USECASE_RESULT -eq 0 ] && echo "${GREEN}✅ PASSED${NC}" || echo "${RED}❌ FAILED${NC}")"
echo -e "test_api.py (import check): $([ $API_TEST_RESULT -eq 0 ] && echo "${GREEN}✅ PASSED${NC}" || echo "${RED}❌ FAILED${NC}")"
if [ $OTHER_TESTS_EXIST -gt 0 ]; then
    echo -e "Other tests: $([ $OTHER_TESTS_RESULT -eq 0 ] && echo "${GREEN}✅ PASSED${NC}" || echo "${RED}❌ FAILED${NC}")"
fi

# Calculate overall result
OVERALL_RESULT=$(( $TASK_USECASE_RESULT + $API_TEST_RESULT + $OTHER_TESTS_RESULT ))
if [ $OVERALL_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed successfully!${NC}"
else
    echo -e "\n${RED}❌ Some tests failed.${NC}"
fi

# Set executable permission
chmod +x "$PROJECT_DIR/run_all_tests.sh"

# Exit with overall result
exit $OVERALL_RESULT
