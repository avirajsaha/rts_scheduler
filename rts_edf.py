import rts_util as rts_util

import math as math
from operator import itemgetter, attrgetter


T_INSTANCE_OFF  = 0
T_TIME_FROM_OFF = 1
T_TIME_TO_OFF   = 2
T_REL_TIME_OFF  = 3
T_DEADLINE_OFF  = 4
T_EXEC_LEFT_OFF = 5
T_PERIOD_OFF    = 6
T_ACTIVE_OFF    = 7
T_PROMOTION_OFF = 8

def rts_edf_schedule(task_set, check_feasible=False, show=True, enhanced_edf = False):
    ret = True
    #sort the task set to get the lowest priority task
    task_set = sorted(task_set, key=itemgetter(2))

    #sched dict 
    sched_dict = {} 

    #
    # task_no : [instance, time_from, time_to, rel_time, deadline, execution_left, period, active]

    # current task
    curr_task = 0

    #
    task_list = range(0, len(task_set));
    task_attr_list = []

    #Assuming the release time of all tasks is 0. 
    for task_no in range(0, len(task_set)):
        task_attr_list.append([0, 0, -1, 0, task_set[task_no][2], (task_set[task_no][1]), task_set[task_no][2], True, False])

    #print task_attr_list

    sched_dict = dict(zip(task_list, task_attr_list)) 


    #Calculate the hyper-period for the task set 
    if(len(task_set) == 1):
        hyper_period = task_set[-1][2]
    elif(len(task_set) == 2):
        hyper_period = (task_set[-1][2]*task_set[-2][2])/rts_util.gcd(task_set[-1][2], task_set[-2][2])
    else:
        time_period = set() 
        for task_no in range(0, len(task_set)):
            time_period.add(task_set[task_no][2])
       
        hyper_period = rts_util.lcm(*time_period)


    #print "Hyper Period =", hyper_period
    hyper_period = 3*hyper_period;

    #find the schedule between time 0 to hyper-period
    need_resched = True 
    curr_task    = (-1);
    deadline_misses = 0
    skip_time       = 0;
    window_size     = 0
    window_deadline_misses  = 0
    for time_point in range(0, hyper_period):
        if (skip_time): 
            skip_time = -1;
            continue;
        #print "Time:", time_point 
        for task_no in range(0, len(task_set)):
            if ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                   ((time_point) // (sched_dict[task_no][T_PERIOD_OFF])== sched_dict[task_no][T_INSTANCE_OFF])):
                #print "2. Swithing",curr_task,"->",task_no 
                sched_dict[task_no][T_ACTIVE_OFF]    = True
                sched_dict[task_no][T_TIME_TO_OFF]   = -1 
                sched_dict[task_no][T_REL_TIME_OFF]  = -1; 
                break;
        new_task = -1;
        for task_no in range(0, len(task_set)):
            if (new_task == (-1)) and (sched_dict[task_no][T_ACTIVE_OFF] == True):
                new_task = task_no; 

            if (new_task != (-1)): 
                if (sched_dict[task_no][T_ACTIVE_OFF] == True) and (((sched_dict[task_no][T_REL_TIME_OFF] + sched_dict[task_no][T_DEADLINE_OFF]) < 
                     (sched_dict[new_task][T_REL_TIME_OFF] + sched_dict[new_task][T_DEADLINE_OFF]))):
                    new_task = task_no

        if(need_resched):
            if (new_task != (-1)): 
                if (curr_task != (-1)): pass
                    #print "2. Time:", time_point 
                    #print "2. Swithing",curr_task,"->",new_task 
                    #rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                curr_task = new_task;
                sched_dict[curr_task][T_ACTIVE_OFF]    = True
                sched_dict[curr_task][T_TIME_TO_OFF]   = -1 
                sched_dict[curr_task][T_REL_TIME_OFF]  = -1; 
                need_resched = False;
            if(need_resched): continue;
        else:
            #logic for preemption
            if (new_task != (-1)) and (new_task != curr_task): 
                if (curr_task != (-1)):
                    #print "3. Time:", time_point 
                    #print "3. Swithing",curr_task,"->",new_task 
                    rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                curr_task = new_task;
                sched_dict[curr_task][T_ACTIVE_OFF]    = True
                sched_dict[curr_task][T_TIME_TO_OFF]   = -1 
                sched_dict[curr_task][T_REL_TIME_OFF]  = -1; 

                
        if sched_dict[curr_task][T_ACTIVE_OFF] == True:
            #running for the first time 
            if sched_dict[curr_task][T_TIME_TO_OFF] == -1:
                sched_dict[curr_task][T_TIME_FROM_OFF] = time_point;
                sched_dict[curr_task][T_TIME_TO_OFF] = time_point;
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = task_set[curr_task][1]; 
            if sched_dict[curr_task][T_REL_TIME_OFF] == -1:
                sched_dict[curr_task][T_REL_TIME_OFF] = time_point; 
                sched_dict[curr_task][T_DEADLINE_OFF] = time_point + task_set[curr_task][2]; 

            sched_dict[curr_task][T_TIME_TO_OFF] = time_point 
            sched_dict[curr_task][T_EXEC_LEFT_OFF] -= 1

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] < 0:
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = 0

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] == 0:
                #Done with the job. Move to the next one
                rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                sched_dict[curr_task][T_ACTIVE_OFF] = False
                sched_dict[curr_task][T_INSTANCE_OFF]  += 1 
                window_size += 1
                if (check_feasible and sched_dict[curr_task][T_TIME_TO_OFF] > sched_dict[curr_task][T_DEADLINE_OFF]):
                    ret = False
                    deadline_misses += 1
                    window_deadline_misses +=1
                    if(enhanced_edf == True and window_deadline_misses == 2):
                        val_ret, val_deadline_misses, val_skip_time, sched_dict =  enhanced_edf_switch_to_rm(time_point, sched_dict, hyper_period, curr_task, task_set)
                        skip_time +=val_skip_time 
                        deadline_misses += val_deadline_misses; 
                        window_size = 0;
                        window_deadline_misses = 0
                if(window_size % 5 == 0):
                    window_size = 0;
                    window_deadline_misses = 0 
                need_resched = True
                continue;


    if (not check_feasible):
        rts_util.rts_rm_schedule_show(show);

    return (ret, deadline_misses)


