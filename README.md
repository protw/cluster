### Clustering of geo points

#### Problem

Sometimes there is a need to group (cluster) geo points. In addition, coordinates of geo points can be obtained in the form of flat text and in various formats.

#### Solution

The application offers:

1. text parsing to search for pairs of geo coordinates and several typical formats
2. automated clustering of geo points
3. presentation of clusters of points and outlayers on the map and in tabular form with an estimate of the geometric size of the cluster.
4. the solution works as a web server whether on a local computer or based on a Docker container
5. Docker container can be run on external hosting, for example, Heroku

#### How to use the app

The application interface is represented by five tabs:

- `Параметри (Parameters)`- task of input parameters and data
- `Мапа (Map)`- presentation of the result on the map
- `Текст (Text)`- presentation of the result in text and tabular forms
- `Допомога (Help)`- actually this text is an explanation of what you are reading now
- `Приклад (Example)` - text containing a set of geo points for testing the application

#### Parameters

Input parameters and data consist of three groups: `Розборка тексту на координати (Parsing)` , `Кластеризація точок (Clustering)`and `Відображення (Rendering)`.

##### Parsing the text into coordinates

The parsing the text into coordinates accepts the following representations of geo coordinates in the text for their automated processing:

| Id   | Description                            | Example                                                     |
| ---- | -------------------------------------- | ----------------------------------------------------------- |
| 0    | Decimal point and comma between values | `qwerty (44.6857, 33.56173); (44.68599 ,33.56555); ...`     |
| 1    | Decimal point and slash between values | `Lorem ipsum 46,7369/ 32,8103 adsc 46,7373 /32,812 ei ...`  |
| 2    | Decimal point and space between values | `АБВГД 48.01388 38.796 07:59 АГД 48.0141 38.9056 07:53 ...` |

Also, the sequence of coordinate notation in different sources may differ, namely: `[Широта (Latitude), Довгота (Longitude)]`or `[Довгота, Широта]`.

##### Clustering of points

Clustering of points is carried out using the DBSCAN method, which has two main intuitively clear parameters:

- `epsilon`- or neighborhood distance is the radius / distance (m) within which points are considered neighbors
- `min_samples`- the minimum number of points to form a cluster

Part of the points, that may not fall into any cluster, form a separate group. These points are called `outlayers`(i.e. outside clusters).

##### Rendering

To estimate the geometric size of the cluster, the diameter of the circle (around the central point) that contains the specified part of the points (in %) is calculated.

You can also set the starting scale of the map display here.

#### TODO

- test the clustering algorithm for critical situations (run time errors), install stubs and generate error messages, ensure the stability of the application, centrally process messages about critical situations and generate a pop-up window (pywebio toast or popup)
- complicate parsing: extract the description of the point from the text: (left, right, target in a separate line)
- deploy a Docker container on external hosting

#### Useful links

- [Qingkai's Blog: Clustering with DBSCAN](http://qingkaikong.blogspot.com/2016/08/clustering-with-dbscan.html)
- [Folium and Geopandas: FeatureGroup for categorial data | Florian Neukirchen](https://www.riannek.de/2022/folium-featuregroup-categorial-data/)
- [Heroku + Docker in 10 Minutes. | by Kay Jan Wong | Towards Data Science](https://towardsdatascience.com/heroku-docker-in-10-minutes-f4329c4fd72f)