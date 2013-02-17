"""
Author : Seshadri Sridharan

A script that calculates the Bandwidth matrix for all EC2 instances using 'netconf'
Input : Instances txt file with each line in the format "<ami-id> <public-dns>"

"""

import subprocess
import sys
 

class EC2Instance:
  """ 
	lets you ssh to an EC2 instance using subprocess, execute a command, return result.
	"""

	def __init__(self, uname, host, pemfile=None):
		"""uname, host and key file(optional)"""

		self.UNAME = uname
		self.HOST = host
		self.KEY = pemfile

	def execute(self, command):
		"""executes shell command and returns result as a string"""

		ssh = None
		if self.KEY:
			ssh = subprocess.Popen(["ssh",  "-i "+ self.KEY, self.UNAME+"@"+self.HOST, command],
	                       shell=False,
	                       stdout=subprocess.PIPE,
	                       stderr=subprocess.PIPE)
		else:
			ssh = subprocess.Popen(["ssh", self.UNAME+"@"+self.HOST, command],
	                       shell=False,
	                       stdout=subprocess.PIPE,
	                       stderr=subprocess.PIPE)

		result = ssh.stdout.readlines()
		if result == []:
		    error = ssh.stderr.readlines()
		    print >> sys.stderr, "ERROR: %s" % error
		return ''.join(result)

	def executeMulti(self, commands):
		""" executes multiple commands. 
		takes as input a list of commands to execute
		returns the nested-list of the result string """

		results=[]
		ssh = None

		for command in commands:
			result = self.execute(command)
			results.append(result)

		return results

	
	def processorType(self):
		"""
		returns a list containing the instance's processor type and the cpuinfo file content
		"""
		cpuinfo = self.execute("cat /proc/cpuinfo")
		lines = cpuinfo.split('\n')
		for l in lines:
			if l[:10]=="model name":
				return [l.split(':')[1].strip(), cpuinfo]
		return [None,cpuinfo]



def get_bw(netconfRes):
	"""
	Extracts n/w bandwidth from netconf result
	"""
	bw = netconfRes.strip().split('    ')[-1]
	return bw




if __name__ == "__main__":
	

	print "# OBTAINING ALL INSTANCES FORM instances txt file\n"
	IPs=[]
	for l in open(sys.argv[1]).readlines():
		l=l.strip()
		if l:
			IPs.append(l.split(' ')[-1].strip())
	instances = [EC2Instance("ubuntu",ip) for ip in IPs]
	print "\n".join(IPs)
	
	# print "# STARTING NETSERVER ON ALL INSTANCES\n"
	# for instance in instances:
	# 	print instance.execute("sudo netserver")	#start the netserver in all 

	
	#run netconf test on all A-B pair-combinations of instances
	print "# RUNNING NETCONF SERVER ON ALL INSTANCES\n"
	combinations ={}	#holds result for all A-B combinations
	for a in range(len(instances)):
		for b in range(len(instances)):
			combination = tuple(sorted([a,b]))
			if b!=a and combination not in combinations:
				print "=> RUNNING COMBINATION ",a,b, IPs[a], IPs[b]
				res = instances[a].execute("netperf -H "+IPs[b])	#A as client, B as server
				bw = get_bw(res)
				combinations[combination] = bw
				print bw, res

	print "# COMPLETED RUNNING ON ", len(combinations), " COMBINATIONS\n"


	print "# CONSTRUCTING BANDWIDTH MATRIX\n"
	bwmat=[["" for x in range(len(instances))] for y in range(len(instances))]
	for i in range(len(instances)):
		for j in range(len(instances)):
			if j==i:
				bwmat[i][i]="0"
			elif j>i:
				combination = tuple(sorted([i,j]))
				bwmat[i][j]=combinations[combination]
			else:
				bwmat[i][j]=""

	print "#BANDWIDTH MATRIX:\n"
	for i in range(len(instances)):
		print ", ".join(bwmat[i])