def enhanced_edf_switch_to_rm(time_start, sched_dict, hyper_period, curr_task, task_set):

    print "Entered enhanced_edf_switch_to_rm"

    ret = True
    skip_time = 0;
    need_resched = True
    deadline_misses = 0;
    deadline_nomisses = 0;
    window_size = 0
    for time_point in range(time_start, hyper_period):
        #print "Time:", time_point 
        skip_time += 1
        if(need_resched):
            for task_no in range(0, len(task_set)):
                if(sched_dict[task_no][T_ACTIVE_OFF] == True):
                    rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "1. Swithing",curr_task,"->",task_no 
                    curr_task = task_no;
                    need_resched = False;
                    break;
                elif ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                       ((time_point) // (sched_dict[task_no][T_PERIOD_OFF])== sched_dict[task_no][T_INSTANCE_OFF])):
                    rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "2. Swithing",curr_task,"->",task_no 
                    curr_task = task_no
                    sched_dict[curr_task][T_ACTIVE_OFF]    = True
                    sched_dict[curr_task][T_TIME_TO_OFF]   = -1 
                    sched_dict[curr_task][T_REL_TIME_OFF]  = -1; 
                    need_resched = False;
                    break;
            if(need_resched): continue;
        else:
            #logic for preemption
            for task_no in range(0, curr_task):
                if(sched_dict[task_no][T_ACTIVE_OFF] == True):
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    curr_task = task_no;
                    #print "3. Swithing",curr_task,"->",task_no 
                    break;
                elif ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                       ((time_point) // (sched_dict[task_no][T_PERIOD_OFF]) == sched_dict[task_no][T_INSTANCE_OFF])):
                    rts_util.rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "4. Swithing",curr_task,"->",task_no 
                    curr_task = task_no
                    sched_dict[curr_task][T_ACTIVE_OFF]    = True
                    sched_dict[curr_task][T_TIME_TO_OFF]   = -1
                    sched_dict[curr_task][T_REL_TIME_OFF]  = -1; 
                    break;
                
        if sched_dict[curr_task][T_ACTIVE_OFF] == True:
            #running for the first time 
            if sched_dict[curr_task][T_TIME_TO_OFF] == -1:
                sched_dict[curr_task][T_TIME_FROM_OFF] = time_point;
                sched_dict[curr_task][T_TIME_TO_OFF] = time_point;
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = task_set[curr_task][1]; 
            if sched_dict[curr_task][T_REL_TIME_OFF] == -1:
                sched_dict[curr_task][T_REL_TIME_OFF] = time_point; 
                sched_dict[curr_task][T_DEADLINE_OFF] = time_point + task_set[curr_task][2]; 

            sched_dict[curr_task][T_TIME_TO_OFF] = time_point 
            sched_dict[curr_task][T_EXEC_LEFT_OFF] -= 1

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] < 0:
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = 0

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] == 0:
                #Done with the job. Move to the next one
                sched_dict[curr_task][T_ACTIVE_OFF] = False
                sched_dict[curr_task][T_INSTANCE_OFF]  += 1 
                window_size += 1
                if (sched_dict[curr_task][T_TIME_TO_OFF] > sched_dict[curr_task][T_DEADLINE_OFF]):
                    ret = False
                    deadline_misses += 1
                    deadline_nomisses = 0
                else:
                    deadline_nomisses += 1
                    if (deadline_nomisses == 2):
                        break;
                if ((window_size % 5) == 0):
                    window_size = 0
                    deadline_nomisses = 0
                need_resched = True
                continue;

    return (ret, deadline_misses, skip_time, sched_dict)



