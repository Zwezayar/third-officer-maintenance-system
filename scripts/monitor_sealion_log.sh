#!/bin/bash
# Persistent SEA-LION & Ollama Monitor
PROJECT=~/third-officer-maintenance-system
DOCS=$PROJECT/docs
TARGET=$DOCS/risk_analysis.json     # change if you want to watch a different output
LOG=$PROJECT/logs/sealion_monitor_$(date +%Y-%m-%d).log
mkdir -p $(dirname "$LOG")

echo "=== SEA-LION Monitor Started $(date) ===" | tee -a "$LOG"
echo "Watching: $TARGET" | tee -a "$LOG"
echo "Logging to: $LOG"
echo "Press Ctrl+C to stop."
echo

while true; do
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp]" | tee -a "$LOG"
  echo "--- Ollama Processes ---" | tee -a "$LOG"
  ps aux | grep "[o]llama" | awk '{printf "%-8s %-6s %-5s %s\n",$1,$2,$3,$11}' | tee -a "$LOG"
  echo "--- File Progress ---" | tee -a "$LOG"

  if [ -f "$TARGET" ]; then
      size=$(stat -f%z "$TARGET")
      pct=$(awk "BEGIN {printf \"%.1f\", ($size/5000000)*100}") # 5 MB ≈ 100 %
      human=$(du -h "$TARGET" | cut -f1)
      echo "Current size: $human (~$pct%)" | tee -a "$LOG"
  else
      echo "File not yet created." | tee -a "$LOG"
  fi

  echo "--- Active Port ---" | tee -a "$LOG"
  lsof -i :11434 | grep LISTEN | tee -a "$LOG" || echo "No listener on 11434" | tee -a "$LOG"

  echo "----------------------------------------" | tee -a "$LOG"
  sleep 60    # refresh every 1 minute
done
