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

