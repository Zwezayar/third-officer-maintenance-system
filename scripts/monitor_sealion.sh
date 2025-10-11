#!/bin/bash
# Live monitor for SEA-LION model and file progress
PROJECT=~/third-officer-maintenance-system
DOCS=$PROJECT/docs
TARGET=$DOCS/risk_analysis.json   # change to the file you're waiting for

echo "=== SEA-LION Monitor Started ==="
echo "Watching: \$TARGET"
echo "Press Ctrl+C to stop."

# Get starting size (0 if not yet created)
start_size=0
[ -f "$TARGET" ] && start_size=$(stat -f%z "$TARGET")

while true; do
  clear
  echo "⏱ $(date '+%H:%M:%S')"
  echo
  echo "--- Ollama Processes ---"
  ps aux | grep "[o]llama" | awk '{printf "%-8s %-6s %-5s %s\n",$1,$2,$3,$11}'
  echo
  echo "--- File Progress ---"
  if [ -f "$TARGET" ]; then
      size=$(stat -f%z "$TARGET")
      diff=$((size - start_size))
      if [ $size -gt 0 ]; then
          pct=$(awk "BEGIN {printf \"%.1f\", ($size/5000000)*100}") # rough scale to 5MB = 100%
          echo "Current size: $(du -h "$TARGET" | cut -f1)  (~$pct%)"
      else
          echo "Waiting for file to start growing..."
      fi
  else
      echo "File not created yet."
  fi
  echo
  echo "--- Active Port ---"
  lsof -i :11434 | grep LISTEN || echo "No listener on 11434"
  sleep 5
done
