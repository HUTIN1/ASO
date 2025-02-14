from Methode.Methode import Methode
from Methode.Progress import DisplayALIIOS,DisplayASOIOS,DisplayCrownSeg
import slicer
import webbrowser
import glob
import os
import vtk
import shutil

class Auto_IOS(Methode):
    def __init__(self, widget):
        super().__init__(widget)


        self.list_landmark = {'DB','MB','O','CB','CL','OIP','R','RIP'}
        self.list_teeth = {'UR1', 'UR2', 'UR3', 'UR4', 'UR5', 'UR6', 'UR7', 'UR8', 'UL1', 'UL2', 'UL3', 'UL4', 'UL5', 'UL6', 'UL7', 'UL8', 
        'LL1', 'LL2', 'LL3', 'LL4', 'LL5', 'LL6', 'LL7', 'LL8', 'LR1', 'LR2', 'LR3', 'LR4', 'LR5', 'LR6', 'LR7', 'LR8'}
        self.list_landmark_exit = []


    def NumberScan(self, scan_folder: str):
            
        return len(super().search(scan_folder,'.vtk')['.vtk'])


    def TestScan(self, scan_folder: str):
        out = None
        if self.NumberScan(scan_folder) == 0 :
            out = 'Give folder with vkt file'
        return out

    def TestModel(self, model_folder: str,lineEditName) -> str:
        files = self.search(model_folder,'.pth')['.pth']
        out = None
        if 'lineEditModelSegOr' == lineEditName:
            if len(files) != 1 :
                out = 'Please give folder with only one .pth file'


        # elif lineEditName == 'lineEditModelAli':
        #     if len(files) !=4 :
        #         out == 'Please five folder with 4 .pth files'

        return out
        
    def TestReference(self, ref_folder: str):
        
        out = []
        if ref_folder!= '':
            dic = self.search(ref_folder,'.vtk','.json')
            if len(dic['.json']) == 0:
                out.append('Please choose a folder with json file')
            elif len(dic['.json'])>2:
                out.append( 'Too many json file ')

            if len(dic['.vtk']) ==0:
                out.append('Please choose a folder with vkt file')
            
            elif len(dic['.vtk'])>2:
                out.append('Too many vkt file in reference folder')

        else :
            out = 'Give reference folder with json and vtk file'

        if len(out)== 0:
            out = None
        
        else :
            out = ' '.join(out)
        return out

    def TestCheckbox(self,dic_checkbox) -> str:
        list_teeth, list_landmark, mix, jaw = self.__CheckboxisChecked(dic_checkbox)
        out = []
        if len(list_teeth) != 3 and len(list_teeth)!=4:
             out.append('Give 3 teeth or 4')


        if len(jaw)<1 :
            out.append('Choose one jaw')

        # dif_landmark = list(set(mix)-set(self.list_landmark_exit))
        # if len(dif_landmark) != 0:
        #     out.append(f'This landmark {" ".join(dif_landmark)} are not available please select another one, choose in this list {" ".join(self.list_landmark_exit)}')

        dic = {'Upper': {'left': ['UR8', 'UR7', 'UR6', 'UR5', 'UR4', 'UR3'], 'middle': ['UR2', 'UR1', 'UL1', 'UL2'], 'right': ['UL3', 'UL4', 'UL5', 'UL6', 'UL7', 'UL8']}, 
        'Lower': {'left': ['LR8', 'LR7', 'LR6', 'LR5', 'LR4', 'LR3'], 'middle': ['LR2', 'LR1', 'LL1', 'LL2'], 'right': ['LL3', 'LL4', 'LL5', 'LL6', 'LL7', 'LL8']}}

        print('list teeth',list_teeth)
        if len(jaw) >=1 and len(list_teeth) >= 1 :
            for j in jaw :
                good = 0
                for side in ['left','middle','right']:
                    for tooth in list_teeth:
                        if tooth in dic[j][side] :
                            good += 1 
                            break
                if good != 3 :
                    out.append(f'Please give one right tooth one left tooth and one anterior tooth')


        if len(out) == 0:
            out = None
        else :
            out = ','.join(out)
        return out


    def DownloadRef(self):
        webbrowser.open('https://github.com/HUTIN1/ASO/releases/tag/v1.0.0')

    def DownloadModels(self):
        webbrowser.open('https://github.com/HUTIN1/ASO/releases/tag/v1.0.0')
        # webbrowser.open('https://github.com/HUTIN1/ASO/releases/download/v1.0.0/model_segmentation.zip')
        # webbrowser.open('https://github.com/HUTIN1/ASO/releases/download/v1.0.0/identification_landmark_ios_model.zip')

    def DownloadTestFile(self):
        webbrowser.open("https://github.com/HUTIN1/ASO/releases/tag/v1.0.1")

    def __Model(self,path):
        
        model = self.search(path,'.pth')['.pth'][0]

        return model


        

    def TestProcess(self,**kwargs) -> str:
        out  = ''

        scan = self.TestScan(kwargs['input_folder'])
        if isinstance(scan,str):
            out = out + f'{scan},'

        reference =self.TestReference(kwargs['gold_folder'])
        if isinstance(reference,str):
            out = out + f'{reference},'

        if kwargs['folder_output'] == '':
            out = out + "Give output folder,"

        testcheckbox = self.TestCheckbox(kwargs['dic_checkbox'])
        if isinstance(testcheckbox,str):
            out = out + f"{testcheckbox},"

        if kwargs['add_in_namefile']== '':
            out = out + "Give something to add in name of file,"


        if out != '':
            out=out[:-1]

        else : 
            out = None

        return out


    def __BypassCrownseg__(self,folder,folder_toseg,folder_bypass):
        files = self.search(folder,'.vtk')['.vtk']
        toseg = 0
        for file in files :
            name = os.path.basename(file)
            if self.__isSegmented__(file):
                shutil.copy(file,os.path.join(folder_bypass,name))

            else :
                shutil.copy(file,os.path.join(folder_toseg,name))
                toseg += 1

        return toseg



    def __isSegmented__(self,path):
        properties = ['PredictedID','UniversalID','Universal_ID']
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(path)
        reader.Update()
        surf = reader.GetOutput()
        list_label = [surf.GetPointData().GetArrayName(i) for i in range(surf.GetPointData().GetNumberOfArrays())]
        out = False 
        if True in [label in properties for label in list_label]:
            out = True

        print('segmented', out, path)
        return out


    def Process(self, **kwargs):
        list_teeth, list_landmark , mix, jaw = self.__CheckboxisChecked(kwargs['dic_checkbox']) 

        path_tmp = slicer.util.tempDirectory()
        path_input = os.path.join(path_tmp,'intpu_seg')
        path_seg = os.path.join(path_tmp, 'seg')
        path_preor = os.path.join(path_tmp, 'PreOr')

        if not os.path.exists(path_seg):
            os.mkdir(os.path.join(path_seg))


        if not os.path.exists(path_preor):
            os.mkdir(path_preor)

        if not os.path.exists(path_input):
            os.mkdir(path_input)

        if not os.path.exists(kwargs['folder_output']):
            os.mkdir(kwargs['folder_output'])

        path_error = os.path.join(kwargs['folder_output'],'Error')

        number_scan_toseg = self.__BypassCrownseg__(kwargs['input_folder'],path_input,path_seg)

        parameter_seg = {'input':path_input,
                        'output':path_seg,
                        'rotation':40,
                        'resolution':320,
                        'model':self.__Model(kwargs['model_folder_segor']),
                        'predictedId':'Universal_ID',
                        'sepOutputs':False,
                        'chooseFDI':0,
                        'logPath':kwargs['logPath']
                        }
        parameter_pre_aso= {'input':path_seg,
                        'gold_folder':kwargs['gold_folder'],
                        'output_folder':kwargs['folder_output'],
                        'add_inname':kwargs['add_in_namefile'],
                        'list_teeth':','.join(list_teeth),
                        'jaw':'/'.join(jaw),
                        'folder_error': path_error,
                        'log_path': kwargs['logPath']}

        # parameter_pre_aso= {'input':path_seg,
        #                 'gold_folder':kwargs['gold_folder'],
        #                 'output_folder':path_preor,
        #                 'add_inname':kwargs['add_in_namefile'],
        #                 'list_teeth':','.join(list_teeth),
        #                 'jaw':'/'.join(jaw),
        #                 'folder_error': path_error,
        #                 'log_path': kwargs['logPath']}

        # parameter_aliios ={'input':path_preor,
        #                     'dir_models':kwargs['model_folder_ali'],
        #                     'landmarks':' '.join(list_landmark),
        #                     'teeth':' '.join(list_teeth),
        #                     'save_in_folder':'false',
        #                     'output_dir':path_preor
        #                     }

        # parameter_semi_aso= {'input':path_preor,
        #                     'gold_folder':kwargs['gold_folder'],
        #                     'output_folder':kwargs['folder_output'],
        #                     'add_inname':kwargs['add_in_namefile'],
        #                     'list_landmark':','.join(mix),
        #                     'jaw':'/'.join(jaw),
        #                     'folder_error':path_error,
        #                     'log_path': kwargs['logPath']}

        print('parameter pre aso',parameter_pre_aso)
        print('parameter seg',parameter_seg)
        # print('parameter aliios ',parameter_aliios)
        # print('parameter semi ios',parameter_semi_aso)

        PreOrientProcess = slicer.modules.pre_aso_ios
        SegProcess = slicer.modules.crownsegmentationcli
        aliiosProcess = slicer.modules.ali_ios
        OrientProcess = slicer.modules.semi_aso_ios

