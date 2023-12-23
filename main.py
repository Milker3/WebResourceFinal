from flask import Flask, render_template, request, url_for
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import pandas as pd
import requests

url = 'https://www.worldometers.info/world-population/population-by-country/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html',
    'Upgrade-Insecure-Requests': '1'
}
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")

table = soup.find('tbody').findAll('tr')

df = pd.DataFrame(columns=[i.text.split()[0].lower() for i in soup.find("thead").findAll('th')[1:]])

for index, row in enumerate(table):
    row = row.findAll('td')
    df.loc[index] = [i.text for i in row[1:]]

df['population'] = df['population'].str.replace(',', '').astype(int)
country_list = list(df['country'])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', country_list = country_list)

@app.route('/description')
def description():

    site_description = "This site gives information about population of selected country"
    return render_template('description.html', description=site_description)

@app.route('/graph', methods=['POST'])
def graph():

    data = request.form['data']

    table = df[df['country'] == data]

    k = int(table.index[0])
    graph = df[k:k + 5][['country', 'population']]
    plt = graph.plot.bar(x='country').get_figure()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('graph.html', plot_url=plot_url, country=data)

if __name__ == '__main__':
    app.run(debug=True)

