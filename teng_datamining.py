from chemdataextractor.doc import Paragraph
from collections import Counter
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')

def is_decimal(string):
    if string.count('.') > 1:
        return False
    if string.replace('.', '', 1).isdigit():
        return True
    return False

def postag_lemmatize_combine(sentence):
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for word, tag in tagged:
        if tag.startswith('J'):
            pos = 'a'  # Adjective
        elif tag.startswith('V'):
            pos = 'v'  # Verb
        elif tag.startswith('N'):
            pos = 'n'  # Noun
        elif tag.startswith('R'):
            pos = 'r'  # Adverb
        else:
            pos = 'n'  # Default - Noun
        lemmatized_word = lemmatizer.lemmatize(word, pos)
        lemmatized_words.append(lemmatized_word)
    combined_sentence = ' '.join(lemmatized_words)
    return combined_sentence

def application_mining(para, application, title):
    # application_specific classification:
    # energy harvester: use of energy from motion, use of energy from wind, use of energy from water,
    #                   use of energy from sound, use of energy from magnetic field induced motion
    # sensor: tactile/motion sensor, chemical sensor, audio sensor, magnetic field sensor
    application_specific = ''
    if application == '':
        appl = []
        for x in range(len(para.sentences)):
            for y in range(len(para.sentences[x].tokens)):
                if para.sentences[x].tokens[y].text.lower() == 'harvesting' \
                        or para.sentences[x].tokens[y].text.lower() == 'harvester':
                    appl.append('energy harvester')
                elif para.sentences[x].tokens[y].text.lower() == 'sensing' \
                        or para.sentences[x].tokens[y].text.lower() == 'sensor':
                    appl.append('sensor')
        if appl != []:
            if appl.count('energy harvester') > appl.count('sensor'):
                application = 'energy harvester'
            elif appl.count('energy harvester') < appl.count('sensor'):
                application = 'sensor'
    if application == 'energy harvester':
        tactile = ['motion', 'movement', 'mechanical', 'gesture']
        for keyword in tactile:
            if keyword in title and 'magnetic field' not in title:
                application_specific = 'use of energy from motion'
        if 'wind' in title:
            application_specific = 'use of energy from wind'
        elif 'water' in title or 'fluid' in title or 'droplet' in title:
            application_specific = 'use of energy from water/fluid'
        elif 'audio' in title or 'sound' in title:
            application_specific = 'use of energy from sound'
        elif 'magnetic field' in title:
            application_specific = 'use of energy from magnetic field induced motion'
        if application_specific == '':  # check inside text
             for x in range(len(para.sentences)):
                 for y in range(len(para.sentences[x].tokens)):
                     if para.sentences[x].tokens[y].text.lower() == 'motion' \
                             or para.sentences[x].tokens[y].text.lower() == 'movement':
                         application_specific = 'use of energy from motion'
                     elif para.sentences[x].tokens[y].text.lower() == 'wind':
                         application_specific = 'use of energy from wind'
                     elif para.sentences[x].tokens[y].text.lower() == 'water':
                         application_specific = 'use of energy from water/fluid'
                     elif para.sentences[x].tokens[y].text.lower() == 'audio' \
                             or para.sentences[x].tokens[y].text.lower() == 'sound':
                         application_specific = 'use of energy from sound'
    elif application == 'sensor':
        if 'magnetic field' in title:
            application_specific = 'magnetic field sensor'
        tactile = ['tactile', 'pressure', 'motion', 'mechanical']
        for keyword in tactile:
            if keyword in title:
                application_specific = 'tactile/motion sensor'
        if 'chemical sensor' in title:
            application_specific = 'chemical sensor'
        elif 'audio' in title or 'sound' in title:
            application_specific = 'audio sensor'
        if application_specific == '':  # check inside text
            for x in range(len(para.sentences)):
                for y in range(len(para.sentences[x].tokens)-1):
                    if para.sentences[x].tokens[y].text.lower() == 'motion' \
                            or para.sentences[x].tokens[y].text.lower() == 'tactile' \
                            or para.sentences[x].tokens[y].text.lower() == 'pressure':
                        application_specific = 'tactile/motion sensor'
                    elif para.sentences[x].tokens[y].text.lower() == 'chemical' \
                            and para.sentences[x].tokens[y+1].text.lower() == 'sensor':
                        application_specific = 'chemical sensor'
                    elif para.sentences[x].tokens[y].text.lower() == 'audio' \
                            or para.sentences[x].tokens[y].text.lower() == 'sound':
                        application_specific = 'audio sensor'
    return application, application_specific

