%basic student modelling
% based on dhmm1
% Make an HMM with discrete observations
%   X1 -> X2
%   |     | 
%   v     v
%   Y1    Y2 
% http://bnt.googlecode.com/svn/trunk/docs/usage_dbn.html
% https://www.coursera.org/course/pgm

clear

intra = zeros(2);
intra(1,2) = 1;
inter = zeros(2);
inter(1,1) = 1;
n = 2;

Q = 2; % num hidden states
O = 2; % num observable symbols

ns = [Q O];
dnodes = 1:2; %'discrete'
onodes = [2]; %'observed'

rand('state', 0);
%prior1 = normalise(rand(Q,1));
%transmat1 = mk_stochastic(rand(Q,Q));
%obsmat1 = mk_stochastic(rand(Q,O));
prior1 = [1 0]';
transmat1 = [.9 .1;
             0  1];
obsmat1 = [1 0;
           0 1];

eclass1 = [1 2];
eclass2 = [3 2];
bnet = mk_dbn(intra, inter, ns, 'discrete', dnodes, 'eclass1', eclass1, 'eclass2', eclass2, ...
	      'observed', onodes);

bnet.CPD{1} = tabular_CPD(bnet, 1, prior1);
bnet.CPD{2} = tabular_CPD(bnet, 2, obsmat1);
bnet.CPD{3} = tabular_CPD(bnet, 3, transmat1);

%sampling
ncases = 10; % number of students
T = 9; % T time steps
cases = cell(1, ncases);
ss = length(bnet.intra);
for i=1:ncases
  ev = sample_dbn(bnet, 'length', T);
  cases{i} = cell(ss,T);
  cases{i}(onodes,:) = ev(onodes, :);
end

%engine{end+1} = jtree_unrolled_dbn_inf_engine(bnet, T);
%engine{end+1} = hmm_inf_engine(bnet);
%engine{end+1} = smoother_engine(hmm_2TBN_inf_engine(bnet));
engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
%engine{end+1} = bk_inf_engine(bnet, 'clusters', {[1]});
%engine{end+1} = jtree_dbn_inf_engine(bnet);

[bnet2, LLtrace] = learn_params_dbn_em(engine, cases, 'max_iter', 10);

CPD_to_CPT(bnet.CPD{1})
CPD_to_CPT(bnet2.CPD{1})
CPD_to_CPT(bnet.CPD{2})
CPD_to_CPT(bnet2.CPD{2})
CPD_to_CPT(bnet.CPD{3})
CPD_to_CPT(bnet2.CPD{3})


engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
% updating probabilities
[engine, ll] = enter_evidence(engine, cases{2});

% inferring hidden information
for ii=1:T
    aux = marginal_nodes(engine, [1], ii);
    m(:,ii) = aux.T;
end
m
