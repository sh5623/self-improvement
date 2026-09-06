#!/bin/sh
# Count the work blocks in a data file's log section, ignoring fenced code.
#
# A fence follows CommonMark 0.31.2 §4.5: at most 3 spaces of indentation, then
# 3 or more backticks or tildes. It closes only on a line with the same fence
# character, at least as many of them, at most 3 spaces of indentation, and
# nothing but spaces after. Anything else inside the fence (a shorter fence, the
# other fence character, a heading) is content. Headings inside a fence do not
# open or close sections, and headings outside the log section are not counted.
#
# usage: count_log_blocks.sh <datafile> [unit-regex] [section-regex]
#   unit-regex     one record, anchored at column 0. Default: the plugin layout,
#                  '^### '. A registered system substitutes the unit its format
#                  map names (dated bullets: '^- ').
#   section-regex  matched against '## ' headings; counting is on while the
#                  latest '## ' heading matches. Default: '§(log|로그)'. Pass ''
#                  to count the whole file (a data file with no '## ' headings).
#
# The awk program between BEGIN and END is copied verbatim into si-improve §5,
# si-archive §0 and references/data.md; tests/test_compat.py fails if a copy drifts.
awk -v unit="${2-^### }" -v sec="${3-§(log|로그)}" '
BEGIN { inlog = (sec == "") }
{ t = ""; if (match($0, /^ ? ? ?(```+|~~~+)/)) { t = substr($0, RSTART, RLENGTH); sub(/^ +/, "", t) } }
fence == "" && t != "" { fence = substr(t, 1, 1); flen = length(t); next }
fence != "" { if (t != "" && substr(t, 1, 1) == fence && length(t) >= flen && substr($0, RSTART + RLENGTH) ~ /^[ \t]*$/) fence = ""; next }
/^## / { inlog = (sec == "" || $0 ~ sec); next }
inlog && $0 ~ unit { n++ }
END { print n + 0 }
' "$1"
