#-*- coding: utf-8 -*-
import sys as sys
import numpy as np
import scipy as scipy
import scipy.stats as sstats
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import pylab as pylab
#from my_functions import *
import kidlearn_lib as k_lib
import kidlearn_lib.config.datafile as datafile

import seaborn
seaborn.set_style("darkgrid")

from scipy.cluster.vq import vq, kmeans, whiten, kmeans2
import copy
import colorsys


###################################################################
###                   Variable global Graph                    ###
###################################################################

# legend  position : 0 => top right corner, 1 => dawn right corner, 2 => top left, 3 => dawn left, 4 custom
legendPosTab = [[0, 0, 1, 1], [0, 0, 1, 0.3], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0.3, 0.3, 0]]

# legend questionnaire
legendQuest = [["Facile", "Normal", "Difficile"], ["Amusante", "Normal", "Ennuyeuse"], ["Simple", "Normal", "Compliquée"], ["Oui", "Non", "ne sait pas"], ["Oui", "Non", "ne sait pas"], ["Courte", "Normal", "Longue"], ["Oui", "Non", "Un peu"], ["Oui", "Non", "Un peu"], ["Oui", "Non", "Un peu"], ["Oui", "Non", "Un peu"], ["Oui", "Non", "Un peu"], ["Oui", "Non", "Un peu"]]

en_legendQuest = [["Simple", "Normal", "Difficult"], ["Funny", "Normal", "Boring"], ["Simple", "Normal", "Complicated"], ["Yes", "No", "don't know"], ["Yes", "No", "don't know"], ["Short", "Normal", "Long"], ["Yes", "No", "A little"], ["Yes", "No", "A little"], ["Yes", "No", "A little"], ["Yes", "No", "A little"], ["Yes", "No", "A little"], ["Yes", "No", "A little"]]

#legendQuest = [["Facile","Normal","Difficile"],["Amusant","Normal","Ennuyeux"],["Simple","Normal","Complique"],["Refaire","Pas refaire","Sais pas"],["Appris","Pas appris","Sais pas"],["Court","Normal","Long"],["Fatigue","Pas fatigue","Un peu"],["Distrait","Pas distrait","Un peu"],["Achat 1","Pas achat1","Un peu"],["Rendre","Pas rendre","Un peu"],["Achat 2","Pas achat2","un peu"],["Ameliore","Pas Ameliore","Un peu"]]

# titleQuestionnaire : question
#titleQuestionnaire = ["Comment as-tu trouve vette seance ?","D’apres toi, comment etait la seance ?", "D’apres toi, comment etait la seance ?", "Aimerais-tu refaire une seance comme ça ?", "As-tu appris des choses ?", "Comment as-tu trouve la duree de la seance ?", "As-tu trouve ça fatiguant ?", "As-tu pense à autre chose pendant la seance ?", "Penses-tu savoir payer 1 objet avec des pieces et des billets ?", "Penses-tu savoir rendre la monnaie comme si tu etais un marchand ?", "Penses-tu savoir payer 2 objets avec des pieces et des billets ?", "Crois-tu qu’on puisse ameliorer ces activites ?"]

titleQuestionnaire = ["1.Comment as-tu trouvé \n cette séance ?", "2.D’après toi, comment\n était la séance ?", "3.Comment était la \nprésentation sur l’écran ?", "4.Aimerais-tu refaire une\n séance comme ça ?", "5.As-tu appris des choses ?", "6.Comment as-tu trouvé\n la durée de la séance ?", "7.As-tu trouvé ça fatiguant ?",
                      "8.As-tu pensé à autre \nchose pendant la séance ?", "9.Penses-tu savoir payer 1 objet\n avec des pièces et des billets ?", "10.Penses-tu savoir rendre la monnaie\n comme si tu étais un marchand ?", "11.Penses-tu savoir payer 2 objets\n avec des pièces et des billets ?", "12.Crois-tu qu’on puisse \naméliorer ces activités ?"]

en_titleQuestionnaire = ["1.How did you find \n this session ?", "2.On after you, how\n was the session?", "3.How was the \npresentation on the screen ?", "4.Would you like repeat a\n  session like this?", "5.Did you learn something ?", "6.How did you find\n the session's duration ?", "7.Did you find that exhausting?",
                         "8.Did you think about something \nelse during the session ?", "9.Do you know how to pay an object\n with coin and bills ?", "10.Do you know how to give change\n like you were the merchant   ?", "11.Do you know how to pay two object\n with coin and bills ?", "12.Do you think that we \ncan improve this activity ?"]

###################################################################
###   Plot epic curve with following of population evolution    ###
###################################################################


def compute_orgaSeqDataToPopPlot(data, regroup=2):
    newData = [[] for x in range(len(data[0]))]
    for x in range(len(data[0])):
        for i in range(len(data)):
            newData[x] = newData[x] + data[i][x]

    for x in range(len(newData) / regroup):
        for y in range(len(newData[regroup * x])):
            for j in range(1, regroup):
                newData[regroup * x][y] += newData[regroup * x + j][y]
                newData[regroup * x + j][y] = 0
            newData[regroup * x][y] = 1.0 * newData[regroup * x][y] / regroup

        #newData[4*x] = [(newData[4*x][y]+newData[4*x+1][y]+newData[4*x+2][y]+newData[4*x+3][y])/4 for y in range(len(newData[4*x]))]
        #newData[4*x+1] = [0]*len(newData[4*x+1])
        #newData[4*x+2] = [0]*len(newData[4*x+1])
        #newData[4*x+3] = [0]*len(newData[4*x+1])

    return newData


def plot_popullationFollowing(data, nbStud=0, path="result_xp/pointPopGrpah/", ref=""):

    plt.cla()
    plt.clf()
    plt.close()
    nbStud = data[0][0]
    #nb_y = nb_stud + nb_stud/4
    # print nb_y

    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    data_lvl = []
    for j in range(0, len(data[0])):
        data_lvl.append([])
    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            data_lvl[j].append(data[i][j])

    #N = len(data[0])

    sizeMax = 500
    x = []
    y = []
    for i in range(len(data_lvl)):
        y.append([i + 1] * (len(data_lvl[0]) - 1))
        x.append(range(1, len(data_lvl[0])))

    s = data_lvl
    for ss in range(len(s)):
        for sss in range(len(s[ss])):
            s[ss][sss] = (np.pi * (s[ss][sss])**2) / 10

    for i in range(len(data_lvl)):
        plt.scatter(x[i], y[i], s=s[i])

    plt.yticks(range(len(y) + 1), ["", "M1", "M2", "M3", "M4", "M5", "M6", "R1", "R2", "R3", "R4", "MM1", "MM2", "MM3", "MM4", "RM1", "RM2", "RM3", "RM4"])

    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    """
    from pylab import *
from scipy import *

# reading the data from a csv file
durl = 'http://datasets.flowingdata.com/crimeRatesByState2005.csv'
rdata = genfromtxt(durl,dtype='S8,f,f,f,f,f,f,f,i',delimiter=',')

rdata[0] = zeros(8) # cutting the label's titles
rdata[1] = zeros(8) # cutting the global statistics

x = []
y = []
color = []
area = []

for data in rdata:
 x.append(data[1]) # murder
 y.append(data[5]) # burglary
 color.append(data[6]) # larceny_theft 
 area.append(sqrt(data[8])) # population
 # plotting the first eigth letters of the state's name
 text(data[1], data[5], 
      data[0],size=11,horizontalalignment='center')

# making the scatter plot
sct = scatter(x, y, c=color, s=area, linewidths=2, edgecolor='w')
sct.set_alpha(0.75)

axis([0,11,200,1280])
xlabel('Murders per 100,000 population')
ylabel('Burglaries per 100,000 population')
show()
    """

    return

###################################################################
###                    Histo with error barr                    ###
###################################################################


def prepDataToHistoPlot(data, colors=["#00BBBB", "#00BB00", '#FF0000'], title="title", xticks=["Not", "1", "2", "3", "4", "5", "6"], legend=["ExpSeq", "ZPDES", "RiARiT"], ylab="nb student", path="result_xp/histo/", ref="file"):
    dataToPlot = [[np.mean(data[i][j]) for j in range(len(data[i]))] for i in range(len(data))]
    stdPlot = [[np.std(data[i][j]) / len(data[i][j]) for j in range(len(data[i]))] for i in range(len(data))]
    plotHisto_errorBar_stacked(dataToPlot, stdPlot, colors, title, xticks, legend, ylab, path, ref)

    return

##############################################
# Bar horizontal


