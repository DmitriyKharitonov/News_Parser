import requests
from bs4 import BeautifulSoup
import time
from random import randrange
import json
import asyncio
import aiohttp


articles_urls_list = []

async def get_articles_urls(session, page):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }

    url=f'https://hi-tech.news/page/{page}/'


    async with session.get(url=url, headers=headers) as response:
        response_text  = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')

        articles_urls = soup.find_all('a', class_='post-title-a')

        for au in articles_urls:
            art_url = au.get('href')
            articles_urls_list.append(art_url)

            # time.sleep(randrange(2, 5))
        print(f'Обработал {page}')

result_data = []

async def get_data(session, url,current_position, all_count):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }

    current_url = url

    async with session.get(url=current_url, headers=headers) as response:

        response_text  = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')

        article_title = soup.find('div', class_='post-content').find('h1', class_='title').text.strip()
        article_date = soup.find('div', class_='post').find('div', class_='tile-views').text.strip()
        article_img = f"https://hi-tech.news{soup.find('div', class_='post-media-full').find('img').get('src')}"
        article_text = soup.find('div', class_='the-excerpt').text.strip().replace('\n', '')

        result_data.append(
            {
                'original_url': url,
                'article_title': article_title,
                'article_date': article_date,
                'article_img': article_img,
                'article_text': article_text
            }
        )
        print(f'Обработал {current_position}/{all_count}')




async def url_gather_data():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }
    url = 'https://hi-tech.news/'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        pagination_count = int(soup.find('span', class_='navigations').find_all('a')[-1].text)

        urls_tasks = []

        for page in range(1, pagination_count + 1):
            task = asyncio.create_task(get_articles_urls(session, page))
            urls_tasks.append(task)

        await asyncio.gather(*urls_tasks)


async def data_gather_data():

    async with aiohttp.ClientSession() as session:
        data_tasks = []

        with open("articles_urls_acync.txt") as file:
            urls = [line.strip() for line in file.readlines()]

        for i, url in enumerate(urls):
            task = asyncio.create_task(get_data(session, url,i,len(urls)))
            data_tasks.append(task)

        await asyncio.gather(*data_tasks)


def main():
    asyncio.get_event_loop().run_until_complete(url_gather_data())
    # asyncio.run(url_gather_data())

    with open('articles_urls_acync_11.11.txt', 'w') as file:
        for url in articles_urls_list:
            file.write(f'{url}\n')

    asyncio.get_event_loop().run_until_complete(data_gather_data())
    # asyncio.run(data_gather_data())

    with open('result.json_11.11.json', 'w', encoding = 'utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()