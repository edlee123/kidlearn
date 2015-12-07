function [cases, fcases] = generatedata(bnet, ncases, T)

%sampling
%ncases = 5; % number of students
%T = 100; % T time steps
cases = cell(1, ncases);
fcases = cell(1, ncases);
ss = length(bnet.intra);
for i=1:ncases
  ev = sample_dbn(bnet, 'length', T);
  cases{i} = cell(ss,T);
  cases{i}( bnet.onodes,:) = ev(bnet.onodes, :);
  fcases{i} = cell(ss,T);
  fcases{i}(:,:) = ev(:, :);
end