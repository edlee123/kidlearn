function [l,bnet2] = learnparam(cases, bnet)

%engine = jtree_unrolled_dbn_inf_engine(bnet, T);
%engine = hmm_inf_engine(bnet);
%engine = smoother_engine(hmm_2TBN_inf_engine(bnet));
%engine = smoother_engine(jtree_2TBN_inf_engine(bnet));
%engine = bk_inf_engine(bnet, 'clusters', {[1]});
engine = jtree_dbn_inf_engine(bnet);

[bnet2, LLtrace] = learn_params_dbn_em(engine, cases, 'max_iter', 10);

bnet2.onodes = bnet.onodes;

l(1) = norm(CPD_to_CPT(bnet.CPD{1})-CPD_to_CPT(bnet2.CPD{1}));
l(2) = norm(CPD_to_CPT(bnet.CPD{2})-CPD_to_CPT(bnet2.CPD{2}));
res3 = CPD_to_CPT(bnet.CPD{3})-CPD_to_CPT(bnet2.CPD{3});
res4 = CPD_to_CPT(bnet.CPD{4})-CPD_to_CPT(bnet2.CPD{4});
l(3) = norm(res3(:));
l(4) = norm(res4(:));