def plotHisto_errorBarh_subStacked(dataToPlot, dataToUseRange=[0], std=None, colors=["#00BBBB", "#00BB00", '#FF0000'], title="", titleSub=["title"], xticks=["Not", "1", "2", "3", "4", "5", "6"], legend=["ExpSeq", "ZPDES", "RiARiT", "Reached", "Achieved"], legendSpec=[[]], legendPos=0, ylab="nb student", path="result_xp/histo/", ref="file", hatch_tab=[None, "\\", "//", "o", "|", "-", "x", "O", "+", ".", "*"], subplot=1):

    plt.cla()
    plt.clf()
    plt.close()
    fig = plt.figure()  # figsize=(20, 13))
    ax = fig.add_subplot(111)

    if not std:
        std = [None] * len(dataToPlot[0])
    ind = np.array([0])  # np.arange(len(dataToPlot[0][0])) # the x locations for the groups
    width = 0.25                        # the width of the bars: can also be len(x) sequenc
    bottomPlot = np.array([[0] * len(dataToPlot[0][0]) for x in range(len(dataToPlot))])
    # alpha = [0.5]#/len(dataToUseRange)]*len(dataToUseRange)

    # if len(dataToUseRange) > 1:
    #    for x in range(len(dataToUseRange)):
    #        plegend.append(plt.barh(ind+width*i, [0]*len(dataToPlot[0][0]), width,color = 'white', hatch = hatch_tab[x]))

    nb_cols = len(dataToUseRange)

    for x in range(len(dataToUseRange)):
        plt.subplot(nb_cols, 2, x + 1)  # config full quest : (nb_cols, 2, x+1)
        bottomPlot = np.array([[0] * len(dataToPlot[0][0][0]) for k in range(len(dataToPlot[0][0]))])
        # bottomPlot.append(np.array([0]*len(dataToPlot[dataToUseRange[x]][0])))
        # alpha.append(0.6)
        plegend = []
        alpha = [0.8, 0.6, 0.4]
        for i in range(0, len(dataToPlot[dataToUseRange[x]])):  # [dataToUseRange[x]])):
            plegend.append(plt.barh(ind + width * 1, [0] * len(dataToPlot[dataToUseRange[x]][i][0]), width, color="white", hatch=hatch_tab[i]))

            pltPlot = []
            for j in range(0, len(dataToPlot[dataToUseRange[x]][i])):
                pltPlot.append(plt.barh(ind + width * j, dataToPlot[dataToUseRange[x]][i][j], width, color=colors[j], yerr=std[j], hatch=hatch_tab[i], alpha=alpha[i], left=bottomPlot[j]))
                bottomPlot[j] += np.array(dataToPlot[dataToUseRange[x]][i][j])

            if len(legendSpec) >= dataToUseRange[x]:
                if len(legendSpec[dataToUseRange[x]]) < len(plegend):
                    legendSpec[dataToUseRange[x]] = ["Yo"] * len(pltPlot)
            else:
                for k in range(dataToUseRange[x] - len(legendSpec) + 1):
                    legendSpec.append(["Yo"] * len(plegend))
        if x % 2 == 0:
            bboxAnchor = (0, 0, 0.01, 1.1)
        else:
            bboxAnchor = (0, 1.1, 1.4, 0)

        plt.legend(plegend, [unicode(legendSpec[dataToUseRange[x]][k], "utf-8") for k in range(len(legendSpec[dataToUseRange[x]]))], bbox_to_anchor=bboxAnchor, prop={'size': 8})

        #plt.ylabel("Q %s" % (x+1))
        plt.yticks([])

        if len(titleSub) < dataToUseRange[x]:
            for k in range(dataToUseRange[x] - len(titleSub) + 1):
                titleSub.append("Yo")

        plt.title(unicode(titleSub[dataToUseRange[x]], "utf-8"), size=10)

        maxX = max([max(bottomPlot[k]) for k in range(len(bottomPlot))])
        if maxX > 50:
            maxX = int(maxX * 1.0 / 10 + 1) * 10
            plt.xticks([])  # np.arange(0,maxX+1,10))#maxX/10))

        elif maxX > 10:
            maxX = int(maxX) + 1
            plt.xticks(np.arange(0, maxX + 1, 2))  # maxX/10))

        else:
            maxX = int(maxX)
            plt.xticks([])  # np.arange(0,maxX+1,0.5))#maxX/10))

        # if xticks:
            #plt.xticks(ind+width*3/2, xticks)
    #maxY = int(maxY*1.0/10+(min(1,maxY % 10)))*10
    # maxY = (int(max([max([max([max(dataToPlot[x][i]) for i in range(len(dataToPlot[x]))]) for x in range(len(dataToPlot))])])*1.0/10+1)+)*10
    #plt.subplot(nb_cols, 1, 0)
    plegend = []
    for i in range(len(dataToPlot[0][0])):
        plegend.append(plt.bar(ind + width * i, [0] * len(dataToPlot[0][0][0]), width, color=colors[i]))

    if legend:
    # plt.legend( plegend, legend , bbox_to_anchor=(0,0,1,1),prop={'size':10})
        plt.figlegend(plegend, legend, loc='upper center', ncol=len(dataToUseRange), prop={'size': 10})
    fig.subplots_adjust(hspace=.8, wspace=0.1, top=.85, right=.85, left=0.15, bottom=-.8)
    # plt.show()
    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    return

############################################
# Bar vertical
# grey #555555


def plotHisto_errorBar_stacked(dataToPlot, dataToUseRange=[0], std=None, colors=["#00BBBB", "#00BB00", '#FF0000'], title="title", xticks=["Not", "1", "2", "3", "4", "5", "6"], legend=["ExpSeq", "ZPDES", "RiARiT", "Reached", "Achieved"], ylab="nb student", xlab="level", path="result_xp/histo/", ref="file", hatch_tab=[None, "\\", "o", "|", "x", ".", "-", "O", "+", "*", "//"], legendPos=0):

    plt.cla()
    plt.clf()
    plt.close()
    fig = plt.figure()  # figsize=(20, 13))
    ax = fig.add_subplot(111)

    if not std:
        std = [None] * len(dataToPlot[0])
    ind = np.arange(len(dataToPlot[0][0]))  # the x locations for the groups
    width = 0.25                        # the width of the bars: can also be len(x) sequenc
    pltPlot = []
    bottomPlot = np.array([[0] * len(dataToPlot[0][0]) for x in range(len(dataToPlot[0]))])
    alpha = [0.9]  # 1,0.9,0.8,0.7,0.6,0.5,0.4] #[1.0]#/len(dataToUseRange)]*len(dataToUseRange)
    plegend = []

    for i in range(len(dataToPlot[0])):
        plegend.append(plt.bar(ind + width * i, [0] * len(dataToPlot[0][0]), width, color=colors[i]))

    if len(dataToUseRange) > 1:
        for x in range(len(dataToUseRange)):
            plegend.append(plt.bar(ind + width * i, [0] * len(dataToPlot[0][0]), width, color='white', hatch=hatch_tab[x]))

    for x in range(len(dataToUseRange)):
        alpha.append(0.9)  # max(0.1,alpha[x] - 0.15))
        for i in range(0, len(dataToPlot[dataToUseRange[x]])):
            pltPlot.append(plt.bar(ind + width * i, dataToPlot[dataToUseRange[x]][i], width, color=colors[i], yerr=std[i], hatch=hatch_tab[x], alpha=alpha[x], bottom=bottomPlot[i]))
            bottomPlot[i] += np.array(dataToPlot[dataToUseRange[x]][i])

    plt.ylabel(ylab)
    plt.title(title)
    if xticks:
        plt.xticks(ind + width * 3 / 2, xticks)
    maxY = max([max(bottomPlot[i]) for i in range(len(bottomPlot))])
    maxY = int(maxY * 1.0 / 10 + (min(1, maxY % 10))) * 10
    # maxY = (int(max([max([max([max(dataToPlot[x][i]) for i in range(len(dataToPlot[x]))]) for x in range(len(dataToPlot))])])*1.0/10+1)+)*10

    plt.yticks(np.arange(0, maxY + 1, 5))  # maxY/10))
    if legend:
        #plt.legend( plegend, legend , bbox_to_anchor=(0,0,1,1),prop={'size':10})
        plt.legend(plegend, legend, bbox_to_anchor=legendPosTab[legendPos], prop={'size': 10})

    # plt.show()
    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    return


