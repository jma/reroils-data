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

"""Organisation with Members module tests."""

from __future__ import absolute_import, print_function

from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_records.models import RecordMetadata

from reroils_data.locations.api import Location
from reroils_data.members_locations.api import MemberWithLocations
from reroils_data.members_locations.models import MembersLocationsMetadata


def test_members_locations_create(
            app, db, minimal_member_record, minimal_location_record
        ):
    """Test organisation with members creation."""

    with app.app_context():
        memb = MemberWithLocations.create(minimal_member_record)
        loc = Record.create(minimal_location_record)
        assert memb.locations == []

        memb.add_location(loc)
        db.session.commit()
        assert memb.locations[0] == loc

        dump = memb.dumps()
        assert dump['locations'][0] == loc.dumps()


def test_delete_location(
            app, db, minimal_member_record, minimal_location_record
        ):
    """Test MembersLocations delete."""
    with app.app_context():
        del minimal_member_record['pid']
        memb = MemberWithLocations.create(
            minimal_member_record,
            pid=True
        )
        del minimal_location_record['pid']
        location = Location.create(minimal_location_record, pid=True)
        memb.add_location(location)
        db.session.commit()
        pid = PersistentIdentifier.get_by_object('loc', 'rec', location.id)
        assert pid.is_registered()
        memb.remove_location(location)
        db.session.commit()
        assert pid.is_deleted()
        assert memb.locations == []

        del minimal_location_record['pid']
        location1 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location1)
        del minimal_location_record['pid']
        location2 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location2)
        del minimal_location_record['pid']
        location3 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location3)
        db.session.commit()
        memb.remove_location(location2)
        db.session.commit()
        assert len(memb.locations) == 2
        assert memb.locations[0]['pid'] == '2'
        assert memb.locations[1]['pid'] == '4'


def test_delete_member(
            app, db, minimal_member_record, minimal_location_record
        ):
    """Test Member delete."""
    with app.app_context():
        del minimal_member_record['pid']
        memb = MemberWithLocations.create(
            minimal_member_record,
            pid=True
        )
        del minimal_location_record['pid']
        location1 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location1)
        pid1 = PersistentIdentifier.get_by_object('loc', 'rec', location1.id)
        del minimal_location_record['pid']
        location2 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location2)
        pid2 = PersistentIdentifier.get_by_object('loc', 'rec', location2.id)
        del minimal_location_record['pid']
        location3 = Location.create(minimal_location_record, pid=True)
        memb.add_location(location3)
        pid3 = PersistentIdentifier.get_by_object('loc', 'rec', location3.id)
        db.session.commit()
        assert MembersLocationsMetadata.query.count() == 3
        assert RecordMetadata.query.count() == 4
        assert pid1.is_registered()
        assert pid2.is_registered()
        assert pid3.is_registered()
        memb.delete(force=True)
        db.session.commit()
        assert MembersLocationsMetadata.query.count() == 0
        assert RecordMetadata.query.count() == 0
        assert pid1.is_deleted()
        assert pid2.is_deleted()
        assert pid3.is_deleted()
