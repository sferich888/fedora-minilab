#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4


class FilterModule(object):

    @staticmethod
    def create_dns_names(group, hostvars):
        dns_names = []
        for host in group:
            dns_names.append({'shortname': host,
                              'ip': hostvars[host]['ip'],
                              'mac': hostvars[host]['mac']})
        return dns_names

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return { "create_dns_names": self.create_dns_names }
