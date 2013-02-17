"""
Author : Seshadri Sridharan

Feb 17 >> Lets you ssh to an EC2 instance using subprocess, execute a command, return result. 
		- no interactivity yet
		- inefficient. subprocess, ssh connection established for every command execution

"""
import subprocess
import sys
 

class EC2Execute:
	""" 
	lets you ssh to an EC2 instance using subprocess, execute a command, return result.
	"""

	def __init__(self, uname, host, pemfile=None):
		"""uname, host and key file(optional)"""

		self.UNAME = uname
		self.HOST = host
		self.KEY = pemfile

	def execute(self, command):
		"""executes shell command and returns result, a list of sentences"""

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
		return result

	def executeMulti(self, commands):
		""" executes multiple commands. 
		takes as input a list of commands to execute
		returns the nested-list of the results """

		results=[]
		ssh = None

		for command in commands:
			result = self.execute(command)
			results.append(result)

		return results



if __name__ == "__main__":
	
	m1 = EC2Execute("ubuntu","ec2-184-73-66-207.compute-1.amazonaws.com")
	print m1.execute("ls")
	print m1.executeMulti(["ls","pwd"])