def plotHisto_errorBar(dataToPlot, dataToUseRange=[0], std=None, colors=["#00BBBB", "#00BB00", '#FF0000'], title="title", xticks=["Not", "1", "2", "3", "4", "5", "6"], legend=["ExpSeq", "ZPDES", "RiARiT", "Reached", "Achieved"], ylab="nb student", xlab="level", path="result_xp/histo/", ref="file", hatch_tab=[None, "\\", "/", "o", "|", "-", "x", "O", "+", ".", "*"]):
    plt.cla()
    plt.clf()
    plt.close()
    fig = plt.figure()  # figsize=(20, 13))
    ax = fig.add_subplot(111)

    if not std:
        std = [None] * len(dataToPlot[0])
    ind = np.arange(len(dataToPlot[0][0]))  # the x locations for the groups
    width = 0.25                        # the width of the bars: can also be len(x) sequenc
    pltPlot = []
    bottomPlot = []
    alpha = [0.7]
    plegend = []

    for i in range(len(dataToPlot[0])):
        plegend.append(plt.bar(ind + width * i, [0] * len(dataToPlot[0][0]), width, color=colors[i]))

    if len(dataToUseRange) > 1:
        for x in range(len(dataToUseRange)):
            plegend.append(plt.bar(ind + width * i, [0] * len(dataToPlot[0][0]), width, color='white', hatch=hatch_tab[x]))

    for x in range(len(dataToUseRange)):
        bottomPlot.append(np.array([0] * len(dataToPlot[dataToUseRange[x]][0])))
        alpha.append(0.6)
        for i in range(0, len(dataToPlot[dataToUseRange[x]])):
            pltPlot.append(plt.bar(ind + width * i, dataToPlot[dataToUseRange[x]][i], width, color=colors[i], yerr=std[i], hatch=hatch_tab[x], alpha=alpha[x]))  # ,bottom=bottomPlot))
            bottomPlot[x] += np.array(dataToPlot[dataToUseRange[x]][i])

    plt.ylabel(ylab)
    plt.xlabel(xlab)
    plt.title(title)
    if xticks:
        plt.xticks(ind + width * len(dataToPlot[0]) / 2, xticks)
    #maxY = int(max(bottomPlot)*1.0/10+1)*10
    #maxY = 100
    maxY = max([max([max([max(dataToPlot[x][i]) for i in range(len(dataToPlot[x]))]) for x in range(len(dataToPlot))])])
    if maxY > 50:
        maxY = int(maxY * 1.0 / 10 + 1) * 10
        plt.yticks(np.arange(0, maxY + 1, 5))  # maxY/10))

    elif maxY > 10:
        maxY = int(maxY) + 1
        plt.yticks(np.arange(0, maxY + 1, 2))  # maxY/10))

    else:
        maxY = int(maxY)
        plt.yticks(np.arange(0, maxY + 1, 0.5))  # maxY/10))

    if legend:
        #plt.legend( plegend, legend , bbox_to_anchor=(0,0,1,1),prop={'size':10})
        plt.legend(plegend, legend, bbox_to_anchor=(0, 0, 0.5, 1), prop={'size': 10})

    # plt.show()
    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    return


###################################################################
###                      Treat data clustering                  ###
###################################################################

def find_cluster(data, nb_centroid=2, type_clustering="lvl_time", whiten_b=True, type_data="skill"):

    interval_treat = [0, 2]
    if type_data == "skill":
        data_to_c = orga_learn_data(data, "user")
    elif type_data == "seq":
        data_to_c = orga_seq(data)
        interval_treat = [0]
    al_def_clust = []
    fail = 0
    for type_d in interval_treat:
        if whiten_b:
            """
            if type_data == "seq" :
                for d in data_to_c[type_d][-1]: 
                    print d
                raw_input()
            #"""
            data_to_treat = whiten(array(data_to_c[type_d][-1]))
            """
            if type_data == "seq" :
                for d in data_to_treat: 
                    print d
                raw_input()
            #"""
        else:
            data_to_treat = array(data_to_c[type_d][-1])

        nb_try = 0
        while nb_try < 200:
            try:
                centroids, clusters = kmeans2(data_to_treat, nb_centroid)
                empty = 0
                empty_t = []

                for c in clusters:
                    if c not in empty_t:
                        empty_t.append(c)
                # print empty_t
                if len(empty_t) < nb_centroid:
                    empty += 1

                if empty == 0:
                    break
            except:
                nb_try += 1

        if nb_try >= 200:
            print "NO CLUSTER FOUND 1rst"
            fail += 1
            nb_try = 0
            while nb_try < 200:
                try:
                    centroids, distortion = kmeans(data_to_treat, nb_centroid)
                    centroids, clusters = kmeans2(data_to_treat, centroids)
                    empty = 0
                    for c in clusters:
                        if c == [] or c > 3 or c < 0:
                            empty += 1

                    if empty == 0:
                        nb_try = 201
                        break
                    else:
                        nb_try += 1
                except:
                    nb_try += 1

        if nb_try == 200 and fail > 0:
            print "NO CLUSTER FOUND"
            clusters = []
            nb_stud = len(data_to_treat)
            nb_stud_clust = len(data_to_treat) / nb_centroid
            for i in range(0, nb_centroid):
                for j in range(0, nb_stud_clust):
                    clusters.append(i)

        orga_clust = []
        for i in range(0, nb_centroid):
            orga_clust.append([])
        # print "len cluster %s" % len(clusters)
        # print clusters
        # try :
        for i in range(0, len(clusters)):
            orga_clust[clusters[i]].append(i)
        # except:
        """    #print clusters[i]
            #raw_input()
            clusters = []
            nb_stud = len(data_to_treat)
            nb_stud_clust = len(data_to_treat)/nb_centroid
            for i in range(0,nb_centroid):
                for j in range(0,nb_stud_clust):
                    clusters.append(i)
            orga_clust = []
            for i in range(0,nb_centroid):
                orga_clust.append([])
            for i in range(0,len(clusters)):
                #print clusters[i]
                orga_clust[clusters[i]].append(i)
                #"""
        # print clusters
        # for centroid in centroids:
         #   print centroid
        # print orga_clust
        al_def_clust.append(orga_clust)

    return al_def_clust

###################################################################
####                     Boxplot                              #####
###################################################################


def boxPlotData(n, fdata, time_skill, save_data=False):
    datas_box = []
    ski_lab = ["KnowMoney", "IntSum", "IntDec", "DecSum", "DecDec", "Memory"]
    groups_s2 = []
    for al in fdata.keys():
        if al[0] != "p" or al[0] != "P":
            Name_Algo = al

    if save_data:
        for key2 in [Name_Algo, "Predefined"]:
            if len(groups_s2) < 2:
                groups_s2.append(key2)
            dat = []
            for key in ski_lab:
                dat.append(fdata[key2]["final_skills"][n][key])
            datas_box.append(dat)
        return datas_box
    else:
        for key in ski_lab:
            dat = []
            for key2 in [Name_Algo, "Predefined"]:
                if len(groups_s2) < 2:
                    groups_s2.append(key2)
                dat.append(fdata[key2]["final_skills"][n][key])
            datas_box.append(dat)
        return datas_box, groups_s2, ski_lab

# Plot boxplot


