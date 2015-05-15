import os

for i in range(4):
	i=i+1
	os.system('sudo docker create --privileged -i -t --name grade_container'+str(i)+' -v /container'+str(i)+':/tmpdir gradeserver:1.0 /bin/bash')
	os.system('sudo docker start grade_container'+str(i))
	os.system('sudo docker exec grade_container' + str(i) + ' mount -t nfs 192.168.0.133:/mnt/shared /mnt/shared')
