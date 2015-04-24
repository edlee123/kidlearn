#!/usr/bin/python
#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        custom_graph
# Purpose: 
#
# Authors:      Bclement, WSchueller
#
# Created:     14-03-2015
# Copyright:   (c) BClement 2015
# Licence:     CreativeCommon
#-------------------------------------------------------------------------------

from custom_graph import *

class Curve(CustomGraph):
    def __init__(self,y,*arg,**kwargs):
        self.keepwinopen=0
        self.sort=1
        self.filename="graph"+time.strftime("%Y%m%d%H%M%S", time.localtime())
        if "filename" in kwargs.keys():
            self.filename=kwargs["filename"]
        self.title=self.filename
        self.xlabel="X"
        self.ylabel="Y"
        self.alpha=0.3

        self.Yoptions=[{}]

        self.xmin=[0,0]
        self.xmax=[0,5]
        self.ymin=[0,0]
        self.ymax=[0,5]
        
        self.std=0
        
        self._y=[y]
        self.stdvec=[0]*len(y)

        if len(arg)!=0:
            self._x=[y]
            self._y=[arg[0]]
        else:
            self._x=[range(0,len(y))]


        self.extensions=["eps","png"]

        for key,value in kwargs.iteritems():
            setattr(self,key,value)

        self.stdvec=[self.stdvec]

        if not isinstance(self.xmin,list):
            temp=self.xmin
            self.xmin=[1,temp]
        if not isinstance(self.xmax,list):
            temp=self.xmax
            self.xmax=[1,temp]
        if not isinstance(self.ymin,list):
            temp=self.ymin
            self.ymin=[1,temp]
        if not isinstance(self.ymax,list):
            temp=self.ymax
            self.ymax=[1,temp]


    def show(self):
        plt.figure()
        plt.ion()
        self.draw()
        plt.show()

    def save(self,*path):
        if len(path)!=0:
            out_path=path[0]
        else:
            out_path=""
        with open(out_path+self.filename+".b", 'wb') as fichier:
            mon_pickler=pickle.Pickler(fichier)
            mon_pickler.dump(self)

    def write_files(self,*path):
        if len(path)!=0:
            out_path=path[0]
        else:
            out_path=""

        self.draw()
        self.save(out_path)
        for extension in self.extensions:
            plt.savefig(out_path+self.filename+"."+extension,format=extension)


    def draw(self):
        colormap=['blue','red','green','black','yellow','cyan','magenta']
        #plt.figure()
        plt.ion()
        plt.cla()
        plt.clf()
        for i in range(0,len(self._y)): 

            Xtemp=self._x[i]
            Ytemp=self._y[i]
            if self.sort:
                tempdic={}
                for j in range(0,len(Xtemp)):
                    tempdic[Xtemp[j]]=Ytemp[j]
                temptup=sorted(tempdic.items())
                for j in range(0,len(temptup)):
                    Xtemp[j]=temptup[j][0]
                    Ytemp[j]=temptup[j][1]

            Xtemp=self._x[i]
            stdtemp=self.stdvec[i]
            if self.sort:
                tempdic={}
                for j in range(0,len(Xtemp)):
                    tempdic[Xtemp[j]]=stdtemp[j]
                temptup=sorted(tempdic.items())
                for j in range(0,len(temptup)):
                    Xtemp[j]=temptup[j][0]
                    stdtemp[j]=temptup[j][1]
            if self.std:
                Ytempmin=[0]*len(Ytemp)
                Ytempmax=[0]*len(Ytemp)
                for j in range(0,len(Ytemp)):
                    Ytempmax[j]=Ytemp[j]+stdtemp[j]
                    Ytempmin[j]=Ytemp[j]-stdtemp[j]
                plt.fill_between(Xtemp,Ytempmin,Ytempmax,alpha=self.alpha,color=colormap[i%7],**self.Yoptions[i])
            plt.plot(Xtemp,Ytemp,color=colormap[i%7],**self.Yoptions[i])
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)

        if self.xmin[0]:
            plt.xlim(xmin=self.xmin[1])
        if self.xmax[0]:
            plt.xlim(xmax=self.xmax[1])
        if self.ymin[0]:
            plt.ylim(ymin=self.ymin[1])
        if self.ymax[0]:
            plt.ylim(ymax=self.ymax[1])
        plt.legend()
        plt.draw()


    def add_graph(self,other_graph):
        self._x=self._x+other_graph._x
        self._y=self._y+other_graph._y
        self.Yoptions=self.Yoptions+other_graph.Yoptions
        self.stdvec=self.stdvec+other_graph.stdvec

    def merge(self):
        Yarray=np.array(self._y)
        stdarray=np.array(self.stdvec)
        stdtemp=[]
        Ytemp=[]
        self.Yoptions=[self.Yoptions[0]]

        for i in range(0,len(self._y[0])):
            Ytemp.append(np.mean(list(Yarray[:,i])))
            stdtemp.append(np.std(list(Yarray[:,i])))
        self._y=[Ytemp]
        self.stdvec=[stdtemp]
        self._x=[self._x[0]]


    def wise_merge(self):
        param_list=[]
        for i in range(len(self.Yoptions)):
            param_list.append(self.Yoptions[i]["label"])
        param_values={}
        for ind,param in enumerate(param_list):
            if param not in param_values.keys():
                param_values[param]=copy.deepcopy(self)
                param_values[param]._x=[self._x[ind]]
                param_values[param]._y=[self._y[ind]]
                param_values[param].Yoptions=[self.Yoptions[ind]]
            else:
                tempgraph=copy.deepcopy(self)
                tempgraph._x=[self._x[ind]]
                tempgraph._y=[self._y[ind]]
                tempgraph.Yoptions=[self.Yoptions[ind]]
                param_values[param].add_graph(copy.deepcopy(tempgraph))
        tempgraph=copy.deepcopy(self)
        tempgraph._x=[]
        tempgraph._y=[]
        tempgraph.Yoptions=[]
        tempgraph.stdvec=[]
        for key in param_values.keys():
            param_values[key].merge()
            tempgraph.add_graph(param_values[key])
        return tempgraph

    def empty(self):
        self._y=[]
        self._x=[]
        self.Yoptions=[]
        self.stdvec=[]


