%% Author: Cecelia Shuai %%%%%%%%%%%%%%%%%%%
%  Created date: 11/28/2023
%  Purpose: preprocess the extracted 
%  parameters before feeding in GLM 
%  Last edit time: 11/28/2023
%  Last edit made: - change choice val from {1,2} to {0,1}(11/29)
%                  - remove some redundant var (flanker,
%                  reactT,prevType&Choice (11/30)
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
% choice = currrent trial choice
% stim = {1, 2} = {vertical, horizontal}
% flanker = {0, 1, 2}
% flankerContrast (relative) = stim cont - flanker cont [-6,2]
% rewarded = {1, -1} = {rewarded/correct, unrewarded/incorrect}
% trialType  = {0, 1, 2} =  {no flanker, congruent, incongruent}
% reactionT = reaction time 
% wsls_covariate = {-1, 1} = {stay/shift to vert, stay/shift to horz}
    % requires prev choice & prev reward
% prevType = {0, 1, 2} = {no flanker, congruent, incongruent}

%% Load data
clear
clc
% load data
load('./data/M1_data.mat')
animal = 'A';
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

    %idx of trials where there's no flanker
    id_no_flanker = find(session_data.dist_cont_arr==0); 
    % idx of weak/stronger flanker contrast
    temp_contr = session_data.dist_cont_arr - target_contrast;
    temp_weak_id = find(temp_contr <= -3); % weaker flanker
    idx_stronger_flanker = find(temp_contr >=0);  % stronger contrast
    Acommon = intersect(id_no_flanker,temp_weak_id);
    idx_weaker_flanker = setxor(temp_weak_id,Acommon);
    
    % intermediate contrast trials are omitted
    trials_to_keep = sort([temp_weak_id idx_stronger_flanker]);

    % modify trialtype to be {-2, -1, 0, 1, 2}
    % cong_tr_arr = {0, 1} = {incongruent, congruent}
    trialType = session_data.cong_tr_arr;
    trialType(trialType==0) = -1;trialType(trialType==1) = 1;
    trialType(id_no_flanker) = 0;
%     trialType(idx_weaker_flanker) = trialType(idx_weaker_flanker)*1;
    trialType(idx_weaker_flanker) = trialType(idx_weaker_flanker)*2;
    trialType = trialType(trials_to_keep);

    save([save_path '/trialType.mat'],"trialType")

    
    % get stim history 
    stim = session_data.target_type_arr + 1;
    stim = stim(trials_to_keep);
    save([save_path '/stim.mat'],"stim")

    rewarded = session_data.corr_arr;
    rewarded = rewarded(trials_to_keep);
    save([save_path '/rewarded.mat'],"rewarded")

    if rewarded %stim {1,2}, choice {0,1}
        choice = stim - 1;
    else
        choice = 2 - stim;
    end
    save([save_path '/choice.mat'],"choice")

    prevChoice = horzcat(choice(1),choice); prevChoice = prevChoice(1:end-1);
    save([save_path '/predChoice.mat'],"prevChoice")

    wsls = create_wsls_covariate(prevChoice, rewarded);
    save([save_path '/wsls.mat'],"wsls")

    % not to save but to visualize inputs and y
    X = horzcat(stim', trialType', rewarded', wsls');
    y = choice';
    design_matrix = [X y];
end

%% performance visualization

figure(1)
plot(stim(rewarded==1),'.', 'color','b', 'MarkerSize', 10)
hold on
plot(stim(rewarded==-1),'.', 'color','r', 'MarkerSize', 10)
ylim([0.5 2.5])
title(['Accuracy = ' num2str(sum(rewarded==1)/length(stim))])
xlabel('trials')
yticks([1 2])
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
    failure
    -1 corresponds to prevChoice = vert and success OR prevChoice = horz and
    failure
%}

% remap choice vals
remapped_choice = prevChoice * 2 - 1;
assert(sum(unique(remapped_choice) == [-1,1])==2,'remapping error')
pre_rewarded = horzcat(rewarded(1),rewarded); pre_rewarded = pre_rewarded(1:end-1);
wsls = remapped_choice .* pre_rewarded;
assert(length(unique(wsls)) == 2, "wsls should be in {-1, 1}")
end



