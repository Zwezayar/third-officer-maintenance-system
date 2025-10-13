#!/bin/bash
# Task 1 Setup Script - SECURE VERSION (No PATs)

set -e  # Exit on error

echo "🚀 Starting Task 1: Third Officer Responsibilities Setup"

# Create directories
mkdir -p docs output backend/data scripts logs

# Generate responsibilities matrix
cat > docs/responsibilities_matrix.csv << 'CSV_EOF'
Category,Duty,Regulation,Tech_Integration,Gaps
Navigation,Maintain watch,SOLAS Ch. V,ECDIS AI collision avoidance,ECDIS training needed
Safety,LSA inspections,SOLAS Ch. III,Python expiry checker,SEA-LION integration
Safety,FFA maintenance,SOLAS Ch. II-2,AI deficiency prediction,Model validation
Medical,Crew health checks,MLC 2022,Health monitoring app,App access
Logs,Deck log entries,STCW A-II/1,Digital logbook,Digital training
Defects,Report to C/O,ISM Code,Mobile reporting,Standard format
Drills,LSA/FFA drills,SOLAS Ch. III,AI drill scheduler,Drill templates
Training,Onboard training,STCW A-II/1,AI modules,Module access
CSV_EOF

# Risk assessment
cat > docs/risk_assessment.md << 'MD_EOF'
# Risk Assessment for Third Officer

## High Risk Items
- **Lifeboat Release (309 defects)**: Weekly tests (SOLAS III/20)
- **Fire Dampers (287 failures)**: Monthly checks (SOLAS II-2)
- **ECDIS Cyber Risk**: Updates per MSC.428(98)

## Mitigations
- AI scheduled inspections
- Digital checklists
- Automated alerts
MD_EOF

# JSON analysis template
cat > docs/risk_analysis.json << 'JSON_EOF'
{
  "high_risk": ["Lifeboat Release", "Fire Dampers"],
  "mitigations": {
    "lifeboat": "Weekly visual + monthly load test",
    "fire_dampers": "Monthly functional test"
  },
  "compliance": "SOLAS 2025 ready"
}
JSON_EOF

# Generate PDF if pandoc available
if command -v pandoc >/dev/null 2>&1; then
    echo "Generating PDF report..."
    pandoc docs/risk_assessment.md -o docs/task_1_report.pdf || echo "PDF optional - Markdown ready"
else
    echo "Pandoc not found - Markdown report ready"
fi

# Git operations (SECURE - no PATs)
echo "Setting up Git..."
git add docs/ backend/ scripts/ .gitignore || true
git status

echo "✅ Task 1 files created:"
echo "- docs/responsibilities_matrix.csv"
echo "- docs/risk_assessment.md"
echo "- docs/task_1_report.pdf (if pandoc installed)"
echo "- Git ready for manual push"

echo ""
echo "🚀 NEXT STEPS:"
echo "1. source venv/bin/activate"
echo "2. git commit -m 'Task 1 complete'"
echo "3. git push origin main  (use SSH or new PAT)"
echo "4. Ready for Task 2: Checklist Digitization"

echo "🎉 Task 1 setup complete - manually push to GitHub"
