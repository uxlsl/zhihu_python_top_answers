# -*- coding: utf-8 -*-
"""
主要是查询在知乎python话题上,用户回答.从而统计出python话题活跃的用户.
"""
from collections import defaultdict
import itertools
import requests
from bs4 import BeautifulSoup
from jinja2 import Template


def main():
    # 获取pythono精华问题的链接
    URL = 'https://www.zhihu.com/topic/19552832/top-answers'
    question_hrefs = []
    for i in itertools.count(1):
        params = {'page': i}
        r = requests.get(URL, params=params, verify=False)
        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.content, 'lxml')
        for j in soup.find_all(class_='feed-item feed-item-hook folding'):
            question = j.find(class_='question_link')
            question_hrefs.append(question.get('href'))

    print(len(question_hrefs))

    # 统计回答者的数据
    # 返回字典 {key:val} key 是用户名,val 字典, aria, count
    BASE_URL = 'https://www.zhihu.com'
    answer_user_info = defaultdict(lambda: dict(aria=0,
                                                count=0,
                                                home='',
                                                answer_links=[]))
    for href in question_hrefs:
        question_link = BASE_URL + href
        r = requests.get(question_link, verify=False)
        soup = BeautifulSoup(r.content, 'lxml')
        title = soup.title.get_text().strip()
        for user in soup.find_all('div', {'class': 'zm-item-answer'}):
            vote = int(user.find(
                'div', {'class': 'zm-item-vote-info'})
                .get('data-votecount')
                .strip())
            author_link = user.find('a', class_='author-link')
            if author_link is None:
                break
            name = author_link.get_text()
            href = author_link.get('href')
            answer_user_info[name]['aria'] += vote
            answer_user_info[name]['count'] += 1
            answer_user_info[name]['home'] = BASE_URL + href
            answer_user_info[name]['answer_links'].append(
                (title, question_link))

    # 排序
    result = sorted(answer_user_info.iteritems(),
                    key=lambda x: (x[1]['aria'], x[1]['count']), reverse=True)

    # 打印
    template = Template(u"""
# 知乎python精华 回答者信息
{% for item in users %}
## [ {{ item[0] }} ]({{ item[1]['home']}})
+ 声望 {{ item[1]['aria']}}
+ 回答数 {{ item[1]['count']}}

回答问题
{% for title,link in item[1]['answer_links'] %}
[{{ title }}]({{ link }})
{% endfor %}
{% endfor %}
    """)
    print(template.render(users=result).encode('utf-8'))

if __name__ == '__main__':
    main()