def mode_mining(para):
    # 4 modes: contact-separation mode, lateral sliding mode, single-electrode mode, and freestanding mode
    mode = ''
    mod = []
    modes_f = ['contact-separation', 'contact separation', 'lateral sliding',
               'single-electrode', 'single electrode', 'freestanding']
    modes_f2 = ['CS', 'LS', 'SE', 'FT']
    for x in range(len(para.sentences)):
        count_modes_f = 0
        for mo in modes_f:
            if mo in para.sentences[x].text.lower():
                count_modes_f += 1
        for mo2 in modes_f2:
            if mo2 in para.sentences[x].text:
                count_modes_f += 1
        if count_modes_f < 3:
            for y in range(len(para.sentences[x].tokens)-2):
                if para.sentences[x].tokens[y].text.lower() == 'contact-separation' \
                        or para.sentences[x].tokens[y].text.lower() == 'contact' and para.sentences[x].tokens[y+1].text.lower() == 'separation'\
                        or ('CS' in para.sentences[x].tokens[y].text
                            and ('TENG' in para.sentences[x].tokens[y].text or 'TENG' in para.sentences[x].tokens[y+1].text
                                 or 'TENG' in para.sentences[x].tokens[y+2].text or 'mode' in para.sentences[x].tokens[y+1].text)):
                    mod.append('contact-separation')
                elif (('vertical' in para.sentences[x].text.lower() and 'contact' in para.sentences[x].text.lower())
                      or ('charge' in para.sentences[x].text.lower() and 'contact' in para.sentences[x].text.lower() and 'separation' in para.sentences[x].text.lower())):
                    mod.append('contact-separation')
                    break
                if (para.sentences[x].tokens[y].text.lower() == 'lateral' or para.sentences[x].tokens[y].text.lower() == 'in-plane'
                    or para.sentences[x].tokens[y].text.lower() == 'linear') and para.sentences[x].tokens[y+1].text.lower() == 'sliding' \
                        or ('LS' in para.sentences[x].tokens[y].text
                            and ('TENG' in para.sentences[x].tokens[y].text or 'TENG' in para.sentences[x].tokens[y + 1].text
                                 or 'TENG' in para.sentences[x].tokens[y + 2].text or 'mode' in para.sentences[x].tokens[y + 1].text)):
                    mod.append('lateral sliding')
                if para.sentences[x].tokens[y].text.lower() == 'single-electrode' \
                        or para.sentences[x].tokens[y].text.lower() == 'single' and para.sentences[x].tokens[y+1].text.lower() == 'electrode' \
                        or ('SE' in para.sentences[x].tokens[y].text
                            and ('TENG' in para.sentences[x].tokens[y].text or 'TENG' in para.sentences[x].tokens[y + 1].text
                                 or 'TENG' in para.sentences[x].tokens[y + 2].text or 'mode' in para.sentences[x].tokens[y + 1].text)):
                    mod.append('single-electrode')
                if para.sentences[x].tokens[y].text.lower() == 'freestanding' \
                        or para.sentences[x].tokens[y].text.lower() == 'free-standing' \
                        or ('FT' in para.sentences[x].tokens[y].text
                            and ('TENG' in para.sentences[x].tokens[y].text or 'TENG' in para.sentences[x].tokens[y + 1].text
                                 or 'TENG' in para.sentences[x].tokens[y + 2].text or 'mode' in para.sentences[x].tokens[y + 1].text)):
                    mod.append('freestanding')
    mode_t = Counter(mod).most_common()
    if mode_t != []:
        mode = mode_t[0][0]
    return mode

