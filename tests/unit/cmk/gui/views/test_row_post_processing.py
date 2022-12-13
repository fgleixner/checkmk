#!/usr/bin/env python3
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.utils.structured_data import StructuredDataNode

from cmk.gui.type_defs import Rows
from cmk.gui.view import View
from cmk.gui.views.page_show_view import _post_process_rows
from cmk.gui.views.row_post_processing import _ROW_POST_PROCESSORS
from cmk.gui.views.store import multisite_builtin_views


def test_post_processor_registrations() -> None:
    names = [f.__name__ for f in _ROW_POST_PROCESSORS]
    assert names == []


def test_post_process_rows_not_failing_on_empty_rows(view: View) -> None:
    rows: Rows = []
    _post_process_rows(view, [], rows)
    assert rows == []


def test_post_process_rows_adds_inventory_data() -> None:
    inv_view = inventory_view()
    host_row = {"host_name": "ding"}
    rows: Rows = [host_row]
    _post_process_rows(inv_view, [], rows)
    assert rows == [host_row]
    assert isinstance(host_row["host_inventory"], StructuredDataNode)


def inventory_view() -> View:
    view_spec = multisite_builtin_views["inv_hosts_cpu"].copy()
    return View("inv_hosts_cpu", view_spec, view_spec.get("context", {}))