def boxplot(data, legend, ylabel=None, title=None, groups=('RiARiT', 'Predefined'), path="", ref=""):
    plt.cla()
    plt.clf()
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # pylab.boxplot(data,1)
    #number = []
    # for i in range(1,len(data)+1):
    #    number.append(i)
    #pylab.xticks(number, legend)
    # pylab.show()

    # print "len(data) : %s" % len(data[0])

    # function for setting the colors of the box plots pairs
    def setBoxColors(bp, lenData):
        pylab.setp(bp['boxes'][0], color='blue')
        pylab.setp(bp['caps'][0], color='blue')
        pylab.setp(bp['caps'][1], color='blue')
        pylab.setp(bp['whiskers'][0], color='blue')
        pylab.setp(bp['whiskers'][1], color='blue')
        pylab.setp(bp['fliers'][0], color='blue')
        pylab.setp(bp['fliers'][1], color='blue')
        pylab.setp(bp['medians'][0], color='blue')

        if lenData <= 2:
            pylab.setp(bp['boxes'][1], color='red')
            pylab.setp(bp['caps'][2], color='red')
            pylab.setp(bp['caps'][3], color='red')
            pylab.setp(bp['whiskers'][2], color='red')
            pylab.setp(bp['whiskers'][3], color='red')
            pylab.setp(bp['fliers'][2], color='red')
            pylab.setp(bp['fliers'][3], color='red')
            pylab.setp(bp['medians'][1], color='red')

        else:
            pylab.setp(bp['boxes'][1], color='black')
            pylab.setp(bp['caps'][2], color='black')
            pylab.setp(bp['caps'][3], color='black')
            pylab.setp(bp['whiskers'][2], color='black')
            pylab.setp(bp['whiskers'][3], color='black')
            pylab.setp(bp['fliers'][2], color='black')
            pylab.setp(bp['fliers'][3], color='black')
            pylab.setp(bp['medians'][1], color='black')

            pylab.setp(bp['boxes'][2], color='red')
            pylab.setp(bp['caps'][4], color='red')
            pylab.setp(bp['caps'][5], color='red')
            pylab.setp(bp['whiskers'][4], color='red')
            pylab.setp(bp['whiskers'][5], color='red')
            pylab.setp(bp['fliers'][4], color='red')
            pylab.setp(bp['fliers'][5], color='red')
            pylab.setp(bp['medians'][2], color='red')

    #fig =  pylab.figure()
    ax = pylab.axes()
    pylab.hold(True)
    interv = []
    for i in range(0, len(data)):
        print "data : %s" % i
        print data[i]
        if len(data[0]) <= 2:
            x = 1 + 3 * i
            y = 2 + 3 * i
            pos = [x, y]
        else:
            x = 0.5 + 3 * i
            y = 1.5 + 3 * i
            z = 2.5 + 3 * i
            pos = [x, y, z]
        bp = pylab.boxplot(data[i], 1, positions=pos, widths=0.6)
        interv.append(y - 0.0)
        setBoxColors(bp, len(data[0]))

    # set axes limits and labels
    pylab.xlim(0, interv[-1] + 1.5)
    if len(data[0]) <= 2:
        v = round(max(1.2, min(1.3, max(max(data[-1][0]), max(data[-1][1])))), 1)
    else:
        v = 1.3
    pylab.ylim(0, v)
    ax.set_xticklabels(legend)
    ax.set_xticks(interv)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    # draw temporary red and blue lines and use them to create a legend
    hB, = pylab.plot([1, 1], 'b-')
    hR, = pylab.plot([1, 1], 'r-')
    if len(data[0]) > 2:
        hK, = pylab.plot([1, 1], 'k-')
    if len(data[0]) > 2:
        h_to_plot = (hB, hK, hR)
    else:
        h_to_plot = (hB, hR)
    pylab.legend(h_to_plot, groups, bbox_to_anchor=(0, 0, 0.7, 1),)
    hB.set_visible(False)
    hR.set_visible(False)
    if len(data[0]) > 2:
        hK.set_visible(False)
    # pylab.savefig('boxcompare.png')
    # pylab.show()
    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    return


def plot_box_ms(n, fdata, time_skill, path):
    datas_box, groups_s2, ski_lab = boxPlotData(n, fdata, time_skill)

    boxplot(datas_box, ski_lab, "Skill Level", "Skill's levels at time : %s" % time_skill[n], groups=groups_s2, path=path, ref="box_skill_t%s" % time_skill[n])


def modif_skills(user):
    A = SSBanditGroup()
    A.loadRT()
    Game = MoneyGame()
    seq = user["seq"]
    lvls = []
    for s in seq:
        act = s[0:4]
        #A.update(act, s[4], s[5])
        lvl = A.getLevel()
        lvls.append({"Memory": lvl[5], "IntSum": lvl[1], "IntDec": lvl[2], "DecSum": lvl[3], "DecDec": lvl[4], "KnowMoney": lvl[0]})
        A.update(act, s[4], s[5])
    user["skill_estim"] = lvls

    return


def modif_def_skills(datas):
    for clas in datas:
        for user in clas:
            modif_skills(user)

    return

######################################################################
#               Stats test
#####################################################################


def orgaMultiSeq():
    return


def orga_seq(seq_al_def, type_treat="time", step=7):
    seqs = []

    nb_type = len(seq_al_def)
    nb_user = len(seq_al_def[0])
    nb_time = len(seq_al_def[0][0])
    nb_param = len(seq_al_def[0][0][0])
    nb_step = nb_time / step

    for type_d in range(0, nb_type):
        seqs.append([])
        for param in range(0, nb_param + 1):
            seqs[type_d].append([])
            for user in range(0, nb_user):
                seqs[type_d][param].append([])

    for type_d in range(0, nb_type):
        for user in range(0, nb_user):
            for time in range(0, nb_time):
                for param in range(0, nb_param):
                    p = int(seq_al_def[type_d][user][time][param])
                    if param == 1:
                        if p == 2:
                            p = 1
                        elif p == 1:
                            p = 2
                    seqs[type_d][param][user].append(p + 1)

    for type_d in range(0, len(seqs)):
        for param in range(0, len(seqs[type_d])):
            for user in range(0, len(seqs[type_d][param])):
                for i in range(0, nb_step):
                    m = max(np.mean(seqs[type_d][param][user][i * step:step * (i + 1)]), pow(10, -8))
                    seqs[type_d][-1][user].append(m)

    return seqs


def orgaMultiSkill():
    return


def orga_learn_data(data, type_treat="time", step=4):
    data_to_ttest = []

    nb_type = len(data[0]) + len(data[1])
    nb_skill = len(data[0][0][0][0])
    # print nb_skill
    nb_time = len(data[0][0][0])
    nb_user = len(data[0][0])
    nb_step = nb_time / step
    #nb_step = 20
    #step = nb_time/nb_step

    for type_d in range(0, nb_type):
        data_to_ttest.append([])
        for skill in range(0, nb_skill + 1):
            data_to_ttest[type_d].append([])
            if type_treat == "time":
                for k in range(0, nb_time):
                    data_to_ttest[type_d][skill].append([])
            elif type_treat == "user":
                for k in range(0, nb_user):
                    data_to_ttest[type_d][skill].append([])

    for type_al_def in range(0, len(data)):
        for real_esti in range(0, len(data[type_al_def])):
            for user in range(0, len(data[type_al_def][real_esti])):
                for time in range(0, len(data[type_al_def][real_esti][user])):
                    for skill in range(0, len(data[type_al_def][real_esti][user][time])):
                        if type_treat == "time":
                            data_to_ttest[type_al_def + 2 * real_esti][skill][time].append(data[type_al_def][real_esti][user][time][skill])
                            data_to_ttest[type_al_def + 2 * real_esti][6][time].append(data[type_al_def][real_esti][user][time][skill])
                        elif type_treat == "user":
                            data_to_ttest[type_al_def + 2 * real_esti][skill][user].append(data[type_al_def][real_esti][user][time][skill])
    if type_treat == "user":
        for type_d in range(0, len(data_to_ttest)):
            for skill in range(0, len(data_to_ttest[type_d])):
                for user in range(0, len(data_to_ttest[type_d][skill])):
                    for i in range(0, nb_step):
                        # print "step : %s , i : %s, nb_time : %s, step*(i+1)-1 : %s" % (step,i,nb_time, step*(i+1)-1)
                        # print data_to_ttest[type_d][skill][user][i*step:step*(i+1)]
                        # raw_input()
                        m = max(np.mean(data_to_ttest[type_d][skill][user][i * step:step * (i + 1)]), pow(10, -8))
                        data_to_ttest[type_d][-1][user].append(m)

    """if type_treat == "user":
        print "0,0,0 : %s" % data_to_ttest[0][0][0]
        print "len 0,0,0 : %s" % len(data_to_ttest[0][0][0])
        raw_input()
        print "0,6,0 : %s" % data_to_ttest[0][6][0]
        print "len 0,6,0 : %s" % len(data_to_ttest[0][6][0])
        raw_input()
    """
    return data_to_ttest


def ttest_learning_skills(tab_data1, tab_data2, time=0, stats_data=""):
    if len(stats_data) != time:
        print "Massive ERROR ERROR ERROR ERROR"
        t, prob = 0
    else:
        t, prob = sstats.ttest_ind(tab_data1, tab_data2)

    return prob


