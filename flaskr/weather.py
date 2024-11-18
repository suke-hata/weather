import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_image_link(url, alt_text):
    try:
        # ページを取得
        response = requests.get(url)
        response.raise_for_status()

        # BeautifulSoupを使ってHTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')

        # 指定されたalt属性を持つ画像のsrc属性を取得
        img_tag = soup.find('img', alt=alt_text)
        if img_tag:
            img_url = img_tag['src']
            full_img_url = urljoin(url, img_url)
            return full_img_url
        else:
            return "画像が見つかりませんでした。"

    except requests.exceptions.RequestException as e:
        return f"リクエストエラーが発生しました: {e}"

