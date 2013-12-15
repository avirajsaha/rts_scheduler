##
# Author Aviraj Saha (asaha3@hawk.iit.edu)
# Given a schedule the module finds out whether a feasible schedule 
# can be obtained using the RM-PP scheduling algorithm.
# Since the utilization is above 69% the method used is the 
# time analysis method.
# The function also returns the time point where the  priority 
# promotion is needed. 
##

import math as math
from operator import itemgetter, attrgetter

def rts_rm_time_analysis(task_set):
    """
    Test whether the task set is schedulable using the RM algorithm
    using time analysis.
    """

    ret = False
    #sort the task set to get the lowest priority task
    task_set = sorted(task_set, key=itemgetter(2))
 
    #lowest priority task
    lowest_prio_task = task_set[-1]

    #the set of time points
    time_samples = set() 
    #find the interference due to higher priority job

    for task in task_set[:-1]:
        for time_point in range(1, int(math.floor(lowest_prio_task[2]/task[2])) + 1):
            time_samples.add(time_point*task[2]);

    for time_val in time_samples:
        wet = lowest_prio_task[1]
        for task in task_set[:-1]:
            wet += float(float(time_val)/task[2])*task[1]

        #print ("wet = %f, t = %f\n" %(wet, time_val));
        if(wet < time_val):
            #print "Task set is schedulable"
            ret = True
            break; 
    return ret

schedule_chart = []
def rts_rm_schedule_dump(curr_task, sched_info):
    global schedule_chart
    schedule_chart.append([curr_task+1, sched_info[T_INSTANCE_OFF], sched_info[T_TIME_FROM_OFF], sched_info[T_TIME_TO_OFF], sched_info[T_REL_TIME_OFF], sched_info[T_DEADLINE_OFF], sched_info[T_EXEC_LEFT_OFF], sched_info[T_PROMOTION_OFF]])


def rts_rm_schedule_show(show=True):
    global schedule_chart
    if show:
	    print "\"Promotion\"\t\"Time(from)\"\t\"Time(to)\"\t\"Task Id\"\t\"Instance\"\t\"Rel Time\"\t\"Deadline\"\t\"Execution Left\""
	    for sched_entry in schedule_chart:
		if (sched_entry[7] == True):
		    promotion = "yes"
		else:
		    promotion = "no"
		print "%s\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t%d\t\t\t" %(promotion, sched_entry[2], sched_entry[3], sched_entry[0], sched_entry[1], sched_entry[4],  sched_entry[5],  sched_entry[6])
    #Flush after the display
    schedule_chart = []



T_INSTANCE_OFF  = 0
T_TIME_FROM_OFF = 1
T_TIME_TO_OFF   = 2
T_REL_TIME_OFF  = 3
T_DEADLINE_OFF  = 4
T_EXEC_LEFT_OFF = 5
T_PERIOD_OFF    = 6
T_ACTIVE_OFF    = 7
T_PROMOTION_OFF = 8

def gcd(*numbers):
    """Return the greatest common divisor of the given integers"""
    from fractions import gcd
    return reduce(gcd, numbers)

def lcm(*numbers):
    """Return lowest common multiple."""    
    def lcm(a, b):
        return (a * b) // gcd(a, b)
    return reduce(lcm, numbers, 1)

def rts_rm_hyperperiod(task_set):
    hyper_period = 0
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
    return hyper_period;


def rts_rm_schedule(task_set, check_feasible=False, show=True):
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
    hyper_period = 3*hyper_period
    
    #find the schedule between time 0 to hyper-period
    need_resched = False 
    deadline_misses = 0
    for time_point in range(0, hyper_period):
        #print "Time:", time_point 

        if(need_resched):
            for task_no in range(0, len(task_set)):
                if(sched_dict[task_no][T_ACTIVE_OFF] == True):
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
                    #print "1. Swithing",curr_task,"->",task_no 
                    curr_task = task_no;
                    need_resched = False;
                    break;
                elif ((sched_dict[task_no][T_ACTIVE_OFF] == False) and
                       ((time_point) // (sched_dict[task_no][T_PERIOD_OFF])== sched_dict[task_no][T_INSTANCE_OFF])):
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
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
                    rts_rm_schedule_dump(curr_task, sched_dict[curr_task]);
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
                if (check_feasible and sched_dict[curr_task][T_TIME_TO_OFF] > sched_dict[curr_task][T_DEADLINE_OFF]):
                    ret = False
                    deadline_misses += 1
                need_resched = True
                continue;


    if (not check_feasible):
        rts_rm_schedule_show(show);

    return (ret, deadline_misses)



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




