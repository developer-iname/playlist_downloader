import youtube_dl
import sys
import math

class ResourceNotFoundError(Exception):
    pass


class NoFilesizeError(Exception):
    pass

class YoutubeDlHandler:
   # init method
    def __init__(self, url, ydl_options = {}):
        self._ydlobject = youtube_dl.YoutubeDL(ydl_options)
        try:
            playlistinformation = self._ydlobject.extract_info(url, process=False)
        except youtube_dl.utils.DownloadError:
            raise ResourceNotFoundError
        if 'entries' in playlistinformation:
            self._videos = list(playlistinformation['entries'])
        else:
            self._videos = [playlistinformation]
        self._number_of_videos = len(self._videos)
        

    def _get_size(self, videoentryinformation):
        try:
            video = self._ydlobject.process_ie_result(videoentryinformation, download=False)
        except youtube_dl.utils.DownloadError:
            raise NoFilesizeError
        try:
            if 'requested_formats' in video:
                for videoformat in video['requested_formats']:
                    if videoformat['filesize'] != None:
                        size = int(videoformat['filesize'])
                        print(size)
            else:
                size = video['filesize']
        except (TypeError, KeyError):
            raise NoFilesizeError
        return size

    def _readable_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def _get_totalsize(self):
        totalsize = 0
        for videoentry in self._videos:
            try:
                size = self._get_size(videoentry)
            except NoFilesizeError:
                print(f"Filesize of {videoentry['title']} is unavailable.")
            else:
                print(f"{videoentry['title']}: {self._readable_size(size)}")
                totalsize += size
        return self._readable_size(totalsize)

    def _download(self, url):
        self._ydlobject.download([url])
        return

def main(url, mode="download"):
    ydlhandle = YoutubeDlHandler(url,{"quiet": False, 'format': 'bestaudio', 'playliststart': 1,'outtmpl': './downloads/%(title)s.mp3'})
    if mode == "check":
        print('Total size of all videos with reported filesize: ' + ydlhandle._get_totalsize())
        print('Total number of videos: %s' % ydlhandle._number_of_videos)
    if mode == 'download':
        ydlhandle._download(url)

if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except IndexError:
        sys.exit('Please supply an url.')
    except ResourceNotFoundError:
        sys.exit('Resource not found.')