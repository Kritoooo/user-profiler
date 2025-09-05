#!/bin/bash

echo "🔍 User Profiler System Integrity Check"
echo "======================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ISSUES=0

# Check Python
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "  ✅ Python $PYTHON_VERSION found"
else
    echo "  ❌ Python 3 not found"
    ISSUES=$((ISSUES + 1))
fi

# Check Node.js
echo "📦 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js $NODE_VERSION found"
else
    echo "  ❌ Node.js not found"
    ISSUES=$((ISSUES + 1))
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "  ✅ npm $NPM_VERSION found"
else
    echo "  ❌ npm not found"
    ISSUES=$((ISSUES + 1))
fi

# Check backend files
echo "🏗️  Checking backend structure..."
BACKEND_FILES=(
    "backend/requirements.txt"
    "backend/src/api/main.py"
    "backend/src/models.py"
    "backend/src/config.py"
    "backend/.env.example"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check frontend files
echo "🎨 Checking frontend structure..."
FRONTEND_FILES=(
    "frontend/package.json"
    "frontend/vite.config.js"
    "frontend/index.html"
    "frontend/src/main.js"
    "frontend/src/App.vue"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file missing"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check scripts
echo "📜 Checking scripts..."
SCRIPTS=(
    "start.sh"
    "start_manual.sh"
    "run_tests.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "  ✅ $script (executable)"
    elif [ -f "$script" ]; then
        echo "  ⚠️  $script (not executable)"
        chmod +x "$script"
        echo "  ✅ Made $script executable"
    else
        echo "  ❌ $script missing"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check virtual environment
echo "🔧 Checking Python virtual environment..."
if [ -d "backend/venv" ]; then
    echo "  ✅ Virtual environment exists"
    cd backend
    source venv/bin/activate
    if pip list | grep -q fastapi; then
        echo "  ✅ Dependencies installed"
    else
        echo "  ⚠️  Dependencies not installed"
        echo "  💡 Run: pip install -r requirements.txt"
    fi
    deactivate
    cd ..
else
    echo "  ⚠️  Virtual environment not created"
    echo "  💡 It will be created automatically when starting"
fi

# Check npm modules
echo "📁 Checking npm modules..."
if [ -d "frontend/node_modules" ]; then
    echo "  ✅ Node modules exist"
else
    echo "  ⚠️  Node modules not installed"
    echo "  💡 They will be installed automatically when starting"
fi

# Port availability check
echo "🌐 Checking port availability..."
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ⚠️  Port 8000 is in use"
    echo "  💡 Stop any services using port 8000"
else
    echo "  ✅ Port 8000 available"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  ⚠️  Port 3000 is in use"
    echo "  💡 Stop any services using port 3000"
else
    echo "  ✅ Port 3000 available"
fi

# Summary
echo ""
echo "📊 Summary"
echo "=========="
if [ $ISSUES -eq 0 ]; then
    echo "✅ System integrity check passed!"
    echo "🚀 Ready to start with: ./start.sh"
    echo ""
    echo "💡 Next steps:"
    echo "   1. Run './start.sh' to launch the system"
    echo "   2. Open http://localhost:3000 in browser"
    echo "   3. Try analyzing a user like 'testuser'"
    echo "   4. Configure OpenAI API key for LLM features"
else
    echo "❌ Found $ISSUES issues that need attention"
    echo "🔧 Please resolve the issues above before starting"
fi

echo ""
echo "📚 Documentation:"
echo "   - README.md: Basic setup instructions"
echo "   - USAGE.md: Detailed usage guide"
echo "   - test_report.md: Test results and validation"