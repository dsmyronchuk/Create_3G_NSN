import xml.etree.ElementTree as ET
from xml.dom import minidom
import data_file
import secret


class WBTS:
    def __init__(self, name, row, folder_name):
        self.BS_Name = name
        self.folder_name = folder_name
        self.OAM_IP = row[3]
        self.OAM_Mask = row[4]
        self.OAM_DG = row[5]
    #    self.OAM_VLAN = int(row[6])
        self.WBTS_ID = int(row[15])
        self.WBTS_RNC = int(row[16])
        self.WBTS_BS_SCTP = int(row[18])
        self.WBTS_Iub_DG = row[19]
        self.WBTS_Iub_IP = row[20]
        self.WBTS_Iub_Mask = row[21]
    #    self.WBTS_Iub_VLAN_ID = int(row[22])
        self.ipbr_num = self.calculate_ipbr_nub()

        self.ipbr_xml()                      # Вызываю функцию создания IPBR

    def calculate_ipbr_nub(self):
        if self.WBTS_BS_SCTP > 53126:
            return str(self.WBTS_BS_SCTP - 52949)
        else:
            return str(self.WBTS_BS_SCTP - 49000)

    def ipbr_xml(self):
        # словари нужны потому что в managedObject не принимает слово class напрямую
        cls_1 = {'class': 'com.nsn.mcrncipa:IPBR'}
        cls_2 = {'class': 'com.nsn.mcrncipa:IPRO'}

        new = ET.Element('raml', version='2.0', xmlns='raml20.xsd')  # 3 строка
        cmData = ET.SubElement(new, 'cmData', type='plan')
        header = ET.SubElement(cmData, 'header')
        log = ET.SubElement(header, 'log', dateTime='29.09.2021', action="created", appInfo="PlanExporter")
        log.text = 'InternalValues are used'

        # первый блок
        managedObject = ET.SubElement(cmData, 'managedObject', cls_1, version='mcRNC17', distName=
        f'PLMN-PLMN/RNC-{self.WBTS_RNC}/IP-1/IPBR-{self.ipbr_num}',
                                      operation='create')
        p_name = ET.SubElement(managedObject, 'p', name='committedBW')
        p_name.text = '100000'
        p_name = ET.SubElement(managedObject, 'p', name='committedDcnBW')
        p_name.text = '1000'
        p_name = ET.SubElement(managedObject, 'p', name='committedSigBW')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='dspmProfileID')
        p_name.text = '4'
        p_name = ET.SubElement(managedObject, 'p', name='ifcNRTDCH')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='ifcNRTHSDPA')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='ipBasedRouteName')
        p_name.text = self.BS_Name.replace('_', '-')
        p_name = ET.SubElement(managedObject, 'p', name='localMuxUDPPort')
        p_name.text = '65535'
        p_name = ET.SubElement(managedObject, 'p', name='maxMuxPackets')
        p_name.text = '30'
        p_name = ET.SubElement(managedObject, 'p', name='phbProfileID')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='remoteMuxUDPPort')
        p_name.text = '65535'
        p_name = ET.SubElement(managedObject, 'p', name='routeBW')
        p_name.text = '1000000'
        p_name = ET.SubElement(managedObject, 'p', name='schedulerType')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='udpMuxDSCP')
        p_name.text = '46'
        p_name = ET.SubElement(managedObject, 'p', name='udpMuxEnabled')
        p_name.text = '0'

        # Второй блок ( для каждого QNUP )
        for i in secret.dct_rnc_ip[self.WBTS_RNC]:  # i[0] - IP, i[1] - Номер QNUP
            managedObject = ET.SubElement(cmData, 'managedObject', cls_2, version='mcRNC17', distName=
            f'PLMN-PLMN/RNC-{self.WBTS_RNC}/IP-1/OWNER-QNUP-{i[1]}/IPRO-'
            f'{self.ipbr_num}-{i[0]}-lo11', operation='create')
            p_name = ET.SubElement(managedObject, 'p', name='address')
            p_name.text = i[0]
            p_name = ET.SubElement(managedObject, 'p', name='iface')
            p_name.text = 'lo11'
            p_name = ET.SubElement(managedObject, 'p', name='ipBasedRouteId')
            p_name.text = str(self.ipbr_num)
            p_name = ET.SubElement(managedObject, 'p', name='phbAF1')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='phbAF2')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='phbAF3')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='phbAF4')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='phbBE')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='phbEF')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='vrf')
            p_name.text = 'iub'

        xml_string = ET.tostring(new).decode(errors='ignore')
        xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
        with open(f'C:\Python\Create_3G_NSN\{self.folder_name}\{self.BS_Name}_IPBR_{self.WBTS_ID}.xml',
                  'w') as xml_file:
            xml_file.write(xml_prettyxml)
