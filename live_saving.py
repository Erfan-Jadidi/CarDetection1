import streamlink
import time
import cv2 as cv

stream_url = "https://manifest.googlevideo.com/api/manifest/hls_variant/expire/1726699152/ei/MALrZpH9FajGi9oP8JeGgQQ/ip/86.107.43.88/id/DnUFAShZKus.1/source/yt_live_broadcast/requiressl/yes/xpc/EgVo2aDSNQ%3D%3D/tx/51257031/txs/51257028%2C51257029%2C51257030%2C51257031%2C51257032/hfr/1/playlist_duration/30/manifest_duration/30/maudio/1/spc/54MbxWGYEv10L5MZxcl1QBLH03orKC2Lm1DTpiyQY2Mqo9MPwbAv0LqcZ42gVds/vprv/1/go/1/rqh/5/pacing/0/nvgoi/1/keepalive/yes/dover/11/itag/0/playlist_type/DVR/sparams/expire%2Cei%2Cip%2Cid%2Csource%2Crequiressl%2Cxpc%2Ctx%2Ctxs%2Chfr%2Cplaylist_duration%2Cmanifest_duration%2Cmaudio%2Cspc%2Cvprv%2Cgo%2Crqh%2Citag%2Cplaylist_type/sig/AJfQdSswRgIhAIlr1yE85xJ5e1k2sQEPQAsoRyX_kXRyWcJU-8igQExGAiEA-PvI-ZgPrvU1ETolGEfhqC0SIG7bN7sDRbpblyL6Umg%3D/file/index.m3u8"
# https://anym3u8player.com/yt/
streams = streamlink.streams(stream_url)
print(streams) 

if "best" in streams:
    stream = streams["best"]
else:
    print("استریم 'best' در دسترس نیست.")
    stream = None

if stream:
    start_time = time.time()
    max_duration = 20 * 60 # 10 min

    with open("F:\DA\Projects\Peace_bridge\output3.mp4", "wb") as f:
        for chunk in stream.open():
            f.write(chunk)
            elapsed_time = time.time() - start_time
            if elapsed_time > max_duration:
                print("مدت زمان ضبط به پایان رسید.")
                break