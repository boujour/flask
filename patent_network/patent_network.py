
from flask import Blueprint
from flask import Flask,request,render_template

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

project = 'Yangtze_data'
domain = 'city_patent'

Yangtze_city = gpd.read_file('./shp/%s/Yangtze_city_41.shp'%(project))
Yangtze_city_27 = gpd.read_file('./shp/%s/Yangtze_city_27.shp'%(project))

China_city = pd.read_csv('./csv/China_city/China_city.csv',encoding='gbk')
city_stat = pd.read_csv('./csv/%s/%s/city_patent_number.csv'%(project,domain),encoding='gbk')
#whole_network = city_network
target_attri = 'patent_num'


network_type = ['all','single']

def network_analysis(target_city,network_type):
    city_network = pd.read_csv('./csv/%s/%s/patent_network_GIS.csv'%(project,domain),encoding='gbk')
    target_city_en = China_city[China_city['City_CH']==target_city]['City_CH_EN'].to_list()[0]
    if network_type != 'all':
        city_network = city_network[(city_network['origin']==target_city)|(city_network['destination']==target_city)]
        city_network.index = range(len(city_network))
        target_stat = city_network.iloc[:,:3]
        for i in range(len(target_stat)):
            origin = target_stat.loc[i,'origin']
            destination = target_stat.loc[i,'destination']
            if origin==target_city:
                target_stat.loc[i,'origin'] = destination
                target_stat.loc[i,'destination'] = origin
        target_stat = target_stat.sort_values('link',ascending=False)
        target_stat.columns = ['city','destination',target_attri]
    else:
        target_stat = city_stat
    #target_stat.to_csv(r'/Users/lijun/Documents/spyder/getTrafficInfo/csv/railway/%s/patent_network/single_city.csv'%(project),
    #                   index=None,encoding='gbk')
    if network_type=='single':
        title_list = ['Patent network of %s'%(target_city_en),'Patent number between each cities and %s'%(target_city_en)]
    else:
        title_list = ['Patent network of Yangtze River Delta','Patent number of each city']        
    head_num_max = city_stat[target_attri].max()
    link_max = city_network['link'].max()
    
    Yangtze_point = gpd.GeoDataFrame(city_stat,geometry=gpd.points_from_xy
                                  (city_stat['lon'],city_stat['lat']))
    Yangtze_point_solid = Yangtze_point
    
    line_list = []
    for i in range(len(city_network)):
        O_lon = city_network.loc[i,'lon_origin']
        O_lat = city_network.loc[i,'lat_origin']
        D_lon = city_network.loc[i,'lon_destination']
        D_lat = city_network.loc[i,'lat_destination']
        info_df = city_network.iloc[:,:3]
        line_shape = LineString([[O_lon,O_lat],[D_lon,D_lat]])
        line_list.append(line_shape)
        
    gpd_line = gpd.GeoDataFrame(info_df,geometry=line_list)
    gpd_line.sort_values('link',ascending=True,inplace=True)
    color_list = ['#A5BFCF','#A5BFCF','#7D9FB8','#557FA1','#2E648C']
    line_num = len(gpd_line)
    each_color_num = line_num//5
    last_color_num = line_num-4*each_color_num
    line_color_list = color_list[0:1]*each_color_num+color_list[1:2]*each_color_num+color_list[2:3]*each_color_num+color_list[3:4]*each_color_num+color_list[4:5]*last_color_num
    color = 'r'
    
    ax0 = Yangtze_city.plot(figsize=(9,9),color='#e1e1e1',edgecolor='w')
    ax = Yangtze_city_27.plot(ax=ax0,figsize=(9,9),color='#cccccc',edgecolor='w')
    ax1 = gpd_line.plot(ax=ax,color=color,linewidth=gpd_line['link']*10/link_max,alpha=0.5)
    ax2 = Yangtze_point.plot(ax=ax1,color='#cccccc',markersize=Yangtze_point[target_attri]*5*100/head_num_max
                    ,legend=True,marker='o',label='city',edgecolor=color)
    Yangtze_point_solid.plot(ax=ax2,color=color,markersize=Yangtze_point[target_attri]*1.5*100/head_num_max
                    ,legend=True,marker='o',label='city')
    
    for i in range(len(city_stat)):
        if i != -1:
            text_lon = city_stat.loc[i,'lon']+0.1
            text_lat = city_stat.loc[i,'lat']
            text = city_stat.loc[i,'city']
            plt.text(text_lon,text_lat,text,fontsize=12)
    plt.title(title_list[0],{'fontsize':18})
    plt.axis('off')
    plt.savefig('static/patent_network/img/%s/%s/patent_network_%s_%s.jpg'%(project,domain,target_city_en,network_type),dpi=300,bbox_inches = 'tight') 

    #全部区域联系网络图
    #目标城市设置不同颜色
    target_stat.sort_values(target_attri,ascending=False,inplace=True)
    city_list = list(target_stat['city'])
    color_list = ['b']*len(target_stat)
    try:
        target_rank = city_list.index(target_city)
        color_list[target_rank]='r'
    except:
        pass
    
    title=title_list[1]
    fig,ax = plt.subplots(figsize = (8,8))
    rects = ax.bar(x = range(target_stat.shape[0]),height=target_stat[target_attri],
            tick_label=target_stat['city'],width=0.5,color=color_list)
    
    ax.grid(True,which='both',linestyle=':',visible=True)
    ax.set_title(title,{'fontsize':18})
    ax.set_ylabel(target_attri)
    ax.set_axisbelow(True)
    plt.xticks(rotation=90)
    
    
    #添加数据标签
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    autolabel(rects)
    
    plt.savefig('static/patent_network/img/%s/%s/patent_num_%s_%s.jpg'%(project,domain,target_city_en,network_type),dpi=300,bbox_inches = 'tight') 

import os

file_dir = './static/patent_network/img/Yangtze_data/city_patent'
file_list = os.listdir(file_dir)

patent_bp = Blueprint('patent',__name__)
@patent_bp.route('/patent_network',methods=['POST','GET'])
def patent_network():
    if request.method=='POST':
        if request.form['city']!='':
            target_city = request.form['city']
            target_city_en = China_city[China_city['City_CH']==target_city]['City_CH_EN'].to_list()[0]
            file_name = 'patent_network_%s_all.jpg'%(target_city_en)
            if file_name not in file_list:
                print('compute again')                
                network_analysis(target_city,'single')
                network_analysis(target_city,'all')
            url_1 = '/static/patent_network/img/Yangtze_data/city_patent/patent_network_%s_all.jpg'%(target_city_en)               
            url_2 = '/static/patent_network/img/Yangtze_data/city_patent/patent_num_%s_all.jpg'%(target_city_en)  
            url_3 = '/static/patent_network/img/Yangtze_data/city_patent/patent_network_%s_single.jpg'%(target_city_en)               
            url_4 = '/static/patent_network/img/Yangtze_data/city_patent/patent_num_%s_single.jpg'%(target_city_en)  
        else:
            pass
    else:
        target_city=''
        url_1,url_2,url_3,url_4 = '','','',''
    return render_template('/patent_network/patent_network.html',city=target_city,
                           url_1=url_1,url_2=url_2,url_3=url_3,url_4=url_4)


    