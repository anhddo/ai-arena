# ©2020 Johns Hopkins University Applied Physics Laboratory LLC.
import sys
import time
from mpi4py import MPI
from inspect import currentframe, getframeinfo
import inspect

def mpi_lag(wait=2.0):
	r = float(MPI.COMM_WORLD.Get_rank())
	sz = float(MPI.COMM_WORLD.Get_size())
	delay = (r/sz)*wait
	time.sleep(delay)

def mpi_print(*args):
    frameinfo = inspect.stack()[1]
    print('file:', frameinfo[1], 'line:',  frameinfo[2],'==>', *args)
    sys.stdout.flush()

def count_needed_procs(match_list):
	#we need 1 process for each first-level entry in this list (environment)
	#for each second-level entry (match participant) we need another process
	#finally, we need 1 root process to orchestrate everything
	
	num_procs = 1 #root
	for m in match_list:
		num_procs += 1 #env
		for participant in m:
			num_procs += 1 #worker process

	return num_procs

def count_number_scaled_matches(match_list):
	min_procs = count_needed_procs(match_list)
	avail_procs = MPI.COMM_WORLD.Get_size()
	num_duplicates = (avail_procs-1) // (min_procs-1)
	return len(match_list)*num_duplicates


def total_steps_to_match_steps(match_list, total_steps):
	num_scaled_matches = count_number_scaled_matches(match_list)
	if num_scaled_matches <= 0:
		procs_needed = count_needed_procs(match_list)
		raise ValueError("Not enough processes have been allocated, need: "+str(procs_needed))
	return total_steps // num_scaled_matches
