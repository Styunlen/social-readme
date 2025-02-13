import datetime
import re

import feedparser

BLOG_START_COMMENT = '<!-- START_SECTION:blog -->'
BLOG_END_COMMENT = '<!-- END_SECTION:blog -->'

DOUBAN_START_COMMENT = '<!-- START_SECTION:douban -->'
DOUBAN_END_COMMENT = '<!-- END_SECTION:douban -->'

DOUBAN_RATING = {
    '<p>推荐: 很差</p>': '🌟☆☆☆☆ 很差',
    '<p>推荐: 较差</p>': '🌟🌟☆☆☆ 较差',
    '<p>推荐: 还行</p>': '🌟🌟🌟☆☆ 还行',
    '<p>推荐: 推荐</p>': '🌟🌟🌟🌟☆ 推荐',
    '<p>推荐: 力荐</p>': '🌟🌟🌟🌟🌟 力荐'
}


def generate_blog(rss_link, limit, readme) -> str:
    """Generate blog"""
    entries = feedparser.parse(rss_link)["entries"]
    arr = [
        {
            # "title": (entry["title"][0:20] + "...") if(len(entry["title"]) > 22) else entry["title"],
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": format_time_blog(entry["published"]),
        }
        for entry in entries[:limit]
    ]

    content = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in arr]
    )

    return generate_new_readme(BLOG_START_COMMENT, BLOG_END_COMMENT, content, readme)


def generate_douban(username, limit, readme) -> str:
    """Generate douban"""
    entries = feedparser.parse("https://www.douban.com/feed/people/" + username + "/interests")["entries"]
    arr = [
        {
            "title": item["title"],
            "url": item["link"].split("#")[0],
            "published": format_time(item["published"]),
            "rating_star": generate_rating_star(item["description"])
        }
        for item in entries[:limit]
    ]

    content = "\n".join(
        ["* <a href='{url}' target='_blank'>{title}</a> {rating_star}- {published}".format(**item) for item in arr]
    )

    return generate_new_readme(DOUBAN_START_COMMENT, DOUBAN_END_COMMENT, content, readme)


def generate_new_readme(start_comment: str, end_comment: str, content: str, readme: str) -> str:
    """Generate a new Readme.md"""
    pattern = f"{start_comment}[\\s\\S]+{end_comment}"
    repl = f"{start_comment}\n{content}\n{end_comment}"
    if re.search(pattern, readme) is None:
        print(f"can not find section in your readme, please check it, it should be {start_comment} and {end_comment}")

    return re.sub(pattern, repl, readme)


def format_time(timestamp) -> datetime:
    gmt_format = '%a, %d %b %Y %H:%M:%S GMT'
    date_str = datetime.datetime.strptime(timestamp, gmt_format) + datetime.timedelta(hours=8)
    return date_str.date()

def format_time_blog(timestamp) -> datetime:
    gmt_format = '%a, %d %b %Y %H:%M:%S +0000'
    date_str = datetime.datetime.strptime(timestamp, gmt_format) + datetime.timedelta(hours=8)
    return date_str.strftime("%Y-%m-%d %H:%M")


def generate_rating_star(desc) -> str:
    pattern = re.compile(r'<p>推荐: [\s\S]+</p>')
    matches = re.findall(pattern, desc)
    if len(matches) > 0:
        return DOUBAN_RATING[matches[0]]
    return ''
