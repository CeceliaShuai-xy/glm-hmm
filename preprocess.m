%% Author: Cecelia Shuai %%%%%%%%%%%%%%%%%%%
%  Created date: 11/28/2023
%  Purpose: preprocess the extracted 
%  parameters before feeding in GLM 
%  Last edit time: 11/28/2023
%  Last edit made: Save each input as individual 
%      with dir name ../data/Subjects/animal/session#
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
% flanker = {1, 2}
% flankerContrast (relative) = stim cont - flanker cont 
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

    % get stim history 
    stim = session_data.target_type_arr + 1;
    save([save_path '/stim.mat'],"stim")

    flanker = session_data.dist_type_arr + 1;
    id_no_flanker = flanker==10; %idx of trials where there's no flanker
    flanker(id_no_flanker) = 0; % no distractor/flanker situation
    save([save_path '/flanker.mat'],"flanker")
    
    rewarded = session_data.corr_arr;
    save([save_path '/rewarded.mat'],"rewarded")
    if rewarded
        choice = stim;
    else
        choice = 3 - stim;
    end
    save([save_path '/choice.mat'],"choice")
    
    flankerContrast = session_data.dist_cont_arr - target_contrast;
    flankerContrast(id_no_flanker) = 0;
    save([save_path '/flankerContrast.mat'],"flankerContrast")

    trialType = session_data.cong_tr_arr + 1;
    trialType(id_no_flanker) = 0;
    save([save_path '/trialType.mat'],"trialType")

    reactionT = session_data.rxt_arr';
    save([save_path '/reactionT.mat'],"reactionT")

    prevType = horzcat(trialType(1),trialType); prevType = prevType(1:end-1);
    save([save_path '/prevType.mat'],"prevType")

    prevChoice = horzcat(choice(1),choice); prevChoice = prevChoice(1:end-1);
    save([save_path '/prevChoice.mat'],"prevChoice")

    wsls = create_wsls_covariate(prevChoice, rewarded);
    save([save_path '/wsls.mat'],"wsls")

end

function wsls =  create_wsls_covariate(prevChoice, rewarded)
%{
inputs:
    rewarded: {-1, 1}, -1 corresponds to failure, 1 corresponds to success
    prevChoice: {1,2} and 1 corresponds to vertical, 2 corresponds to
    horizontal
output:
    wsls: {-1, 1}.  
    1 corresponds to prevChoice = horz and success OR prevChoice = vert and
    failure
    -1 corresponds to prevChoice = vert and success OR prevChoice = horz and
    failure
%}

% remap choice vals
remapped_choice = prevChoice * 2 - 3;
pre_rewarded = horzcat(rewarded(1),rewarded); pre_rewarded = pre_rewarded(1:end-1);
wsls = remapped_choice .* pre_rewarded;
assert(length(unique(wsls)) == 2, "wsls should be in {-1, 1}")
end