def material_mining(para):
    # tribopositive layer (such as human skin, positive charge affinity, tend to be positively charged)
    # tribonegative layer (such as rubber, tend to gain electron and be negatively charged)
    # electrode layer
    materials_classified = {}
    electrode_list1 = ['Copper', 'Gold', 'Silver', 'Graphene', 'Nickel', 'Zinc', 'Aluminum', 'Aluminium',
                       'Polypyrrole', 'Titanium', 'Platinum']
    electrode_list3 = ['Cu', 'Al', 'Au', 'Ag', 'CNT', 'Sn', 'Ni', 'Zn', 'PPy', 'PEDOT',
                       'ZnO', 'SnO2', 'In2O3', 'ITO', 'Pt', 'FTO', 'AgCl', 'MoS2', 'GO', 'AgNW', 'CNT', 'IZO']
    electrode_list2 = ['Indium Tin Oxide', 'Stainless steel', 'Carbon Nanotube', 'Zinc Oxide',
                       'Tin Oxide', 'Indium Oxide', 'Graphene Oxide', 'Carbon Black', 'Carbon Fiber', 'Carbon',
                       'Ti3C2Tx MXene', 'Mxene']
    tribopositive_list1 = ['aniline formaldehyde resin', 'polyformaldehyde', 'polyoxymethylene', 'polyamide',
                           'melamine formaldehyde', 'melamine', 'Asbestos', 'Quartz', ' Silk ', 'Wool', ' Fur ',
                           'Cotton', 'Polycarbonate', 'Polystyrene', 'Cellulose', 'Aluminum', 'Nylon',
                           'Leather', 'Keratin', ' Hair ', ' Wood ', 'Ceramics', ' Mica ', 'Human Skin']
    tribopositive_list3 = ['AFR', 'POM', 'ABS']
    tribonegative_list1 = ['fluorinated ethylene propylene', 'polytetrafluoroethylene', 'polytrifluorochloroethylene',
                           'polyvinyl chloride', 'acetonitrile butadiene styrene', 'polycarbonate', 'polystyrene',
                           'polyetherimide', 'polydimethylsiloxane', 'polyester fabric', 'polyvinylidene fluoride',
                           'DuraLar polyester film', 'silicone rubber', 'garolite', 'polyetheretherketone',
                           ' Saran ', 'quart glass', 'polyvinylidene chloride', 'polychloroethene']
    tribonegative_list3 = ['FEP', 'PVC', 'PDMS', 'PVDF', 'PEEK', 'PE', 'PVDC', 'PPO',
                           'Teflon', 'Glossy', 'ULTEM', 'Kapton']
    electrode_bool = 0
    tribopositive_bool = 0
    tribonegative_bool = 0
    for x in range(len(para.sentences)):
        if 'electrode' in para.sentences[x].text:
            for mat in electrode_list1:
                if mat.lower() in para.sentences[x].text.lower():
                    materials_classified['electrode'] = mat.lower()
                    electrode_bool = 1
                    break
            for mat in electrode_list2:
                if mat.lower() in para.sentences[x].text.lower():
                    materials_classified['electrode'] = mat.lower()
                    electrode_bool = 1
                    break
            if electrode_bool == 0:
                for y in range(len(para.sentences[x].tokens)-2):
                    for mat in electrode_list3:
                        if para.sentences[x].tokens[y].text == mat:
                            materials_classified['electrode'] = mat
                            electrode_bool = 1
                            break
    para_processed = Paragraph(postag_lemmatize_combine(para.text))
    target_tribo = ['fabricate', 'charge', 'generate', 'contact', 'select', 'use', 'assemble',
                    'attach', 'prepare', 'positive', 'friction']
    for x in range(len(para_processed.sentences)):
        if (any(word.lower() in para_processed.sentences[x].text for word in target_tribo)
                and 'electrode' not in para_processed.sentences[x].text):
            for mat in tribopositive_list1:
                if mat.lower() in para_processed.sentences[x].text.lower():
                    materials_classified['tribopositive'] = mat.lower()
                    tribopositive_bool = 1
                    break
            if tribopositive_bool == 0:
                for y in range(len(para_processed.sentences[x].tokens)-2):
                    for mat in tribopositive_list3:
                        if para_processed.sentences[x].tokens[y].text == mat:
                            materials_classified['tribopositive'] = mat
            for mat in tribonegative_list1:
                if mat.lower() in para_processed.sentences[x].text.lower():
                    materials_classified['tribonegative'] = mat.lower()
                    tribonegative_bool = 1
                    break
            if tribonegative_bool == 0:
                for y in range(len(para_processed.sentences[x].tokens)-2):
                    for mat in tribonegative_list3:
                        if para_processed.sentences[x].tokens[y].text == mat:
                            materials_classified['tribonegative'] = mat
    return materials_classified

