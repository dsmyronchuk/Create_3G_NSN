import xml.etree.ElementTree as ET
import numpy as np
from xml.dom import minidom


class WCELL:
    WCELL_rpdb_lst = []

    def __init__(self, row):

        self.BSC = int(row[0])
        self.CI = int(row[1])
        self.SAC = int(row[2])
        self.LAC = int(row[3])
        self.RAC = int(row[4])
        self.Site_name = row[5]
        self.Azimuth = row[6]
        self.Latitude = row[7]
        self.Longitude = row[8]
        self.Tilt = row[9]
        if not np.isnan(row[10]):
            self.BSIC = int(row[10])
        if np.isnan(row[10]):
            self.BSIC = input(f'Введите BSIC для CI {self.CI}: ')
        self.Channel = int(row[11])
        self.BCCH = row[12]

        self.__class__.WCELL_rpdb_lst.append(self)

    # заполнить азимуты та где их нет (на 2, 3 несущих)
    @staticmethod
    def azimuth_23_carrier(lst):
        for i in lst:
            if i.Channel == 10712:
                azzimuth = i.Azimuth
            for j in lst:
                if j.SAC == i.SAC and j.Channel != 10712:
                    j.Azimuth = azzimuth


    @staticmethod
    def create_full_name(inp_azimuth, inp_channel, inp_sitename, ci):
        def azimuth():
            if inp_azimuth == 'indoor':
                indoor_name = input(f'Введите имя для индор соты {ci} (901,902,903...): ')
                return indoor_name
            else:
                azz = inp_azimuth[:-1]
                if len(azz) == 2 or len(azz) == 1:
                    azz = azz.zfill(3)
                return azz

        def u1u2u3():
            if inp_channel == 10712:
                return 'U1'
            if inp_channel == 10737:
                return 'U2'
            if inp_channel == 10762:
                return 'U3'
            if inp_channel == 10662:
                return 'U4'

        return f'{inp_sitename[:11]}_{azimuth()}_{u1u2u3()}'

    @staticmethod
    def create_wcell(wbts_obj, lst_wcell, folder_name, bs_type, name_u='U'):
        # Корректировка имен
        for i in lst_wcell:
            i.full_name = WCELL.create_full_name(i.Azimuth, i.Channel, i.Site_name, i.CI)

        # словари нужны потому что в managedObject не принимает слово class напрямую
        cls_ipnb = {'class': 'IPNB'}
        cls_wbts = {'class': 'WBTS'}
        cls_wcell = {'class': 'WCEL'}
        cls_adjl = {'class': 'ADJL'}

        new = ET.Element('raml', version='2.0', xmlns='raml20.xsd')  # 3 строка
        cmData = ET.SubElement(new, 'cmData', type='plan')
        header = ET.SubElement(cmData, 'header')
        log = ET.SubElement(header, 'log', dateTime='29.09.2021', action="created", appInfo="PlanExporter")
        log.text = 'InternalValues are used'

        #   Create IPNB
        managedObject = ET.SubElement(cmData, 'managedObject', cls_ipnb, version='mcRNC17', distName=
        f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/IPNB-{wbts_obj.WBTS_ID}', operation='create')

        p_name = ET.SubElement(managedObject, 'p', name='MinSCTPPortIub')
        p_name.text = str(wbts_obj.WBTS_BS_SCTP)
        p_name = ET.SubElement(managedObject, 'p', name='name')
        p_name.text = f'{wbts_obj.BS_Name}_{name_u}'
        p_name = ET.SubElement(managedObject, 'p', name='NBAPDSCP')
        p_name.text = '34'
        p_name = ET.SubElement(managedObject, 'p', name='NodeBIPAddress')
        p_name.text = str(wbts_obj.WBTS_Iub_IP)
        p_name = ET.SubElement(managedObject, 'p', name='SourceNBAPIPAddress')
        p_name.text = '0.0.0.0'
        p_name = ET.SubElement(managedObject, 'p', name='SourceNBAPIPNetmask')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='WBTSId')
        p_name.text = str(wbts_obj.WBTS_ID)
        p_name = ET.SubElement(managedObject, 'p', name='VRF')
        p_name.text = 'iub'
        lst_name = ET.SubElement(managedObject, 'list', name='DNBAP')
        item = ET.SubElement(lst_name, 'item')
        p_name = ET.SubElement(item, 'p', name='CControlPortID')
        p_name.text = '1'

        # Create WBTS
        managedObject = ET.SubElement(cmData, 'managedObject', cls_wbts, version='mcRNC17', distName=
        f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/WBTS-{wbts_obj.WBTS_ID}', operation='create')

        p_name = ET.SubElement(managedObject, 'p', name='BlindHOIntraBTSQCheck')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='BroadcastSIB15')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='BroadcastSIB15_2')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='BroadcastSIB15_3')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='BTSSupportForHSPACM')
        p_name.text = '2'
        p_name = ET.SubElement(managedObject, 'p', name='DCNLinkStatus')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='DCNSecurityStatus')
        p_name.text = '255'
        p_name = ET.SubElement(managedObject, 'p', name='DedicatedMeasReportPeriod')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='DediMeasRepPeriodCSdata')
        p_name.text = '3'
        p_name = ET.SubElement(managedObject, 'p', name='DediMeasRepPeriodPSdata')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMax')
        p_name.text = '10000'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMax2msTTI')
        p_name.text = '10000'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMid')
        p_name.text = '7000'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMid2msTTI')
        p_name.text = '7000'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMin')
        p_name.text = '5000'
        p_name = ET.SubElement(managedObject, 'p', name='DelayThresholdMin2msTTI')
        p_name.text = '5000'
        p_name = ET.SubElement(managedObject, 'p', name='DLCECapacity')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='DLORLAveragingWindowSize')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='DSCPHigh')
        p_name.text = '46'
        p_name = ET.SubElement(managedObject, 'p', name='DSCPLow')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='DSCPMedDCH')
        p_name.text = '34'
        p_name = ET.SubElement(managedObject, 'p', name='DSCPMedHSPA')
        p_name.text = '26'
        p_name = ET.SubElement(managedObject, 'p', name='HARQRVConfiguration')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='HSDPA14MbpsPerUser')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='HSDPACCEnabled')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='HSDPACodeCapacity')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='HSDPAULCToDSCP')
        p_name.text = '34'
        p_name = ET.SubElement(managedObject, 'p', name='HSUPACCEnabled')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='HSUPADLCToDSCP')
        p_name.text = '34'
        p_name = ET.SubElement(managedObject, 'p', name='HSUPAXUsersEnabled')
        p_name.text = '12'
        p_name = ET.SubElement(managedObject, 'p', name='InactCACThresholdATM')
        p_name.text = '170'
        p_name = ET.SubElement(managedObject, 'p', name='InactCACThresholdIP')
        p_name.text = '80'
        p_name = ET.SubElement(managedObject, 'p', name='InactUsersCIDThreshold')
        p_name.text = '6'
        p_name = ET.SubElement(managedObject, 'p', name='IntelligentSDPrioHO')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='IPBasedRouteIdIub')
        p_name.text = wbts_obj.ipbr_num
        p_name = ET.SubElement(managedObject, 'p', name='IPBasedRouteIdIub2')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='IPBasedRouteIdIub3')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='IPBasedRouteIdIub4')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='IPNBId')
        p_name.text = str(wbts_obj.WBTS_ID)
        p_name = ET.SubElement(managedObject, 'p', name='IubTransportSharing')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='LoadControlPeriodPS')
        p_name.text = '20'
        p_name = ET.SubElement(managedObject, 'p', name='MaxBTSOMFrameSize')
        p_name.text = '1460'
        p_name = ET.SubElement(managedObject, 'p', name='MaxFPDLFrameSizeIub')
        p_name.text = '1428'
        p_name = ET.SubElement(managedObject, 'p', name='MaxNumberEDCHLCG')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='MDCBufferingTime')
        p_name.text = '50'
        p_name = ET.SubElement(managedObject, 'p', name='MeasFiltCoeff')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='MinUDPPortIub')
        p_name.text = '1026'
        p_name = ET.SubElement(managedObject, 'p', name='name')
        p_name.text = f'{wbts_obj.BS_Name}_{name_u}'
        p_name = ET.SubElement(managedObject, 'p', name='nbrRepeater')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='NodeBRABReconfigSupport')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='numFa')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='OverbookingSwitch')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PDUSize656WithHSDSCH')
        p_name.text = '2'
        p_name = ET.SubElement(managedObject, 'p', name='ProbabilityFactorMax')
        p_name.text = '1000'
        p_name = ET.SubElement(managedObject, 'p', name='ProbabilityFactorMax2msTTI')
        p_name.text = '1000'
        p_name = ET.SubElement(managedObject, 'p', name='PrxAlpha')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PrxMeasAveWindow')
        p_name.text = '10'
        p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSAdjustPeriod')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='PSAveragingWindowSize')
        p_name.text = '4'
        p_name = ET.SubElement(managedObject, 'p', name='PSRLAveragingWindowSize')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PtxAlpha')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PtxDPCHmax')
        p_name.text = '-30'
        p_name = ET.SubElement(managedObject, 'p', name='PtxDPCHmin')
        p_name.text = '-28'
        p_name = ET.SubElement(managedObject, 'p', name='PtxMeasAveWindow')
        p_name.text = '10'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMAVTrafficVERLogic')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMEnableWakeUpTime')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMInUse')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMRemCellSDBeginHour')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMRemCellSDBeginMin')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMRemCellSDEndHour')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMRemCellSDEndMin')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownBeginHour')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownBeginMin')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownEndHour')
        p_name.text = '6'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownEndMin')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='PWSMWeekday')
        p_name.text = '3'
        p_name = ET.SubElement(managedObject, 'p', name='RACHloadIndicationPeriod')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='RFSharingState')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='RRIndPeriod')
        p_name.text = '40'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorCSAMR')
        p_name.text = '50'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorCSNTData')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorCSTData')
        p_name.text = '100'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorPSBackgr')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorPSStream')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorPSTHP1')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorPSTHP2')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorPSTHP3')
        p_name.text = '95'
        p_name = ET.SubElement(managedObject, 'p', name='RRMULDCHActivityFactorSRB')
        p_name.text = '1'
        p_name = ET.SubElement(managedObject, 'p', name='SatelliteIubUsage')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='SchedulingPeriod')
        p_name.text = '100'
        p_name = ET.SubElement(managedObject, 'p', name='ToAWEOffsetNRTDCHIP')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='ToAWEOffsetRTDCHIP')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='ToAWSOffsetNRTDCHIP')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='ToAWSOffsetRTDCHIP')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='TQMId')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='TQMId2')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='TQMId3')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='TQMId4')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='type')
        p_name.text = '3'
        p_name = ET.SubElement(managedObject, 'p', name='ULCECapacity')
        p_name.text = '0'
        p_name = ET.SubElement(managedObject, 'p', name='WBTSName')
        p_name.text = f'{wbts_obj.BS_Name}_{name_u}'
        p_name = ET.SubElement(managedObject, 'p', name='WBTSSWBuildId')
        p_name.text = 'No information available'
        p_name = ET.SubElement(managedObject, 'p', name='WinACRABsetupDL')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='WinACRABsetupUL')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='WinLCHSDPA')
        p_name.text = '5'
        p_name = ET.SubElement(managedObject, 'p', name='WinLCHSUPA')
        p_name.text = '5'

        # Парам которые меняются для pico/micro bs
        ptxcellmax = '430'
        ptxdlabsmax = '370'
        ptxhighhsdpapwr = '410'
        ptxmaxhsdpa = '430'
        ptxoffset = '10'
        ptxprimarycpich = '330'
        ptxtarget = '420'
        ptxtargetpsmax = '400'
        ptxtargetpsmin = '360'
        if bs_type == 'flexi':
            ptxcellmax = '210'
            ptxdlabsmax = '150'
            ptxhighhsdpapwr = '190'
            ptxmaxhsdpa = '210'
            ptxoffset = '8'
            ptxprimarycpich = '110'
            ptxtarget = '200'
            ptxtargetpsmax = '200'
            ptxtargetpsmin = '150'
        if bs_type == 'micro':
            ptxcellmax = '240'
            ptxdlabsmax = '180'
            ptxhighhsdpapwr = '220'
            ptxmaxhsdpa = '240'
            ptxoffset = '8'
            ptxprimarycpich = '140'
            ptxtarget = '230'
            ptxtargetpsmax = '230'
            ptxtargetpsmin = '180'


        # Create WCELL
        for i in lst_wcell:
            # расчёт доп параметров
            if lst_wcell.index(i) + 1 in (1, 2, 3):
                Tcell = '0'
                sector_id = '1'
            elif lst_wcell.index(i) + 1 in (4, 5, 6):
                Tcell = '3'
                sector_id = '2'
            elif lst_wcell.index(i) + 1 in (7, 8, 9):
                Tcell = '1'
                sector_id = '3'
            elif lst_wcell.index(i) + 1 in (10, 11, 12):
                Tcell = '4'
                sector_id = '4'
            elif lst_wcell.index(i) + 1 in (13, 14, 15):
                Tcell = '2'
                sector_id = '5'
            elif lst_wcell.index(i) + 1 in (16, 17, 18):
                Tcell = '5'
                sector_id = '6'

            pwsmshutdownOrder = '0'
            if lst_wcell.index(i) in (3, 6, 9, 12, 15, 18):
                pwsmshutdownOrder = '1'

            managedObject = ET.SubElement(cmData, 'managedObject', cls_wcell, version='mcRNC17', distName=
            f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/WBTS-{wbts_obj.WBTS_ID}/WCEL-{lst_wcell.index(i) + 1}',
                                          operation='create')

            p_name = ET.SubElement(managedObject, 'p', name='AdminCellState')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AppAwareRANCapability')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='CellRange')
            p_name.text = '10000'
            p_name = ET.SubElement(managedObject, 'p', name='CId')
            p_name.text = str(i.CI)
            p_name = ET.SubElement(managedObject, 'p', name='CSGroupId')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CTCHCapaHighPri')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CUCEcNoThreshold')
            p_name.text = '31'
            p_name = ET.SubElement(managedObject, 'p', name='CUCRSCPThreshold')
            p_name.text = '-92'
            p_name = ET.SubElement(managedObject, 'p', name='DRXInactiveTimerHSFACH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='EVAMCapability')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHCapability')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHCapability')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='LAC')
            p_name.text = str(i.LAC)
            p_name = ET.SubElement(managedObject, 'p', name='MDTPeriodicMeasEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='name')
            p_name.text = i.full_name
            p_name = ET.SubElement(managedObject, 'p', name='CellAdditionalInfo')
            p_name.text = i.full_name
            p_name = ET.SubElement(managedObject, 'p', name='OffsetToBeginCTCHBSIndex')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='PCH24kbpsEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='PowerSaveHSPAType')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PRACHDelayRange')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PriScrCode')
            p_name.text = str(i.BSIC)
            p_name = ET.SubElement(managedObject, 'p', name='PSGroupId')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PtxPrimaryCPICH')
            p_name.text = ptxprimarycpich
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVLimitDCHSDPA')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVLimitNRTHSDPA')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVLimitRTDCH')
            p_name.text = '37'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVLimitRTHSDPA')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVPwrNRTHSDPA')
            p_name.text = '31'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMAVPwrRTHSDPA')
            p_name.text = '37'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMCellGroup')
            p_name.text = sector_id
            p_name = ET.SubElement(managedObject, 'p', name='PWSMEXPwrLimit')
            p_name.text = '37'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMEXUsrLimit')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDLimitDCHSDPA')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDLimitNRTDCH')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDLimitNRTHSDPA')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDLimitRTDCH')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDLimitRTHSDPA')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDPwrNRTHSDPA')
            p_name.text = '34'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDPwrRTDCH')
            p_name.text = '37'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMSDPwrRTHSDPA')
            p_name.text = '34'
            p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownOrder')
            p_name.text = pwsmshutdownOrder
            p_name = ET.SubElement(managedObject, 'p', name='PWSMShutdownRemCell')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RAC')
            p_name.text = str(i.RAC)
            p_name = ET.SubElement(managedObject, 'p', name='RACHCapacity')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='RelocComm_in_InterRNC_HHO')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RNARGroupId')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RRCconnRepTimer1')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='RRCconnRepTimer2')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='SABEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SAC')
            p_name.text = str(i.SAC)
            p_name = ET.SubElement(managedObject, 'p', name='SACB')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='ShutdownStepAmount')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='ShutdownWindow')
            p_name.text = '15'
            p_name = ET.SubElement(managedObject, 'p', name='SIB11bisLength')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SIB11Length')
            p_name.text = '55'
            p_name = ET.SubElement(managedObject, 'p', name='SIB12Length')
            p_name.text = '23'
            p_name = ET.SubElement(managedObject, 'p', name='Tcell')
            p_name.text = Tcell
            p_name = ET.SubElement(managedObject, 'p', name='ToAWE_CCH')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='ToAWS_CCH')
            p_name.text = '25'
            p_name = ET.SubElement(managedObject, 'p', name='UARFCN')
            p_name.text = str(i.Channel)
            p_name = ET.SubElement(managedObject, 'p', name='UTRAN_DRX_length')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='WCELMCC')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='WCELMNC')
            p_name.text = '01'
            p_name = ET.SubElement(managedObject, 'p', name='WCelState')
            p_name.text = '129'
            p_name = ET.SubElement(managedObject, 'p', name='AdminPICState')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='AmpliRatioOptHSRACH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AMROverSC')
            p_name.text = '90'
            p_name = ET.SubElement(managedObject, 'p', name='AMROverTransmission')
            p_name.text = '9'
            p_name = ET.SubElement(managedObject, 'p', name='AMROverTxNC')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='AMROverTxNonHSPA')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AMROverTxTotal')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='AMRSF')
            p_name.text = '-2'
            p_name = ET.SubElement(managedObject, 'p', name='AMRTargetSC')
            p_name.text = '70'
            p_name = ET.SubElement(managedObject, 'p', name='AMRTargetTransmission')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='AMRTargetTxNC')
            p_name.text = '-20'
            p_name = ET.SubElement(managedObject, 'p', name='AMRTargetTxNonHSPA')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='AMRTargetTxTotal')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AMRUnderSC')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='AMRUnderTransmission')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='AMRUnderTxNC')
            p_name.text = '-100'
            p_name = ET.SubElement(managedObject, 'p', name='AMRUnderTxNonHSPA')
            p_name.text = '-100'
            p_name = ET.SubElement(managedObject, 'p', name='AMRUnderTxTotal')
            p_name.text = '-100'
            p_name = ET.SubElement(managedObject, 'p', name='AssignedPICPool')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CableLoss')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='CCHSetupEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CIRForFDPCH')
            p_name.text = '-44'
            p_name = ET.SubElement(managedObject, 'p', name='CodeTreeOptimisation')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='CodeTreeOptimisationGuardTime')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CodeTreeOptTimer')
            p_name.text = '3600'
            p_name = ET.SubElement(managedObject, 'p', name='CodeTreeUsage')
            p_name.text = '60'
            p_name = ET.SubElement(managedObject, 'p', name='CPICHEcNoSRBMapRRC')
            p_name.text = '-16'
            p_name = ET.SubElement(managedObject, 'p', name='CPICHRSCPSRBMapRRC')
            p_name.text = '-92'
            p_name = ET.SubElement(managedObject, 'p', name='CPICHtoRefRABoffset')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='CSAMRModeSET')
            p_name.text = '15'
            p_name = ET.SubElement(managedObject, 'p', name='CSAMRModeSETWB')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='DPCHOverHSPDSCHThreshold')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='DRRCprxMargin')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DRRCprxOffset')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='DRRCptxMargin')
            p_name.text = '-5'
            p_name = ET.SubElement(managedObject, 'p', name='DRRCptxOffset')
            p_name.text = '-30'
            p_name = ET.SubElement(managedObject, 'p', name='EbNoSetIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='EvamDInit')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='EVAMInUse')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='EvamNumPhaseOffset')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='EvamTKeep')
            p_name.text = '4320'
            p_name = ET.SubElement(managedObject, 'p', name='EvamTSweep')
            p_name.text = '216'
            p_name = ET.SubElement(managedObject, 'p', name='FDPCHCodeChangeEnabled')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='FDPCHEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='FDPCHSetup')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HappyBitDelayConHSRACH')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPA64QAMallowed')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPA64UsersEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAenabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHRel7ConSetupEC')
            p_name.text = '458124'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHRel8ConSetupEC')
            p_name.text = '458124'
            p_name = ET.SubElement(managedObject, 'p', name='HSPA128UsersPerCell')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSPA72UsersPerCell')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSPDSCHCodeSet')
            p_name.text = '54560'
            p_name = ET.SubElement(managedObject, 'p', name='HSPDSCHMarginSF128')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHExtendedAI')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHImplicitRelease')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHMaxAllocTimeCCCH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHMaxPeriodCollis')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHSubChannelNumber')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHTransmisBackOff')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='HSUPA16QAMAllowed')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSUPA2MSTTIEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSUPAUserLimit16QAM')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='MaxBitRateDLPSNRT')
            p_name.text = '384'
            p_name = ET.SubElement(managedObject, 'p', name='MaxBitRateULPSNRT')
            p_name.text = '384'
            p_name = ET.SubElement(managedObject, 'p', name='MaxCodeReleases')
            p_name.text = '40'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNbrOfHSSCCHCodes')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='MHA')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PICState')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='PowerOffsetPreamHSRACH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PrxLoadMarginDCH')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='PrxLoadMarginMaxDCH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PrxOffsetWPS')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='PtxCellMax')
            p_name.text = ptxcellmax
            p_name = ET.SubElement(managedObject, 'p', name='PtxDLabsMax')
            p_name.text = ptxdlabsmax
            p_name = ET.SubElement(managedObject, 'p', name='PtxFDPCHMax')
            p_name.text = '90'
            p_name = ET.SubElement(managedObject, 'p', name='PtxFDPCHMin')
            p_name.text = '200'
            p_name = ET.SubElement(managedObject, 'p', name='PtxMaxHSDPA')
            p_name.text = ptxmaxhsdpa
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetExxCH2ms')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetExxCHSHO')
            p_name.text = '12'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetFDPCHSHO')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetWPS')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='PtxPSstreamAbsMax')
            p_name.text = '370'
            p_name = ET.SubElement(managedObject, 'p', name='FMCLIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetTotMax')
            p_name.text = '32767'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetTotMin')
            p_name.text = '32767'
            p_name = ET.SubElement(managedObject, 'p', name='RefServForCodePower')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RxDivIndicator')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='SectorID')
            p_name.text = sector_id
            p_name = ET.SubElement(managedObject, 'p', name='SIRDPCCHOffsetEDPCH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SRBBitRateRRCSetupEC')
            p_name.text = '218623'
            p_name = ET.SubElement(managedObject, 'p', name='SRBMapRRCSetupEC')
            p_name.text = '457728'
            p_name = ET.SubElement(managedObject, 'p', name='TPCCommandERTarget')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='UEtxPowerMaxDPCH')
            p_name.text = '24'
            p_name = ET.SubElement(managedObject, 'p', name='UEtxPowerMaxPRACH')
            p_name.text = '21'
            p_name = ET.SubElement(managedObject, 'p', name='UEtxPowerMaxPRACHConn')
            p_name.text = '21'
            p_name = ET.SubElement(managedObject, 'p', name='UsersPerHSSCCHCode')
            p_name.text = '32'
            p_name = ET.SubElement(managedObject, 'p', name='WACSetIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='VoiceCallPriority')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='BlindHOEcNoThrTarget')
            p_name.text = '-24'
            p_name = ET.SubElement(managedObject, 'p', name='BlindHORSCPThrTarget')
            p_name.text = '-95'
            p_name = ET.SubElement(managedObject, 'p', name='CellWeightForHSDPALayering')
            p_name.text = '80'
            p_name = ET.SubElement(managedObject, 'p', name='DCellHSDPACapaHO')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DCellHSDPAFmcsId')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='DirectedRRCEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DirectedRRCForHSDPALayerEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='DirectSCCEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DLLoadStateTTT')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='FastActOfTargetServCell')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='FastCompletionOfSCC')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='FastHSPAMobilityEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HHoMaxAllowedBitrateDL')
            p_name.text = '32'
            p_name = ET.SubElement(managedObject, 'p', name='HHoMaxAllowedBitrateUL')
            p_name.text = '32'
            p_name = ET.SubElement(managedObject, 'p', name='HSCapabilityHONumbUE')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='HSCapabilityHOPeriod')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPACellChangeMinInterval')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPACPICHAveWindow')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPACPICHReportPeriod')
            p_name.text = '9'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAFmcgIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAFmciIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAFmcsIdentifier')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPALayeringCommonChEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAMaxCellChangeRepetition')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPAServCellWindow')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSDPASRBWindow')
            p_name.text = '255'
            p_name = ET.SubElement(managedObject, 'p', name='HSLoadStateHSDBRLimit')
            p_name.text = '32'
            p_name = ET.SubElement(managedObject, 'p', name='HSLoadStateHSDOffset')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='HSLoadStateHSUBRLimit')
            p_name.text = '24'
            p_name = ET.SubElement(managedObject, 'p', name='HSLoadStateHSUOffset')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='HSLoadStateHSUResThr')
            p_name.text = '7'
            p_name = ET.SubElement(managedObject, 'p', name='HSPACapaHO')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSPAFmcsIdentifier')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='HSPASCCSpecificATO')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='LayeringRRCRelEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='LHOCapaReqRejRateDL')
            p_name.text = '70'
            p_name = ET.SubElement(managedObject, 'p', name='LHOCapaReqRejRateUL')
            p_name.text = '70'
            p_name = ET.SubElement(managedObject, 'p', name='LHODelayOFFCapaReqRejRate')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='LHODelayOFFHardBlocking')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='LHODelayOFFInterference')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='LHODelayOFFResRateSC')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHardBlockingBaseLoad')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHardBlockingRatio')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHystTimeCapaReqRejRate')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHystTimeHardBlocking')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHystTimeInterference')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='LHOHystTimeResRateSC')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='LHONRTTrafficBaseLoad')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='LHONumbUEInterFreq')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='LHONumbUEInterRAT')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='LHOPwrOffsetDL')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='LHOPwrOffsetUL')
            p_name.text = '-40'
            p_name = ET.SubElement(managedObject, 'p', name='LHOResRateSC')
            p_name.text = '90'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeOFFCapaReqRejRate')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeOFFHardBlocking')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeOFFInterference')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeOFFResRateSC')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeONCapaReqRejRate')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeONHardBlocking')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeONInterference')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LHOWinSizeONResRateSC')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='LTECellReselection')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberUECmSLHO')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBInactivityEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBLoadInfoDistr')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBMobilityEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBRABSetupEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBRABSetupMultiRAB')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='MBLBStateTransEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MIMOHSDPACapaHO')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='NrtFmcgIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='NrtFmciIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='NrtFmcsIdentifier')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PFLIdentifier')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PowerOffsetUpdMsgSize')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RtFmcgIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RtFmciIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RtFmcsIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RTWithHSDPAFmcgIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RTWithHSDPAFmciIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RTWithHSDPAFmcsIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RTWithHSPAFmcsIdentifier')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='ServHONumbUEInterFreq')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='ServHONumbUEInterRAT')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='ServHOPeriodInterFreq')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='ServHOPeriodInterRAT')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SRBDCHFmcsId')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SRBHSPAFmcsId')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemBackgroundCall')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemConversationalCall')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemDetach')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemEmergencyCall')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemHighPrioritySignalling')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemInteractiveCall')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsysteminterRATchangeorder')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsysteminterRATreselection')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemLowPrioritySignalling')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemMBMSrbrequest')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemMBMSreception')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Targetsystemreestablishment')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Targetsystemregistration')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemStreamingCall')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetsystemSubscribedTraffic')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Targetsystemunknown')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AutoACDSACRestriction')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='AutoACResULOLThr')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='AutoACRPrxTotalAvgWs')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='MaxIncrInterferenceUL')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PrxMeasFilterCoeff')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PrxNoise')
            p_name.text = '-1050'
            p_name = ET.SubElement(managedObject, 'p', name='PrxNoiseAutotuning')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='PrxOffset')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTarget')
            p_name.text = '60'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetMax')
            p_name.text = '65535'
            p_name = ET.SubElement(managedObject, 'p', name='PtxMeasFilterCoeff')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffset')
            p_name.text = ptxoffset
            p_name = ET.SubElement(managedObject, 'p', name='PtxTarget')
            p_name.text = ptxtarget
            p_name = ET.SubElement(managedObject, 'p', name='RACHmeasFilterCoeff')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='VoiceOverrideSTHSUPA')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='DPCModeChangeSupport')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='PO1_15')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='PO1_30')
            p_name.text = '12'
            p_name = ET.SubElement(managedObject, 'p', name='PO1_60')
            p_name.text = '16'
            p_name = ET.SubElement(managedObject, 'p', name='PowerOffsetLastPreamblePRACHmessage')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PowerRampStepPRACHpreamble')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PRACHRequiredReceivedCI')
            p_name.text = '-25'
            p_name = ET.SubElement(managedObject, 'p', name='PtxAICH')
            p_name.text = '-8'
            p_name = ET.SubElement(managedObject, 'p', name='PtxBCCHHSPDSCH')
            p_name.text = '70'
            p_name = ET.SubElement(managedObject, 'p', name='PtxBCCHHSSCCH')
            p_name.text = '-20'
            p_name = ET.SubElement(managedObject, 'p', name='PtxMaxEHICH')
            p_name.text = '84'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetEAGCH')
            p_name.text = '108'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetEAGCHDPCCH')
            p_name.text = '128'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetEHICHDPCCH')
            p_name.text = '128'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetERGCH')
            p_name.text = '84'
            p_name = ET.SubElement(managedObject, 'p', name='PtxOffsetERGCHDPCCH')
            p_name.text = '128'
            p_name = ET.SubElement(managedObject, 'p', name='PTxPICH')
            p_name.text = '-8'
            p_name = ET.SubElement(managedObject, 'p', name='PtxPrimaryCCPCH')
            p_name.text = '-50'
            p_name = ET.SubElement(managedObject, 'p', name='PtxPrimarySCH')
            p_name.text = '-30'
            p_name = ET.SubElement(managedObject, 'p', name='PtxSCCPCH1')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PtxSCCPCH2')
            p_name.text = '-50'
            p_name = ET.SubElement(managedObject, 'p', name='PtxSCCPCH2SF128')
            p_name.text = '-20'
            p_name = ET.SubElement(managedObject, 'p', name='PtxSCCPCH3')
            p_name.text = '-20'
            p_name = ET.SubElement(managedObject, 'p', name='PtxSecSCH')
            p_name.text = '-30'
            p_name = ET.SubElement(managedObject, 'p', name='RsrvdSignaturesOffset')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='ActivationTimeOffset')
            p_name.text = '65535'
            p_name = ET.SubElement(managedObject, 'p', name='AltScramblingCodeCM')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AppAwareRANEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='ATOSRBsOnHSPA')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='CPCEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='DCellAndMIMOUsage')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DCellHSDPAEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='DCellHSUPAEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DeltaPrxMaxDown')
            p_name.text = '15'
            p_name = ET.SubElement(managedObject, 'p', name='DeltaPrxMaxUp')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='DeltaPtxMaxDown')
            p_name.text = '15'
            p_name = ET.SubElement(managedObject, 'p', name='DeltaPtxMaxUp')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='DRXCycleHSFACH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='DRXInterruptHSDSCHData')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='EDCHMinimumSetETFCI')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='EDCHMinSetETFCIT0')
            p_name.text = '29'
            p_name = ET.SubElement(managedObject, 'p', name='FachLoadMarginCCH')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='FachLoadThresholdCCH')
            p_name.text = '75'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHActivityAveWin')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHActivityThr')
            p_name.text = '16'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHActTimeToTrigger')
            p_name.text = '100'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHDRXEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHRABDRAEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHRLCTimeToTrigger')
            p_name.text = '200'
            p_name = ET.SubElement(managedObject, 'p', name='HSFACHVolThrDL')
            p_name.text = '512'
            p_name = ET.SubElement(managedObject, 'p', name='HspaMultiNrtRabSupport')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSPAQoSEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSPwrOffsetUpdateDelay')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHActivityAveWin')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHActivityThr')
            p_name.text = '12'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHActTimeToTrigger')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHCommonEDCHRes')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHMaxTotSymbolRate')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHMPO')
            p_name.text = '12'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHTimeToTrigger')
            p_name.text = '100'
            p_name = ET.SubElement(managedObject, 'p', name='HSRACHVolThrUL')
            p_name.text = '512'
            p_name = ET.SubElement(managedObject, 'p', name='HSUPAEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='InitialBitRateDL')
            p_name.text = '64'
            p_name = ET.SubElement(managedObject, 'p', name='InitialBitRateUL')
            p_name.text = '64'
            p_name = ET.SubElement(managedObject, 'p', name='MassEventHandler')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberEDCHCell')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberEDCHS')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberHSDPAUsers')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberHSDSCHMACdFlows')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberUECmHO')
            p_name.text = '16'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberUEHSPACmHO')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumberUEHSPACmNCHO')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumbHSDPAUsersS')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxNumbHSDSCHMACdFS')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MaxTotalUplinkSymbolRate')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='MEHHSDPAUserNbrCQI')
            p_name.text = '25'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHEnabled')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHCellStates')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHOptions')
            p_name.text = '26'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHLowHSUPATput')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHNormalHSUPATput')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHPreventivePrxOffset')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='EMEHReactivePrxOffset')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='MEHHSUPAUserNbr2msTTI')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='MEHLoadStateTtT')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='MEHMaxHSUPAUsers')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='MEHQueueThreshold')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='MEHULLHSDPAUALimit')
            p_name.text = '35'
            p_name = ET.SubElement(managedObject, 'p', name='MIMOEnabled')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MIMOWith64QAMUsage')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='MinAllowedBitRateDL')
            p_name.text = '32'
            p_name = ET.SubElement(managedObject, 'p', name='MinAllowedBitRateUL')
            p_name.text = '16'
            p_name = ET.SubElement(managedObject, 'p', name='NASsignVolThrDL')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='NASsignVolThrUL')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='NumberEDCHReservedSHOBranchAdditions')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='OCdlNrtDCHgrantedMinAllocT')
            p_name.text = '60'
            p_name = ET.SubElement(managedObject, 'p', name='OCULNRTDCHGrantedMinAllocT')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PBSgrantedMinDCHallocTequalP')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='PBSgrantedMinDCHallocThigherP')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='PBSgrantedMinDCHallocTlowerP')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PrxLoadMarginEDCH')
            p_name.text = '20'
            p_name = ET.SubElement(managedObject, 'p', name='PrxMaxOrigTargetBTS')
            p_name.text = '80'
            p_name = ET.SubElement(managedObject, 'p', name='PrxMaxTargetBTS')
            p_name.text = '80'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSMax')
            p_name.text = '60'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSMaxtHSRACH')
            p_name.text = '32767'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSMin')
            p_name.text = '60'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSStepDown')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PrxTargetPSStepUp')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PtxHighHSDPAPwr')
            p_name.text = ptxhighhsdpapwr
            p_name = ET.SubElement(managedObject, 'p', name='PtxMarginCCH')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSAdjustPeriod')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSMax')
            p_name.text = ptxtargetpsmax
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSMaxtHSRACH')
            p_name.text = '32767'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSMin')
            p_name.text = ptxtargetpsmin
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSStepDown')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PtxTargetPSStepUp')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='PtxThresholdCCH')
            p_name.text = '-10'
            p_name = ET.SubElement(managedObject, 'p', name='RachLoadMarginCCH')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='RachLoadThresholdCCH')
            p_name.text = '75'
            p_name = ET.SubElement(managedObject, 'p', name='RXBurstHSFACH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SmartTrafVolThrDL')
            p_name.text = '256'
            p_name = ET.SubElement(managedObject, 'p', name='SmartTrafVolThrUL')
            p_name.text = '256'
            p_name = ET.SubElement(managedObject, 'p', name='T321')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='TargetNSEDCHToTotalEDCHPR')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='TrafVolThresholdDLLow')
            p_name.text = '256'
            p_name = ET.SubElement(managedObject, 'p', name='ULLoadStateHSUBRLimit')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='ULLoadStateHSUOffset')
            p_name.text = '-5'
            p_name = ET.SubElement(managedObject, 'p', name='VCPMaxHSDPAUsers')
            p_name.text = '30'
            p_name = ET.SubElement(managedObject, 'p', name='VCPPtxOffset')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AbsPrioCellReselec')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='ACBarredList')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AICHTraTime')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='AllowedRACHSubChannels')
            p_name.text = '4095'
            p_name = ET.SubElement(managedObject, 'p', name='Cell_Reserved')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='CellBarred')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='CellSelQualMeas')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='DefMeasCtrlReading')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='GSMCellReselection')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HCS_PRIO')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='InterFreqScaleTresel')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='InterRATScaleTresel')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='IntraFreq_Cell_Reselect_Ind')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='KforCTCH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='N300')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='N312')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='N312Conn')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='N313')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='N315')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='NbrOfSCCPCHs')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='NCr')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='NforCTCH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='NonHCSNcr')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='NonHCSTcrMax')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='NonHCSTcrMaxHyst')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='PI_amount')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='PRACH_preamble_retrans')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='PRACHScramblingCode')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='QHCS')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst1')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst1FACH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst1PCH')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst2')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst2FACH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='Qhyst2PCH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='QqualMin')
            p_name.text = '-18'
            p_name = ET.SubElement(managedObject, 'p', name='QrxlevMin')
            p_name.text = '-56'
            p_name = ET.SubElement(managedObject, 'p', name='RACH_tx_Max')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='RACH_Tx_NB01max')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='RACH_Tx_NB01min')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='RACHInterFreqMesQuant')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='RACHIntraFreqMesQuant')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SHCS_RAT')
            p_name.text = '-1'
            p_name = ET.SubElement(managedObject, 'p', name='SHCS_RATConn')
            p_name.text = '-1'
            p_name = ET.SubElement(managedObject, 'p', name='SIB4Indicator')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='SIB7factor')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Sintersearch')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='SintersearchConn')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='Sintrasearch')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='SintrasearchConn')
            p_name.text = '5'
            p_name = ET.SubElement(managedObject, 'p', name='Slimit_SearchRAT')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='Slimit_SearchRATConn')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='SpeedScaleTresel')
            p_name.text = '7'
            p_name = ET.SubElement(managedObject, 'p', name='Sprioritysearch1')
            p_name.text = '7'
            p_name = ET.SubElement(managedObject, 'p', name='Sprioritysearch2')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='Ssearch_RAT')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='Ssearch_RATConn')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='SsearchHCS')
            p_name.text = '-1'
            p_name = ET.SubElement(managedObject, 'p', name='SsearchHCSConn')
            p_name.text = '-1'
            p_name = ET.SubElement(managedObject, 'p', name='SmartLTELayeringEnabled')
            p_name.text = '8'
            p_name = ET.SubElement(managedObject, 'p', name='T300')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='T312')
            p_name.text = '6'
            p_name = ET.SubElement(managedObject, 'p', name='T312Conn')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='T313')
            p_name.text = '3'
            p_name = ET.SubElement(managedObject, 'p', name='T315')
            p_name.text = '4'
            p_name = ET.SubElement(managedObject, 'p', name='TBarred')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='TCrmax')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='TCrmaxHyst')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Threshservlow')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='Threshservlow2')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='Treselection')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='TreselectionFACH')
            p_name.text = '10'
            p_name = ET.SubElement(managedObject, 'p', name='TreselectionPCH')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='UseOfHCS')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='WCDMACellReselection')
            p_name.text = '0'
            l_name = ET.SubElement(managedObject, 'list', name='URAId')
            lst = ET.SubElement(l_name, 'p')
            lst.text = '1'

        # Create HO 3G > LTE
        for i in lst_wcell:
            # LTE 2600
            managedObject = ET.SubElement(cmData, 'managedObject', cls_adjl, version='mcRNC17', distName=
            f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/WBTS-{wbts_obj.WBTS_ID}/WCEL-{lst_wcell.index(i) + 1}/ADJL-1')

            p_name = ET.SubElement(managedObject, 'p', name='ADJLChangeOrigin')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLEARFCN')
            p_name.text = '2900'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLMeasBw')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLSelectFreq')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HopLIdentifier')
            p_name.text = '1'

            # LTE 1800
            managedObject = ET.SubElement(cmData, 'managedObject', cls_adjl, version='mcRNC17', distName=
            f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/WBTS-{wbts_obj.WBTS_ID}/WCEL-{lst_wcell.index(i) + 1}/ADJL-2')

            p_name = ET.SubElement(managedObject, 'p', name='ADJLChangeOrigin')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLEARFCN')
            p_name.text = '1700'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLMeasBw')
            p_name.text = '50'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLSelectFreq')
            p_name.text = '0'
            p_name = ET.SubElement(managedObject, 'p', name='HopLIdentifier')
            p_name.text = '2'

            # LTE 900
            managedObject = ET.SubElement(cmData, 'managedObject', cls_adjl, version='mcRNC17', distName=
            f'PLMN-PLMN/RNC-{wbts_obj.WBTS_RNC}/WBTS-{wbts_obj.WBTS_ID}/WCEL-{lst_wcell.index(i) + 1}/ADJL-3')

            p_name = ET.SubElement(managedObject, 'p', name='ADJLChangeOrigin')
            p_name.text = '2'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLEARFCN')
            p_name.text = '3676'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLMeasBw')
            p_name.text = '25'
            p_name = ET.SubElement(managedObject, 'p', name='AdjLSelectFreq')
            p_name.text = '1'
            p_name = ET.SubElement(managedObject, 'p', name='HopLIdentifier')
            p_name.text = '3'

        # Запись всех данных в file WCELL.xml
        xml_string = ET.tostring(new).decode(errors='ignore')
        xml_prettyxml = minidom.parseString(xml_string).toprettyxml()

        if bs_type == 'normal':
            with open(f'C:\Python\Create_3G_NSN\{folder_name}\{wbts_obj.BS_Name}_WCELL_{wbts_obj.WBTS_ID}.xml',
                      'w') as xml_file:
                xml_file.write(xml_prettyxml)
        if bs_type == 'flexi':
            with open(f'C:\Python\Create_3G_NSN\{folder_name}\{wbts_obj.BS_Name}_flexi_WCELL_{wbts_obj.WBTS_ID}.xml',
                      'w') as xml_file:
                xml_file.write(xml_prettyxml)
        if bs_type == 'micro':
            with open(f'C:\Python\Create_3G_NSN\{folder_name}\{wbts_obj.BS_Name}_micro_WCELL_{wbts_obj.WBTS_ID}.xml',
                      'w') as xml_file:
                xml_file.write(xml_prettyxml)



