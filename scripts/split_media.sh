# split_media.sh — split files bigger than a size limit into smaller parts.
#
#   * video/audio  -> ffmpeg segment muxer, NO re-encoding (fast, lossless).
#                     Each part is playable on its own. Cuts happen on keyframes,
#                     so the script verifies every part and retries with shorter
#                     segments until all parts are <= the limit.
#   * anything else -> plain byte split (`split -b`). Parts are NOT usable alone;
#                     join them back with:  cat name.ext.part* > name.ext
#
# Parts go to "<file>.parts/" next to the original (or under -o DIR).
#
# Join video parts again:
#   cd movie.mp4.parts && printf "file '%s'\n" movie_part*.mp4 > list.txt
#   ffmpeg -f concat -safe 0 -i list.txt -c copy ../movie_joined.mp4


set -u -o pipefail

MAX_MB=50
OUT_ROOT=""
DELETE_ORIG=0
DRY_RUN=0
SAFETY=0.90   # aim a bit below the limit (VBR / container overhead)
MAX_TRIES=6   # shrink-and-retry attempts per file

usage() {
  cat <<EOF
Usage: ${0##*/} [-s MB] [-o DIR] [-D] [-n] <file-or-folder>...

  -s MB   max size of each part in MB (default: $MAX_MB; decimals allowed)
  -o DIR  put the *.parts folders under DIR instead of next to the originals
  -D      delete the original after a successful split
  -n      dry run: only show what would be done
  -h      this help

Folders are scanned recursively; only files bigger than the limit are touched.
Examples:
  ${0##*/} movie.mkv
  ${0##*/} -s 45 ~/Videos
  ${0##*/} -s 1900 -D big_backup.zip
EOF
}

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
log() { printf '%s\n' "$*" >&2; }
calc() { LC_ALL=C awk "$@"; }
fsize() { wc -c <"$1" | tr -d ' '; }
mb() { calc -v b="$1" 'BEGIN{printf "%.1f MB", b/1048576}'; }

while getopts ":s:o:Dnh" opt; do
  case $opt in
    s) MAX_MB=$OPTARG ;;
    o) OUT_ROOT=$OPTARG ;;
    D) DELETE_ORIG=1 ;;
    n) DRY_RUN=1 ;;
    h) usage; exit 0 ;;
    :) die "option -$OPTARG needs a value" ;;
    *) usage >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
