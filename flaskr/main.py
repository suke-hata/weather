
import math
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import requests
import sqlite3
from flaskr import jr as jr
import os

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # ここでsecret_keyを設定

# Blueprintの作成
main = Blueprint('main', __name__)

# 都道府県とその緯度・経度の辞書
prefs = [   
            ['北海道', 43.03, 141.21],
            ['青森県', 40.49, 140.44],
            ['岩手県', 39.42, 141.09],
            ['宮城県', 38.16, 140.52],
            ['秋田県', 39.43, 140.06],
            ['山形県', 38.15, 140.20],
            ['福島県', 37.45, 140.28],
            ['茨城県', 36.22, 140.28],
            ['栃木県', 36.33, 139.53],
            ['群馬県', 36.23, 139.03],
            ['埼玉県', 35.51, 139.38],
            ['千葉県', 35.36, 140.06],
            ['東京都', 35.41, 139.45],
            ['神奈川県', 35.26, 139.38],
            ['新潟県', 37.55, 139.02],
            ['富山県', 36.41, 137.13],
            ['石川県', 36.33, 136.39],
            ['福井県', 36.03, 136.13],
            ['山梨県', 35.39, 138.34],
            ['長野県', 36.39, 138.11],
            ['岐阜県', 35.25, 136.45],
            ['静岡県', 34.58, 138.23],
            ['愛知県', 35.11, 136.54],
            ['三重県', 34.43, 136.30],
            ['滋賀県', 35.00, 135.52],
            ['京都府', 35.00, 135.46],
            ['大阪府', 34.41, 135.29],
            ['兵庫県', 34.41, 135.11],
            ['奈良県', 34.41, 135.48],
            ['和歌山県', 34.14, 135.10],
            ['鳥取県', 35.29, 134.13],
            ['島根県', 35.27, 133.04],
            ['岡山県', 34.39, 133.54],
            ['広島県', 34.23, 132.27],
            ['山口県', 34.11, 131.27],
            ['徳島県', 34.03, 134.32],
            ['香川県', 34.20, 134.02],
            ['愛媛県', 33.50, 132.44],
            ['高知県', 33.33, 133.31],
            ['福岡県', 33.35, 130.23],
            ['佐賀県', 33.16, 130.16],
            ['長崎県', 32.45, 129.52],
            ['熊本県', 32.48, 130.42],
            ['大分県', 33.14, 131.37],
            ['宮崎県', 31.56, 131.25],
            ['鹿児島県', 31.36, 130.33],
            ['沖縄県', 26.13, 127.41]
        ]

# 都道府県ナンバーを取得
CITIES = {
    '北海道': '016010',  '青森県': '020010', '岩手県': '030010',
    '宮城県': '040010',  '秋田県': '050010', '山形県': '060010', '福島県': '070010',
    '茨城県': '080010', '栃木県': '090010', '群馬県': '100010',
     '埼玉県': '110010', '千葉県': '120010', '東京都': '130010',
    '神奈川県': '140010', '新潟県': '150010', '富山県': '160010',
    '石川県': '170010',
    '福井県': '180010', '山梨県': '190010', '長野県': '200010',
    '岐阜県': '210010', '静岡県': '220010', '愛知県': '230010','三重県': '240010',
    '滋賀県': '250010', '京都府': '260010', '大阪府': '270000',
    '兵庫県': '280010', '奈良県': '280010', '和歌山県': '290010', '鳥取県': '310010',
    '島根県': '320010', '岡山県': '330010', '広島県': '340010', '山口県': '350020',
    '徳島県': '360010', '香川県': '370000', '愛媛県': '380010', 
    '高知県': '390010', '福岡県': '400010', '佐賀県': '410010', '長崎県': '420010', '熊本県': '430010',
    '大分県': '440010', '宮崎県': '450010', '鹿児島県': '460010', '沖縄県': '471010'
}

# データベースのパス
DATABASE = r'users.db'
# グローバル変数を定義
weather_data = None

login = False

# データベースに接続する関数
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # 結果を辞書形式で取得
    return conn

