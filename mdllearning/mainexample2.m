%mainexample to test learning from big data of benjamin
clc
clear

%initialization
nkc = 6;
nE = 6;
nO = 2;
load OT
bnet = createmodel(nkc,nE,nO,T,O);

load simures
data = double(POMDP(1:50,:,1:200))+1;
%convert in cases format of BNT
for ii = 1:size(POMDP,1)
    cases{ii} = cell(3,size(data,3));
    cases{ii}(2:3,:) = mat2cell(squeeze(data(1,:,:)),[1 1],ones(1,size(data,3)));
end

tic
% learn the parameters from the data
[l,bnet2] = learnparam(cases, bnet);
toc
% learned matrices
prior1 = CPD_to_CPT(bnet2.CPD{1});
observmat = CPD_to_CPT(bnet2.CPD{3});
transmat = CPD_to_CPT(bnet2.CPD{4});
