# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from .conftest import trans_gnd_prep


def _test_gnd_FIELDNAME():
    """Test FIELDNAME DESCRIPTION"""
    xml_part_to_add = """
        <datafield ind1="_A_" ind2="_B_" tag="_CCC_">
            <subfield code="_D_">_SUBFIELDATA_</subfield>
        </datafield>
     """
    trans = trans_gnd_prep(xml_part_to_add)
    trans.trans_gnd_FIELDNAME()
    assert trans.json == {
        "_FIELDNAME_": [
            "_FIELDATA_"
        ]
    }
