%mainexample to test creation of models and loading from benjamin /
%generation of data / learning
clc
clear

%initialization
nkc = 6;
nE = 6;
nO = 2;
load OT
bnet = createmodel(nkc,nE,nO,T,O);

%generate data
ncases = 5;
T = 100;
[cases, fcases] = generatedata(bnet, ncases, T);

% learn the parameters from the data
[l,bnet2] = learnparam(cases, bnet);

% learned matrices
prior1 = CPD_to_CPT(bnet2.CPD{1});
observmat = CPD_to_CPT(bnet2.CPD{3});
transmat = CPD_to_CPT(bnet2.CPD{4});
