import csv
import requests
from lxml import html
import time
import random
import re

if __name__ == '__main__':
    #定义表头
    header = ['电影名', '年份', '上映时间', '类型', '时长', '评分', '语言', '导演', '作者', '主演', 'Slogan', '简介']
    # 创建csv文件
    with open("csv_data/tmdb.csv", "w", encoding="UTF-8", newline="") as f:
        # 创建操作的csv文件对象，并指定文件对象和表头列表
        writer = csv.DictWriter(f, fieldnames=header)
        # 写入表头
        writer.writeheader()

        # 获取数据  数字为页码
        for i in range(100):
            # 发送带参数请求
            top_rate_res = requests.request("POST", "https://www.themoviedb.org/discover/movie/items",
                                            data={"air_date.gte": "",
                                                  "air_date.lte": "",
                                                  "certification": "",
                                                  "certification_country": "CN",
                                                  "debug": "",
                                                  "first_air_date.gte": "",
                                                  "first_air_date.lte": "",
                                                  "include_adult": "false",
                                                  "include_softcore": "false",
                                                  "latest_ceremony.gte": "",
                                                  "latest_ceremony.lte": "",
                                                  "page": f"{i + 1}",
                                                  "primary_release_date.gte": "",
                                                  "primary_release_date.lte": "",
                                                  "region": "",
                                                  "release_date.gte": "",
                                                  "release_date.lte": "2026-10-06",
                                                  "show_me": "everything",
                                                  "sort_by": "vote_average.desc",
                                                  "vote_average.gte": "0",
                                                  "vote_average.lte": "10",
                                                  "vote_count.gte": "300",
                                                  "watch_region": "CN",
                                                  "with_genres": "",
                                                  "with_keywords": "",
                                                  "with_networks": "",
                                                  "with_origin_country": "",
                                                  "with_original_language": "",
                                                  "with_watch_monetization_types": "",
                                                  "with_watch_providers": "",
                                                  "with_release_type": "",
                                                  "with_runtime.gte": "0",
                                                  "with_runtime.lte": "400"})
            # 解析页面拿到每个电影的详情页面的链接
            top_rate_document = html.fromstring(top_rate_res.text)
            top_rate_href = top_rate_document.xpath("//div[@class='page_wrapper']/div/div/div/div/div/a/@href")

            # 获取每个电影的详情数据
            for href in top_rate_href:
                # 拼接每个电影的详情页的链接
                movie_url = "https://www.themoviedb.org/" + href
                print("发送请求到" + movie_url + ",获取该电影数据中")
                # 发送请求获得详情页的源代码对象
                movie_info_res = requests.request("GET", movie_url)
                movie_info_document = html.fromstring(movie_info_res.text)



                # 电影名
                movie_name = movie_info_document.xpath("//div[@class='title ott_false']/h2/a/text()")
                if movie_name:
                    movie_name = movie_name[0].strip()
                else:
                    movie_name = ""
                print("已获取电影名：" + movie_name)



                # 年份
                movie_year = movie_info_document.xpath("//div[@class='title ott_false']/h2/span/text()")
                if movie_year:
                    movie_year = movie_year[0].strip()
                    movie_year = re.search("\\d{4,}",movie_year).group()
                else:
                    movie_year = ""
                print("已获取电影年份：" + movie_year)



                # 上映时间
                movie_release = movie_info_document.xpath("//span[@class='release']/text()")
                if movie_release:
                    movie_release = movie_release[0].strip()
                    movie_release = re.search("\\d{4,}-\\d{2,}-\\d{2,}",movie_release).group()
                else:
                    movie_release = ""
                print("已获取电影上映时间：" + movie_release)



                # 类型
                movie_genre_list = movie_info_document.xpath("//span[@class='genres']/a")
                movie_genres = ""
                for movie_genre in movie_genre_list:
                    movie_genres += movie_genre.xpath("./text()")[0] + " "
                if movie_genres:
                    movie_genres = movie_genres.strip()
                else:
                    movie_genres = ""
                print("已获取电影类型：" + movie_genres)

                # 时长
                movie_runtime = movie_info_document.xpath("//span[@class='runtime']/text()")
                if movie_runtime:
                    movie_runtime = movie_runtime[0].strip()

                    # 提取小时部分
                    h = re.search(r"(\d+)\s*h", movie_runtime)
                    # 提取分钟部分
                    m = re.search(r"(\d+)\s*m", movie_runtime)

                    num = 0
                    if h:
                        num += int(h.group(1)) * 60  # group(1) 直接获取括号内的数字
                    if m:
                        num += int(m.group(1))  # group(1) 直接获取括号内的数字

                    movie_runtime = str(num)
                else:
                    movie_runtime = ""
                print("已获取电影时长：" + movie_runtime)



                # 评分
                movie_score = movie_info_document.xpath("//div[@class='user_score_chart']/@data-percent")
                if movie_score:
                    movie_score = movie_score[0].strip()
                else:
                    movie_score = ""
                print("已获取电影评分：" + movie_score)



                # 语言
                if movie_info_document.xpath("//section[@class='facts left_column']/p[3]/strong/bdi/text()")[
                    0] == "默认语言":
                    movie_language = movie_info_document.xpath("//section[@class='facts left_column']/p[3]/text()")
                    if movie_language:
                        movie_language = movie_language[0].strip()
                    else:
                        movie_language = ""
                else:
                    movie_language = movie_info_document.xpath("//section[@class='facts left_column']/p[2]/text()")
                    if movie_language:
                        movie_language = movie_language[0].strip()
                    else:
                        movie_language = ""
                print("已获取电影语言：" + movie_language)



                # 导演
                movie_director = movie_info_document.xpath("//ol[@class='people no_image']/li[1]/p/a/text()")
                if movie_director:
                    movie_director = movie_director[0].strip()
                else:
                    movie_director = ""
                print("已获取电影导演：" + movie_director)



                # 编剧
                movie_novel = movie_info_document.xpath("//ol[@class='people no_image']/li[2]/p/a/text()")
                if movie_novel:
                    movie_novel = movie_novel[0].strip()
                else:
                    movie_novel = ""
                print("已获取电影编剧：" + movie_novel)



                # 演员
                movie_actor_list = movie_info_document.xpath("//ol[@class='people scroller']/li[@class='card']")
                movie_actors_name = ""
                for movie_actor in movie_actor_list:
                    movie_actor_name = movie_actor.xpath("./p[1]/a/text()")
                    movie_actors_name += movie_actor_name[0] + " "
                if movie_actors_name:
                    movie_actors_name = movie_actors_name.strip()
                else:
                    movie_actors_name = ""
                print("已获取电影演员：" + movie_actors_name)



                # 宣传语
                movie_slogan = movie_info_document.xpath("//div[@class='header_info']/h3[@class='tagline']/text()")
                if movie_slogan:
                    movie_slogan = movie_slogan[0].strip()
                else:
                    movie_slogan = ""
                print("已获取电影宣传语：" + movie_slogan)



                # 介绍
                movie_introduction = movie_info_document.xpath("//div[@class='overview']/p/text()")
                if movie_introduction:
                    movie_introduction = movie_introduction[0].strip()
                else:
                    movie_introduction = ""
                print("已获取电影介绍：" + movie_introduction)



                body = [movie_name, movie_year, movie_release, movie_genres,
                        movie_runtime, movie_score, movie_language, movie_director,
                        movie_novel, movie_actors_name, movie_slogan, movie_introduction]

                # 写入文件
                writer.writerow(dict(zip(header, body)))
                print("已写入文件：" + movie_name)
            time.sleep(random.uniform(5, 10))












