#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""


def thumbnail_url(record, thumbnail_field, thumbnail_params):

    url = record.get(thumbnail_field)

    # If we have thumbnail params, add them in here
    if thumbnail_params:
        q ='&' if '?' in url else '?'
        url += q + thumbnail_params

    return url