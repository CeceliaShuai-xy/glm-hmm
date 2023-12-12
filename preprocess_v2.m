%% Author: Cecelia Shuai %%%%%%%%%%%%%%%%%%%
%  Created date: 12/07/2023
%  Purpose: preprocess the extracted 
%  parameters before feeding in GLM 
%  Last edit time: 12/07/2023
%  Last edit made: - change the plotting stype, also adapt code for
%                    no-flanker situation
%  TODOs: visualization of the performance
% ===========================================
% --------- DATA TO BE PROCESSED ------------
% corr_arr =  {-2, -1, 1} = {missed, incorrect, correct}
% target_type_arr = {0, 1} = {vertical, horizontal}
% dist_type_arr = {0, 1} = {vertical, horizontal}
% dist_cont_arr = {0,1,2,3,4,5,6,7,8} = {contrast level, 0 = no distractor}
% incong_tr_arr = {0, 1} = {congruent, incongruent}
% cong_tr_arr = {0, 1} = {incongruent, congruent}
% nodist_tr_arr = {1, 0} = {no distractor, distractor}
% rxt_arr: reaction times
% -------------- DATA WE NEED ---------------
% choice = currrent trial choice = {0,1} 
% stim = {0, 1} = {vertical, horizontal}
% flanker orientation = {0, 1, 2}
% flankerContrast [0,8]
% rewarded = {1, -1} = {rewarded/correct, unrewarded/incorrect}
% trialType  = {0, -1, 1} =  {no flanker, congruent, incongruent}
% reactionT = reaction time 
% wsls_covariate = {-1, 1} = {stay/shift to vert, stay/shift to horz}
    % requires prev choice & prev reward
% prevType = {0, 1, 2} = {no flanker, congruent, incongruent}

%% Load data
clear
clc
% load data
animal = 'M1';
load(['./data/' animal '_data.mat'])
target_contrast = 6; 
data_path = ['./data/Subjects/' animal '/'];
if ~exist(data_path,'dir')
    mkdir(data_path)
end
%% Save data in separate files regarding to session and animal name
% Stim ori: 
% Choice: if rewarded => choice = target orientation
choice = [];

for session_id = 1:length(mdata)
    save_path = [data_path 'session' int2str(session_id) '/'];
    if ~exist(save_path,'dir')
        mkdir(save_path)    
    end

    session_data = mdata{session_id};

    %[stim{0,1}, trialType {-1 incongruent,0 no flanker,1 congruent}, 
    % previous Choice, wsls {-1, 1}, flanker contrast {0,8}]

    %idx of trials where there's no flanker
    id_no_flanker = find(session_data.dist_cont_arr==0); 
    
    % modify trialtype to be {-1, 0, 1}
    % cong_tr_arr = {0, 1} = {incongruent, congruent}
    trialType = session_data.cong_tr_arr;
    trialType(trialType==0) = -1;%trialType(trialType==1) = 1;
    trialType(id_no_flanker) = 0;
    save([save_path '/trialType.mat'],"trialType")
    
    % get flanker contrast
    flankerCont = session_data.dist_cont_arr;
    save([save_path '/flankerCont.mat'],"flankerCont")

    % get stim history 
    stim = session_data.target_type_arr;
    save([save_path '/stim.mat'],"stim")

    rewarded = session_data.corr_arr; %{-2 missed, -1 incorrect,1 correct}
    save([save_path '/rewarded.mat'],"rewarded")

    if rewarded == 1 %stim {0,1}, choice {0,1}
        choice = stim;
    else
        choice = 1 - stim;
    end
    save([save_path '/choice.mat'],"choice")

    prevChoice = horzcat(choice(1),choice); prevChoice = prevChoice(1:end-1);
    save([save_path '/predChoice.mat'],"prevChoice")

    wsls = create_wsls_covariate(prevChoice, rewarded);
    save([save_path '/wsls.mat'],"wsls")

    % not to save but to visualize inputs and y
    X = horzcat(stim', trialType', prevChoice', wsls',flankerCont');
    y = choice';
    design_matrix = [X y];
    DesignTable = array2table(design_matrix,'VariableNames',{'Stim','TrialType','PrevChoice','WSLS','FlankerContrast','Choice(y)'});
end

%% performance visualization
close all
f1 = figure(1);
f1.Position  = [200 800 800 200];
plot(find(rewarded==1),stim(rewarded==1),'.', 'color','b', 'MarkerSize', 10)
hold on
plot(find(rewarded==-1),stim(rewarded==-1),'.', 'color','r', 'MarkerSize', 10)
ylim([-0.5 1.5])
title([animal ' Accuracy = ' num2str(sum(rewarded==1)/length(stim))])
xlabel('trials')
yticks([0 1])
yticklabels(["vertical"; "horizontal"])
ytickangle(90)

%% Helper functions
function wsls =  create_wsls_covariate(prevChoice, rewarded)
%{
inputs:
    rewarded: {-1, 1}, -1 corresponds to failure, 1 corresponds to success
    prevChoice: {0,1} and 0 corresponds to vertical, 1 corresponds to
    horizontal
output:
    wsls: {-1, 1}.  
    1 corresponds to prevChoice = horz and success OR prevChoice = vert and
    failure (choose HORZ next trial)
    -1 corresponds to prevChoice = vert and success OR prevChoice = horz and
    failure (choose VERTICAL next trial)
%}

% remap choice vals
remapped_choice = prevChoice * 2 - 1;
assert(sum(unique(remapped_choice) == [-1,1])==2,'remapping error')
pre_rewarded = horzcat(rewarded(1),rewarded); pre_rewarded = pre_rewarded(1:end-1);
wsls = remapped_choice .* pre_rewarded;
assert(length(unique(wsls)) == 2, "wsls should be in {-1, 1}")
end