def make_t_test(learn_esti_al, learn_esti_predef, path="", legend_group=['RiARiT/Predefined, student learning', 'RiARiT/Predefined, estimated learning', 'RiARiT : student/estimated learning', 'Predef : student/estimated learning'], group_to_test=[[0, 1], [2, 3], [0, 2], [1, 3]], title_fig="Student test for different comparison", ref="", line_type=['solid', 'dashed', 'dashdot', 'dotted']):
    plt.cla()
    plt.clf()
    plt.close()

    data = learn_esti_al, learn_esti_predef

    data_to_ttest = orga_learn_data(data)

    t_test_tab = []

    def t_test(data1, data2):
        tab_t_test = [[], [], [], [], [], [], []]

        for nb_skills in range(0, len(data1)):
            for time in range(0, len(data1[0])):
                tab_t_test[nb_skills].append(ttest_learning_skills(data1[nb_skills][time], data2[nb_skills][time]))

        return tab_t_test

    for i in range(0, len(group_to_test)):
        t_test_tab.append(t_test(data_to_ttest[group_to_test[i][0]], data_to_ttest[group_to_test[i][1]]))

    """
    t_test_tab["group1"] = t_test(data_to_ttest[0],data_to_ttest[1])
    t_test_tab["group2"] = t_test(data_to_ttest[2],data_to_ttest[3])
    t_test_tab["group3"] = t_test(data_to_ttest[0],data_to_ttest[2])
    t_test_tab["group4"] = t_test(data_to_ttest[1],data_to_ttest[3])
    #"""

    # print "YOLO"
    # Plotting

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    labels = ["Time", "p-value"]
    x = range(0, len(t_test_tab[0][0]))
    ski_lab = ["KnowMoney", "IntSum", "IntDec", "DecSum", "DecDec", "Memory", "All skill"]
    for i in range(0, 7):
        plt.clf()
        # print ski_lab[i]
        title = title_fig + ", %s skill " % (ski_lab[i])
        plt.xlabel(labels[0], fontsize=20)
        plt.ylabel(labels[1], fontsize=20)
        for j in range(0, len(t_test_tab)):
            linewidth_fig = 2
            if line_type[j] == 'solid':
                linewidth_fig = 1
            plt.plot(x, t_test_tab[j][i], label=legend_group[j], linestyle=line_type[j], linewidth=linewidth_fig)
        #plt.plot(x, t_test_tab["group2"][i], label = legend_group[1], linestyle = 'solid',linewidth = 1)
        #plt.plot(x, t_test_tab["group3"][i], label = legend_group[2],linestyle = 'dashdot',linewidth = 2)
        #plt.plot(x, t_test_tab["group4"][i], label = legend_group[3],linestyle = 'dotted',linewidth = 2)
        plt.title(title, fontsize=20)
        plt.yticks(np.arange(0, 1.4, 0.1))
        plt.legend(bbox_to_anchor=(0, 0, 1, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 15})
        # plt.show()
        plt.draw()
        if path != "":
            path_f = path + ref + "%s_ttest_curve" % ski_lab[i]
            plt.savefig(path_f)

    return

##################################################################
#                           PLOT, DRAW
##################################################################
#### Show param_time Curve ####


def draw_param_lvl_curve(data1, nb_stud=1000, title='% of student doing each type at each time', legend=["type1", "type2", "type3", "type4", "type5", "type6", "End"], labels=['Time', '% of student'], yerr_al=None, yerr_def=None, path="", ref="haha"):

    plt.cla()
    plt.clf()
    plt.close()
    nb_y = nb_stud + nb_stud / 4
    # print nb_y

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    p = []
    data_lvl = []
    for i in range(0, len(data1[0])):
        data_lvl.append([])
    for i in range(0, len(data1)):
        for j in range(0, len(data1[i])):
            # print sum(data1[i])
            data_lvl[j].append(data1[i][j] * 100.0 / max(1, nb_stud))
            # print "d1, i j  %s,%s,%s" % (data1[i][j],i,j)

    N = len(data1)

    ind = np.arange(N)    # the x locations for the groups
    width = 1.0       # the width of the bars: can also be len(x) sequence
    #         red,        orange    yellow,    gree,    cyan,     blue,   purple
    colors = ["#ff0000", "#ffbb00", "#ffff00", "#99FF00", "#66ccFF", "#0055ff", "#bb00ff", "#ff99ff", "#555599", "#888888", "#ffffff"]

    plt.xlabel(labels[0], fontsize=30)
    plt.ylabel(labels[1], fontsize=30)

    x = range(1, len(data_lvl[0]) + 1)
    for i in range(0, len(data_lvl)):
        plt.plot(x, data_lvl[i], label=legend[i], color=colors[i], linewidth=1)
    # plt.yticks(np.arange(0,80,10))
    plt.title(title, fontsize=30)
    plt.legend(bbox_to_anchor=(0, 0, 1.13, 0.7), ncol=1, fancybox=True, shadow=True, prop={'size': 20})
    # plt.show()
    plt.draw()
    if path != "":
        path_f = path + ref
        plt.savefig(path_f)

    return

#### Show learned Curve ####


def draw_p_learn_curve(p_al, p_def, nbstud, path=""):

    # plt.cla()
    plt.clf()
    data = p_al, p_def
    # print data[0][0]

    def make_mean(data):
        max_l = [[], [], [], [], [], []]
        min_l = [[], [], [], [], [], []]
        mean = []

        for i in range(0, len(data[0][0])):
            mean.append([])
            for j in range(0, len(data[0][0][i])):
                mean[i].append([])
                for k in range(0, len(data[0])):
                    mean[i][j].append(0.0)

        # print mean
        nb_to_d = 0

        for i in range(0, len(data)):
            for j in range(0, len(data[i])):
                for k in range(0, len(data[i][j])):
                    for l in range(0, len(data[i][j][k])):
                        # if k == 0:
                            # print data[i][j][k]
                        mean[k][l][j] = mean[k][l][j] + data[i][j][k][l]
                        if k == 0:
                            nb_to_d += 1
        # print mean[0][0]
        for i in range(0, len(mean)):
            for j in range(0, len(mean[i])):
                for k in range(0, len(mean[i][j])):
                    mean[i][j][k] = mean[i][j][k] / nbstud

        # print mean
        # print "\n"
        return mean

    mean_data = []
    for d in data:
        mean_data.append(make_mean(d))

    x = range(0, len(mean_data[0][0][0]))
    p_lab = []
    p_lab.append("Type")
    pop = ["R", "P"]
    colors = [['#000028', '#00008F', '#0000FF', '#003B6E', '#00749B', '#0099FF'],
              ['#8F0000', '#FF0000', '#6E0020', '#9B0050', '#9B6000', '#FF9900']]
    labels = ["Time", "Parameter's comprehension"]
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)
    for n_param in range(0, len(p_lab)):
        for j in range(0, len(mean_data)):
            for i in range(0, len(mean_data[0][0])):
                #title = "Evolution of %s params's level" % p_lab[n_param]
                ax.plot(x, mean_data[j][0][i], label='%s type %s' % (pop[j], i + 1),  color=colors[j][i])
                #plt.plot(x, mean_data[0][0][i], label = 'Al type %s' % i)
                #plt.plot(x, mean_data[1][0][i], label = 'Def type %s' % i)

        title = "Evolution of %s params's level" % p_lab[n_param]
        plt.xlabel(labels[0], fontsize=20)
        plt.ylabel(labels[1], fontsize=20)
        plt.title(title, fontsize=30)
        ax.legend(bbox_to_anchor=(0, 0, 1.13, 0.5), ncol=1, fancybox=True, shadow=True, prop={'size': 14})
        # plt.show()
        plt.draw()
        print path
        if path != "":
            fig.savefig(path + "%s_pl_curve" % p_lab[n_param])  # ,dpi=1000, bbox_inches='tight', format = "svg")

    return

# Generate colors


def gen_colors(data):
    colors = []
    for nbPdata in range(0, len(data)):
        nb_group = len(data[nbPdata])
        for group in range(0, nb_group):
            HSV_tuples = [(x * 1.0 / nb_group, 0.5, 0.5) for x in range(nb_group)]
            #RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
            RGB_tuples2 = [colorsys.hsv_to_rgb(*x) for x in HSV_tuples]
            rgb2 = [tuple([(x * 255) for x in y]) for y in RGB_tuples2]
            colorsTmp = ['#%02x%02x%02x' % x for x in rgb2]
            colors.append(colorsTmp)
    return colors

# draw_curve


