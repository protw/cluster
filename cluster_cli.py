import webbrowser

## Власні методи
from cluster_util import load_resourses, cluster_main

in_pars, _, _, _ = load_resourses()

pin = {}
pin['coord_format']  = '46.7373, 32.8128'
pin['lat_lon_order'] = 'LatLon'
pin['epsilon']       = 40
pin['min_samples']   = 2
pin['perctl']        = 75
pin['zoom_start']    = 17
pin['text']          = \
    '47.37615, 35.548962; 47.376573, 35.548576; 47.376334, 35.54824; ' + \
    '47.376752, 35.548695; 47.376577, 35.549218; 47.376281, 35.549977; ' + \
    '47.376106, 35.549702; 47.376092, 35.548638; 47.374925, 35.548208;'

html_file = 'cluster_cli.html'

## Calculate map, points grouped in clusters and group stats
m, grouped, group_stats = cluster_main(in_pars, pin)

m.save(html_file)
webbrowser.open(html_file)

def print_res():
    print('## ПАРАМЕТРИ')
    msg_pars = [
        f"Формат координат: `{pin['coord_format']}`",
        f"Порядок координат: `{pin['lat_lon_order']}`",
        f"Радіус сусідства: `{pin['epsilon']}` м",
        f"Мін. кількість точок у кластері: `{pin['min_samples']}`" ]
    print(', '.join(msg_pars[:2]))
    print(', '.join(msg_pars[2:]))
    print('## РЕЗУЛЬТАТ')
    msg_stats = [
        f"Всього виявлено точок: `{group_stats['n_pnts']}`",
        f"кластерів: `{group_stats['n_clust']}`",
        f"точок поза кластерами: `{group_stats['n_outlier']}`" ]
    print(', '.join(msg_stats))

print_res()