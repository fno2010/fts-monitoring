# Copyright notice:
#
# Copyright (C) OpenALTO 2023
#
# Copyright (C) CERN 2013-2015
#
# Copyright (C) Members of the EMI Collaboration, 2010-2013.
#   See www.eu-emi.eu for details on the copyright holders
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db import connection

from ftsmon.models import File, NetlinkStat
from libs.util import paged
from libs.jsonify import jsonify, jsonify_paged


class NetlinkDecorator(object):
    """
    Wrapper of Netlink
    """

    def __init__(self):
        self.cursor = connection.cursor()

    def get_netlink_list(self, interval=5):
        self.cursor.execute(
            "SELECT n.netlink, n.vo_name, n.activity, COUNT(*) AS transfers, SUM(n.tput) AS total_tput "
            "FROM "
            "(SELECT nt.netlink AS netlink, f.vo_name AS vo_name, f.activity AS activity, "
            "  IF(f.throughput, f.throughput, f.transferred / (UTC_TIMESTAMP() - f.start_time)) AS tput "
            " FROM t_file f, t_netlink_trace nt "
            " WHERE f.source_se = nt.source_se AND f.dest_se = nt.dest_se "
            "  AND (f.file_state = 'ACTIVE' "
            "   OR (f.file_state IN ('FINISHED', 'ARCHIVING') "
            "    AND f.finish_time >= (UTC_TIMESTAMP() - INTERVAL {} SECOND)))) n "
            "GROUP BY n.netlink, n.vo_name, n.activity".format(interval), [])
        result = self.cursor.fetchall()
        stat = {}
        for r in result:
            netlink = r[0]
            vo_name = r[1]
            activity = r[2]
            transfers = r[3]
            total_tput = r[4]
            if netlink not in stat:
                stat[netlink] = {}
            stat[netlink][(vo_name, activity)] = {
                'transfers': transfers,
                'total_throughput': total_tput
            }
        return stat

    def get_netlink_transfer(self, netlink_id, interval=5):
        self.cursor.execute(
            "SELECT n.vo_name, n.activity, COUNT(*) AS transfers, SUM(n.tput) AS total_tput "
            "FROM "
            "(SELECT f.vo_name AS vo_name, f.activity AS activity, "
            "  IF(f.throughput, f.throughput, f.transferred / (UTC_TIMESTAMP() - f.start_time)) AS tput "
            " FROM t_file f, t_netlink_trace nt "
            " WHERE f.source_se = nt.source_se AND f.dest_se = nt.dest_se AND nt.netlink = %s "
            "  AND (f.file_state = 'ACTIVE' "
            "   OR (f.file_state IN ('FINISHED', 'ARCHIVING') "
            "    AND f.finish_time >= (UTC_TIMESTAMP() - INTERVAL {} SECOND)))) n "
            "GROUP BY n.vo_name, n.activity".format(interval), [netlink_id])
        result = self.cursor.fetchall()
        transfer_stat = {}
        tput_stat = {}
        total_active_transfers = 0
        total_tput = 0
        for r in result:
            vo_name = r[0]
            activity = r[1]
            transfers = r[2]
            tput = r[3]
            if vo_name not in transfer_stat:
                transfer_stat[vo_name] = {}
            transfer_stat[vo_name][activity] = transfers
            total_active_transfers += transfers
            if vo_name not in tput_stat:
                tput_stat[vo_name] = {}
            tput_stat[vo_name][activity] = tput
            total_tput += tput
        return {
            'transfers': transfer_stat,
            'throughput': tput_stat,
            'total_active_transfers': total_active_transfers,
            'total_throughput': total_tput
        }


def _get_transfer_per_netlink(limit):
    netlinks = NetlinkDecorator()
    stat = netlinks.get_netlink_list()
    netlink_list = []
    for n in stat:
        item = {}
        item['netlink_id'] = n
        item['statistics'] = {}
        total_active_transfers = 0
        total_throughput = 0
        for vo, act in stat[n]:
            transfers = stat[n][(vo, act)]['transfers']
            tput = stat[n][(vo, act)]['total_throughput']
            if vo not in item['statistics']:
                item['statistics'][vo] = {}
            item['statistics'][vo][act] = {
                'transfers': transfers,
                'throughput': tput
            }
            total_active_transfers += transfers
            total_throughput += tput
        item['total_active_transfers'] = total_active_transfers
        item['total_throughput'] = total_throughput
        netlink_list.append(item)
    sorted_netlink_list = sorted(netlink_list, key=(lambda d: d['total_throughput']), reverse=True)
    if limit:
        sorted_netlink_list = sorted_netlink_list[:limit]
    return sorted_netlink_list


@jsonify_paged
def get_netlinks(http_request):
    limit = http_request.GET.get('limit', None)
    # netlink = Netlink.objects.values('source_se', 'dest_se', 'netlink')
    return _get_transfer_per_netlink(limit)


@jsonify
def get_netlink_details(http_request):
    netlink_id = http_request.GET.get('netlink_id', None)
    if not netlink_id:
        raise Http404

    netlink = NetlinkStat.objects.get(netlink_id=netlink_id)
    pairs_count = 0
    active_transfers_count = 0
    transfers = None
    for trace in netlink.traces.all():
        pairs_count += 1
        if not transfers:
            transfers = File.objects.filter(source_se__exact=trace.source_se, dest_se__exact=trace.dest_se)
        else:
            transfers.union(File.objects.filter(source_se__exact=trace.source_se, dest_se__exact=trace.dest_se))

    transfers = transfers.values(
        'file_id', 'file_state', 'job_id',
        'source_se', 'dest_se', 'start_time', 'finish_time',
        'activity', 'user_filesize', 'filesize'
    )


    netlink_query = NetlinkDecorator()
    stat = netlink_query.get_netlink_transfer(netlink_id)
    stat['active_pairs'] = pairs_count

    return {
        'netlink_id': netlink_id,
        'head_ip': netlink.head_ip,
        'tail_ip': netlink.tail_ip,
        'head_asn': netlink.head_asn,
        'tail_asn': netlink.tail_asn,
        'head_rdns': netlink.head_rdns,
        'tail_rdns': netlink.tail_rdns,
        'transfers': paged(transfers, http_request),
        'statistics': stat
    }
