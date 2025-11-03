<%!
import re
from alembic import util
%>
<%def name="render_python_string(value)">
<%
value = value.replace("'", "\\'")
%>
${value}
</%def>
"""
Revision ID: ${up_revision}
Revises: ${down_revision | render_python_string}
Create Date: ${create_date}
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}


def upgrade() -> None:
${upgrades if upgrades else "    pass"}


def downgrade() -> None:
${downgrades if downgrades else "    pass"}