[[ $# -gt 0 ]] || { usage >&2; exit 2; }

[[ $MAX_MB =~ ^[0-9]+([.][0-9]+)?$ ]] || die "-s must be a positive number (MB)"
MAX_BYTES=$(calc -v m="$MAX_MB" 'BEGIN{printf "%d", m*1024*1024}')
(( MAX_BYTES > 0 )) || die "-s must be greater than 0"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null ||
  die "ffmpeg and ffprobe are required"

# NOTE: capture ffprobe output in a variable instead of piping into `grep -q` /
# `head`: with `pipefail` an early-closing reader kills ffprobe (SIGPIPE) and the
# pipeline reports failure even though the answer was fine.
is_media() { # has a video or audio stream?
  local out
  out=$(ffprobe -v error -show_entries stream=codec_type -of csv=p=0 "$1" </dev/null 2>/dev/null) || return 1
  [[ $out == *video* || $out == *audio* ]]
}

get_duration() {
  local out
  out=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" </dev/null 2>/dev/null) || return 1
  printf '%s\n' "${out%%$'\n'*}"
}

run_ffmpeg() { # in seg pattern  (retries without subtitle streams if the first try fails)
  local in=$1 seg=$2 pattern=$3
  local common=(-nostdin -hide_banner -loglevel error -y -i "$in")
  local tail=(-c copy -f segment -segment_time "$seg" -reset_timestamps 1 "$pattern")
  ffmpeg "${common[@]}" -map 0:v? -map 0:a? -map 0:s? "${tail[@]}" </dev/null 2>/dev/null ||
    ffmpeg "${common[@]}" -map 0:v? -map 0:a? "${tail[@]}" </dev/null
}

split_media() { # in size outdir base suffix duration
  local in=$1 size=$2 outdir=$3 base=$4 suffix=$5 dur=$6
  local factor=$SAFETY tries=0 seg part biggest
  while (( tries < MAX_TRIES )); do
    rm -f "$outdir/${base}_part"*"$suffix"
    seg=$(calc -v d="$dur" -v m="$MAX_BYTES" -v s="$size" -v f="$factor" \
      'BEGIN{t=d*m/s*f; if (t<1) t=1; printf "%.3f", t}')
    run_ffmpeg "$in" "$seg" "$outdir/${base}_part%03d$suffix" || return 1
    biggest=0
    for part in "$outdir/${base}_part"*"$suffix"; do
      [[ -f $part ]] || continue
      (( $(fsize "$part") > biggest )) && biggest=$(fsize "$part")
    done
    (( biggest > 0 && biggest <= MAX_BYTES )) && return 0
    log "  largest part is $(mb "$biggest") (> limit); retrying with shorter segments"
    factor=$(calc -v f="$factor" 'BEGIN{printf "%.4f", f*0.8}')
    tries=$((tries + 1))
  done
  log "  could not get all parts under the limit (a single GOP may be too large)"
  return 1
}

split_generic() { # in outdir name
  local in=$1 outdir=$2 name=$3
  rm -f "$outdir/$name".part*
  split -b "$MAX_BYTES" -a 3 -d "$in" "$outdir/$name.part" 2>/dev/null ||
    split -b "$MAX_BYTES" -a 3 "$in" "$outdir/$name.part" || return 1
  cat "$outdir/$name".part* | cmp -s - "$in" # verify byte-for-byte
}

n_done=0; n_failed=0

process_file() {
  local f=$1 size dir name base="" ext="" suffix="" outdir dur mode
  size=$(fsize "$f")
  (( size > MAX_BYTES )) || return 0

  dir=$(dirname "$f"); name=$(basename "$f")
  if [[ $name == *.* && $name != .* ]]; then ext=${name##*.}; base=${name%.*}; suffix=".$ext"; fi
  outdir="${OUT_ROOT:-$dir}/$name.parts"

  mode=generic
  if [[ -n $ext ]] && is_media "$f"; then
    dur=$(get_duration "$f")
    calc -v d="$dur" 'BEGIN{exit !(d+0 > 0)}' && mode=media
  fi

  log "$f  ($(mb "$size"))  ->  $outdir/  [$mode split]"
  (( DRY_RUN )) && return 0
  mkdir -p "$outdir" || { n_failed=$((n_failed + 1)); return 1; }
  # clear leftovers of an earlier run for this file (either split mode)
  rm -f "$outdir/$name".part*
  [[ -n $base ]] && rm -f "$outdir/${base}_part"*"$suffix"

  if [[ $mode == media ]]; then
    split_media "$f" "$size" "$outdir" "$base" "$suffix" "$dur"
  else
    split_generic "$f" "$outdir" "$name"
  fi
  # shellcheck disable=SC2181
  if [[ $? -ne 0 ]]; then
    log "  FAILED: $f"; n_failed=$((n_failed + 1)); return 1
  fi

  local count; count=$(find "$outdir" -maxdepth 1 -type f | wc -l | tr -d ' ')
  log "  ok: $count parts"
  n_done=$((n_done + 1))
  if (( DELETE_ORIG )); then rm -f -- "$f" && log "  original deleted"; fi
}

for target in "$@"; do
  if [[ -d $target ]]; then
    while IFS= read -r -d '' f; do
      process_file "$f"
    done < <(find "$target" -type f -size +"${MAX_BYTES}"c -not -path '*.parts/*' -print0)
  elif [[ -f $target ]]; then
    process_file "$target"
  else
    log "skip: not a file or folder: $target"
    n_failed=$((n_failed + 1))
  fi
done

log "done: $n_done split, $n_failed failed"
(( n_failed == 0 ))