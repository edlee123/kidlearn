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
nnodes = 3;
%nodes 1-KC 2-EX 3-OB 
intra = zeros( nnodes );
intra(1,3) = 1;
intra(2,3) = 1;

inter = zeros( nnodes );
inter(1,1) = 1;
inter(2,1) = 1;

Q = 4; % num hidden states
O = 2; % num observable symbols
E = 3; % num exercises

ns = [Q E O];
dnodes = 1:3;   %'discrete'
onodes = [2 3]; %'observed'

rand('state', 0);
%prior1 = normalise(rand(Q,1));
%transmat1 = mk_stochastic(rand(Q,Q));
%obsmat1 = mk_stochastic(rand(Q,O));
prior1 = [1 0 0 0]';

% states 00-01-10-11
%Exercise 1
transmat1(:,1,:) = [.9 .1 .0 .0;
                    .0 1. .0 .0;
                    .0 .0 .9 .1;
                    .0 .0 .0 1.]; 
%Exercise 2
transmat1(:,2,:) = [.9 .0 .1 .0;
                    .0 .9 .0 .1;
                    .0 .0 1. .0;
                    .0 .0 .0 1.]; 
%Exercise 2
transmat1(:,3,:) = [.9 .0 .1 .0;
                    .0 .9 .0 .1;
                    .0 .0 1. .0;
                    .0 .0 .0 1.]; 
                
slip = .1;
guess = .1;
obsmat1(:,1,:) = [ 1-guess guess;
                   slip    1-slip;
                   1-guess guess;
                   slip    1-slip;];
    
obsmat1(:,2,:) = [ 1-guess guess;
                   1-guess guess;
                   slip    1-slip;
                   slip    1-slip;];
               
obsmat1(:,3,:) = [ 1-guess guess;
                   1-guess guess;
                   slip    1-slip;
                   slip    1-slip;];
               
prior2 = [1 1 1]/3';

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
T = 15; % T time steps
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

CPD_to_CPT(bnet.CPD{1})-CPD_to_CPT(bnet2.CPD{1})
CPD_to_CPT(bnet.CPD{2})-CPD_to_CPT(bnet2.CPD{2})
CPD_to_CPT(bnet.CPD{3})-CPD_to_CPT(bnet2.CPD{3})
CPD_to_CPT(bnet.CPD{4})-CPD_to_CPT(bnet2.CPD{4})


engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
% updating probabilities
[engine, ll] = enter_evidence(engine, cases{2});

% inferring hidden information
for ii=1:T
    aux = marginal_nodes(engine, [1], ii);
    m(:,ii) = aux.T;
end
m
