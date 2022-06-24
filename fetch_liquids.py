import os
import json
import asyncio
import aiohttp
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

headers = {
        'authority': 'ekb.zenmod.shop',
        'accept': '*/*',
        'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'OCSESSID=6aV5gZcs8LhRlm8AnL1EiojsWQB1okLTXjgs9FhU; _ym_d=1655744426; _ym_uid=1655744426816686386; age_confirmed=1; _ym_isad=1; _ga=GA1.2.1079771521.1655744427; _gid=GA1.2.144469565.1655744427; skip_geolocation_device=1; view=grid; city_id=8; cf_clearance=KEumwKrfIBgPeflM01NgvnlCI7Fspf7v0.BgllB6EQU-1655795176-0-150; __cf_bm=5x51S6IIz1Y27umP8S3YFC08X5zzF_NHVIrP7ufkr_w-1655795180-0-AQ7fv1qlqbm8N4gGcuPOu7waKu2DyKHUa4QU9ruW5KNAD/wg7rvmD+jZCQTgZ/0bdd031c4vUPhUI7vkNPAjqeeis1r+2vGB05VhsYD2Lubam2c6kQN6VDABeJe6MZ1Ujg==',
        'origin': 'https://ekb.zenmod.shop',
        'referer': 'https://ekb.zenmod.shop/ec/pod/?sort=p.price&order=ASC&page=4',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41',
        'x-requested-with': 'XMLHttpRequest',
    }
cookies = {
    'OCSESSID': '6aV5gZcs8LhRlm8AnL1EiojsWQB1okLTXjgs9FhU',
    '_ym_d': '1655744426',
    '_ym_uid': '1655744426816686386',
    'age_confirmed': '1',
    '_ym_isad': '1',
    '_ga': 'GA1.2.1079771521.1655744427',
    '_gid': 'GA1.2.144469565.1655744427',
    'skip_geolocation_device': '1',
    'view': 'grid',
    'city_id': '8',
    'cf_clearance': 'KEumwKrfIBgPeflM01NgvnlCI7Fspf7v0.BgllB6EQU-1655795176-0-150',
    '__cf_bm': '5x51S6IIz1Y27umP8S3YFC08X5zzF_NHVIrP7ufkr_w-1655795180-0-AQ7fv1qlqbm8N4gGcuPOu7waKu2DyKHUa4QU9ruW5KNAD/wg7rvmD+jZCQTgZ/0bdd031c4vUPhUI7vkNPAjqeeis1r+2vGB05VhsYD2Lubam2c6kQN6VDABeJe6MZ1Ujg==',
}

errors = []
liquids = {}
ua = UserAgent()
url = 'https://ekb.zenmod.shop/index.php?route=product/product/getList'


class ProductSpec(BaseModel):
    name: str
    values: list

class Products(BaseModel):
    product_id: int
    image: str
    name: str
    short_description: str
    price: str
    href: str
    product_spec: list[ProductSpec]

class Liquids(BaseModel):
    count: int
    products: list[Products]


async def get_page_data(session, page):
    data = {
        'sort': 'p.price',
        'stock': 'in_stock',
        'category_id': '954',
        'canonical': '',
        'route': 'product/category',
        'page': page,
        'path': '64_954',
    }
    
    async with session.post(url=url, headers=headers, cookies=cookies, data=data) as response:
        response_json = await response.json()
        data = json.dumps(response_json, indent=2)
        items = Liquids.parse_raw(data)

    for product in items.products:

        liquids[product.product_id] = {
            'link': product.href,
            'image': product.image,
            'title': product.name,
            'description': f'{product.short_description if product.short_description else "Отсутствует"}',
            'taste': '; '.join(product.product_spec[0].values),
            'is_salt': ''.join(product.product_spec[1].values),
            'price': product.price,
            'destiny': 'liquid'
        }


async def gather_data():
    async with aiohttp.ClientSession() as session:
        response = await session.get('https://ekb.zenmod.shop/liquid/all_liquid/?sort=p.price&order=ASC&stock=in_stock', headers=headers, cookies=cookies)
        soup = BeautifulSoup(await response.text(), 'lxml')
        try:
            pages = int(soup.find('div', class_='pagination__list').find_all('a')[-1].text)
        except AttributeError:
            pages = 1

        tasks = []
        
        for page in range(1, pages + 1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)


def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(gather_data())
    
    if not os.path.isfile(f'jsons/liquids.json'):
        with open('jsons/liquids.json', 'w', encoding='utf8') as file:
            json.dump(liquids, file, indent=4, ensure_ascii=False)
    else:
        with open('jsons/liquids.json', 'r', encoding='utf8') as file:
            old_liquids = json.load(file)
        try:
            for item in liquids:
                if liquids[item] != old_liquids[str(item)]:
                    errors.append(item)
        except KeyError:
            print(f'Лота {item} нет в базе')
            print(f'{liquids[item].get("link")}')
            os.remove('jsons/liquids.json')
            main()
        try:
            for item in old_liquids:
                if old_liquids[item] != liquids[int(item)]:
                    errors.append(item)
        except KeyError:
            print(f'Лота {item} нет на сайте')
            print(f'{old_liquids[item].get("link")}')
            os.remove('jsons/liquids.json')
            main()

        if errors:
            print(f'Расхождение в продуктах: {errors}')
        else:
            pass
    
    print(errors)

if __name__ == '__main__':
    main()