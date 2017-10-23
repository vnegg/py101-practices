"""
Chương trình tải các bài viết từ tuoitre.vn
"""
from urllib.parse import urljoin
import os
import json
import codecs
import requests
import bs4
import arrow

BASE_URL = 'http://tuoitre.vn/'
SOURCE_URL = 'http://tuoitre.vn/tin-moi-nhat.htm'


def get_article_content(url):
    """
    Lấy nội dung bài viết từ `url`
    """
    data = {}
    r = requests.get(url)
    if r.ok:
        s = bs4.BeautifulSoup(r.content, 'lxml')

        title = s.select_one('h1.title-2')
        data['title'] = title.text.strip() if title else ''

        sub_title = s.select_one('h2.txt-head')
        data['sub_title'] = sub_title.text.strip() if sub_title else ''

        content = s.select_one('.left-side .fck')
        data['content'] = content.prettify() if content else ''

        pub_date = s.select_one('.tool-bar > span.date')
        # 22/10/2017 16:03 GMT+7
        pub_date = pub_date.text.replace(' GMT+7', '') if pub_date else ''
        pub_date = arrow.get(pub_date, 'DD/MM/YYYY HH:mm').replace(tzinfo='Asia/Ho_Chi_Minh')
        data['pub_date'] = pub_date.format(locale='vi')
    return data


def main():
    r = requests.get(SOURCE_URL)
    if r.ok:
        s = bs4.BeautifulSoup(r.content, 'lxml')
        links = s.select('.list-news-content > .block-left.clearfix')
        for a in links:
            id_ = a.attrs['data-newsid']
            link = a.select_one('h3 > a')

            article = get_article_content(urljoin(BASE_URL, link.attrs['href']))

            # tạo thư mục
            dir_name = arrow.get(article['pub_date']).format('YYYY-MM')
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)
            
            # tạo tên tệp
            file_name = arrow.get(article['pub_date']).format('YYYY-MM-DD')
            file_name = file_name + '-' + id_ + '.json'
            file_name = os.path.join(dir_name, file_name)

            f = codecs.open(file_name, encoding='utf-8', mode='w')
            json.dump(article, f, ensure_ascii=False, indent=2)

    else:
        print('Không truy cập được.')


# if __name__ == '__main__':
#     main()
    # print(get_article_content('http://tuoitre.vn/kien-nghi-rut-khang-nghi-vu-chi-em-tranh-chap-80m2-dat-o-vung-tau-20171022134608379.htm'))
