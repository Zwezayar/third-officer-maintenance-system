#!/bin/zsh
# Smart monitor: prints "Task Completed" only when file is fully written

WATCH_DIR="docs"
SLEEP_INTERVAL=5       # check every 5 s
STABLE_TIME=10          # file must stay unchanged for 10 s
TMP_TRACK="/tmp/task_monitor_sizes.txt"

echo "🔎 Smart Task Monitor started. Watching $WATCH_DIR ..."

touch $TMP_TRACK

while true; do
  for file in $WATCH_DIR/*.json; do
    [ -e "$file" ] || continue
    size=$(stat -f "%z" "$file")
    prev_size=$(grep "^$file " $TMP_TRACK | awk '{print $2}')

    # update record of last seen size
    grep -v "^$file " $TMP_TRACK > ${TMP_TRACK}.tmp
    mv ${TMP_TRACK}.tmp $TMP_TRACK
    echo "$file $size" >> $TMP_TRACK

    # check if file size stopped changing
    if [[ "$size" = "$prev_size" && -n "$size" ]]; then
      # confirm it's stable for STABLE_TIME seconds
      sleep $STABLE_TIME
      new_size=$(stat -f "%z" "$file")
      if [[ "$new_size" = "$size" ]]; then
        echo "✅ Task Completed: $file fully written at $(date)"
        # remove entry so it won't repeat
        grep -v "^$file " $TMP_TRACK > ${TMP_TRACK}.tmp
        mv ${TMP_TRACK}.tmp $TMP_TRACK
      fi
    fi
  done
  sleep $SLEEP_INTERVAL
done

