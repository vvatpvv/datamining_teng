# coding:utf-8
import pymysql
import os
import re
from decimal import Decimal
from bs4 import BeautifulSoup
from chemdataextractor.doc import Paragraph
from teng_datamining import (is_decimal, application_mining, mode_mining, material_mining,
                             performance_param_mining, performance_param_additional_mining,
                             dimensions_mining, operating_conditions_mining)

folder = 'teng_htmls'

# connection to the database
pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='tengdevices',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor
                       )
cursor = conn.cursor()

def get_htmls():
    html_files = []
    for (root, dirs, files) in os.walk('.', topdown=True):
        if folder in root:
            for file in files:
                if '.html' in file:
                    html_files.append(folder + '/' + file)
    return html_files

def get_txts():
    txt_files = []
    for (root, dirs, files) in os.walk('.', topdown=True):
        if folder in root:
            for file in files:
                if '.txt' in file:
                    txt_files.append(file)
    return txt_files

def data_insert_ref(html_files):
    for f in html_files:
        try:
            if '10.1038' in f:      # Nature
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = soup.find("meta", attrs={'name': "citation_fulltext_html_url"})["content"]
                title = soup.find("meta", attrs={'name': "citation_title"})["content"]
                doi = soup.find("meta", attrs={'name': "DOI"})["content"]
                publication_date = soup.find("meta", attrs={'name': "dc.date"})["content"]
                author = soup.find("meta", attrs={'name': "dc.creator"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
            elif '10.1039' in f:    # RSC
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = soup.find("meta", attrs={'name': "citation_fulltext_html_url"})["content"]
                title = soup.find("meta", attrs={'name': "citation_title"})["content"]
                doi = soup.find("meta", attrs={'name': "citation_doi"})["content"]
                publication_date = soup.find("meta", attrs={'name': "citation_online_date"})["content"]
                author = soup.find("meta", attrs={'name': "DC.Creator"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
            elif '10.1021' in f:    # ACS
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                title = soup.find("meta", attrs={'name': "dc.Title"})["content"]
                doi = soup.find("meta", attrs={'name': "dc.Identifier"})["content"]
                html_link = "https://pubs.acs.org/doi/" + str(doi)
                publication_date = soup.find("meta", attrs={'name': "dc.Date"})["content"]
                author = soup.find("meta", attrs={'name': "dc.Creator"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
            elif '10.1002' in f or '10.1088' in f or '10.1149' in f or '10.7567' in f or '10.35848' in f:    # Wiley Advanced and IOP
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = soup.find("meta", attrs={'name': "citation_fulltext_html_url"})["content"]
                title = soup.find("meta", attrs={'name': "citation_title"})["content"]
                doi = soup.find("meta", attrs={'name': "citation_doi"})["content"]
                publication_date = soup.find("meta", attrs={'name': "citation_online_date"})["content"]
                author = soup.find("meta", attrs={'name': "citation_author"})["content"]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
            elif '10.1016' in f:    # Nano Ene, etc
                cont = open(f, "r", encoding="utf-8")
                soup = BeautifulSoup(cont, "lxml")
                html_link = ''
                anchors = soup.find_all("span", attrs={'class': "anchor-text"})
                for anchor in anchors:
                    if 'doi.org/10.1016/j.' in str(anchor):
                        print(anchor)
                        html_link = anchor.contents[0]
                        break
                titl = soup.find("span", attrs={'class': "title-text"}).contents
                title = ''
                if len(titl) == 1:
                    title = titl[0]
                else:
                    for i in range(len(titl)):
                        title += re.sub(r"<.*?>", '', str(titl[i]))
                doi = html_link.split('doi.org/')[1]
                div = str(soup.find("div", attrs={'class': "publication-volume"}))
                publication_date = div.split("<!-- -->")[1]
                author = soup.find("span", attrs={'class': "given-name"}).contents[0] + ' ' + soup.find("span", attrs={'class': "surname"}).contents[0]
                sqlStr = "insert into device_attributes(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`,`Ref_html_link`)" \
                         "VALUES ('%s','%s','%s','%s','%s');" \
                            % (doi, author, publication_date, title, html_link)
                res = cursor.execute(sqlStr)
                conn.commit()
        except:
            print('', end=' ')

def data_insert_application(txt_files):
    for fil in txt_files:
        title = ''
        try:
            query = "select Ref_title from device_attributes where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                    % (fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
            cursor.execute(query)
            ttl = cursor.fetchall()
            for row in ttl:
                title = row['Ref_title'].lower()
        except:
            print('record does not exist')
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break
                method_list.append([section_number, tex])
        application = ''
        if 'harvesting' in title.lower() or 'harvester' in title.lower():
            application = 'energy harvester'
        elif 'sensing' in title.lower() or 'sensor' in title.lower() or 'self-powered' in title.lower():
            application = 'sensor'
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        temp, application_specific = application_mining(para, application, title)
        if application == '':
            application = temp
        sqlStr = "update device_attributes set `Application` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (application, fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        res = cursor.execute(sqlStr)
        sqlStr2 = "update device_attributes set `Application_specific` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (application_specific, fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        res2 = cursor.execute(sqlStr2)
        conn.commit()

def data_insert_mode(txt_files):
    for fil in txt_files:
        try:
            query = "select Ref_title from device_attributes where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                    % (fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
            cursor.execute(query)
        except:
            print('record does not exist')
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break
                method_list.append([section_number, tex])
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        mod = mode_mining(para)
        mode = mod
        sqlStr = "update device_attributes set `Mode` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (mode, fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        res = cursor.execute(sqlStr)
        conn.commit()

def data_insert_materials(txt_files):
    for fil in txt_files:
        title = ''
        try:
            query = "select Ref_title from device_attributes where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                    % (fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
            cursor.execute(query)
        except:
            print('record does not exist')
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            bo = 0
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break  # EOF
                method_list.append([section_number, tex])
        electrode = ''
        tribopositive = ''
        tribonegative = ''
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        mate = material_mining(para)
        keys_list = list(mate.keys())
        if 'electrode' in keys_list and electrode == '':
            electrode = mate['electrode'].strip()
        if 'tribopositive' in keys_list and tribopositive == '':
            tribopositive = mate['tribopositive'].strip()
        if 'tribonegative' in keys_list and tribonegative == '':
            tribonegative = mate['tribonegative'].strip()
        sqlStr1 = "update device_attributes set `Tribopositive` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(tribopositive), fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        sqlStr2 = "update device_attributes set `Tribonegative` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(tribonegative), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        sqlStr3 = "update device_attributes set `Electrode` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(electrode), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        res1 = cursor.execute(sqlStr1)
        res2 = cursor.execute(sqlStr2)
        res3 = cursor.execute(sqlStr3)
        conn.commit()

def data_insert_performance_params(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break  # EOF
                method_list.append([section_number, tex])
        max_Isc_final = ''
        val = 0
        max_Voc_final = ''
        val2 = 0
        current_density_final = ''
        val3 = 0
        power_density_final = ''
        val4 = 0
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        max_Isc, max_Voc, current_density, power_density = performance_param_mining(para)
        for st in max_Isc:
            if is_decimal(st.split()[0]):
                de = Decimal(st.split()[0])
                if de > val:
                    val = de
                    max_Isc_final = st
        for st2 in max_Voc:
            if is_decimal(st2.split()[0]):
                de = Decimal(st2.split()[0])
                if de > val2:
                    val2 = de
                    max_Voc_final = st2
        for st3 in current_density:
            if is_decimal(st3.split()[0]):
                de = Decimal(st3.split()[0])
                if de > val3:
                    val3 = de
                    current_density_final = st3
        for st4 in power_density:
            if is_decimal(st4.split()[0]):
                de = Decimal(st4.split()[0])
                if de > val4:
                    val4 = de
                    power_density_final = st4
        sqlStr1 = "update device_attributes set `Open_circuit_voltage` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(max_Voc_final), fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        sqlStr2 = "update device_attributes set `Short_circuit_current` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(max_Isc_final), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        sqlStr3 = "update device_attributes set `Power_density` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(power_density_final), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        sqlStr4 = "update device_attributes set `Current_density` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                  % (str(current_density_final), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        res1 = cursor.execute(sqlStr1)
        res2 = cursor.execute(sqlStr2)
        res3 = cursor.execute(sqlStr3)
        res4 = cursor.execute(sqlStr4)
        conn.commit()

def data_insert_performance_additional_params(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break
                method_list.append([section_number, tex])
        charge_density_final = ''
        val4 = 0
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        charge_density = performance_param_additional_mining(para)
        for st4 in charge_density:
            if is_decimal(st4.split()[0]):
                de = Decimal(st4.split()[0])
                if de > val4:
                    val4 = de
                    charge_density_final = st4
        sqlStr4 = "update device_attributes set `Charge_density` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                  % (str(charge_density_final), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        res4 = cursor.execute(sqlStr4)
        conn.commit()

def data_insert_dimensions(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break
                method_list.append([section_number, tex])
        thickness_fin = ''
        area_fin = ''
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        thickness, area = dimensions_mining(para)
        if thickness_fin == '' and thickness != {'electrode': '', 'tribopositive': '', 'tribonegative': ''}:
            if thickness['electrode'] != '':
                thickness_fin += 'electrode ' + thickness['electrode'] + ' '
            if thickness['tribopositive'] != '':
                thickness_fin += 'tribopositive layer ' + thickness['tribopositive'] + ' '
            if thickness['tribonegative'] != '':
                thickness_fin += 'tribonegative layer ' + thickness['tribonegative'] + ' '
        for st2 in area:
            if area_fin == '':
                area_fin = st2
        sqlStr1 = "update device_attributes set `Thickness` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(thickness_fin), fil[0:7]+'/'+fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/'+ fil[8:-4])
        sqlStr2 = "update device_attributes set `Area` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(area_fin), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        res1 = cursor.execute(sqlStr1)
        res2 = cursor.execute(sqlStr2)
        conn.commit()

def data_insert_operating_conditions(txt_files):
    for fil in txt_files:
        method_list = []
        with open(folder + '/' + fil, 'r', encoding='utf8') as f:
            while True:
                section_number = f.readline().rstrip('\n')
                tex = f.readline().rstrip('\n')
                if not section_number or not tex:
                    break
                method_list.append([section_number, tex])
        freq_fin = ''
        para = ''
        for process in method_list:
            para = para + process[1] + '\n'
        para = Paragraph(get_results_discussion_conclusions_methods(para))
        freq = operating_conditions_mining(para)
        for st in freq:
            freq_fin = st
        sqlStr1 = "update device_attributes set `Operating_frequency` = '%s' where Ref_DOI_number = '%s' or Ref_DOI_number = '%s' or Ref_html_link = '%s';" \
                 % (str(freq_fin), fil[0:7] + '/' + fil[8:-4], fil[:-4].replace('_', '/'), 'https://www.nature.com/articles/' + fil[8:-4])
        res1 = cursor.execute(sqlStr1)
        conn.commit()

def calculate_record_score():
    wanted_score = 0.5
    total_score = 10
    try:
        query = "select * from device_attributes;"
        cursor.execute(query)
        record = cursor.fetchall()
        successful = 0
        unsuccessful = 0
        for row in record:
            try:
                record_score = 0
                if row['Mode'] != '':
                    record_score += 1
                if row['Application'] != '':
                    record_score += 1
                if row['Tribopositive'] != '':
                    record_score += 1
                if row['Tribonegative'] != '':
                    record_score += 1
                if row['Electrode'] != '':
                    record_score += 1
                if row['Open_circuit_voltage'] != '':
                    record_score += 1
                if row['Short_circuit_current'] != '':
                    record_score += 1
                if row['Power_density'] != '':
                    record_score += 1
                if row['Current_density'] != '':
                    record_score += 1
                if row['Operating_frequency'] != '':
                    record_score += 1
                if record_score/total_score >= wanted_score:
                    successful += 1
                    sqlStr = "insert ignore into device_attributes_filtered_verif(`Ref_DOI_number`,`Ref_lead_author`,`Ref_publication_date`,`Ref_title`," \
                             "`Ref_html_link`,`Application`,`Application_specific`,`Mode`,`Tribopositive`,`Tribonegative`," \
                             "`Electrode`,`Open_circuit_voltage`,`Short_circuit_current`," \
                             "`Power_density`,`Current_density`,`Charge_density`,`Thickness`,`Area`,`Operating_frequency`)" \
                             "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" \
                             % (row['Ref_DOI_number'], row['Ref_lead_author'], row['Ref_publication_date'], row['Ref_title'],
                                row['Ref_html_link'], row['Application'], row['Application_specific'], row['Mode'],
                                row['Tribopositive'], row['Tribonegative'], row['Electrode'],
                                row['Open_circuit_voltage'], row['Short_circuit_current'],
                                row['Power_density'], row['Current_density'], row['Charge_density'], row['Thickness'], row['Area'], row['Operating_frequency'])
                    res = cursor.execute(sqlStr)
                    conn.commit()
                else:
                    unsuccessful += 1
            except:
                print(row)
        print('successful:', end=' ')
        print(successful)
        print('total:', end=' ')
        print(successful + unsuccessful)
    except:
        print("error calculating score")

def get_results_discussion_conclusions_methods(input_para):
    key_list = ['abstractBox', 'Result', 'Results', 'Discussion', 'Conclusion', 'Conclusions', 'Methods', 'Methodology']
    output_para = ''
    for keyword in key_list:
        idx = input_para.find(keyword)
        if idx != -1:
            output_para = input_para[idx:]
            break
    remove_key_list = ['Acknowledgement', 'Appendix', 'CRediT']
    for rkeyword in remove_key_list:
        idx = output_para.find(rkeyword)
        if idx != -1:
            output_para = output_para[:idx]
            break
    if output_para == '' or len(output_para) < 500:
        try:
            idx = input_para.find('Abstract')
            if idx != -1:
                output_para = input_para[idx+300:]
            remove_key_list = ['Acknowledgement', 'Appendix', 'CRediT']
            for rkeyword in remove_key_list:
                idx = output_para.find(rkeyword)
                if idx != -1:
                    output_para = output_para[:idx]
                    break
        except:
            print('?')
    if output_para == '' or len(output_para) < 500:
        try:
            idx = input_para.find('Introduction')
            if idx != -1:
                output_para = input_para[idx+300:]
            remove_key_list = ['Acknowledgement', 'Appendix', 'CRediT']
            for rkeyword in remove_key_list:
                idx = output_para.find(rkeyword)
                if idx != -1:
                    output_para = output_para[:idx]
                    break
        except:
            print('?')
    return output_para


if __name__ == '__main__':
    html_files = get_htmls()
    data_insert_ref(html_files)
    txt_files = get_txts()
    data_insert_application(txt_files)
    data_insert_mode(txt_files)
    data_insert_materials(txt_files)
    data_insert_performance_params(txt_files)
    data_insert_performance_additional_params(txt_files)
    data_insert_dimensions(txt_files)
    data_insert_operating_conditions(txt_files)
    calculate_record_score()