# テーブルを作成する関数
def create_user_table():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                place TEXT NOT NULL
            )
        ''')
        conn.commit()

# サーバー起動時にテーブルを作成
create_user_table()

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        place = request.form['place']
        with get_db() as conn:
            try:
                conn.execute('INSERT INTO users (username, password,place) VALUES (?, ?, ?)', (username, password, place))
                conn.commit()
                return redirect(url_for('main.login'))
            except sqlite3.IntegrityError:
                return "Username already exists. Please choose a different one."
    
    return render_template('register.html', cities=CITIES)

# 位置情報を取得して天気を自動出力
@main.route('/', methods=['GET'])
def index():
    image_link,jisyo_texts= index_train()
    global weather_data
    error = None
    login_status = session.get('logged_in', False)
    username = session.get('username', 'ゲスト')

    if weather_data is None:
        # ページが再読み込みされるたびに位置情報を取得
        latitude, longitude = get_location()
        if latitude is not None and longitude is not None:
            try:
                prefecture_name = find_nearest_prefecture(latitude, longitude)
                if prefecture_name:
                    city_code = CITIES.get(prefecture_name)
                    if city_code:
                        weather_data = get_weather(city_code)
                        if not weather_data:
                            error = "天気データが見つかりませんでした。"
                    else:
                        error = "都道府県が辞書に存在しません。"
                else:
                    error = "近くの都道府県が見つかりませんでした。"
            except Exception as e:
                error = f"エラーが発生しました: {str(e)}"
        else:
            error = "位置情報が取得できませんでした。"
    print(weather_data)
    print(login)
    return render_template('index.html', weather=weather_data, cities=CITIES, error=error,image_link=image_link, jisyo_texts=jisyo_texts, login=login_status, username=username)
    

# POSTリクエストを処理して、選択した都市の天気情報を取得
@main.route('/', methods=['POST'])
def handle_request():
    image_link,jisyo_texts= index_train()
    print('aaa!')
    if request.method == 'POST':
        print('ccc')
        data = request.form  # request.json ではなく request.form を使用
        if data is None:
            print('ddd')
            return {"error": "リクエストボディが空です。"}, 400
        city_code = data.get('city')
        if city_code is None:
            print('ddd')
            return {"error": "都市が指定されていません。"}, 400
        
        # ここで都市コードを使って天気を取得
        global weather_data
        weather_data = get_weather(city_code)
        print('hhh!')
        if weather_data is None:
            return {"error": "天気データが見つかりませんでした。"}, 404
        
        # POSTリクエストの場合のレスポンスを返す
        print(weather_data)
        print('bbb!')
        return render_template('index.html', weather=weather_data, cities=CITIES,image_link=image_link, jisyo_texts=jisyo_texts)


@main.route('/login', methods=['GET', 'POST'])
def login():
    global login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            if user:
                session['username'] = user['username']
                session['place'] = user['place']  # place情報をセッションに保存
                session['logged_in'] = True
                return redirect(url_for('main.dashboard'))
            else:
                return "Invalid credentials. Please try again."
    
    return render_template('login.html')

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    if 'username' in session and 'place' in session:
        place = session['place']
        city_code = CITIES.get(place)
        global weather_data
        global error
        weather_data = None
        if city_code:
            weather_data = get_weather(city_code)
            print(weather_data)
        if weather_data:
            # render_template('index.html', username=session['username'], weather=weather_data, cities=CITIES)
            return redirect(url_for('main.index'))
        else:
            # return render_template('index.html', username=session['username'], error="天気データが見つかりませんでした。", cities=CITIES)
            error="天気データが見つかりませんでした。"
            return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.login'))

@main.route('/logout')
def logout():
    session.pop('username', None)
    session['logged_in'] = False
    return redirect(url_for('main.index'))


def index_train():
    url = "https://trafficinfo.westjr.co.jp/kinki.html"
    alt_text = "京阪神地区の路線図"
    image_link = jr.get_image_link(url, alt_text)
    gaiyo_texts = jr.get_gaiyo_texts(url)
    jisyo_texts = jr.get_jisyo_texts(url)
    print(f"画像のURL: {image_link}")
    print(f"gaiyoクラスのテキスト: {gaiyo_texts}")
    print(f"jisyoクラスのテキスト: {jisyo_texts}")
    return image_link, jisyo_texts


def get_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        
        # 緯度と経度を取得
        loc = data.get('loc', '0,0').split(',')
        latitude = float(loc[0])
        longitude = float(loc[1])
        
        return latitude, longitude
    except Exception as e:
        print(f"位置情報の取得に失敗しました: {e}")
        return None, None


def find_nearest_prefecture(lat, lon):
    nearest_prefecture = None
    shortest_distance = float('inf')

    for pref in prefs:
        name = pref[0]  # 都道府県名はリストの最初の要素
        pref_lat = pref[1]  # 緯度はリストの2番目の要素
        pref_lon = pref[2]  # 経度はリストの3番目の要素
        
        distance = math.sqrt((lat - pref_lat) ** 2 + (lon - pref_lon) ** 2)
        
        if distance < shortest_distance:
            shortest_distance = distance
            nearest_prefecture = name

    return nearest_prefecture

def get_weather(city_code):
    url = f'https://weather.tsukumijima.net/api/forecast/city/{city_code}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'forecasts' in data:
            forecasts = data['forecasts']
            weather_info = {
                'title': data['title'],
                'publishing_office': data['publishingOffice'],
                'description': data['description']['text'],
                'forecasts': []
            }
            for forecast in forecasts:
                weather_detail = {
                    'date': forecast['date'],
                    'date_label': forecast['dateLabel'],
                    'telop': forecast['telop'],
                    'temperature_min': forecast.get('temperature', {}).get('min', {}).get('celsius'),
                    'temperature_max': forecast.get('temperature', {}).get('max', {}).get('celsius'),
                    'image_url': forecast['image']['url'],
                    'rain_probability': forecast['chanceOfRain']
                }
                weather_info['forecasts'].append(weather_detail)
            return weather_info
    return None

# BlueprintをFlaskアプリに登録
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)