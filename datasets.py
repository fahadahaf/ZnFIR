import numpy as np
import pandas as pd
import random
import torch
from fastprogress import progress_bar
from random import randint
from torch.utils.data import Dataset


class DatasetLoadAll(Dataset):
    def __init__(self, df_path, num_labels=2, for_embeddings=False):
        self.DNAalphabet = {'A':'0', 'C':'1', 'G':'2', 'T':'3'}
        df_path = df_path.split('.')[0] #just in case the user provide extension
        self.df_all = pd.read_csv(df_path+'.txt',delimiter='\t',header=None)
        self.df_seq = pd.read_csv(df_path+'.fa',header=None)
        strand = self.df_seq[0][0][-3:] #can be (+) or (.) 
        self.df_all['header'] = self.df_all.apply(lambda x: '>'+x[0]+':'+str(x[1])+'-'+str(x[2])+strand, axis=1)
        
        self.chroms = self.df_all[0].unique()
        self.df_seq_all = pd.concat([self.df_seq[::2].reset_index(drop=True), self.df_seq[1::2].reset_index(drop=True)], axis=1, sort=False)
        self.df_seq_all.columns = ["header","sequence"]
        #self.df_seq_all['chrom'] = self.df_seq_all['header'].apply(lambda x: x.strip('>').split(':')[0])
        self.df_seq_all['sequence'].apply(lambda x: x.upper())
        self.num_labels = num_labels
        
        self.df = self.df_all
        self.df_seq_final = self.df_seq_all
            

        self.df = self.df.reset_index()
        self.df_seq_final = self.df_seq_final.reset_index()
        #self.df['header'] = self.df.apply(lambda x: '>'+x[0]+':'+str(x[1])+'-'+str(x[2])+'('+x[5]+')', axis=1)
        if for_embeddings == False:
            self.One_hot_Encoded_Tensors = []
            self.Label_Tensors = []
            self.Seqs = []
            self.Header = []
            for i in progress_bar(range(0,self.df.shape[0])): #tqdm() before
                if self.num_labels == 2:
                    y = self.df[self.df.columns[-2]][i]
                else:
                    y = np.asarray(self.df[self.df.columns[-2]][i].split(',')).astype(int)
                    y = self.one_hot_encode_labels(y)
                header = self.df['header'][i]
                self.Header.append(header)
                X = self.df_seq_final['sequence'][self.df_seq_final['header']==header].array[0].upper()
                X = X.replace('N',list(self.DNAalphabet.keys())[randint(0,3)])
                X = X.replace('N',list(self.DNAalphabet.keys())[random.choice([0,1,2,3])])
                X = X.replace('S',list(self.DNAalphabet.keys())[random.choice([1,2])])
                X = X.replace('W',list(self.DNAalphabet.keys())[random.choice([0,3])])
                X = X.replace('K',list(self.DNAalphabet.keys())[random.choice([2,3])])
                X = X.replace('Y',list(self.DNAalphabet.keys())[random.choice([1,3])])
                X = X.replace('R',list(self.DNAalphabet.keys())[random.choice([0,2])])
                X = X.replace('M',list(self.DNAalphabet.keys())[random.choice([0,1])])
                self.Seqs.append(X)
                X = self.one_hot_encode(X)
                self.One_hot_Encoded_Tensors.append(torch.tensor(X))
                self.Label_Tensors.append(torch.tensor(y))
        
    def __len__(self):
        return self.df.shape[0]
    
    def get_all_data(self):
        return self.df, self.df_seq_final
    
    def get_all_chroms(self):
        return self.chroms
    
    def one_hot_encode(self,seq):
        mapping = dict(zip("ACGT", range(4)))    
        seq2 = [mapping[i] for i in seq]
        return np.eye(4)[seq2].T.astype(np.long)
  
    def one_hot_encode_labels(self,y):
        lbArr = np.zeros(self.num_labels)
        lbArr[y] = 1
        return lbArr.astype(np.long)
    
    def __getitem__(self, idx):
        return self.Header[idx],self.Seqs[idx],self.One_hot_Encoded_Tensors[idx],self.Label_Tensors[idx]


