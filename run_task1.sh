#!/bin/bash

git config --global user.name "Zwe Zayar"
git config --global user.email "zwezayar88@gmail.com"

git remote set-url origin https://zwezayar88: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@github.com/Zwezayar/third-officer-maintenance-system.git

mkdir -p backend/data docs scripts logs output

touch docs/responsibilities_matrix.csv docs/risk_assessment.md docs/risk_analysis.json

echo "Task,Description,Status" > docs/responsibilities_matrix.csv
echo "# Risk Assessment" > docs/risk_assessment.md
echo '{"status":"pending","tasks":[]}' > docs/risk_analysis.json

if command -v pandoc >/dev/null 2>&1; then
    pandoc docs/risk_assessment.md -o output/risk_assessment.pdf
fi

git add docs/ backend/ output/ scripts/
git commit -m "✅ Task 1 completed: documents generated and PDF report"
git push origin main

echo "🎉 Task 1 fully completed and pushed to GitHub!"

