%basic student modelling
% based on dhmm1
% Make an HMM with discrete observations
%   X1 -> X2
%   |     | 
%   v     v
%   Y1    Y2 
% http://bnt.googlecode.com/svn/trunk/docs/usage_dbn.html
% https://www.coursera.org/course/pgm
clc
clear

load OT
nnodes = 3;
%nodes 1-KC 2-EX 3-OB 

nkc = 6;
nQ = 2^nkc; % num hidden states
nO = 2; % num observable symbols
nE = 6; % num exercises

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

bnet.CPD{1} = tabular_CPD(bnet, 1, prior1);
bnet.CPD{2} = tabular_CPD(bnet, 2, prior2);
bnet.CPD{3} = tabular_CPD(bnet, 3, obsmat1);
bnet.CPD{4} = tabular_CPD(bnet, 4, transmat1);



%sampling
ncases = 5; % number of students
T = 100; % T time steps
cases = cell(1, ncases);
fcases = cell(1, ncases);
ss = length(bnet.intra);
for i=1:ncases
  ev = sample_dbn(bnet, 'length', T);
  cases{i} = cell(ss,T);
  cases{i}( onodes,:) = ev(onodes, :);
  fcases{i} = cell(ss,T);
  fcases{i}(:,:) = ev(:, :);
end

%engine{end+1} = jtree_unrolled_dbn_inf_engine(bnet, T);
%engine{end+1} = hmm_inf_engine(bnet);
%engine{end+1} = smoother_engine(hmm_2TBN_inf_engine(bnet));
engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
%engine{end+1} = bk_inf_engine(bnet, 'clusters', {[1]});
%engine{end+1} = jtree_dbn_inf_engine(bnet);

[bnet2, LLtrace] = learn_params_dbn_em(engine, cases, 'max_iter', 10);

norm(CPD_to_CPT(bnet.CPD{1})-CPD_to_CPT(bnet2.CPD{1}))
norm(CPD_to_CPT(bnet.CPD{2})-CPD_to_CPT(bnet2.CPD{2}))
res3 = CPD_to_CPT(bnet.CPD{3})-CPD_to_CPT(bnet2.CPD{3});
res4 = CPD_to_CPT(bnet.CPD{4})-CPD_to_CPT(bnet2.CPD{4});
norm(res3(:))
norm(res4(:))


%engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
% updating probabilities
%[engine, ll] = enter_evidence(engine, cases{2});

% % inferring hidden information
% for ii=1:T
%     aux = marginal_nodes(engine, [1], ii);
%     m(:,ii) = aux.T;
% end
% m