# {'Process':SegProcess,'Parameter':parameter_seg},{'Process':PreOrientProcess,'Parameter':parameter_pre_aso},
        list_process = [{'Process':SegProcess,'Parameter':parameter_seg},
        {'Process':PreOrientProcess,'Parameter':parameter_pre_aso},
        # {"Process":aliiosProcess,"Parameter":parameter_aliios},
        # {'Process':OrientProcess,'Parameter':parameter_semi_aso}
        ]


        numberscan = self.NumberScan(kwargs['input_folder'])
        display = {'CrownSegmentationcli':DisplayCrownSeg(number_scan_toseg,kwargs['logPath']),
                    # 'ALI_IOS':DisplayALIIOS(len(mix),numberscan),
                    'PRE_ASO_IOS': DisplayASOIOS(numberscan if len(jaw) ==1 else int(numberscan/2) , jaw,kwargs['logPath'] ),
                    # 'SEMI_ASO_IOS': DisplayASOIOS(numberscan if len(jaw) ==1 else int(numberscan/2) , jaw,kwargs['logPath'] )
                    }
#
        return list_process ,display 

    def DicLandmark(self):
        dic = {'Landmark':{'Occlusal':['O','MB','DB'],'Cervical':['CB','CL','OIP','R','RIP']}}

        return dic





    def existsLandmark(self,folderpath,reference_folder,model_folder):
        out  = None
        if reference_folder!='':
            list_json = self.search(reference_folder,'.json')['.json']
            list_landmark = []
            for file_json in list_json:
                list_landmark += self.ListLandmarksJson(file_json)

            self.list_landmark_exit = list_landmark
            teeth=[]
            landmarks=[]
            for lmk in list_landmark:
                teeth.append(lmk[:3])
                landmarks.append(lmk[3:])
            teeth = set(teeth)
            landmarks = set(landmarks)

            out = {}
            for tooth in self.list_teeth:
                out[tooth]=False
            for lmk in self.list_landmark:
                out[lmk]= False

            for tooth in teeth:
                out[tooth] = True

            for lmk in landmarks:
                out[lmk]= True
            


            print(out)

        return out


    def Sugest(self):
        return ['UR6','UL1','UL6','LL6','LR1','LR6','O']


    def __CheckboxisChecked(self,diccheckbox : dict):
        dic = {'UR8': 1, 'UR7': 2, 'UR6': 3, 'UR5': 4, 'UR4': 5, 'UR3': 6, 'UR2': 7, 'UR1': 8, 'UL1': 9, 'UL2': 10, 'UL3': 11, 
       'UL4': 12, 'UL5': 13, 'UL6': 14, 'UL7': 15, 'UL8': 16, 'LL8': 17, 'LL7': 18, 'LL6': 19, 'LL5': 20, 'LL4': 21, 'LL3': 22, 
       'LL2': 23, 'LL1': 24, 'LR1': 25, 'LR2': 26, 'LR3': 27, 'LR4': 28, 'LR5': 29, 'LR6': 30, 'LR7': 31, 'LR8': 32}
        dic_child = {'A': 'UR5', 'B': 'UR4', 'C': 'UR3', 'D': 'UR2', 'E': 'UR1', 'F': 'UL1', 'G': 'UL2', 'H': 'UL3', 'I': 'UL4', 'J': 'UL5', 'K': 'LL5', 'L': 'LL4', 'M': 'LL3', 'N': 'LL2', 'O': 'LL1', 'P': 'LR1', 'Q': 'LR2', 'R': 'LR3', 'S': 'LR4', 'T': 'LR5'}

        teeth = []
        landmarks= []
        jaw = []
        mix = []
        if not len(diccheckbox) == 0:

            for checkboxs in diccheckbox['Teeth']['Adult'].values():
                for checkbox in checkboxs:
                    if checkbox.isChecked():
                        teeth.append(checkbox.text)

            for checkboxs in diccheckbox['Teeth']['Child'].values():
                for checkbox in checkboxs:
                    if checkbox.isChecked():
                        teeth = list(set(teeth).union(set((dic_child[checkbox.name]))))


            for checkboxs in diccheckbox['Landmark'].values():
                for checkbox in checkboxs:
                    if checkbox.isChecked():
                        landmarks.append(checkbox.text)


            for tooth in teeth :
                for landmark in landmarks :
                    mix.append(f'{tooth}{landmark}')


            for key , checkbox in diccheckbox['Jaw'].items():
                if checkbox.isChecked():
                    jaw.append(key)

        return teeth , landmarks, mix, jaw