def performance_param_mining(para):
    # performance parameters including:
    # maximum open circuit voltage, maximum short circuit current, current density, power density
    max_Voc = []
    max_Isc = []
    current_density = []
    power_density = []
    target_tribo = ['short circuit current', 'short-circuit current', 'output current', 'open circuit voltage', 'open-circuit voltage', 'output voltage',
                    'current density', 'power density', 'output performance',
                    'Isc', 'ISC', 'Voc', 'VOC', 'Jsc', 'A/m2', 'A/cm2', 'A cm−2', 'A m−2', 'A·m−2', 'A·cm−2', 'W/m2', 'W/cm2', 'W m−2', 'W cm−2', 'W·m−2', 'W·cm−2']
    for x in range(len(para.sentences)):
        try:
            if any(word in para.sentences[x].text for word in target_tribo):
                if ('short circuit current' in para.sentences[x].text or 'short-circuit current' in para.sentences[x].text or 'output current' in para.sentences[x].text or 'output performance' in para.sentences[x].text or
                        'ISC' in para.sentences[x].text or 'Isc' in para.sentences[x].text) and 'A' in para.sentences[x].text:
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'A' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3 and ('m−2' not in para.sentences[x].tokens[y+1].text and '/' not in para.sentences[x].tokens[y+1].text):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                if str(para.sentences[x].tokens[y].text) == 'A' and float(para.sentences[x].tokens[y-1].text) > 1:
                                    print('out of range: ', end='')
                                    print(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                                else:
                                    max_Isc.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                if ('current density' in para.sentences[x].text or 'Jsc' in para.sentences[x].text
                        or 'A m−2' in para.sentences[x].text or 'A·m−2' in para.sentences[x].text or 'A·cm−2' in para.sentences[x].text or 'A cm−2' in para.sentences[x].text or 'A/m2' in para.sentences[x].text or 'A/cm2' in para.sentences[x].text):
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'A' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3 and ('m−2' in para.sentences[x].tokens[y+1].text or 'm−3' in para.sentences[x].tokens[y+1].text):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                current_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + ' ' + para.sentences[x].tokens[y+1].text)
                        elif 'A·m−2' in para.sentences[x].tokens[y].text or 'A·cm−2' in para.sentences[x].tokens[y].text:
                            if is_decimal(para.sentences[x].tokens[y - 1].text):
                                current_density.append(str(para.sentences[x].tokens[y - 1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                        elif 'A' in para.sentences[x].tokens[y].text and '/' in para.sentences[x].tokens[y+1].text and 'm' in para.sentences[x].tokens[y+2].text:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                current_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + str(para.sentences[x].tokens[y+1].text) + str(para.sentences[x].tokens[y+2].text))
                if ('open circuit voltage' in para.sentences[x].text or 'open-circuit voltage' in para.sentences[x].text or 'output voltage' in para.sentences[x].text or 'output performance' in para.sentences[x].text or
                        'VOC' in para.sentences[x].text or 'Voc' in para.sentences[x].text) and 'V' in para.sentences[x].text:
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'V' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3 and ('m−2' not in para.sentences[x].tokens[y+1].text and '/' not in para.sentences[x].tokens[y+1].text):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                max_Voc.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                if 'power density' in para.sentences[x].text or 'W m−2' in para.sentences[x].text or 'W·m−2' in para.sentences[x].text or 'W cm−2' in para.sentences[x].text or 'W·cm−2' in para.sentences[x].text or 'W/m2' in para.sentences[x].text or 'W/cm2' in para.sentences[x].text:
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'W' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3 and ('m−2' in para.sentences[x].tokens[y+1].text or 'm−3' in para.sentences[x].tokens[y+1].text):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                power_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + ' ' + para.sentences[x].tokens[y+1].text)
                        elif 'W·m−2' in para.sentences[x].tokens[y].text or 'W·cm−2' in para.sentences[x].tokens[y].text:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                power_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                        elif 'W' in para.sentences[x].tokens[y].text and '/' in para.sentences[x].tokens[y+1].text and 'm' in para.sentences[x].tokens[y+2].text and len(para.sentences[x].tokens[y+2].text) < 4:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                power_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + str(para.sentences[x].tokens[y+1].text) + str(para.sentences[x].tokens[y+2].text))
        except:
            print('out of range')
    return max_Isc, max_Voc, current_density, power_density