def draw_simple_curves(data, stdData=None, x_range=None, y_range=None, labels=None, title="", xlabel="Time", ylabel="Skill", path="", colors=None, linetype=None, showPlot=True, lineWidth=1, fontSize=20, legendSize=14, bboxAnchor=(0, 0, 1.1, 0), ncol=1, xticks=None, yticks=None):

    plt.cla()
    plt.clf()
    plt.close()
    # plt.figure()
    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    if labels == None:
        labels = [None] * len(data)

    for nbSet in range(len(data)):
        if std_data != None:
            y3 = [data[nbSet][i] + std_data[nbSet][i]/4 for i in range(nb_ex)]
            y4 = [data[nbSet][i] - std_data[nbSet][i]/4 for i in range(nb_ex)]

            plt.fill_between(x_range, y3, y4, facecolor=colors[nbSet], alpha=0.1)

        plt.plot(x, data[nbSet], label=labels[nbSet], color=colors[nbSet], linestyle=line_type[nbSet], linewidth=lineWidth)

    plt.xlabel(xlabel, fontsize=fontSize)
    plt.ylabel(ylabel, fontsize=fontSize)
    plt.title(title, fontsize=fontSize)
    plt.legend(bbox_to_anchor=bboxAnchor, ncol=ncol, fancybox=True, shadow=True, prop={'size': legendSize})

    if xticks != None:
        plt.xticks(xticks)
    if yticks != None:
        plt.yticks(yticks)

    if path != "":
        plt.draw()
        path_f = path
        plt.savefig(path_f)

    if showPlot:
        plt.show()


def draw_curve(data, path="", labels=[["Predefined", "RiARiT", "ZPDES"]], nb_ex=100, typeData="successRate", type_data_spe="MAIN", ref="", markers=None, titleC="", colors=[["#00BBBB", "black", '#FF0000']], line_type=['dashed', 'solid', 'dashdot', 'dotted'], legend_position=1, showPlot=True, std_data=None, lineWidths=[2, 2, 3, 3, 3, 3]):

    plt.cla()
    plt.clf()
    plt.close()
    # plt.figure()
    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    xylabels = ["Time", typeData]
    x = range(nb_ex)
    # print path

    title = titleC
    if title == "":
        title = "Evolution of %s %s" % (type_data_spe, typeData)

    plt.xlabel(xylabels[0], fontsize=30)
    plt.ylabel(xylabels[1], fontsize=30)

    colorsBis = colors  # gen_colors(data)

    plt.xticks(fontsize=30)
    plt.yticks(fontsize=30)

    if std_data is not None:
        plt.ylim(ymin=0, ymax=1)

    for nbPdata in range(0, len(data)):
        nb_group = len(data[nbPdata])

        for group in range(0, nb_group):
            #_lineWidth = 2
            # if line_type[(nbPdata * nb_group + group) % len(line_type)] == 'solid':
            #    _lineWidth = 1

            # print nbPdata
            if len(labels[nbPdata % len(labels)]) <= group:
                lab = labels[nbPdata % len(labels)][0] + "_%s" % str(group)
            else:
                # print len(labels)
                # print nbPdata % len(labels)
                # print len(labels[nbPdata % len(labels)])
                # print group
                lab = labels[nbPdata % len(labels)][group]

            # print  "x %s" %  len(x)
            # print "len %s" % len(data[nbPdata][group])
            # print data[nbPdata][group]
            #x = range(len(data[nbPdata][group]))
            x = range(len(data[nbPdata][group]))
            if std_data is not None:

                y3 = [data[nbPdata][group][i] + std_data[nbPdata][group][i] for i in range(nb_ex)]
                y4 = [data[nbPdata][group][i] - std_data[nbPdata][group][i] for i in range(nb_ex)]
                # for i in range(len(y3)):
                #    if y3[i] > 1:
                #        y4[i] += 1-y3[i]
                #        y3[i] = 1
                #    elif y4[i] < 0:
                #        y3[i] += abs(y4[i])
                #        y4[i] = 0

                plt.fill_between(x, y3, y4, facecolor=colorsBis[nbPdata % len(colorsBis)][group % len(colorsBis[nbPdata % len(colorsBis)])], alpha=0.1)

            plt.plot(x, data[nbPdata][group], label=lab, color=colorsBis[nbPdata % len(colorsBis)][group % len(colorsBis[nbPdata % len(colorsBis)])], linestyle=line_type[group % len(line_type)], linewidth=lineWidths[group % len(lineWidths)])
            #plt.plot(x, data[nbPdata][group], label=lab, color=colorsBis[nbPdata % len(colorsBis)][group % len(colorsBis[nbPdata % len(colorsBis)])], linestyle=line_type[(nbPdata * nb_group + group) % len(line_type)], linewidth=lineWidths[(nbPdata * nb_group + group) % len(line_type)])

                # plt.errorbar(x, data[nbPdata][group],std_data[nbPdata][group], errorevery = 5)#, label = lab, color = colorsBis[nbPdata % len(colorsBis)][group % len(colorsBis[nbPdata % len(colorsBis)])], linestyle = line_type[(nbPdata*nb_group + group) % len(line_type)],linewidth = _lineWidth)

            if markers is not None:  # and len(markers[group]) > skill:
                markers_data = []
                for i in markers[group]:
                    markers_data.append(data[nbPdata][group][i])
                colors_markers = ["cD", "kD", "rD"]
                plt.plot(markers[group], markers_data, colors_markers[group])

        """plt.plot(x, data[0][1][skill], label = labels[0][1],color = colors[0][1], linestyle = 'solid',linewidth = 1)
        plt.plot(x, data[1][0][skill], label = labels[1][0],color = colors[1][0],linestyle = 'dashdot',linewidth = 2)
        plt.plot(x, data[1][1][skill], label = labels[1][1],color = colors[1][1],linestyle = 'dotted',linewidth = 2)
        """
    #plt.title(title, fontsize=30)

    if legend_position == 0:
        plt.legend(bbox_to_anchor=(0, 0, 0.2, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 24})
    elif legend_position == 1:
        plt.legend(bbox_to_anchor=(0, 0, 0.2, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 24})
    elif legend_position == 2:
        plt.legend(bbox_to_anchor=(0, 0, 1.1, 0), ncol=1, fancybox=True, shadow=True, prop={'size': 24})
    else:
        plt.legend(bbox_to_anchor=(0, 0, 1, 0.4), ncol=1, fancybox=True, shadow=True, prop={'size': 24})

    #plt.legend(bbox_to_anchor=(1.05, 1),loc=2, borderaxespad=0., ncol=1, fancybox=True, shadow=True, prop={'size':10})

    curve_data = {"data": data, "path": path, "labels": labels, "nb_ex": nb_ex, "typeData": typeData, "type_data_spe": type_data_spe, "ref": ref, "markers": markers, "titleC": titleC, "colors": colors, "line_type": line_type, "legend_position": legend_position, "showPlot": showPlot, "std_data": std_data, "lineWidths": lineWidths}

    if path != "":
        plt.draw()
        path_f = path + "Curve_%s_%s_%s" % (typeData.replace(" ", "_"), type_data_spe, ref)
        file_data = "data_Curve_%s_%s_%s" % (typeData.replace(" ", "_"), type_data_spe, ref)
        # print path_f
        plt.savefig(path_f, bbox_inches='tight', pad_inches=0)   # transparent="True",
        datafile.save_file(curve_data, file_data, path)

    if showPlot:
        plt.show()

    return


def draw_fill():
    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.sin(x) / 2
    y3 = np.sin(3 * x)
    y4 = np.sin(3 * x) / 2
    plt.fill_between(x, y3, y4, facecolor='b', alpha=0.3)
    #plt.fill(x, y4, 'w', alpha=1)
    plt.show()


