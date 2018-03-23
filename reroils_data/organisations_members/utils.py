# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 RERO.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, RERO does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Utilities functions for reroils-data."""


import uuid

from flask import url_for
from invenio_db import db
from invenio_pidstore.resolver import Resolver
from reroils_record_editor.utils import clean_dict_keys, resolve

from reroils_data.organisations_members.api import OrganisationWithMembers


def delete_member(record_type, pid, record_indexer, parent_pid):
    """Remove an member from an organisation.

    The member is marked as deleted in the db, his pid as well.
    The organisation is reindexed.
    """
    org_resolver = Resolver(
        pid_type='org',
        object_type='rec',
        getter=OrganisationWithMembers.get_record
    )
    pid_org, organisation = org_resolver.resolve(str(parent_pid))
    pid, member = resolve(record_type, pid)
    organisation.remove_member(member)
    db.session.commit()
    record_indexer().index(organisation)
    record_indexer().client.indices.flush()
    try:
        _next = url_for('invenio_records_ui.org', pid_value=parent_pid)
    except Exception:
        _next = None
    return _next, pid


def save_member(
            data, record_type, fetcher, minter,
            record_indexer, record_class, parent_pid
        ):
    """Save a record into the db and index it.

    If the member does not exists, it well be created
    and attached to the parent organisation.
    """
    def get_pid(record_type, record, fetcher):
        try:
            pid_value = fetcher(None, record).pid_value
        except KeyError:
            return None
        return pid_value

    # load and clean dirty data provided by angular-schema-form
    record = clean_dict_keys(data)
    pid_value = get_pid(record_type, record, fetcher)
    org_resolver = Resolver(
        pid_type='org',
        object_type='rec',
        getter=OrganisationWithMembers.get_record
    )
    pid_org, organisation = org_resolver.resolve(str(parent_pid))
    # update an existing record
    if pid_value:
        pid, rec = resolve(record_type, pid_value)
        rec.update(record)
        rec.commit()
    # create a new record
    else:
        # generate pid
        uid = uuid.uuid4()
        pid = minter(uid, record)
        # create a new record
        rec = record_class.create(record, id_=uid)
        organisation.add_member(rec)
    db.session.commit()
    record_indexer().index(organisation)
    record_indexer().client.indices.flush()
    try:
        _next = url_for('invenio_records_ui.org', pid_value=parent_pid)
    except Exception:
        _next = None
    return _next, pid
