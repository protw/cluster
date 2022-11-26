# -*- coding: utf-8 -*-

import folium
from pywebio.output   import put_text, put_markdown, put_html, \
                             put_button, use_scope, put_tabs, \
                             put_scope, put_row, put_table, toast, \
                             put_image
from pywebio.pin      import put_radio, put_slider, put_textarea, pin
from pywebio          import config
#from pywebio          import start_server
from pywebio.platform.flask import start_server

## Власні методи
from cluster_util     import load_resourses, cluster_main, center

in_pars, cluster_help_md, example_text, logo_img = load_resourses()

'''Run "cluster_main" and display resulting map and text report into two 
   scopes "map" and "text" every time when button "РАХУВАТИ" (CALC) is 
   pressed using pywebio.output tools
'''
def disp_res():
    ## Calculate map, points grouped in clusters and group stats
    m, grouped, group_stats = cluster_main(in_pars, pin)

    if 'error' in group_stats:
        toast(group_stats['error'], duration=5, color='error')
        return

    ## Display map into scope 'map'
    with use_scope('map', clear=True):
        # Displays map
        put_html(m._repr_html_())

    ## Display text report into scope 'text'
    with use_scope('text', clear=True):
        put_markdown('## ПАРАМЕТРИ')
        msg_pars = [
            f"Формат координат: `{pin.coord_format}`",
            f"Порядок координат: `{pin.lat_lon_order}`",
            f"Радіус сусідства: `{pin.epsilon}` м",
            f"Мін. кількість точок у кластері: `{pin.min_samples}`" ]
        put_markdown(', '.join(msg_pars[:2]))
        put_markdown(', '.join(msg_pars[2:]))

        put_markdown('## РЕЗУЛЬТАТ')
        msg_stats = [
            f"Всього виявлено точок: `{group_stats['n_pnts']}`",
            f"кластерів: `{group_stats['n_clust']}`",
            f"точок поза кластерами: `{group_stats['n_outlier']}`" ]
        put_markdown(', '.join(msg_stats))

        for group_name, group_data in grouped:
            group_head = f'### Поза кластером' if group_name == -1 \
                else f'### Кластер {group_name}'
            put_markdown(group_head)
            cntr_grp, sz_grp = center(group_data, pin.perctl)
            put_markdown(f'Точок `{len(group_data)}`, ' + \
                f'центр: `{cntr_grp[0]:.6f}, {cntr_grp[1]:.6f}`, ' + \
                f'розмір: `{sz_grp:.1f}` м')
            put_table(group_data.values.tolist(), group_data.columns.tolist())

    toast(msg_stats, duration=5, color='success')

'''Build layout and render input controls in scope "pars" (for parameters' 
   input), input arguments are passed via unpacked dict (**) instead of 
   plain list
'''
@use_scope('pars', clear=True)
def disp_pars():
    put_markdown('#### Розборка тексту на координати')
    put_row(size='60% 3% 40%', content=[
        put_radio(**in_pars['coord_format']), None,
        put_radio(**in_pars['lat_lon_order'])
    ])
    put_textarea(**in_pars['text'])
    put_markdown('#### Кластеризація точок')
    put_row(size='45% 18% 40%', content=[
        put_slider(**in_pars['epsilon']), None,
        put_slider(**in_pars['min_samples'])
    ])
    put_markdown('#### Відображення')
    put_row(size='45% 18% 40%', content=[
        put_slider(**in_pars['perctl']), None,
        put_slider(**in_pars['zoom_start'])
    ])
    put_button('РАХУВАТИ', onclick=lambda: disp_res())

'''Main layout with 5 tabs filled in with starting values. The first 3 tabs 
   correspond to the following 3 scopes: 'pars', 'map', and 'text'. The 2 last
   tabs are static, so they do not need scope names.
'''
@config(title='Геокластеризація', theme='minty')
def app():
    ## Web page heading
    page_header = '<span style="font-size:20px"><b>ГЕО</b><i>КЛАСТЕРИЗАЦІЯ</i></span>'
    put_row([put_image(logo_img,format='png',width='60%'), None, 
        put_html(page_header)], size='50px 20px 90%')

    ## 5 tabs
    put_tabs([
        {'title': 'Параметри', 'content': put_scope('pars', content=put_text('')) },
        {'title': 'Мапа', 
         'content': put_scope('map', content=put_html(folium.Map()._repr_html_()))},
        {'title': 'Текст', 
         'content': put_scope('text', content=put_text('')) },
        {'title': 'Допомога', 'content': put_markdown(cluster_help_md)},
        {'title': 'Приклад', 'content': put_html(example_text)}
    ])

    ## Filling in the scope (tab) 'pars'
    disp_pars()

if __name__ == '__main__':
    start_server(app, port=8080, debug=True)
