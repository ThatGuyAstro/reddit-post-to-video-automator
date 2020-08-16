from __future__ import unicode_literals

import json
import re
import os
import requests
import youtube_dl
from datetime import date
from gtts import gTTS


TAKE = 10
#SUBREDDITS = ["dankvideos", "funnyvideos", "futurology", "nonononoyes", "natureisfuckinglit", "instant_regret", "listentothis", "holdmyredbull", "holdmyfries", "praisethecamerman", "actuallyfunny", "facepalm", "perfecttiming", "interestingasfuck", "damnthatsinteresting"]
SUBREDDITS = ["dankvideos", "funnyvideos", "comedycemetery", "dankmemes", "pewdiepiesubmissions", "funny", "therewasanattempt", "contagiouslaughter", "idiotsfightingthings"]

def insertTransition(index):
    os.system("ffmpeg -i transition.mp4 transition_{0}.mp4".format(index))

def generatePreview(videoFileName, audioFileName, text, outputFileName):

    os.system("ffmpeg -loglevel panic -loop 1 -y -i {0} -i {1} -shortest -acodec copy -vcodec mjpeg {2}".format(

        videoFileName,
        audioFileName,
        outputFileName

    ))

    os.system(str.format('ffmpeg -loglevel panic -i {0} -vf drawtext="fontfile=font.ttf: \
        text={1}: fontcolor=white: fontsize=108: box=1: boxcolor=black@0.5: \
        boxborderw=5: x=(w-text_w) / 2: y=(h-text_h) / 2" -codec:a copy {2}', outputFileName, text, str.format("full_preview_{0}", outputFileName)))



    os.system("ffmpeg -i {0} {1}".format(

        str.format("full_preview_{0}", outputFileName),
        str.format("00_full_preview_{0}", outputFileName) + ".mp4"

    ))



def generateTtsFile(text, fileName):
    # define variables
    s = text
    file = fileName

    # initialize tts, create mp3 and play
    tts = gTTS(s, 'com')
    tts.save(file)

def endpoint(subreddit):
    return str.format("https://api.reddit.com/r/{0}/top?t=today", subreddit)

def extractUrl(value):
    return re.search("(?P<url>https?://[^\s]+)", value).group("url")

def stitchAudioVideo(videoFileName, audioFileName, outputFileName):

    print("Stitching audio and video")
    os.system(str.format("ffmpeg -loglevel panic -i {0} -i {1} -codec copy -shortest {2}", videoFileName, audioFileName, outputFileName))

def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file: 
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)

def downloadVideos(urls):

    today = date.today()
    #os.makedirs(str(today))

    index = 1

    for url in urls:

        #Switch statements? lol
        if("youtube" in url):
            ydl_opts = {
                "nocheckcertificate": True,
                "output": str.format("/{0}", date.today())
            }

            # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            #     ydl.download([url])

        if(isinstance(url, list)):

            generateTtsFile(url[2], "tts_audio_{0}.mp3".format(index))

            generatePreview("background.jpg", "tts_audio_{0}.mp3".format(index), url[2], "preview_{0}.avi".format(index))

            download(url[0], str.format("reddit_video_{0}.mp4", index))
            download(url[1], str.format("reddit_audio_{0}.mp3", index))
            stitchAudioVideo(
                str.format("reddit_video_{0}.mp4", index),
                str.format("reddit_audio_{0}.mp3", index),
                str.format("Stitched_Reddit_Video_{0}.mp4", index)
            )

            os.system(str.format('ffmpeg -loglevel panic -i {0} -vf drawtext="fontfile=font.ttf: \
            text={1}: fontcolor=white: fontsize=16: box=1: boxcolor=black@0.5: \
            boxborderw=5: x=18: y=(h-text_h) - 34" drawtext="fontfile=font.ttf: \
            text={2}: fontcolor=white: fontsize=36: box=1: boxcolor=black: \
            boxborderw=5: x=24: y=(h-text_h)" -codec:a copy {3}', str.format("Stitched_Reddit_Video_{0}.mp4", index), "BingeCorner", url[3], str.format("Final_Stitched_Reddit_Video_{0}.mp4", index)))

            insertTransition(index)

            #Clean up all of our files
            os.remove("preview_{0}.avi".format(index))
            try:
                os.remove("full_preview_preview_{0}.avi".format(index))
            except:
                print("err")
            os.remove(str.format("reddit_video_{0}.mp4", index))
            os.remove(str.format("reddit_audio_{0}.mp3", index))
            os.remove(str.format("tts_audio_{0}.mp3", index))
            #os.remove(str.format("Stitched_Reddit_Video_{0}.mp4", index))
            index += 1



def buildVideoUrls():

    urls = []

    for subreddit in SUBREDDITS:
        response = requests.get(endpoint(subreddit), headers = {'User-agent': 'TopBot 1.1'})

        json = (response.json())

        cap = 0

        for entry in json["data"]["children"]:
            if cap < TAKE:
                postData = entry["data"]

                if(len(postData["media_embed"]) > 0 and "youtube" in str(postData["media_embed"])):
                    videoUrl = extractUrl(postData["media_embed"]["content"])
                    urls.append(videoUrl)

                if("secure_media" in postData):
                    if("reddit_video" in str(postData["secure_media"])):
                        if(postData["secure_media"]["reddit_video"]["is_gif"] == False and postData["secure_media"]["reddit_video"]["duration"] <= 60):
                            videoUrl = postData["secure_media"]["reddit_video"]["fallback_url"]

                            tempVideoUrl = videoUrl.split("/")

                            audioUrl = str.format("{0}/{1}/{2}/DASH_audio.mp4", tempVideoUrl[1], tempVideoUrl[2], tempVideoUrl[3])
                            audioUrl = audioUrl[1:]
                            audioUrl = str.format("https://{0}", audioUrl)

                            urls.append([videoUrl, audioUrl, postData["title"], subreddit])


    print("Built video urls!")
    return urls


def main():

    urls = buildVideoUrls()
    downloadVideos(urls)
    #print(urls)

if __name__ == "__main__":
    main()