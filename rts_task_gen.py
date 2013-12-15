##
# Author: Aviraj Saha (asaha@hawk.iit.edu)
# The file contains the implementation of the task set generation for 
# verifying the RM and RM-PP or any other scheduling algorithm. 
# The total utilization and number of task in the task set is taken 
# as imput.
#
 
import random  as rand
import rts_rm  as rm
import rts_edf as edf

def rts_gen_task_set(n, U):
    """
    Use the unifast algo to generate the task set given the total 
    number of tasks and total utilization 
    """
    task_set = [] # The task set will be populated by the function
    time_period_min = 2
    time_period_max = 15

    sumU = U; # the sum of n uniform random variables
    for i in range(1,n): # i=n-1, n-2,... 1
        nextSumU = sumU*(float(rand.random()**(float(1)/(n-i)))); # the sum of n-i uniform random variables
        #print (float(1)/(n-i))
        time_period = rand.randrange(time_period_min, time_period_max)
        task_util   = (sumU - nextSumU)
        task_set.append((task_util, (task_util*time_period)/100, time_period));
        sumU = nextSumU;
    time_period = rand.randrange(time_period_min, time_period_max)
    task_util   = (sumU)
    task_set.append((task_util, (task_util*time_period)/100, time_period));
    return task_set


def rts_rm_stat():
    #task_set = [(0,3,6), (0,2,8), (0,3,12)]
    for task_util in range(70, 101, 1):
        rm_feasible_tasks = 0
        rm_pp_feasible_tasks = 0
        rm_pp_only_feasible_tasks = 0
        rm_pp_total_promotions = 0
        total_tasks    = 0
        for i in range(0,100):
            task_no = rand.randrange(5,21)
            task_set = rts_gen_task_set(task_no, task_util)
            if(rm.rts_rm_time_analysis(task_set)):
                rm_feasible_tasks += 1
                rm_pp_feasible_tasks += 1
            else: 
                if(rm.rts_rm_pp_schedule(task_set, check_feasible=True, show=False)[0]):
                    rm_pp_total_promotions +=rm.rts_rm_pp_schedule(task_set, show=False)[1]
                    rm_pp_feasible_tasks += 1
                    rm_pp_only_feasible_tasks += 1
            total_tasks += 1
        print "% =",task_util,",","RM SR =",(float(rm_feasible_tasks)/total_tasks)*100,"RM-PP SR =", (float(rm_pp_feasible_tasks)/total_tasks)*100, "RM-PP Superiority=", (float(rm_pp_only_feasible_tasks)/total_tasks)*100,"RM-PP Promotions=",float(rm_pp_total_promotions)/total_tasks

def show_menu():
    print "\t\tRTS Simulator Menu (Choose from options below)"
    print "\t\tTasks to be simulated (1)"
    print "\t\tSpecific task set (2)"
    print "\t\tGenerate Stats for RM and RM-PP (3)"
    print "\t\tGenerate comparision between EDF, Enhanced-EDF and RM (6)"
    print "\t\tGenerate comparision between EDF and RM with 50% mandatory task time (7)"
    print "\t\tShow Help (4)"
    print "\t\tExit (5)"
    

if __name__ == "__main__":
    #task_no = 10
    #task_util = 100
    #task_set = rts_gen_task_set(task_no, task_util)
    #rts_rm_stat();
    #task_set = [(0,3,6), (0,2,8), (0,3,12)]
    show_menu()
    
    while 1: 
            try:
                #x = int(raw_input())
	        op = int(input())
            except:
                continue
            
	    if(type(op) == int):
		if (op == 1):
		    print "Enter number of tasks:"
		    task_no = input()
                    task_util = rand.randrange(70,101)
		    task_set = rts_gen_task_set(task_no, task_util)
		    if (rm.rts_rm_time_analysis(task_set)):
			print "RM Schedule"
                        print "Utilization:", task_util, ",", "No of Tasks:", task_no
                        print "Task Set:", task_set
                        print task_set
			rm.rts_rm_schedule(task_set)
		    elif(rm.rts_rm_pp_schedule(task_set, check_feasible=True)[0]): 
			print "RM-PP Schedule"
                        print "Utilization:", task_util, ",", "No of Tasks:", task_no
                        print "Task Set:", task_set
			rm.rts_rm_pp_schedule(task_set)
                    else:
			print "Task set is not schedulable by RM or RM-PP"
		elif (op == 2):
		    print "Enter task set"
		    task_set = input()
                    for task_no in range(0, len(task_set)):
                        task_set[task_no] = list(task_set[task_no])
                        task_set[task_no].insert(0, 0)
                    print task_set
		    if (rm.rts_rm_time_analysis(task_set)):
			print "RM Schedule"
			rm.rts_rm_schedule(task_set)
		    else: 
			print "RM-PP Schedule"
			rm.rts_rm_pp_schedule(task_set)
		elif (op == 3):
		    rts_rm_stat()
		elif (op == 4):
		    show_menu()
		elif (op == 5):
		    break
		elif (op == 6):
		    print "Enter number of tasks:"
		    task_no = input()
                    task_util = rand.randrange(100, 101)
                    task_util = 999 
                    rounds = 0
                    while rounds < 30:
		        task_set = rts_gen_task_set(task_no, task_util)
		        #print "EDF Schedule"
                        #task_set = list(task_set)
                        #for task_no in range(0, len(task_set)):
                        #    task_set[task_no] = list(task_set[task_no]) 
                        #    task_set[task_no][1] = task_set[task_no][2]
                        print "======================================"
                        ret, misses   = edf.rts_edf_schedule(task_set, check_feasible=True)
                        ret1, misses1 = rm.rts_rm_schedule(task_set, check_feasible=True)
                        ret2, misses2 = edf.rts_edf_schedule(task_set, check_feasible=True, enhanced_edf=True)
                        print ("%d:  %s (%s, %s) %s (%s, %s) %s (%s, %s)") %(rounds, "EDF:", ret, misses, "Enhanced EDF:", ret2, misses2, "RM:", ret1, misses1)
                        #task_set = list(task_set)
                        #for task_no in range(0, len(task_set)):
                        #    task_set[task_no] = list(task_set[task_no]) 
                        #    task_set[task_no][1] = 0.5 * task_set[task_no][2]
                        #ret, misses   = edf.rts_edf_schedule(task_set, check_feasible=True)
                        #ret1, misses1 = rm.rts_rm_schedule(task_set, check_feasible=True)
                        #print ("%d:  %s (%s, %s) %s (%s, %s)") %(rounds, "EDF:",ret, misses, "RM:", ret1, misses1)
                        print "======================================"
                        rounds += 1
		elif (op == 7):
		    print "Enter number of tasks:"
		    task_no = input()
                    task_util = rand.randrange(100, 101)
                    task_util = 999 
                    rounds = 0
                    while rounds < 30:
		        task_set = rts_gen_task_set(task_no, task_util)
                        task_set = list(task_set)
                        for task_no in range(0, len(task_set)):
                            task_set[task_no] = list(task_set[task_no]) 
                            task_set[task_no][1] = 0.5 * task_set[task_no][2]
                        ret, misses   = edf.rts_edf_schedule(task_set, check_feasible=True)
                        ret1, misses1 = rm.rts_rm_schedule(task_set, check_feasible=True)
                        print ("%d:  %s (%s, %s) %s (%s, %s)") %(rounds, "EDF:",ret, misses, "RM:", ret1, misses1)
                        print "======================================"
                        rounds += 1
		else:
		    show_menu()
            else:
                continue



