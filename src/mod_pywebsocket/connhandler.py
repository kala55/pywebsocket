# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""PythonConnectionHandler for mod_pywebsocket.

Apache HTTP Server and mod_python must be configured such that this
function is called to handle Web Socket connection.
"""


from mod_python import apache

import conncontext
import dispatch
import handshake


_PYOPT_HANDLER_ROOT = 'mod_pywebsocket.handler_root'
_HANDLER_ROOT = apache.main_server.get_options().get(
        _PYOPT_HANDLER_ROOT, None)
if not _HANDLER_ROOT:
    raise Exception('PythonOption %s is not defined' % _PYOPT_HANDLER_ROOT,
                    apache.APLOG_ERR)
_dispatcher = dispatch.Dispatcher(_HANDLER_ROOT)
for warning in _dispatcher.source_warnings():
    apache.log_error('mod_pywebsocket: %s' % warning, apache.APLOG_WARNING)


def connectionhandler(conn):
    """Handle connection.

    Args:
        conn: mod_python.apache.mp_conn

    This function is named connectionhandler because it is the default name for
    a PythonConnectionHandler.
    """
    try:
        conn_context = conncontext.ConnContext(conn)
        handshaker = handshake.Handshaker(conn_context, _dispatcher)
        handshaker.shake_hands()
        conn.log_error('mod_pywebsocket: resource:%r' % conn_context.resource,
                       apache.APLOG_DEBUG)
        _dispatcher.transfer_data(conn_context)
    except dispatch.DispatchError, e:
        conn.log_error('mod_pywebsocket: %s' % e, apache.APLOG_WARNING)
        return apache.DECLINED
    return apache.OK


# vi:sts=4 sw=4 et
