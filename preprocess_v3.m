%% Author: Cecelia Shuai %%%%%%%%%%%%%%%%%%%
%  Created date: 12/17/2023
%  Purpose: preprocess the extracted 
%  parameters before feeding in GLM 
%  Last edit time: 1/16/2024
%  Last edit made: - add more input variables 
% 
% ===========================================
% --------- DATA TO BE PROCESSED ------------
% corr_arr =  {-2, -1, 1} = {missed, incorrect, correct}
% target_type_arr = {0, 1} = {vertical, horizontal}
% dist_type_arr = {0, 1} = {vertical, horizontal} -> 9: no flanker
% dist_cont_arr = {0,1,2,3,4,5,6,7,8} = {contrast level, 0 = no distractor}
% incong_tr_arr = {0, 1} = {congruent, incongruent}
% cong_tr_arr = {0, 1} = {incongruent, congruent}
% nodist_tr_arr = {1, 0} = {no distractor, distractor}
% rxt_arr: reaction times
% -------------- DATA WE NEED ---------------
% Dependent variables
% choice = currrent trial choice = {0,1} 
% reaction time
%         ----------------------------
% Independent variables
% stim = {-1, 1} = {vertical, horizontal}
% trialType  = {0, -1, 1} =  {no flanker, incongruent, congruent}
% prevChoice  = {0,1}
% wsls_covariate = {-1, 1} = {stay/shift to vert, stay/shift to horz}
%                   > requires prev choice & prev reward
% flankerContrast [0,8]
% flanker = {0, -1, 1} = {no flanker, vert, horz}
% prevType = {0, -1, 1} 
% (?)rewarded = {1, -1} = {rewarded/correct, unrewarded/incorrect}
% prevReward = {1, -1}
% prevStim = {-1, 1} 
%% Load data
clear
clc
close all
% load data according to the animal id
animal = 'M1_Sal';
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
design_table = cell(length(mdata));

if length(mdata) <= 6
    f = figure;  
    f.Position = [700 900 900 700]; 
    sgtitle([animal " Performance"],'Interpreter', 'none')
else
    f = figure;  
    f.Position = [700 900 1800 700]; 
    sgtitle([animal " Performance"],'Interpreter', 'none')
end

