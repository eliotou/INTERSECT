#!/bin/bash

# THIS SCRIPT CONVERTS EVERY MP4 (IN THE CURRENT FOLDER AND SUBFOLDER) TO A MULTI-BITRATE VIDEO IN MP4-DASH
# For each file "videoname.mp4" it creates a folder "dash_videoname" containing a dash manifest file "stream.mpd" and subfolders containing video segments.


MYDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
SAVEDIR=$(pwd)

# Check programs
if [ -z "$(which ffmpeg)" ]; then
    echo "Error: ffmpeg is not installed"
    exit 1
fi

if [ -z "$(which MP4Box)" ]; then
    echo "Error: MP4Box is not installed"
    exit 1
fi

cd "$MYDIR"

TARGET_FILES=$(find ./ -maxdepth 1 -type f \( -name "*.mov" -or -name "*.mp4" \))
for f in $TARGET_FILES
do
  fe=$(basename "$f") # fullname of the file
  f="${fe%.*}" # name without extension

  if [ ! -d "${f}" ]; then #if directory does not exist, convert
    echo "Converting \"$f\" to multi-bitrate video in MPEG-DASH"

    ffmpeg -i "${fe}" -c:a copy -vn "${f}_audio.mp4"
   
    ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 5300k -maxrate 5300k -bufsize 2650k -vf 'scale=-1:1080' "${f}_1080.mp4"    
    ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 2400k -maxrate 2400k -bufsize 1200k -vf 'scale=-1:720' "${f}_720.mp4"
    ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 1060k -maxrate 1060k -bufsize 530k -vf 'scale=-1:478' "${f}_480.mp4"  
    ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 600k -maxrate 600k -bufsize 300k -vf 'scale=-1:360' "${f}_360.mp4"
    ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 260k -maxrate 260k -bufsize 130k -vf 'scale=-1:242' "${f}_242.mp4"

    rm -f ffmpeg*log*
    # if audio stream does not exist, ignore it
    if [ -e "${f}_audio.mp4" ]; then

       MP4Box -dash 1000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" "${f}_1080.mp4" "${f}_720.mp4" "${f}_480.mp4" "${f}_360.mp4" "${f}_242.mp4" "${f}_audio.mp4" -out "${f}.mpd"
    fi
    # create a jpg for poster. Use imagemagick or just save the frame directly from ffmpeg is you don't have cjpeg installed.
    ffmpeg -i "${fe}" -ss 00:00:00 -vframes 1  -qscale:v 10 -n -f image2 - | cjpeg -progressive -quality 75 -outfile "${f}"/"${f}".jpg

    fi

done

cd "$SAVEDIR"