def rts_rm_pp_schedule(task_set, check_feasible=False, show=True):
    ret = True
    #sort the task set to get the lowest priority task
    task_set = sorted(task_set, key=itemgetter(2))

    #sched dict 
    sched_dict = {} 


    #
    # task_no : [instance, time_from, time_to, rel_time, deadline, execution_left, period, active]

    # current task
    curr_task = 0

    #
    task_list = range(0, len(task_set));
    task_attr_list = []

    #Assuming the release time of all tasks is 0. 
    for task_no in range(0, len(task_set)):
        task_attr_list.append([0, 0, -1, 0, task_set[task_no][2], (task_set[task_no][1]), task_set[task_no][2], True, False])

    #print task_attr_list

    sched_dict = dict(zip(task_list, task_attr_list)) 


    #Calculate the hyper-period for the task set 
    if(len(task_set) == 1):
        hyper_period = task_set[-1][2]
    elif(len(task_set) == 2):
        hyper_period = (task_set[-1][2]*task_set[-2][2])/gcd(task_set[-1][2], task_set[-2][2])
    else:
        time_period = set() 
        for task_no in range(0, len(task_set)):
            time_period.add(task_set[task_no][2])
       
        hyper_period = lcm(*time_period)


    #print "Hyper Period =", hyper_period

    #find the schedule between time 0 to hyper-period
    need_resched = False 
    need_pp_resched = False 
    total_rm_pp_promotions = 0
    for time_point in range(0, hyper_period+1):
        #print "Time:", time_point 

        if(need_resched):
            for task_no in range(0, len(task_set)):
                if(sched_dict[task_no][T_ACTIVE_OFF] == True):
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "1. Swithing",curr_task,"->",task_no 
                    if (need_pp_resched):
                        sched_dict[curr_task][T_PROMOTION_OFF] = False;
                        need_pp_resched = False
                    curr_task = task_no;
                    #check for pp task
                    need_resched = False;
                    sched_dict[curr_task][T_TIME_FROM_OFF] = time_point;
                    break;
                elif ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                       ((time_point) // (sched_dict[task_no][T_PERIOD_OFF])== sched_dict[task_no][T_INSTANCE_OFF])):
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "2. Swithing",curr_task,"->",task_no 
                    if (need_pp_resched):
                        sched_dict[curr_task][T_PROMOTION_OFF] = False;
                        need_pp_resched = False
                    curr_task = task_no
                    sched_dict[curr_task][T_ACTIVE_OFF]    = True
                    sched_dict[curr_task][T_TIME_TO_OFF]   = -1 
                    sched_dict[curr_task][T_REL_TIME_OFF]  = -1; 
                    need_resched = False;
                    break;


            if(need_resched): continue;
        else:
            if (not need_pp_resched):
                #logic for preemption
                #preemption will be disabled when a pp task is executing.
                curr_task_normal = (-1)
                for task_no in range(0, curr_task):
                    if ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                           ((time_point) // (sched_dict[task_no][T_PERIOD_OFF]) == sched_dict[task_no][T_INSTANCE_OFF])):
                        curr_task_normal = task_no
                        break;
                curr_task_pp = (-1) 
                for task_no in range(0, len(task_set)):
                    #check for pp task
                    if sched_dict[task_no][T_ACTIVE_OFF]  == True: 
                        if (time_point + sched_dict[task_no][T_EXEC_LEFT_OFF] >= sched_dict[task_no][T_DEADLINE_OFF]):
                            need_pp_resched = True
                            sched_dict[task_no][T_PROMOTION_OFF] = True
                            curr_task_pp = task_no
                            break;

                if curr_task_pp != (-1):
                    #print "4.1 Swithing",curr_task,"->",curr_task_pp 
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    curr_task = curr_task_pp
                    sched_dict[curr_task][T_TIME_FROM_OFF] = time_point;
                    total_rm_pp_promotions += 1
                elif curr_task_normal != (-1):
                    #print "4.2 Swithing",curr_task,"->",curr_task_normal 
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    sched_dict[curr_task_normal][T_ACTIVE_OFF]    = True
                    sched_dict[curr_task_normal][T_TIME_TO_OFF]   = -1
                    sched_dict[curr_task_normal][T_REL_TIME_OFF]  = -1; 
                    curr_task = curr_task_normal

             
                
        if sched_dict[curr_task][T_ACTIVE_OFF] == True:
            #running for the first time 
            if sched_dict[curr_task][T_TIME_TO_OFF] == -1:
                sched_dict[curr_task][T_TIME_FROM_OFF] = time_point;
                sched_dict[curr_task][T_TIME_TO_OFF] = time_point;
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = task_set[curr_task][1]; 

            if sched_dict[curr_task][T_REL_TIME_OFF] == -1:
                sched_dict[curr_task][T_REL_TIME_OFF] = time_point; 
                sched_dict[curr_task][T_DEADLINE_OFF] = time_point + task_set[curr_task][2]; 

            sched_dict[curr_task][T_TIME_TO_OFF] = time_point 
            sched_dict[curr_task][T_EXEC_LEFT_OFF] -= 1

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] < 0:
                sched_dict[curr_task][T_EXEC_LEFT_OFF] = 0

            if sched_dict[curr_task][T_EXEC_LEFT_OFF] == 0:
                #Done with the job. Move to the next one
                sched_dict[curr_task][T_ACTIVE_OFF] = False
                sched_dict[curr_task][T_INSTANCE_OFF]  += 1 
                if (check_feasible and sched_dict[curr_task][T_TIME_TO_OFF] > sched_dict[curr_task][T_DEADLINE_OFF]):
                    ret = False
                    break;
                need_resched = True
                continue;


    if (not check_feasible):
        rts_rm_schedule_show(show);

    return (ret, total_rm_pp_promotions)
