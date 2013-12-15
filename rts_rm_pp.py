##
# Author Aviraj Saha (asaha3@hawk.iit.edu)
# Given a schedule the module finds out whether a feasible schedule 
# can be obtained using the RM scduling algorithm.
# Since the utilization is above 69% the method used is the 
# time analysis method.
##


def rts_rm_time_analysis(task_set):
    #sort the task set to get the lowest priority task
    sorted(task_set, key=itemgetter(2))
 
    print task_set


