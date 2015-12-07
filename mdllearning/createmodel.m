function bnet = createmodel(nkc,nE,nO,T,O)

%basic student modelling
% based on dhmm1
% Make an HMM with discrete observations
%   X1 -> X2
%   |     | 
%   v     v
%   Y1    Y2 
% http://bnt.googlecode.com/svn/trunk/docs/usage_dbn.html
% https://www.coursera.org/course/pgm

nnodes = 3;
%nodes 1-KC 2-EX 3-OB 

%nkc = 6; % number of knowledge component
%nO = 2; % num observable symbols
%nE = 6; % num exercises

nQ = 2^nkc; % num hidden states

intra = zeros( nnodes );
intra(1,3) = 1;
intra(2,3) = 1;

inter = zeros( nnodes );
inter(1,1) = 1;
inter(2,1) = 1;


ns = [nQ nE nO];
dnodes = 1:3;   %'discrete'
onodes = [2 3]; %'observed'

rand('state', 0);
%transmat1 = mk_stochastic(rand(nQ,nE,nQ));
%obsmat1 = mk_stochastic(rand(nQ,nE,nO));
transmat1 = T;
obsmat1 = O;

% starting in 0 knowledge
prior1 = zeros(nQ,1);
prior1(1) = 1;
% exercices are shown randomly
prior2 = ones(nE,1)/nE;

eclass1 = [1 2 3];
eclass2 = [4 2 3];
bnet = mk_dbn(intra, inter, ns, 'discrete', dnodes, ...
                'eclass1', eclass1, 'eclass2', eclass2, ...
                'observed', onodes, 'names', {'K','O','E'});
%draw_dbn(intra,inter);
bnet.onodes = onodes;

bnet.CPD{1} = tabular_CPD(bnet, 1, prior1);
bnet.CPD{2} = tabular_CPD(bnet, 2, prior2);
bnet.CPD{3} = tabular_CPD(bnet, 3, obsmat1);
bnet.CPD{4} = tabular_CPD(bnet, 4, transmat1);