def performance_param_additional_mining(para):
    # charge density
    charge_density = []
    target_tribo = ['efficiency', 'charge density',
                    '%', 'C/m2', 'C/cm2', 'C cm−2', 'C m−2', 'C/m3', 'C/cm3', 'C cm−3', 'C m−3', 'C·m−2', 'C·cm−2', 'C·m−3', 'C·cm−3']
    for x in range(len(para.sentences)):
        try:
            if any(word in para.sentences[x].text for word in target_tribo):
                if ('charge density' in para.sentences[x].text or 'Jsc' in para.sentences[x].text
                        or 'C m−2' in para.sentences[x].text or 'C cm−2' in para.sentences[x].text or 'C/m2' in para.sentences[x].text or 'C/cm2' in para.sentences[x].text):
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'C' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3 and ('m−2' in para.sentences[x].tokens[y+1].text or 'm−3' in para.sentences[x].tokens[y+1].text):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                charge_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + ' ' + para.sentences[x].tokens[y+1].text)
                        elif 'C·m−2' in para.sentences[x].tokens[y].text or 'C·cm−2' in para.sentences[x].tokens[y].text:
                            if is_decimal(para.sentences[x].tokens[y - 1].text):
                                charge_density.append(str(para.sentences[x].tokens[y - 1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                        elif 'C' in para.sentences[x].tokens[y].text and '/' in para.sentences[x].tokens[y+1].text and 'm' in para.sentences[x].tokens[y+2].text:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                charge_density.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text) + str(para.sentences[x].tokens[y+1].text) + str(para.sentences[x].tokens[y+2].text))
        except:
            print('out of range')
    return charge_density

def dimensions_mining(para):
    # thickness, area
    thickness = {'electrode': '', 'tribopositive': '', 'tribonegative': ''}
    area = []
    target_tribo = ['thickness', 'area']
    electrode_list1 = ['Copper', 'Gold', 'Silver', 'Graphene', 'Nickel', 'Zinc', 'Aluminum', 'Aluminium',
                       'Polypyrrole', 'Titanium', 'Platinum', 'Indium Tin Oxide', 'Stainless steel', 'Carbon Nanotube', 'Zinc Oxide',
                       'Tin Oxide', 'Indium Oxide', 'Graphene Oxide', 'Carbon Black', 'Carbon Fiber', 'Carbon',
                       'Ti3C2Tx MXene', 'Mxene']
    electrode_list3 = ['Cu', 'Al', 'Au', 'Ag', 'CNT', 'Sn', 'Ni', 'Zn', 'PPy', 'PEDOT',
                       'ZnO', 'SnO2', 'In2O3', 'ITO', 'Pt', 'FTO', 'AgCl', 'MoS2', 'GO', 'AgNW', 'CNT', 'IZO']
    tribopositive_list1 = ['aniline formaldehyde resin', 'polyformaldehyde', 'polyoxymethylene', 'polyamide',
                           'melamine formaldehyde', 'Asbestos', 'Quartz', 'Aluminum', 'Nylon', 'Silk', 'Wool', ' Fur ',
                           'Cotton', 'Polycarbonate', 'Polystyrene', 'Cellulose', 'Leather', 'Keratin', 'Hair', 'Wood',
                           'Ceramics', ' Mica ', 'Human Skin']
    tribonegative_list1 = ['fluorinated ethylene propylene', 'polytetrafluoroethylene', 'polytrifluorochloroethylene',
                           'polyvinyl chloride', 'acetonitrile butadiene styrene', 'polycarbonate', 'polystyrene',
                           'polyetherimide', 'polydimethylsiloxane', 'polyester fabric', 'polyvinylidene fluoride',
                           'DuraLar polyester film', 'silicone rubber', 'garolite', 'polyetheretherketone',
                           ' Saran ', 'quart glass', 'polyvinylidene chloride', 'polychloroethene']
    tribonegative_list3 = ['FEP', 'PVC', 'PDMS', 'PVDF', 'PEEK', 'PE', 'PVDC', 'PPO',
                           'Teflon', 'Glossy', 'ULTEM', 'Kapton']
    for x in range(len(para.sentences)):
        try:
            if any(word in para.sentences[x].text for word in target_tribo):
                if 'thickness' in para.sentences[x].text and 'm ' in para.sentences[x].text:
                    for y in range(5, len(para.sentences[x].tokens) - 1):
                        if (('m' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3
                                and para.sentences[x].tokens[y].text[-1] == 'm') and
                                (para.sentences[x].tokens[y-1].text == 'thickness' or para.sentences[x].tokens[y-2].text == 'thickness'
                                 or para.sentences[x].tokens[y-3].text == 'thickness')):
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                electrode_bool = 0
                                if 'electrode' in para.sentences[x].text.lower():
                                    electrode_bool += 1
                                for mat in electrode_list1:
                                    if mat.lower() in para.sentences[x].text.lower():
                                        electrode_bool += 1
                                        break
                                if electrode_bool == 0:
                                    for mat in electrode_list3:
                                        if str(mat + ' ') in para.sentences[x].text:
                                            electrode_bool += 1
                                            break
                                triboposi_bool = 0
                                if 'tribopositive' in para.sentences[x].text.lower():
                                    triboposi_bool += 1
                                for mat in tribopositive_list1:
                                    if mat.lower() in para.sentences[x].text.lower():
                                        triboposi_bool += 1
                                        break
                                tribonega_bool = 0
                                if 'tribonegative' in para.sentences[x].text.lower():
                                    tribonega_bool += 1
                                for mat in tribonegative_list1:
                                    if mat.lower() in para.sentences[x].text.lower():
                                        tribonega_bool += 1
                                        break
                                if tribonega_bool == 0:
                                    for mat in tribonegative_list3:
                                        if str(mat + ' ') in para.sentences[x].text:
                                            tribonega_bool = 1
                                            break
                                if electrode_bool + triboposi_bool + tribonega_bool == 1:
                                    if electrode_bool == 1:
                                        thickness['electrode'] = str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text)
                                    if triboposi_bool == 1:
                                        thickness['tribopositive'] = str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text)
                                    if tribonega_bool == 1:
                                        thickness['tribonegative'] = str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text)
                # area
                if ('area' in para.sentences[x].text and
                        ('m2' in para.sentences[x].text or ('m ' in para.sentences[x].text and ('×' in para.sentences[x].text or 'x' in para.sentences[x].text)))):
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'm2' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 4:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                if ('×' in para.sentences[x].tokens[y-2].text or 'x' in para.sentences[x].tokens[y-2].text) and is_decimal(para.sentences[x].tokens[y-3].text):
                                    area.append(str(para.sentences[x].tokens[y-3].text) + str(para.sentences[x].tokens[y-2].text) + str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                                else:
                                    area.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
                        elif 'm ' in para.sentences[x].text and ('×' in para.sentences[x].text or 'x' in para.sentences[x].text):
                            if 'm' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3:
                                if is_decimal(para.sentences[x].tokens[y-1].text):
                                    if ('×' in para.sentences[x].tokens[y-2].text or 'x' in para.sentences[x].tokens[y-2].text) and is_decimal(para.sentences[x].tokens[y-4].text):
                                        area.append(str(para.sentences[x].tokens[y-4].text) + ' ' + str(para.sentences[x].tokens[y-3].text) + ' ' +
                                                    str(para.sentences[x].tokens[y-2].text) + ' ' + str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
        except:
            print('out of range')
    return thickness, area

def operating_conditions_mining(para):
    # operating frequency
    operating_freq = []
    target_tribo = ['frequency']
    for x in range(len(para.sentences)):
        try:
            if any(word in para.sentences[x].text for word in target_tribo):
                if 'frequency' in para.sentences[x].text and 'Hz' in para.sentences[x].text:
                    for y in range(len(para.sentences[x].tokens) - 1):
                        if 'Hz' in para.sentences[x].tokens[y].text and len(para.sentences[x].tokens[y].text) < 3:
                            if is_decimal(para.sentences[x].tokens[y-1].text):
                                operating_freq.append(str(para.sentences[x].tokens[y-1].text) + ' ' + str(para.sentences[x].tokens[y].text))
        except:
            print('out of range')
    return operating_freq


