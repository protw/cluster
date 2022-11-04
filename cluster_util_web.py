# -*- coding: utf-8 -*-

import re
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import folium
from pygeodesy.sphericalNvector import meanOf, LatLon
import seaborn as sns

'''Розібрати вхідний текст - витягнути пари гео координат з тексту і
   створити список пар координат типу float.
   Аргументи:
     'text' - вхідний текст;
     'format_id' 
         0 - десяткова крапка, кома - "46.737364, 32.812807" (default); 
         1 - десяткова кома, слеш - "46,737364 / 32,812807";
         2 - десяткова кома, пробіл - "46,737364 32,812807";
     'lat_lon_order' - 'LatLon' (default) або 'LonLat'.
   Повертає список пар координат типу float, порядок коорд [Lat,Lon].'''

def parse_text(in_pars, pin):
    def get_coord_format_id(in_pars, coord_format):
        coord_format_options = in_pars['coord_format']['options']
        coord_format_id = coord_format_options.index(coord_format)
        return coord_format_id
    format_id = get_coord_format_id(in_pars, pin.coord_format)
    text = pin.text
    lat_lon_order = pin.lat_lon_order
    format_masks = [
        r'(\d{1,3}\.\d+)\s*\,\s*(\d{1,3}\.\d+)', # 46.737364, 32.812807
        r'(\d{1,3}\,\d+)\s*/\s*(\d{1,3}\,\d+)',  # 46,737364 / 32,812807
        r'(\d{1,3}\.\d+)\s+(\d{1,3}\.\d+)'       # 46.7373 32.8128
    ]
    mask = format_masks[format_id]
    # Повертає список пар (кортежей) координат типу str
    st = re.findall(mask, text)
    # Міняє кому на крапку в кожному елементі
    if format_id == 1:
        sl = [[c.replace(',','.') for c in p] for p in st]
    else:
        sl = [[c for c in p] for p in st]
    # Конвертує елементи str у float, встановлює порядок коорд [Lat,Lon]
    if lat_lon_order == 'LatLon':
        fl = [[float(s[0]), float(s[1])] for s in sl]
    elif lat_lon_order == 'LonLat':
        fl = [[float(s[1]), float(s[0])] for s in sl]

    df = pd.DataFrame(fl, columns=['Lat','Lon'])
    df['descr'] = [str(i) for i in list(df.index)]

    return df

def clustering(pnts, epsilon=0.05, min_samples=3):
    # http://qingkaikong.blogspot.com/2016/08/clustering-with-dbscan.html
    kms_per_radian = 6371.0088
    epsilon = epsilon / kms_per_radian

    # Run the DBSCAN from sklearn
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree',
                metric='haversine').fit(np.radians(pnts[['Lat','Lon']]))

    # get the cluster
    # cluster_labels = -1 means outliers
    n_clusters = len(set(db.labels_)) # including outliers 
    pnts['cluster_label'] = db.labels_

    return pnts, n_clusters

def center(pnts, perctl=75):
    ## Знайти центроїд групи точок 'pnts'
    n_pnts = len(pnts)
    if n_pnts == 1:
        return pnts, None
    pnts_LL = [LatLon(p['Lat'],p['Lon']) for _, p in pnts.iterrows()]
    cntr = meanOf(pnts_LL)
    
    ## Знайти відстань від центру групи до кожної точки групи
    dist_l = [cntr.distanceTo(p) for p in pnts_LL]

    cntr = [float(cntr.lat), float(cntr.lon)]

    # Визначити розмір
    dist_a = np.array(dist_l)
    #dist_mean = np.mean(dist_a)
    sz_pnts = 2 * np.percentile(dist_a, perctl)

    return cntr, sz_pnts

def html2popup(html):
    iframe = folium.IFrame(html=html, width=200, height=130)
    popup = folium.Popup(iframe, max_width=350)
    return popup

def add_marker(f_groups, lat, lon, html, tooltip, color):
    # Add markers to last FeatureGroup
    popup = html2popup(html)
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        popup=popup,
        tooltip=tooltip,
        fill_color=color,
        stroke = False, 
        fill_opacity = 1,
    ).add_to(f_groups[-1])

def build_groups_on_map(pnts, m, perctl):
    ## Побудувати групи точок на мапі з контролем шарів
    ## https://www.riannek.de/2022/folium-featuregroup-categorial-data/

    f_groups = []

    grouped = pnts.groupby('cluster_label')
    pal = sns.color_palette("husl", len(grouped)).as_hex() 

    # n_clust - кількість кластерів без аутлаєрів, 
    # n_outlier - кількість точок-аутлаєрів
    group_stats = {'n_clust': 0, 'n_outlier': 0, 'n_pnts': len(pnts)}

    for group_name, group_data in grouped:
        group_len = len(group_data)
        if group_name==-1:
            group_decr = 'Поза кластерами'
            group_stats['n_outlier'] = group_len
        else:
            group_decr = f'Кластер {group_name}'
            group_stats['n_clust'] += 1
        f_groups.append(folium.FeatureGroup(str(group_decr)))
        color = pal.pop()
        
        # Формуємо для кластеру групу маркерів в окремій FeatureGroup
        
        for i in range(0,group_len):
            lat = group_data.iloc[i]['Lat']
            lon = group_data.iloc[i]['Lon']
            id = group_data.index[i]
            tooltip = f'Класт: {group_name} / Ід: {id}'
            descr = group_data.iloc[i]['descr']
            # html for popup of markers
            html = f"""
                <h4>Окрема точка {i+1}</h4>
                <small>
                <p><b>Опис:</b> {descr}<br/>
                <b>Кластер:</b> {group_name}<br/>
                <b>Ш,Д:</b> {lat:.6f}, {lon:.6f}</p>
                </small>
                """
            add_marker(f_groups, lat, lon, html, tooltip, color)
    
        # Формуємо для кластеру маркер його центральної точки і 
        # додаємо до групи FeatureGroup
        n_pnts_clust = len(group_data)
        cntr_group, sz = center(group_data[['Lat','Lon']])

        color_c = 'red'
        lat = cntr_group[0]
        lon = cntr_group[1]
        tooltip = f'Класт: {group_name} / Кільк: {n_pnts_clust}'
        html = f"""
            <h4>{group_decr}</h4>
            <small>
            <p><b>N точок:</b> {n_pnts_clust}<br/>
            <b>Розмір:</b> {sz:.1f}<br/>
            <b>Центр кластеру</b><br/>
            <b>Ш,Д:</b> {lat:.6f}, {lon:.6f}</p>
            </small>
            """
        add_marker(f_groups, lat, lon, html, tooltip, color_c)

        # побудувати коло за розміром персентиля
        popup = html2popup(html)
        folium.Circle(cntr_group, 
            radius=sz/2.,
            popup=popup,
            tooltip=tooltip,
            color=color,
            dash_array='6').add_to(f_groups[-1])

        # Add last featureGroup to Map
        f_groups[-1].add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    return m, grouped, group_stats