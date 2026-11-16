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
# exit 0 + a number   the count. A matched section with no records prints 0.
# exit 2, no number   not measured: section-regex is not empty and no '## '
#                     heading outside a fence matches it (a wrong or stale
#                     section name). Never read this as 0; fix the regex.
#
# The awk program from BEGIN through the END line is copied verbatim into the Claude
# si-improve §6, si-archive §1 and references/data.md; tests/test_compat.py fails if a
# copy drifts.
awk -v unit="${2-^### }" -v sec="${3-§(log|로그)}" '
BEGIN { inlog = (sec == "") }
{ t = ""; if (match($0, /^ ? ? ?(```+|~~~+)/)) { t = substr($0, RSTART, RLENGTH); sub(/^ +/, "", t) } }
fence == "" && t != "" { fence = substr(t, 1, 1); flen = length(t); next }
fence != "" { if (t != "" && substr(t, 1, 1) == fence && length(t) >= flen && substr($0, RSTART + RLENGTH) ~ /^[ \t]*$/) fence = ""; next }
/^## / { inlog = (sec == "" || $0 ~ sec); if (inlog) seen = 1; next }
inlog && $0 ~ unit { n++ }
END { if (sec != "" && !seen) { print "not measured: no ## heading matches sec=" sec > "/dev/stderr"; exit 2 } print n + 0 }
' "$1"