class Semi_IOS(Auto_IOS):

       


    def TestScan(self, scan_folder: str):
        out = None
        if scan_folder != '':
            dic = self.search(scan_folder,'vtk','json')
            if len(dic['vtk']) != len(dic['json']): 
                print('dif ',len(dic['vtk']) - len(dic['json']))
                # out = 'Give folder with the same number of vkt file and json file'`

        else :
            out = 'Choose a folder with scan and landmark'
        return out 


    def TestReference(self, ref_folder: str):
        out = []
        if ref_folder!= '':
            dic = self.search(ref_folder,'.json')
            if len(dic['.json']) == 0:
                out.append('Please choose a folder with json file')
            elif len(dic['.json'])>2:
                out.append( 'Too many json file ')
        if len(out) == 0:
            out = None

        else :
            out = out.split(',')
          
        return out
    def TestProcess(self,**kwargs) -> str:
        out  = ''

        scan = self.TestScan(kwargs['input_folder'])
        if isinstance(scan,str):
            out = out + f'{scan},'

        reference =self.TestReference(kwargs['gold_folder'])
        if isinstance(reference,str):
            out = out + f'{reference},'

        if kwargs['folder_output'] == '':
            out = out + "Give output folder,"

        testcheckbox = self.TestCheckbox(kwargs['dic_checkbox'])
        if isinstance(testcheckbox,str):
            out = out + f"{testcheckbox},"

        if kwargs['add_in_namefile']== '':
            out = out + "Give something to add in name of file,"


        if out != '':
            out=out[:-1]

        else : 
            out = None

        return out

    def __CheckboxisChecked(self,diccheckbox : dict):
        
        teeth = []
        landmarks= []
        jaw = []
        mix = []
        if not len(diccheckbox) == 0:

            for checkboxs in diccheckbox['Teeth']['Adult'].values():
                for checkbox in checkboxs:
                    if checkbox.isChecked():
                        teeth.append(checkbox.text)


            for checkboxs in diccheckbox['Landmark'].values():
                for checkbox in checkboxs:
                    if checkbox.isChecked():
                        landmarks.append(checkbox.text)


            for tooth in teeth :
                for landmark in landmarks :
                    mix.append(f'{tooth}{landmark}')


            for key , checkbox in diccheckbox['Jaw'].items():
                if checkbox.isChecked():
                    jaw.append(key)

        return teeth , landmarks, mix, jaw



    def Process(self, **kwargs):
        teeth, landmark , mix , jaw = self.__CheckboxisChecked(kwargs['dic_checkbox'])
        path_error = os.path.join(kwargs['folder_output'],'Error')

        parameter= {'input':kwargs['input_folder'],'gold_folder':kwargs['gold_folder'],
        'output_folder':kwargs['folder_output'],
        'add_inname':kwargs['add_in_namefile'],
        'list_landmark':','.join(mix),
        'jaw':'/'.join(jaw),
        'folder_error':path_error,
        'log_path': kwargs['logPath']}


        print('parameter',parameter)
        OrientProcess = slicer.modules.semi_aso_ios
        numberscan = self.NumberScan(kwargs['input_folder'])
        return [{'Process':OrientProcess,'Parameter':parameter}], { 'SEMI_ASO_IOS': DisplayASOIOS(numberscan if len(jaw) ==1 else int(numberscan/2) , jaw,kwargs['logPath'] )}


    def Sugest(self):
        out = ['O','UL6','UL1','UR1','UR6','LL6','LL1','LR1','LR6']
        return out



    def DownloadTestFile(self):
        webbrowser.open("https://github.com/HUTIN1/ASO/releases/tag/v1.0.2")