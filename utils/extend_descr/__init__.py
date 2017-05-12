# ！/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
import base64
from .mediainfo import show_media_info

extend_descr_raw = {
    "before": {   # Key : min_reseed_time, max_reseed_time
        "bbcode": """
        [quote]
        [*]这是一个自动发种的文件，所有信息以主标题或者文件名为准，简介信息采用本站之前相关种子信息，若发现有误请以"举报"或"留言"的形式通知工作人员审查和编辑。
        [*]欢迎下载、辅种、分流。保种{min_reseed_time}-{max_reseed_time}天。断种恕不补种。
        [*]如果发布档较大，请耐心等待校验。
        [*]有关更新说明请查看对应 Github :[url=https://github.com/Rhilip/Pt-Autoseed]Rhilip/Pt-Autoseed[/url]，申请搬运，请发Issues留言。
        [/quote]
        """,
        "html": """
        <fieldset class="autoseed">
            <legend><b>Quote:</b></legend>
            <ul>
                <li>这是一个远程发种的文件，所有信息以主标题或者文件名为准，简介信息采用本站之前剧集信息，若发现有误请以"举报"或"留言"的形式通知工作人员审查和编辑。</li>
                <li>欢迎下载、辅种、分流。保种{min_reseed_time}-{max_reseed_time}天。断种恕不补种。</li>
                <li>如果发布档较大，请耐心等待校验。</li>
                <li>请勿上传机翻字幕，如有发现请"举报"。</li>
                <li>有关更新说明请查看对应 Github : <a href="https://github.com/Rhilip/Pt-Autoseed" target="_blank">Rhilip/Pt-Autoseed</a> ，申请搬运，请发Issues留言。</li>
            </ul>
        </fieldset>
        """
    },
    "shot": {  # Key : img_url
        "bbcode": """
        [color=Red]以下是Autoseed自动完成的截图，不喜勿看 [/color]
        [img]{img_url}[/img]
        """,
        "html": """
        <fieldset class="autoseed">
            <legend><b>自动截图</b></legend>
                <ul>
                    <li><span style="color:red">以下是<a href="//github.com/Rhilip/Byrbt-Autoseed" target="_blank">Autoseed</a>自动完成的截图，不喜勿看。</span></li>
                </ul>
                <img src="{img_url}" style="max-width: 100%">
        </fieldset>
        """
    },
    "mediainfo": {  # Key : info
        "bbcode": "[quote=MediaInfo (Autoseed自动生成，仅供参考)]{info}[/quote]",
        "html": """
        <fieldset class="autoseed">
            <legend><b>MediaInfo:（自动生成，仅供参考）</b></legend>
            <div id="mediainfo">{info}</div>
        </fieldset>
        """
    },
    "clone_info": {  # Key : torrent_id
        "bbcode": "该种子信息克隆自本站种子： [url=/details.php?id={torrent_id}&hit=1]{torrent_id}[/url]",
        "html": """
        <div class="byrbt_info_clone autoseed" data-clone="{torrent_id}" data-version="Autoseed" style="display:none">
            <a href="https://github.com/Rhilip/Pt-Autoseed" target="_blank">Powered by Rhilip's Autoseed</a>
        </div>
        """
    }
}


class ExtendDescr(object):
    def __init__(self, setting):
        self._setting = setting
        self._status_before = setting.descr_before_status
        self._status_mediainfo = setting.descr_media_info_status
        self._status_screenshot = setting.descr_screenshot_status
        self._status_clone_info = setting.descr_clone_info_status

    def out(self, raw, torrent, before_torrent_id, encode="bbcode"):
        file = self._setting.trans_downloaddir + "/" + torrent.files()[0]["name"]
        before = self.build_before(encode)
        shot = self.build_shot(file=file, encode=encode)
        media_info = self.build_mediainfo(file=file, encode=encode)
        clone_info = self.build_clone_info(before_torrent_id=before_torrent_id, encode=encode)

        return """{before}{raw}{shot}{mediainfo}{clone_info}""" \
            .format(before=before, raw=raw, shot=shot, mediainfo=media_info, clone_info=clone_info)

    def build_before(self, encode, str_before=""):
        if self._status_before:
            min_time = int(self._setting.torrent_minSeedTime / 86400)
            max_time = int(self._setting.torrent_maxSeedTime / 86400)
            str_before = extend_descr_raw["before"][encode].format(min_reseed_time=min_time, max_reseed_time=max_time)
        return str_before

    def build_shot(self, file, encode, str_screenshot="") -> str:
        if self._status_screenshot:
            shot_file_name = base64.b64encode(bytes(file, "utf-8"))[:32]
            screenshot_file = "screenshot/{file}.png".format(file=shot_file_name)
            file_loc = "{web_loc}/{s_file}".format(web_loc=self._setting.web_loc, s_file=screenshot_file)
            # TODO Automatically generated Screenshot time.
            ffmpeg_sh = "ffmpeg -ss 00:10:10 -y -i {file} -vframes 1 {file_loc}".format(file=file, file_loc=file_loc)
            shot = os.system(ffmpeg_sh)
            if shot == 0:
                file_url = "{web_url}/{s_f}".format(web_url=self._setting.web_url, s_f=screenshot_file)
                logging.info("The screenshot of \"{0}\" save on: \"{1}\"".format(file, file_loc))
                str_screenshot = extend_descr_raw["shot"][encode].format(img_url=file_url)
            else:
                logging.warning("Can't get Screenshot for \"{0}\".".format(screenshot_file))
        return str_screenshot

    def build_clone_info(self, before_torrent_id, encode, str_clone_info="") -> str:
        if self._status_clone_info:
            str_clone_info = extend_descr_raw["clone_info"][encode].format(torrent_id=before_torrent_id)
        return str_clone_info

    def build_mediainfo(self, file, encode, str_media_info="") -> str:
        info = show_media_info(file=file, encode=encode)
        if self._status_mediainfo and info:
            str_media_info = extend_descr_raw["mediainfo"][encode].format(info=info)
        return str_media_info