def draw_learn_curve(gr1, gr2=0, path="", labels=[["estimated RiARiT", "simu RiARiT"], ["estimated Predef", "simu Predef"]], ref="ql_curve", line_type=['dashed', 'solid', 'dashdot', 'dotted'], colors=[["#00BBBB", '#008800'], ['#FF0000', '#0000FF', '#AA00FF']], legend_position=1, markers=None, ski_lab=["KnowMoney", "IntSum", "IntSub", "IntDec", "DecSum", "DecSub", "DecDec", "Total"], tdata="skill_level", nb_ex=None, std_use=1):  # Def : grp 1 : learn_esti_al, gr2 : learn_esti_predef

    plt.cla()
    plt.clf()
    plt.close()
    #fig = plt.figure()
    #ax = fig.add_subplot(111)

    if gr2 != 0:
        data = gr1, gr2
    else:
        data = [gr1]
        if len(gr1) == 1:
            data == [data]

    # treat :

    def make_mean(data):
        max_l = [[] for x in range(len(ski_lab))]
        min_l = [[] for x in range(len(ski_lab))]
        mean = [[] for x in range(len(ski_lab))]
        org_before_mean = [[] for x in range(len(ski_lab))]
        std = [[] for x in range(len(ski_lab))]
        for i in range(0, len(mean)):
            for j in range(0, len(data[0])):
                mean[i].append(0.0)
                std[i].append(0.0)
                org_before_mean[i].append([])

        nb_to_d = 0
        for i in range(0, len(data)):  # stud
            for j in range(0, len(data[i])):  # skill
                for k in range(0, len(data[i][j])):  # k : group
                    org_before_mean[k][j].append(data[i][j][k])
                    if k == 0:
                        nb_to_d += 1

        for i in range(0, len(mean)):
            for j in range(0, len(mean[i])):
                mean[i][j] = np.mean(org_before_mean[i][j])
                std[i][j] = np.std(org_before_mean[i][j])

        return mean, std

    mean_data = []
    std_data = []
    for type_d in range(0, len(data)):
        mean_data.append([])
        std_data.append([])
        for sd in data[type_d]:
            mean_std = make_mean(sd)
            mean_data[type_d].append(mean_std[0])
            std_data[type_d].append(mean_std[1])

    mean_data_skill = []
    std_data_skill = []
    for skill in range(len(ski_lab)):
        mean_data_skill.append([])
        std_data_skill.append([])
        for type_d in range(len(mean_data)):
            mean_data_skill[skill].append([])
            std_data_skill[skill].append([])
            nb_group = len(mean_data[type_d])
            for group in range(nb_group):
                mean_data_skill[skill][type_d].append(mean_data[type_d][group][skill])
                std_data_skill[skill][type_d].append(std_data[type_d][group][skill])
    if not std_use:
        std_data_skill = None

    # print mean_data[0][0]
    # print(len(mean_data[0][0]))
    #xylabels = ["Time","Skill's level"]
    # x = range(0,len(mean_data[0][0][0]))
    if nb_ex == None:
        nb_ex = len(mean_data[0][0][0])
    # print path
    for skill in range(len(ski_lab)):
        plt.clf()
        draw_curve(mean_data_skill[skill], path=path, labels=labels, nb_ex=nb_ex, typeData=tdata, type_data_spe=ski_lab[skill], ref=ref, markers=markers, colors=colors, line_type=line_type, legend_position=legend_position, std_data=std_data_skill[skill])

        """
        title = "Evolution of %s skill's level" % ski_lab[skill]
        #plt.xlabel(xylabels[0], fontsize=20)
        #plt.ylabel(xylabels[1], fontsize=20)
        for type_d in range(0,len(mean_data)):
            nb_group = len(mean_data[type_d])
            for group in range(0,nb_group):
                _lineWidth = 2
                if  line_type[(type_d*nb_group + group) % len(line_type)] == 'solid' :
                    _lineWidth = 1
                plt.plot(x, mean_data[type_d][group][skill], label = labels[type_d][group],color = colors[type_d][group % len(colors[type_d])], linestyle = line_type[(type_d*nb_group + group) % len(line_type)],linewidth = _lineWidth)
                if markers != None and len(markers[group]) > skill:
                    markers_data = []
                    for i in markers[group][skill]:
                        markers_data.append(mean_data[type_d][group][skill][i])
                    colors_markers = ["cD","kD","rD"]
                    plt.plot(markers[group][skill], markers_data,colors_markers[group])
                
            #plt.plot(x, mean_data[0][1][skill], label = labels[0][1],color = colors[0][1], linestyle = 'solid',linewidth = 1)
            #plt.plot(x, mean_data[1][0][skill], label = labels[1][0],color = colors[1][0],linestyle = 'dashdot',linewidth = 2)
            #plt.plot(x, mean_data[1][1][skill], label = labels[1][1],color = colors[1][1],linestyle = 'dotted',linewidth = 2)

        plt.title(title, fontsize=20)
        if legend_position == 1 :
            plt.legend(bbox_to_anchor=(0,0,0.2,1),ncol=1, fancybox=True, shadow=True, prop={'size':14})
        elif legend_position == 2 :
            plt.legend(bbox_to_anchor=(0,0,0.3,1),ncol=1, fancybox=True, shadow=True, prop={'size':14})
        else:
            plt.legend(bbox_to_anchor=(0,0,1,0.3),ncol=1, fancybox=True, shadow=True, prop={'size':14})

        #plt.legend(bbox_to_anchor=(1.05, 1),loc=2, borderaxespad=0., ncol=1, fancybox=True, shadow=True, prop={'size':10})
        #plt.show()
        plt.draw()
        if path != "" :
            path_f = path + "%s_%s_%s" % (tdata,ski_lab[skill],ref)
            #print path_f
            plt.savefig(path_f)
        #"""
    #file_simu = file('Expe/Sequences/text/seq_%s.txt' % Id,'w')
    # file_simu.write("Level\tSound\tRepr\NotTok\tCorr\n")
    # for s in seq_o:
        #file_simu.write("%s\t%s\t%s\t%s\t%s\n" % (s[0],s[1],s[2],s[3],int(s[4])))

    return

# Plot cluster P student without subplot


def bot(b1, b2):
    b = []
    for i in range(0, len(b1)):
        b.append(b1[i] + b2[i])
    return b


def all_bot(data, base=None):
    all_b = []
    if base != None:
        all_b.append(base)
        all_b.append(bot(base, data[0]))
    else:
        all_b.append(0)
        all_b.append(data[0])
    for i in range(1, len(data)):
        all_b.append(bot(all_b[i], data[i]))
    return all_b


def all_bot2(data1):
    all_b = []
    all_b.append(0)
    all_b.append(data1[0][0])
    for j in range(0, len(data1[0])):
        for i in range(0, len(data1)):
            if i != 0 or j != 0:
                all_b.append(bot(all_b[i + j * len(data1)], data1[i][j]))