class DatasetLazyLoad(Dataset):
    def __init__(self, df_path, num_labels=2):
        self.DNAalphabet = {'A':'0', 'C':'1', 'G':'2', 'T':'3'}
        df_path = df_path.split('.')[0] #just in case the user provide extension
        self.df_all = pd.read_csv(df_path+'.txt',delimiter='\t',header=None)
        self.df_seq = pd.read_csv(df_path+'.fa',header=None)
        strand = self.df_seq[0][0][-3:] #can be (+) or (.) 
        self.df_all['header'] = self.df_all.apply(lambda x: '>'+x[0]+':'+str(x[1])+'-'+str(x[2])+strand, axis=1)

        
        self.chroms = self.df_all[0].unique()
        self.df_seq_all = pd.concat([self.df_seq[::2].reset_index(drop=True), self.df_seq[1::2].reset_index(drop=True)], axis=1, sort=False)
        self.df_seq_all.columns = ["header","sequence"]
        #self.df_seq_all['chrom'] = self.df_seq_all['header'].apply(lambda x: x.strip('>').split(':')[0])
        self.df_seq_all['sequence'].apply(lambda x: x.upper())
        self.num_labels = num_labels
        
        self.df = self.df_all
        self.df_seq_final = self.df_seq_all
            

        self.df = self.df.reset_index()
        self.df_seq_final = self.df_seq_final.reset_index()
        #self.df['header'] = self.df.apply(lambda x: '>'+x[0]+':'+str(x[1])+'-'+str(x[2])+'('+x[5]+')', axis=1)
        
    def __len__(self):
        return self.df.shape[0]
    
    def get_all_data(self):
        return self.df, self.df_seq_final
    
    def get_all_chroms(self):
        return self.chroms
    
    def one_hot_encode(self,seq):
        mapping = dict(zip("ACGT", range(4)))    
        seq2 = [mapping[i] for i in seq]
        return np.eye(4)[seq2].T.astype(np.long)
  
    def one_hot_encode_labels(self,y):
        lbArr = np.zeros(self.num_labels)
        lbArr[y] = 1
        return lbArr.astype(np.long)
    
    def __getitem__(self, idx):
        if self.num_labels == 2:
            y = self.df[self.df.columns[-2]][idx]
        else:
            y = np.asarray(self.df[self.df.columns[-2]][idx].split(',')).astype(int)
            y = self.one_hot_encode_labels(y)
        header = self.df['header'][idx]
        X = self.df_seq_final['sequence'][self.df_seq_final['header']==header].array[0].upper()
        X = X.replace('N',list(self.DNAalphabet.keys())[randint(0,3)])
        X = X.replace('N',list(self.DNAalphabet.keys())[random.choice([0,1,2,3])])
        X = X.replace('S',list(self.DNAalphabet.keys())[random.choice([1,2])])
        X = X.replace('W',list(self.DNAalphabet.keys())[random.choice([0,3])])
        X = X.replace('K',list(self.DNAalphabet.keys())[random.choice([2,3])])
        X = X.replace('Y',list(self.DNAalphabet.keys())[random.choice([1,3])])
        X = X.replace('R',list(self.DNAalphabet.keys())[random.choice([0,2])])
        X = X.replace('M',list(self.DNAalphabet.keys())[random.choice([0,1])])
        seq = X 
        X = self.one_hot_encode(X)
        return header,seq,torch.tensor(X),torch.tensor(y)


#code borrowed from DeepRAM work
class DatasetEmbd(Dataset):
    def __init__(self, xy=None, model=None, kmer_len=5, stride=1): 
        self.kmer_len= kmer_len
        self.stride= stride
        data=[el[1] for el in xy]
        self.headers = [h[0] for h in xy]
        self.seqs = [h[1] for h in xy]
        words_doc= self.Gen_Words(data,self.kmer_len,self.stride)
        #print(words_doc[0])
        x_data=[self.convert_data_to_index(el,model.wv) for el in words_doc]
        #print(x_data.shape)
       
        self.x_data = np.asarray(x_data,dtype=np.long)
        self.y_data = np.asarray([el[-1] for el in xy ],dtype=np.long)
        self.x_data = torch.Tensor(self.x_data)
        self.y_data = torch.from_numpy(self.y_data)
        self.len=len(self.x_data)
      
    def __getitem__(self, index):
        return self.headers[index], self.seqs[index], self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len
      
    def Gen_Words(self,pos_data,kmer_len,s):
        out=[]
        for i in pos_data:
            kmer_list=[]
            for j in range(0,(len(i)-kmer_len)+1,s):
                  kmer_list.append(i[j:j+kmer_len])
            out.append(kmer_list)     
        return out
    
    def convert_data_to_index(self, string_data, wv):
        index_data = []
        for word in string_data:
            if word in wv:
                index_data.append(wv.vocab[word].index)
        return index_data