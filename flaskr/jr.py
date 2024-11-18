import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_image_link(url, alt_text):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', alt=alt_text)
        if img_tag:
            img_url = img_tag['src']
            full_img_url = urljoin(url, img_url)
            return full_img_url
        else:
            print("画像が見つかりませんでした。")
            return None

    except requests.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def get_jisyo_texts(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        jisyo_elements = soup.find_all(class_='jisyo')

        # jisyoクラスの要素数をカウント
        jisyo_count = len(jisyo_elements)
        print(f"jisyoクラスの要素数: {jisyo_count}")

        # 「京阪神地区」を含むテキストをフィルタリング
        jisyo_texts = []
        for element in jisyo_elements:
            text = element.get_text(strip=True)
            if '京阪神地区' in text:
                jisyo_texts.append(text)

        return jisyo_texts

    except requests.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None


def get_gaiyo_texts(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        gaiyo_elements = soup.find_all(class_='gaiyo')

        # jisyoクラスの要素数をカウント
        gaiyo_count = len(gaiyo_elements)
        print(f"gaiyoクラスの要素数: {gaiyo_count}")

        # 「京阪神地区」を含むテキストをフィルタリング
        gaiyo_texts = []
        for element in gaiyo_elements:
            text = element.get_text(strip=True)
            if '京阪神地区' in text:
                gaiyo_texts.append(text)

        return gaiyo_texts

    except requests.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None