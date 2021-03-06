#
# Copyright 2016 Universidad de Cantabria
#
# Licensed under the EUPL, Version 1.1 only (the
# "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
#
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#

import re
import drm4g.managers
from string import Template


# The programs needed by these utilities. If they are not in a location
# accessible by PATH, specify their location here.
QCONF = 'LANG=POSIX qconf'
QHOST = 'LANG=POSIX qhost'
QSUB  = 'LANG=POSIX qsub'
QSTAT = 'LANG=POSIX qstat'
QDEL  = 'LANG=POSIX qdel'

class Resource (drm4g.managers.Resource):

    def additional_queue_properties(self, queue):
        out, err = self.Communicator.execCommand('%s -sq %s' % (QCONF, queue.Name))
        if err:
            raise drm4g.managers.ResourceException(' '.join(err.split('\n')))
        reWalltime = re.compile(r'h_rt\s*(\d+):(\d+):\d+')
        if reWalltime.search(out):
            try:
                hours, minutes   = reWalltime.search(out).groups()
                queue.MaxTime    = str(int(hours) * 60 + int(minutes))
            except:
                pass
        reCputime = re.compile(r'h_cpu\s*(\d+):(\d+):\d+')
        if reCputime.search(out):
            try:
                hours, minutes   = reCputime.search(out).groups()
                queue.MaxCpuTime = str(int(hours) * 60 + int(minutes))
            except:
                pass
        return queue

class Job (drm4g.managers.Job):

    #sge job status <--> GridWay job status
    states_sge = {
        'd'  : 'FAILED',   #An error occurred with the job
        'Eqw': 'FAILED',   #An error occurred with the job
        'Ew' : 'FAILED',   #An error occurred with the job
        'h'  : 'PENDING',  #Job is hold
        'r'  : 'ACTIVE',   #Job is running
        'R'  : 'FAILED',   #Job is restarted
        'Rr' : 'FAILED',   #Job is restarted
        's'  : 'SUSPENDED',#Job is suspended
        'S'  : 'SUSPENDED',#Job is suspended
        't'  : 'PENDING',  #Job is transfering
        'T'  : 'PENDING',  #Job is Threshold
        'w'  : 'PENDING',  #Job is waiting
        'qw' : 'PENDING',  #Job is waiting
        }

    def jobSubmit(self, pathScript):
        out, err = self.Communicator.execCommand('%s %s' % (QSUB, pathScript))
        if err:
            raise drm4g.managers.JobException(' '.join(err.split('\n')))
        re_job  = re.compile(r'^Your job (\d*) .*').search(out)
        return re_job.group(1)

    def jobStatus(self):
        out, err = self.Communicator.execCommand('%s | grep %s' % (QSTAT, self.JobId))
        if not out:
            return 'DONE'
        else:
            state = out.split()[4]
            return self.states_sge.setdefault(state, 'UNKNOWN')

    def jobCancel(self):
        out, err = self.Communicator.execCommand('%s %s' % (QDEL, self.JobId))
        if err:
            raise drm4g.managers.JobException(' '.join(err.split('\n')))

    def jobTemplate(self, parameters):
        args  = '#!/bin/bash\n'
        args += '#$ -N JID_%s\n' % (parameters['environment']['GW_JOB_ID'])
        if 'project' in parameters :
            args += '#$ -P $project\n'
        if parameters['queue'] != 'default':
            args += '#$ -q $queue\n'
        args += '#$ -o $stdout\n'
        args += '#$ -e $stderr\n'
        if 'maxWallTime' in parameters :
            args += '#$ -l h_rt=$maxWallTime\n'
        if 'maxCpuTime' in parameters :
            args += '#$ -l cput=$maxCpuTime\n'
        if 'maxMemory' in parameters :
            args += '#$ -l mem_free=$maxMemoryM\n'
        if int(parameters['count']) > 1:
            args += '#$ -pe $parallel_env $count\n'
        args += '#$ -v %s\n' % (','.join(['%s=%s' %(k, v) for k, v in list(parameters['environment'].items())]))
        args += '\n'
        args += '$executable\n'
        return Template(args).safe_substitute(parameters)
