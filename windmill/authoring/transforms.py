#   Copyright (c) 2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import windmill
import simplejson
import tempfile

def create_saves_path():
    directory = tempfile.mkdtemp(suffix='.windmill-saves')
    # Mount the fileserver application for tests
    from wsgi_fileserver import WSGIFileServerApplication
    application = WSGIFileServerApplication(root_path=os.path.abspath(directory), mount_point='/windmill-saves/')
    from windmill.server import wsgi
    wsgi.add_namespace('windmill-saves', application)
    windmill.settings['SAVES_PATH'] = directory
    windmill.teardown_directories.append(directory)

def test_object_transform(test):
    """Transform test object in to controller call in python."""
    params = ', '.join([key+'='+repr(value) for key, value in test['params'].items()])    
    return 'client.%s(%s)' % (test['method'], params)
    
def build_test_file(tests, suite_name=None):
    """Build the test file for python"""
    ts = '# Generated by the windmill services transformer\n'
    ts += 'from windmill.authoring import WindmillTestClient\n\n'
    if suite_name:
        ts += 'def test_'+suite_name.replace('test_', '', 1)+'():\n'
    else:
        ts += 'def test():\n'
    ts += '    client = WindmillTestClient(__name__)\n\n    '
    ts += '\n    '.join([test_object_transform(test) for test in tests])
    return ts
    
def create_python_test_file(suite_name, tests, location=None):
    """Transform and create and build the python test file"""
    if location is None: 
        location = os.path.join(windmill.settings['SAVES_PATH'], suite_name+'.py')
    f = open(location, 'w')
    f.write(build_test_file(tests, suite_name))
    f.flush()
    f.close()
    return '%s/windmill-saves/%s' % (windmill.settings['TEST_URL'], suite_name+'.py')
    
def create_json_test_file(suite_name, tests, location=None):
    """Transform and create a json test file."""
    if location is None: 
        location = os.path.join(windmill.settings['SAVES_PATH'], suite_name+'.json')
    f = open(location, 'w')
    for test in tests:
        # Strip keys that aren't part of the api
        test.pop('suite_name', None) ; test.pop('version', None)
        f.write(simplejson.dumps(test))
        f.write('\n')
    f.flush()
    f.close()
    return '%s/windmill-saves/%s' % (windmill.settings['TEST_URL'], suite_name+'.json')
    
registry = {'python':create_python_test_file, 'json':create_json_test_file}

