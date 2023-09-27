import pandas as pd
import numpy as np


class KAnonymizer:

    def __init__(self,
                 dataset:pd.DataFrame, # Dataset que será anonimizado
                 quasi_identifier:list[str],
                 sensitivity_features:list[str]= None # Lista de features sensiveis a serem retiradas
                 ):
        #Es
        self.__original_data = dataset
        self.__anonymized_data = dataset.copy()

        self._quasi_identifier = quasi_identifier

        if sensitivity_features is not None:
            self._anonymizedData = self._anonymizedData.drop([*sensitivity_features],axis=1)

        # Captura as generalizações de regiao
        self._general_region = pd.DataFrame(index=dataset.index)
        self._general_region[['city', 'country', 'sub-region', 'region']] = dataset['Region'].str.split(';',expand=True)    

        #Captura as generalizações para begindate
        
        self._general_begin_date = pd.DataFrame(index=dataset.index,columns=['year','decade','century'])
        self._general_begin_date['year'] = dataset['BeginDate']
        self._general_begin_date['decade']= dataset['BeginDate'].apply(KAnonymizer.year4decade)
        self._general_begin_date['century'] = dataset['BeginDate'].apply(KAnonymizer.year4century)

        print(self._general_begin_date)

    
    #Setters e Getters

    @property
    def _anonymizedData(self):
        return self.__anonymized_data

    @_anonymizedData.setter
    def _anonymizedData(self,new_data)->pd.DataFrame:
        self.__anonymized_data =new_data


    #Retorna o dataset anonimizado.
    #Metodo usado pelo usuário
    def getAnonymizedData(self)->pd.DataFrame:
        return self._anonymizedData

    #Substitui em uma coluna um certo valor por outro
    def replaceFeatureValues(self, name_feature,old_value, new_value):

        if name_feature not in self._anonymizedData.columns:
            print("Essa feature nao pertence ao dataset")
            return
        
        if old_value=='':
            old_value= np.NaN

        self._anonymizedData= self._anonymizedData.replace({name_feature:{old_value:new_value}})

    #Salva na memória o dataset anonimizado
    def saveAnonymizedData(self,file_name,sep=';'):
        self._anonymizedData.to_csv(path_or_buf=file_name,sep=sep,index=False)

    #Recebe uma lista de feature e as remove do dataset
    def removeSensitivityFeatures(self, sensitivity_features:[str]):
        self._anonymizedData = self._anonymizedData.drop([sensitivity_features],axis=1)

    #Desfazer as alterações feitas no dataset
    def undoAlterations(self):
        self._anonymizedData = self.__original_data.copy()
    
    def verifyKAnonymity(self,):

        count_group = self._anonymizedData.groupby([self._quasi_identifier])[self._quasi_identifier[0]].count()
        print(count_group)

    @staticmethod
    def year4decade(year):

        if not isinstance(year,int):
            raise ValueError("The year must be an integer.")

        digit = year%10

        year = year//10
        
        if digit ==0:
            year-=1
        
        year*=10

        return year

    @staticmethod
    def year4century(year):

        last_2_digit = year %100

        century = year //100
        
        if last_2_digit !=0:
            century += 1
        
        return century
        