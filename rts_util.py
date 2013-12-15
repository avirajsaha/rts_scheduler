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