for session_id = 1:length(mdata)
    save_path = [data_path 'session' int2str(session_id) '/'];
    if ~exist(save_path,'dir')
        mkdir(save_path)    
    end
    session_data = mdata{session_id};
    data_length = length(session_data.cong_tr_arr)-1;

    %idx of trials where there's no flanker
    id_no_flanker = find(session_data.dist_cont_arr==0);
    temp = find(session_data.dist_type_arr==9);
    assert(unique(temp == id_no_flanker),'flanker error')
    
    % modify trialtype to be {0, -1, 1}
    % cong_tr_arr = {0, 1} = {incongruent, congruent}
    trialType = session_data.cong_tr_arr;
    trialType(trialType==0) = -1;% incongruent -> 1
    trialType(trialType==1) = 1;% congruent -> 2
    trialType(id_no_flanker) = 0; % no flanker -> 0
    prevType = trialType(1:end-1);
    trialType = trialType(2:end);
    

    % get flanker contrast
    flankerCont = session_data.dist_cont_arr;
    flankerCont = flankerCont(2:end);
    
    % get stim history 
    stim = session_data.target_type_arr; % {0,1}


    % get flanker orientation {0,1,9} -> {0, -1, 1}
    flanker = session_data.dist_type_arr;
    flanker(flanker==0) = -1;
    flanker(id_no_flanker) = 0;
    flanker = flanker(2:end);

    % get reward history
    rewarded = session_data.corr_arr; %{-2 missed, -1 incorrect,1 correct}
    prevReward = rewarded(1:end-1);
    
    % derive choice history, initiate chocie array
    choice = rewarded;
    % stim = {0,1}
    % choice = {0,1}
    % reward = -1 incorrect -> choice = oposite of stim 
    % reward = 1 correct -> choice = stim orientation
    for idx = 1:length(rewarded)
        if rewarded(idx)== -1
            % incorrect trials
            choice(idx) = 1 - stim(idx);
        else 
            % correct
            choice(idx) = stim(idx);
        end
    end
    
    % transfrom stim {0,1} ->{-1,1}
    stim(stim==0)=-1;
    prevStim = stim(1:end-1);

    prevChoice = choice(1:end-1);
    choice = choice(2:end);
    stim = stim(2:end);
    rewarded = rewarded(2:end);

    % get wsls covariate
    wsls = create_wsls_covariate(prevChoice, prevReward);
    
    % get reaction time
    rxt = session_data.rxt_arr';
    rxt = rxt(2:end);

    % save all vars
    % this step is to avoid using python to read table/struct from matlab, it could
    % be simplified but since we just need to run this code once for each animal, it
    % may just work fine with simple code
    save([save_path '/choice.mat'],"choice")
    save([save_path '/rxt.mat'],"rxt")
    save([save_path '/stim.mat'],"stim")
    save([save_path '/prevStim.mat'],"prevStim")
    save([save_path '/trialType.mat'],"trialType")
    save([save_path '/prevType.mat'],"prevType")
    save([save_path '/predChoice.mat'],"prevChoice")
    save([save_path '/wsls.mat'],"wsls")
    save([save_path '/flanker.mat'],"flanker")
    save([save_path '/flankerCont.mat'],"flankerCont")
    save([save_path '/rewarded.mat'],"rewarded")
    save([save_path '/prevReward.mat'],"prevReward")
    
    

    % check in the design_table to inspect 
    % if all variables have expected values
    X = horzcat(stim', trialType', flanker', ...
        flankerCont', prevStim', prevType', ...
        prevChoice', wsls',prevReward');
    y = horzcat(choice',rxt');
    design_matrix = [X y];
    DesignTable = array2table(design_matrix,'VariableNames', ...
        {'Stim','TrialType','Flanker', 'FlankerContrast','PrevStim', ...
        'PrevType', 'PrevChoice','WSLS', 'PrevReward', 'Choice(y1)','ReactionT(y2)'});
    design_table{session_id} = DesignTable;
    
    
    % performance visualization
    if length(mdata) <= 6
        subplot(6,1,session_id)
    else 
        subplot(6,2,session_id)
    end
    plot(find(rewarded==1),choice(rewarded==1),'.', 'color','b', 'MarkerSize', 10)
    hold on
    plot(find(rewarded==-1),choice(rewarded==-1),'.', 'color','r', 'MarkerSize', 10)
    ylim([-0.5 1.5])
    xlim([0 130])
    title(['Sess ' int2str(session_id) ' Accuracy = ' num2str(sum(rewarded==1)/length(stim))])
    xlabel('trials')
    yticks([0 1])
    yticklabels(["vertical"; "horizontal"])
%     ytickangle(45)
    hold off
    
end
saveas(gcf,[animal '_performance'],'jpg')

%% Helper functions
function wsls =  create_wsls_covariate(prevChoice, PrevReward)
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
remapped_choice = prevChoice * 2 - 1; % map choice to {-1, 1}
assert(sum(unique(remapped_choice) == [-1,1])==2,'remapping error')
wsls = remapped_choice .* PrevReward;
assert(length(unique(wsls)) == 2, "wsls should be in {-1, 1}")
end
% wsls = 1:choose horz this trial
% choice = -1; prev_rewarded = -1 (vert, not rewarded)
% choice = 1; prev_rewarded = 1 (horz, rewarded)
% wsls = -1: choose vert this trial
% choice = -1; prev_rewarded = 1 (vert, rewarded)
% choice = 1; prev_rewarded = -1 (horz, not rewarded)