# Plot cluster P student with subplot
def plot_cluster_lvl_sub(data, nb_stud=100, nb_ex=None, title='Number of student doing each level at each time per cluster', legend=("1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), labels=['Time', 'Number of student'], yerr_al=None, yerr_def=None, path="", ref="haha", dataToUse=[0, 1, 2], show=0, save=1):
    data = [data[x] for x in dataToUse]
    plt.cla()
    plt.clf()
    plt.close()
    nb_y = nb_stud + nb_stud / 4
    # print nb_y

    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    p_legend = []
    p = []
    data_lvl = []
    ptuple = []
    for i in range(0, len(data)):
        data_lvl.append([])
        for k in range(len(data[i])):
            data_lvl[i].append([])
            for j in range(0, len(data[0][k][0])):
                data_lvl[i][k].append([])

    for i in range(0, len(data)):
        for j in range(0, len(data[i])):
            for k in range(0, len(data[i][j])):
                for l in range(0, len(data[i][j][k])):
                    data_lvl[i][j][l].append(data[i][j][k][l])

    N = len(data[0][0])
    ind = np.arange(N)    # the x locations for the groups
    width = 1.0       # the width of the bars: can also be len(x) sequence
    #         red,        orange    yellow,    gree,    cyan,     blue,   purple
    # ["#00DDFF","#00AAFF","#0066AA","#0044BB","#0033DD","#0000FF"]
    if len(data_lvl[0]) > 1:
        colors = [["#BBFFFF", "#6699FF", "#4466FF", "#0066FF", "#004499", "#0000FF"],
                  ["#33CC33", "#00AA00", "#006600", "#003300"],
                  ["#9900CC", "#6633FF", "#500099", "#330066", "#110044"],
                  ["#FF4444", "#EE0000", "#990000", "#662222", "#ffffff"],
                  ["#0055ff", "#bb00ff", "#ff99ff", "#555599", "#888888", "#ffffff"],
                  ["#ff0000", "#ffbb00", "#ffff00", "#99FF00", "#66ccFF", "#0055ff"]]
    else:
        colors = [["#ff0000", "#ffbb00", "#ffff00", "#99FF00", "#66ccFF", "#0055ff", "#bb00ff", "#ff99ff", "#555599", "#888888", "#ffffff"]]
    hatch_tab = [None, "/", "\"", "x", "o", "-", "O", "+", ".", "*", "|"]

    """print "Tpe data_lvl_c %s " % type(data_lvl[0][0])
    print len(data_lvl[0][0])
    print data_lvl[0][0]
    """
    if nb_ex == None:
        nb_ex = len(data_lvl[0][0])

    nb_cols = len(data_lvl)

    for k in range(len(data_lvl[0])):
        for j in range(0, len(data_lvl[0][k])):
            p_legend = plt.bar(ind, data_lvl[0][k][j], width, color=colors[k % len(colors)][j + k % len(colors)])  # , hatch = hatch_tab[k])
            ptuple.append(p_legend[0])

    for i in range(0, len(data_lvl)):
        botBase = None
        plt.subplot(nb_cols, 1, i + 1)  # for clusters
        for k in range(len(data_lvl[i])):
            bota = all_bot(data_lvl[i][k], botBase)
            if len(data_lvl) == 1:
                a = 0
                plt.ylabel("Number of student ", fontsize=30)
            else:
                a = 0
                plt.ylabel("Group %s" % str(i + 1), fontsize=30)

            for j in range(0, len(data_lvl[i][k])):
                plt.bar(ind, data_lvl[i][k][j], width, bottom=bota[j], color=colors[k % len(colors)][j + k % len(colors)])  # ,hatch = hatch_tab[k])#,edgecolor = colors[j], hatch = hatch_tab[i], alpha=0.5))
            botBase = bota[-1]

        plt.xticks(np.arange(0, max(81, nb_ex + 1), (10)),  fontsize=25)
        plt.yticks(fontsize=25)

    if i == 0:
        a = 0
        plt.title(title, fontsize=35)
        plt.legend(ptuple, legend, bbox_to_anchor=(0, 0, 1.13, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 16})

    elif i == len(data_lvl) - 1:
        a = 0
        #plt.xlabel(labels[0], fontsize=40)

    #labelaxe = []
    # for i in range(1,len(data_lvl[0][0])+1):
    #    labelaxe.append(str(i))

    #plt.xticks(ind+width/2., (labelaxe) )

    if save:
        plt.draw()
        path_f = path + ref
        plt.savefig(path_f)

    if show:
        plt.show()

    return

# Plot Student seq


def plot_lvl_curve(data1, nb_stud=1000, title='Number of student doing each level at each time', legend=("1", "2", "3", "4", "5", "6", "End"), labels=['Time', 'Number of student'], yerr_al=None, yerr_def=None, path="", ref="haha", reuse=False):

    plt.cla()
    plt.clf()
    plt.close()
    nb_y = nb_stud + nb_stud / 4
    # print nb_y

    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    p = []
    data_lvl = []
    for i in range(0, len(data1[0])):
        data_lvl.append([])
        data_lvl[i].append(data1[0][i])

    for i in range(0, len(data1)):
        for j in range(0, len(data1[i])):
            data_lvl[j].append(data1[i][j])
    N = len(data1) + 1

    colors = ["#ff0000", "#ffbb00", "#ffff00", "#99FF00", "#66ccFF", "#0055ff", "#bb00ff", "#ff99ff", "#555599", "#888888", "#ffffff"]
    x = np.arange(N)    # the x locations for the groups
    y = np.row_stack(data_lvl)
    y_stack = np.cumsum(y, axis=0)
    r_legend = []
    ax.fill_between(x, 0, y_stack[0, :], facecolor=colors[0])
    r_legend.append(Rectangle((0, 0), 1, 1, facecolor=colors[0]))
    for i in range(1, len(data_lvl)):
        ax.fill_between(x, y_stack[i-1, :], y_stack[i,:], facecolor=colors[i])
        r_legend.append(Rectangle((0, 0), 1, 1, facecolor=colors[i]))

    if reuse:
        return plt
    else:

        plt.xlabel(labels[0], fontsize=40)
        plt.ylabel(labels[1], fontsize=40)
        plt.title(title, fontsize=40)

        """labelaxe = []
        for i in range(1,len(data_lvl[0])+1):
            labelaxe.append(str(i))
            
        plt.xticks(ind+width/2., (labelaxe) )"""
        # plt.yticks(np.arange(0,nb_y,(nb_stud/5)))
        plt.legend(r_legend, legend, bbox_to_anchor=(0, 0, 1.13, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 25})
        # plt.show()
        plt.draw()
        if path != "":
            path_f = path + ref
            plt.savefig(path_f)

# Plot Student seq


def plot_lvl(data1, nb_stud=1000, nb_ex=None, title='Number of student doing each level at each time', legend=("1", "2", "3", "4", "5", "6", "End"), labels=['Time', 'Number of student'], yerr_al=None, yerr_def=None, path="", ref="haha", reuse=False):

    plt.cla()
    plt.clf()
    plt.close()
    nb_y = nb_stud + nb_stud / 4
    # print nb_y

    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(111)

    p = []
    data_lvl = []
    for i in range(0, len(data1[0])):
        data_lvl.append([])
    for i in range(0, len(data1)):
        for j in range(0, len(data1[i])):
            data_lvl[j].append(data1[i][j])
    N = len(data1)

    ind = np.arange(N)    # the x locations for the groups
    width = 1.0       # the width of the bars: can also be len(x) sequence
    #         red,        orange    yellow,    gree,    cyan,     blue,   purple
    colors = ["#ff0000", "#ffbb00", "#ffff00", "#99FF00", "#66ccFF", "#0055ff", "#bb00ff", "#ff99ff", "#555599", "#888888", "#ffffff"]
    p.append(plt.bar(ind, data_lvl[0], width, color=colors[0]))  # , hatch = "/",edgecolor = colors[0]))
    # p.append(plt.bar(ind, data_lvl[0], width, hatch = "/", color='#aaaaaa', alpha=0.2))#, hatch = "/",edgecolor = colors[0]))

    bota = all_bot(data_lvl)
    if nb_ex == None:
        nb_ex = len(data_lvl)
    for i in range(1, len(data_lvl)):
        p.append(plt.bar(ind, data_lvl[i], width, color=colors[i], bottom=bota[i]))  # , edgecolor = colors[i]))

    ptuple = []

    def autolabel(rects, bottom):
        # attach some text labels
        b = 0
        for i in range(0, len(rects)):
            if bottom != 0:
                b = bottom[i]
            height = rects[i].get_height() + b
            if rects[i].get_height() != 0:
                plt.text(rects[i].get_x() + rects[i].get_width() / 2., height, '%s' % str(rects[i].get_height()), ha='center', va='bottom', color='black')

    for i in range(0, len(p)):
        # autolabel(p[i],bota[i])
        ptuple.append(p[i][0])

    # print reuse
    if reuse:
        return plt
    else:
        plt.xlabel(labels[0], fontsize=40)
        plt.ylabel(labels[1], fontsize=40)
        plt.title(title, fontsize=40)
        """labelaxe = []
        for i in range(1,len(data_lvl[0])+1):
            labelaxe.append(str(i))
            
        plt.xticks(ind+width/2., (labelaxe) )"""
        # plt.yticks(np.arange(0,nb_y,(nb_stud/5)))
        plt.legend(ptuple, legend, bbox_to_anchor=(0, 0, 1.13, 1), ncol=1, fancybox=True, shadow=True, prop={'size': 25})
        # plt.show()
        plt.draw()
        if path != "":
            path_f = path + ref
            plt.savefig(path_f)

        return

# Plot analys sequence :


def plot_seq(seq_o, Id="", path="", col=1):
    plt.cla()
    plt.clf()
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    seq = []
    # seq.append((255,4,2,2,0))
    # print len(seq_o)
    step = [0, 12, 18, 22, 26]

    for i in range(100, 130):
        if col:
            s = []
            for j in range(0, 5):
                s.append(seq_o[i][j] * 2 + step[j])
            seq.append(s)
        else:
            seq.append([seq_o[i][0], seq_o[i][1] * 2, seq_o[i][2] * 2, seq_o[i][3] * 2, int(seq_o[i][4]) * 2])
    X = 10 * np.random.rand(9, 2)
    X = np.asarray(seq)
    # print type(X)
    # print X
    plt.imshow(X, interpolation='nearest')
    plt.colorbar()

    numcols, numrows = X.shape
    # def format_coord(x, y):
    #    col = int(x+0.5)
    #    row = int(y+0.5)
    #    if col>=0 and col<numcols and row>=0 and row<numrows:
    #        z = X[row,col]
    #        return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
    #    else:
    #        return 'x=%1.4f, y=%1.4f'%(x, y)

    #ax.format_coord = format_coord
    plt.draw()
    plt.savefig(path + 'seq_%s' % Id)
    #file_simu = file('Expe/Sequences/text/seq_%s.txt' % Id,'w')
    # file_simu.write("Level\tSound\tRepr\NotTok\tCorr\n")
    # for s in seq_o:
    #    file_simu.write("%s\t%s\t%s\t%s\t%s\n" % (s[0],s[1],s[2],s[3],int(s[4])))
    # file_simu.close()
    return


""" Hatch bar :

/   - diagonal hatching
\   - back diagonal
|   - vertical
-   - horizontal
+   - crossed
x   - crossed diagonal
o   - small circle
O   - large circle
.   - dots
*   - stars
"""
