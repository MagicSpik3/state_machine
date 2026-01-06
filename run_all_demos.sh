#!/bin/bash

# Stop on first error
set -e

echo "========================================"
echo "🚀 Starting Full System Demonstration"
echo "========================================"

echo ""
echo "[1/5] Running Unit & Integration Tests..."
PYTHONPATH=src:. pytest
echo "✅ Tests Passed"

echo ""
echo "[2/5] Running Graph Demo..."
PYTHONPATH=src python demo_graph.py
echo "✅ Graph Demo Passed"

echo ""
echo "[3/5] Running Payroll Simulation..."
PYTHONPATH=src python demo_payroll.py
echo "✅ Payroll Simulation Passed"

# Only run Ollama if you have the server running, otherwise skip or warn
# echo ""
# echo "[4/5] Running AI Description Demo..."
# PYTHONPATH=src python demo_ollama.py

echo ""
echo "[4/5] Running Statify (Self-Test on Payroll)..."
# We assume payroll.spss exists in the root or legacy_repo
if [ -f "legacy_repo/payroll.spss" ]; then
    PYTHONPATH=src python statify.py legacy_repo/ --output docs/
    echo "✅ Statify Run Passed"
else
    echo "⚠️  Skipping Statify (legacy_repo/payroll.spss not found)"
fi

echo ""
echo "========================================"
echo "🎉 ALL SYSTEMS GREEN"
echo "========================================"