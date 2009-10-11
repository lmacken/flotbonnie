#!/usr/bin/python -tt
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2008-2009  Luke Macken <lewk@csh.rit.edu>

""" This tool generates flot graphs from bonnie++ output """

import sys

name, size, outchr, ourchrcp, outblock, outblockcp, outre, outrecp, inchr, \
inchrcp, inblock, inblockcp, rndseek, rndseekcp, files, seqcreate, seqcreatecp, \
seqread, seqreadcp, seqdel, seqdelcp, rndcreate, rndcreatecp, rndread, \
rndreadcp, rnddel, rnddelcp = range(27)

graphs = [('Sequential Output (K/sec)', (outchr, outblock, outre)),
          ('Sequential Input (K/sec)', (inchr, inblock)),
          ('Random Seeks (per second)', (rndseek,)),
          ('Sequential Create (files/sec)', (seqcreate, seqread, seqdel)),
          ('Random Create (files/second)', (rndcreate, rndread, rnddel))]

ticks = {
    outchr: 'Character', outblock: 'Block', outre: 'Rewrite',
    inchr: 'Character', inblock: 'Block', seqcreate: 'Create',
    seqread: 'Read', seqdel: 'Delete', rndseek: 'Seeks',
    rndcreate: 'Create', rndread: 'Read', rnddel: 'Delete',
}

HEIGHT = 250
WIDTH = 500


def flot_bonnie(benchmarks):
    html = """<html><head>
        <script language="javascript" type="text/javascript" src="jquery.js"></script>
        <script language="javascript" type="text/javascript" src="jquery.flot.js"></script>
        </head><body><center>
    """

    machines = parse_benchmarks(benchmarks)

    for name, fields in graphs:

        # Add an empty list to the end of each benchmark data to track the
        # list of data plots for flot
        for machine in machines:
            machine.append([])
        x = 1
        for field in fields:
            for machine in machines:
                if machine[field] == '+++++': # inconclusive test (too fast?)
                    machine[field] = '0'
                    print "%s inconclusive" % ticks[field]
                    continue
                machine[-1].append([x, float(machine[field])])
                x += 1
            x += 1

        html += """
            <center><b>%s</b></center>
            <div id="%s" style="width:%dpx;height:%dpx"/>
            <script>
              $.plot($("#%s"), [
        """ % (name, abs(name.__hash__()), WIDTH, HEIGHT, abs(name.__hash__()))

        for machine in machines:
            html += """
                { "data": %s, "label": "%s", "bars": { show: true } },
            """ % (machine[-1], machine[0])
        html += '], {"yaxis": {"min": 0}, '

        # Create the x-axis ticks
        html += '"xaxis": {"ticks": ['
        offset = 0
        if len(fields) == 1:
            offset = x / 2 * -1 + 2
        for field in fields:
            html += '[%s, "%s"],' % (x / len(fields) - 2 + offset, ticks[field])
            offset += x / len(fields)
        html = html[:-1]
        html += "]} });</script>"

    html += "</center></body></html>"
    print html


def parse_benchmarks(benchmarks):
    """ Parse bonnie++ output, and return a list of benchmark data """
    machines = []
    for dataset in benchmarks:
        f = open(dataset, 'r')
        for line in f.readlines():
            data = line.strip().split(',')
            if len(data) == 27:
                machines.append(data)
                break # only pay attention to the first benchmark in the file
        f.close()
    if len(machines) is 0:
        raise Exception("No bonnie++ benchmark data found!")
    return machines


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "%s <bonnie++ log(s)> ..." % sys.argv[0]
        sys.exit(1)
    flot_bonnie(sys.argv[1:])
