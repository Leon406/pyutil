import json
import re
import time

import requests

from M3u8 import M3u8
from common import Hash

HEADER = {'Cookie': 'ko_token=d2f2693901d65e135f593bcd9fba18db;'}
# TERM_ID = 'term_5f4f0dda1a1c2_g62C3Q'
# HEADER = {'Cookie': 'dataUpJssdkCookie={"wxver":"","net":"","sid":""}; ko_token=92eb114a76a742a4060cfa1f23a86555'}
TERM_ID = 'term_5f26a080ecaab_WTVcFW'

URL = 'https://appoxpkjya89223.h5.xiaoeknow.com'
CATALOGUE_URL = URL + "/camp/get_term_catalogue"
SECTION_URL = URL + "/camp/get_task_list"
VIDEO_URL = URL + "/video/base_info"
EXAM_URL = URL + "/evaluation_wechat/exam/get_exam_info"
EXAM_JOIN_URL = URL + "/evaluation_wechat/exam/join_exam"
EXAM_REVIEW_URL = URL + "/exam/review_detail"

choices = 'ABCD'
weight = 61


class XiaoeTong:
    def __init__(self, url=URL, header=HEADER, term=TERM_ID):
        self.session = requests.session()
        self.url = url
        self.header = header
        self.termId = term
        self.appId = ''
        self.catalog = {}
        self.learn_days = {}
        pass

    def catalogue(self):
        rsp = self.session.post(CATALOGUE_URL, data={'bizData[termId]': TERM_ID}, headers=HEADER)
        print(rsp.text)
        self.catalog = json.loads(rsp.text)['data']['catalogue']
        self.appId = self.catalog[0]['app_id']

        # for course in self.catalog:
        #     print(course['title'], course['id'], course['unlock_time'])

    def section_test(self):
        for course in self.catalog:
            # print(course['title'], course['id'])
            # print(course)
            if course['order_weight'] < weight:
                continue

            self.learn_days[course['id']] = course['unlock_time']
            self.section_info(course['id'])

    def section_info(self, sec_id):
        rsp = self.session.post(SECTION_URL, data={'bizData[termId]': TERM_ID, 'bizData[nodeId]': sec_id},
                                headers=HEADER)

        tasks = json.loads(rsp.text)['data']['taskList']
        for task in tasks:
            # print(task['title'], task['id'], task['resource_type'], task['task_progress'])
            # if task['id'].startswith('v_'):
            #     self.video_info(task['id'], sec_id)
            if task['id'].startswith('ex_'):
                self.exam_info(task['id'], sec_id)
            # pass

    def course_info(self):
        pass

    def exam_info(self, id, sec_id):
        rsp = self.session.post(EXAM_URL, data={"bizData[exam_id]": id, "bizData[data_point_type]": "6"},
                                headers=HEADER)

        # print(rsp.text)
        exam = json.loads(rsp.text)['data']

        join_id = exam['user_join_id'] if 'user_join_id' in exam else None
        print(exam['exam_info']['name'], exam['can_join'],
              join_id if join_id else self.learn_days[sec_id] + "解锁")

        if join_id:
            rsp = self.session.post(EXAM_REVIEW_URL, data={"bizData[exam_id]": id, "bizData[participate_id]": join_id},
                                    headers=HEADER)
            data_ = json.loads(rsp.text)['data']
            if 'result' not in data_:
                return
            exam_answer = data_['result']
            # print(exam_answer)
            for i, item in enumerate(exam_answer):

                if 'option' not in item or item['option'] == '':
                    print(f"章节作业:" + re.sub('<[^>]+>', '', item['content']))
                    return
                print(f"第{i + 1}题:" + re.sub('<[^>]+>', '', item['content']))
                maps = {}
                for j, option in enumerate(item['option']):
                    print('\t' + choices[j] + ". " + re.sub('<[^>]+>|&\\w+;', '', option['content']))
                    maps[option['id']] = choices[j]
                    pass
                ans = []
                for answer in item['correct_answer']:
                    ans.append(maps[answer])

                print("答案: " + "".join(ans))
                print("解析: " + re.sub('<[^>]+>|&\\w+;', '', item['analysis']) + '\r\n')
        # else:
        #     rsp = self.session.post(EXAM_JOIN_URL, data={"bizData[exam_id]": id, "bizData[come_type]": "1"},
        #                             headers=HEADER)
        #     print(rsp.text)

    @staticmethod
    def decode_video_url(url):
        return Hash.b64_decode(url.replace('@', '1').replace('#', '2').replace('$', '3').replace('%', '4'))

    def video_info(self, res_id, sec_id):
        pay_info = '{"type":"2","product_id":"%s","from_multi_course":"1","resource_id":"%s","resource_type":3,"app_id":"%s"}' % (
            TERM_ID, res_id, self.appId)
        rsp = self.session.post(VIDEO_URL, data={"pay_info": pay_info},
                                headers=HEADER)
        video_info = json.loads(rsp.text)['data']['bizData']['data']
        url = XiaoeTong.decode_video_url(video_info['videoUrl'])
        print(self.learn_days[sec_id], video_info['title'], video_info['video_audio_url'],
              url)
        # XiaoeTong.download(url, self.learn_days[sec_id] + "_" + video_info['title'])

    @staticmethod
    def download(url, filename):
        M3u8(url).download(filename)


if __name__ == "__main__":
    start = time.time()  # 开始时间
    xet = XiaoeTong()
    xet.catalogue()
    xet.section_test()
    print('共耗时: %s)' % (time.time() - start))
