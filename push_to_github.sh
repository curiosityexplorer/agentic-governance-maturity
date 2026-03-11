#!/bin/bash
#
# push_to_github.sh
# =================
# Initialize the git repo and push to GitHub.
#
# Prerequisites:
#   1. GitHub CLI (gh) authenticated, OR git remote configured
#   2. Repo created at: https://github.com/curiosityexplorer/agentic-governance-maturity
#
# Usage:
#   chmod +x push_to_github.sh
#   ./push_to_github.sh
#

set -e

REPO_URL="https://github.com/curiosityexplorer/agentic-governance-maturity.git"

echo "============================================"
echo "AAGMM Repository Push Script"
echo "============================================"

# Remove pycache before committing
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "[1/5] Initializing git repository..."
    git init
    git branch -M main
else
    echo "[1/5] Git already initialized."
fi

# Add remote
echo "[2/5] Setting remote origin..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# Stage all files
echo "[3/5] Staging files..."
git add -A

# Commit
echo "[4/5] Committing..."
git commit -m "Initial release: AAGMM v1.0.0

Agentic AI Governance Maturity Model (AAGMM)
- Five-level governance framework (12 domains)
- 750 simulation runs (5 scenarios x 5 levels x 30 trials)
- All pairwise comparisons significant at p < 0.001
- Publication figures and aggregated results included
- 15 unit tests, all passing

Paper: 'Governing the Agentic Enterprise: A Governance Maturity
Model for Managing AI Agent Sprawl in Business Operations'
Target: MDPI AI Special Issue

Author: Vivek Acharya (vacharya@bu.edu)
ORCID: 0009-0002-0860-9462"

# Push
echo "[5/5] Pushing to GitHub..."
git push -u origin main

echo ""
echo "============================================"
echo "SUCCESS! Repository pushed to:"
echo "  $REPO_URL"
echo "============================================"
