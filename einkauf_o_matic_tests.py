#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
c-base einkauf-o-matic

@author: Ricardo (XenGi) Band <me@xengi.de>

    This file is part of einkauf-o-matic.

    einkauf-o-matic is licensed under Attribution-NonCommercial-ShareAlike 3.0
    Unported (CC BY-NC-SA 3.0).

    <http://creativecommons.org/licenses/by-nc-sa/3.0/>
"""

import os
import einkauf_o_matic
import unittest
import tempfile


class EinkaufOMaticTestCase(unittest.TestCase):
    """
    unittests for the einkauf-o-matic
    """

    def setUp(self):
        """
        just setting things up
        """
        self.db_fd, einkauf_o_matic.app.config['DATABASE'] = tempfile.mkstemp()
        einkauf_o_matic.app.config['TESTING'] = True
        self.app = einkauf_o_matic.app.test_client()
        einkauf_o_matic.init_db()

    def tearDown(self):
        """
        delete the temporary db after all tests are done
        """
        os.close(self.db_fd)
        os.unlink(einkauf_o_matic.app.config['DATABASE'])

    # helper functions

    def login(self, username, password):
        """
        logs the given user in
        """
        return self.app.post('/login', data=dict(
            username=username,
            password=password
            ), follow_redirects=True)

    def logout(self):
        """
        logs the user off
        """
        return self.app.get('/logout', follow_redirects=True)

    def register(self, member, password, password2=None):
        """
        Helper function to register a user
        """
        if password2 is None:
            password2 = password
        return self.app.post('/register', data={
            'member':       member,
            'password':     password,
            'password2':    password2
        }, follow_redirects=True)

    # testing functions

    def test_root_page(self):
        """
        test if the app shows "You must be logged in to see something useful
        here" if we access root (/)
        """
        retval = self.app.get('/')
        assert 'You must be logged in to see something useful' in retval.data

    def test_register(self):
        """
        Make sure registering works
        """
        retval = self.register('horst', 'passw0rd')
        assert 'You were successfully registered and can login' in retval.data
        retval = self.register('horst', 'passw0rd')
        assert 'The username is already taken' in retval.data
        retval = self.register('', 'passw0rd')
        assert 'You have to enter a username' in retval.data
        retval = self.register('harry', '')
        assert 'You have to enter a password' in retval.data
        retval = self.register('harry', 'passw0rd', 'p@ssword')
        assert 'The two passwords do not match' in retval.data

    def test_login_logout(self):
        """
        testing login and logout functionality
        """
        retval = self.login('root', 'toor')
        assert 'You were logged in' in retval.data
        retval = self.logout()
        assert 'You were logged out' in retval.data
        retval = self.login('wronguser', 'toor')
        assert 'Invalid username' in retval.data
        retval = self.login('root', 'wrongpass')
        assert 'Invalid password' in retval.data

    def test_add_store(self):
        self.login('root', 'toor')
        retval = self.app.post('/addstore',
                               data=dict(name='adafruit INDUSTRIES',
                                         urls='http://www.adafruit.com/,http://adafruit.com/',
                                         minorder='250'),
                                follow_redirects=True)
        assert 'No stores here so far' not in retval.data
        assert '<a href="http://www.adafruit.com/">adafruit' in retval.data

    def test_add_queue(self):
        """
        test adding new queues
        """
        self.login('root', 'toor')
        retval = self.app.post('/add', data=dict(title='raspberrypi stuff',
                                                 deadline='2012-01-30',
                                                 store='0'),
                                follow_redirects=True)
        assert 'No stores here so far' not in retval.data
        assert 'raspberrypi stuff' in retval.data and \
               '2012-01-30' in retval.data


if __name__ == '__main__':
    unittest.main()