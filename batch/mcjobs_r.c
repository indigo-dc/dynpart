/*

Stefano Dal Pra, INFN-CNAF, s.dalpra@gmail.com
stefano.dalpra@cnaf.infn.it

Adapted from lsf 7.06 examples, works with lsf 9.1

HOW TO COMPILE

gcc -Wall badhosts.c -o badhosts -I/usr/share/lsf/9.1/include /usr/share/lsf/9.1/linux2.6-glibc2.3-x86_64/lib/libbat.a $LSF_LIBDIR/liblsf.a /usr/lib64/libnsl.a -lm -lnsl -ldl

If it complains because of missing libnsl.a, it has to be created like this:
[root@lsf-1 lsfc]# ar rcs /lib64/libnsl.a /lib64/libnsl.so

*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>

#include <lsf/lsbatch.h>

int main(int argc, char **argv)
{

  struct submit req; 
  memset(&req, 0, sizeof(req)); /* initializes req */
  int options = RUN_JOB; /* the status of the jobs
                             whose info is returned */
  char *user="all"; /* match jobs for all users */
  struct jobInfoEnt *job; /* detailed job info */
  int more; /* number of remaining jobs
               unread */
  /* initialize LSBLIB and get the configuration
     environment */
  if (lsb_init(argv[0]) < 0) {
    lsb_perror("mcjobs: lsb_init() failed");
    exit(-1);
  }
  /* check if input is in the right format:
   * "./simbjobs COMMAND ARGUMENTS" */
  if (argc < 2) {
    fprintf(stderr, "Usage: simbjobs command\n");
    exit(-1);
  }
  /* gets the total number of pending job. Exits if failure */
  if (lsb_openjobinfo(0, NULL, user, NULL, NULL, options)<0) {
    lsb_perror("lsb_openjobinfo");
    exit(-1);
  }
  /* display all pending jobs */
  //printf("All running jobs submitted by all users:\n");
  for (;;) {
    job = lsb_readjobinfo(&more); /* get the job details */
    if (job == NULL) {
      lsb_perror("lsb_readjobinfo");
      exit(-1);
    }
    printf("%d %s %s %s \"%s\"\n",(int)job->startTime,lsb_jobid2str(job->jobId),job->user, job->exHosts[0], job->submit.resReq  );
    /* continue to display if there is remaining job */
    if (!more)
      /* if there are no remaining jobs undisplayed,
         exits */
      break;
  }
  /* when finished to display the job info, close the
     connection to the mbatchd */
  lsb_closejobinfo();
  exit(0);
}
