'''
 ====================================================================
 Copyright (c) 2003-2006 Barry A Scott.  All rights reserved.

 This software is licensed as described in the file LICENSE.txt,
 which you should have received as part of this distribution.

 ====================================================================
'''
import pysvn
import time
import sys
import os
import parse_datetime
import glob
import locale

class CommandError( Exception ):
    def __init__( self, reason ):
        Exception.__init__( self )
        self._reason = reason

    def reason( self ):
        return self._reason

    def __str__( self ):
        return self._reason

def main( args ):
    progname = os.path.basename( args[0] )
    pause = False
    if args[1:2] == ['--pause']:
        del args[1]
        pause = True

    # if the locale is not setup SVN can report errors handling non ascii file names
    initLocale()

    svn_cmd = SvnCommand( progname )
    rc = svn_cmd.dispatch( args[1:] )
    if pause:
        sys.stdin.readline()
    return rc

def initLocale():
    # init the locale
    if sys.platform == 'win32':
        locale.setlocale( locale.LC_ALL, '' )

    else:
        language_code, encoding = locale.getdefaultlocale()
        if language_code is None:
            language_code = 'en_GB'

        if encoding is None:
            encoding = 'UTF-8'
        if encoding.lower() == 'utf':
            encoding = 'UTF-8'

        try:
            # setlocale fails when params it does not understand are passed
            locale.setlocale( locale.LC_ALL, '%s.%s' % (language_code, encoding) )
        except locale.Error:
            # force a locale that will work
            locale.setlocale( locale.LC_ALL, 'en_GB.UTF-8' )

def fmtDateTime( t ):
    return time.strftime( '%d-%b-%Y %H:%M:%S', time.localtime( t ) )

wc_status_kind_map = {
pysvn.wc_status_kind.added: 'A',
pysvn.wc_status_kind.conflicted: 'C',
pysvn.wc_status_kind.deleted: 'D',
pysvn.wc_status_kind.external: 'X',
pysvn.wc_status_kind.ignored: 'I',
pysvn.wc_status_kind.incomplete: '!',
pysvn.wc_status_kind.missing: '!',
pysvn.wc_status_kind.merged: 'G',
pysvn.wc_status_kind.modified: 'M',
pysvn.wc_status_kind.none: ' ',
pysvn.wc_status_kind.normal: ' ',
pysvn.wc_status_kind.obstructed: '~',
pysvn.wc_status_kind.replaced: 'R',
pysvn.wc_status_kind.unversioned: '?',
}

wc_notify_action_map = {
pysvn.wc_notify_action.add: 'A',
pysvn.wc_notify_action.commit_added: 'A',
pysvn.wc_notify_action.commit_deleted: 'D',
pysvn.wc_notify_action.commit_modified: 'M',
pysvn.wc_notify_action.commit_postfix_txdelta: None,
pysvn.wc_notify_action.commit_replaced: 'R',
pysvn.wc_notify_action.copy: 'c',
pysvn.wc_notify_action.delete: 'D',
pysvn.wc_notify_action.failed_revert: 'F',
pysvn.wc_notify_action.resolved: 'R',
pysvn.wc_notify_action.restore: 'R',
pysvn.wc_notify_action.revert: 'R',
pysvn.wc_notify_action.skip: 'skip',
pysvn.wc_notify_action.status_completed: None,
pysvn.wc_notify_action.status_external: 'X',
pysvn.wc_notify_action.update_add: 'A',
pysvn.wc_notify_action.update_completed: None,
pysvn.wc_notify_action.update_delete: 'D',
pysvn.wc_notify_action.update_external: 'X',
pysvn.wc_notify_action.update_update: 'U',
pysvn.wc_notify_action.annotate_revision: 'A',
}
if hasattr( pysvn.wc_notify_action, 'locked' ):
    wc_notify_action_map[ pysvn.wc_notify_action.locked ] = 'locked'
    wc_notify_action_map[ pysvn.wc_notify_action.unlocked ] = 'unlocked'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_lock ] = 'failed_lock'
    wc_notify_action_map[ pysvn.wc_notify_action.failed_unlock ] = 'failed_unlock'


class SvnCommand:
    def __init__( self, progname ):
        self.progname = progname
        self.client = None
        self.revision_update_complete = None
        self.notify_message_list = []
        self.pysvn_testing = False
        self.debug_enabled = False

    def debug( self, msg, args=() ):
        if self.debug_enabled:
            print 'Debug:', msg % args

    def initClient( self, config_dir ):
        self.client = pysvn.Client( config_dir )
        self.client.exception_style = 1
        self.client.callback_get_login = self.callback_getLogin
        self.client.callback_get_log_message = self.callback_getLogMessage
        self.client.callback_notify = self.callback_notify
        self.client.callback_cancel = self.callback_cancel
        self.client.callback_ssl_client_cert_password_prompt = self.callback_ssl_client_cert_password_prompt
        self.client.callback_ssl_client_cert_prompt = self.callback_ssl_client_cert_prompt
        self.client.callback_ssl_server_prompt = self.callback_ssl_server_prompt
        self.client.callback_ssl_server_trust_prompt = self.callback_ssl_server_trust_prompt

    def callback_ssl_client_cert_password_prompt( self ):
        print 'callback_ssl_client_cert_password_prompt'

    def callback_ssl_client_cert_prompt( self ):
        print 'callback_ssl_client_cert_prompt'

    def callback_ssl_server_prompt( self ):
        print 'callback_ssl_server_prompt'

    def callback_ssl_server_trust_prompt( self, trust_data ):
        for key,value in trust_data.items():
            print '%s: %s' % (key, value)
        print
        answer = ''
        while answer.lower() not in ['p','t','r']:
            sys.stdout.write( '(P)ermanent accept, (T)emporary accept or (R)eject: ' )
            answer = sys.stdin.readline().strip()
        if answer.lower() == 'p':
            return True, trust_data['failures'], True
        if answer.lower() == 't':
            return True, trust_data['failures'], False
        return False, 0, False

    def callback_cancel( self ):
        return False

    def callback_notify( self, arg_dict ):
        if arg_dict['action'] == pysvn.wc_notify_action.update_completed:
            self.revision_update_complete = arg_dict['revision']
        elif arg_dict['path'] != '' and wc_notify_action_map[ arg_dict['action'] ] is not None:
            msg = '%s %s' % (wc_notify_action_map[ arg_dict['action'] ], arg_dict['path'])
            if self.pysvn_testing != '99.99.99':
                self.notify_message_list.append( msg )
            else:
                print msg

    def callback_getLogin( self, realm, username, may_save ):
        print 'May save:',may_save
        print 'Realm:',realm
        if username:
            print 'Username:',username
        else:
            sys.stdout.write( 'Username: ' )
            username = sys.stdin.readline().strip()
            if len(username) == 0:
                return 0, '', '', False

        sys.stdout.write( 'Password: ' )
        password = sys.stdin.readline().strip()

        save_password = 'x'
        while save_password.lower() not in ['y','ye','yes','n', 'no','']:
            sys.stdout.write( 'Save password? [y/n] ' )
            save_password = sys.stdin.readline().strip()
        
        return 1, username, password, save_password in ['y','ye','yes']

    def getLogMessage( self ):
        sys.stdout.write( 'Log message\n' )
        sys.stdout.write( '--- -------\n' )
        message = sys.stdin.read()
        return message

    def callback_getLogMessage( self ):
        return True, self.getLogMessage()

    def dispatch( self, argv ):
        try:
            args = SvnArguments( argv )
            cmd_name = 'cmd_%s' % args.getCommandName( 'help' )

            self.initClient( args.getOptionalValue( '--config-dir', '' ) )
            self.client.set_auth_cache( args.getBooleanOption( '--no-auth-cache', False ) )
            self.pysvn_testing = args.getOptionalValue( '--pysvn-testing', '99.99.99' )
            self.debug_enabled = args.getBooleanOption( '--debug', True )

            getattr( self, cmd_name, self.cmd_help )( args )

            self.printNotifyMessages()

        except pysvn.ClientError, e:
            self.printNotifyMessages()
            print e.args[0]
            return 1
        except CommandError, e:
            self.printNotifyMessages()
            print e.reason()
            return 1

        return 0

    def printNotifyMessages( self ):
            # different versions of SVN notify messages in different orders
            # by sorting before printing we hope to have one set of regression
            # test data for multiple versions of SVN
            self.notify_message_list.sort()
            for msg in self.notify_message_list:
                print msg
            self.notify_message_list = []

    def cmd_version( self, args ):
        print 'PYSVN Version:',pysvn.version
        print 'SVN Version:',pysvn.svn_version
        if hasattr( pysvn, 'svn_api_version' ):
            print 'SVN API Version:',pysvn.svn_api_version
        print 'pysvn._pysvn',pysvn._pysvn


    def cmd_is_url( self, args ):
        path = args.getPositionalArgs( 1 )[0]
        is_url = self.client.is_url( path )
        if is_url:
            print 'url',path
        else:
            print 'path',path

    def cmd_add( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        force = args.getBooleanOption( '--force', False )
        
        self.client.add( args.getPositionalArgs( 1 ), recurse=recurse, force=force )

    def cmd_annotate( self, args ):
        start_revision, end_revision = args.getOptionalRevisionPair( '--revision', '0', 'head' )
        positional_args = args.getPositionalArgs( 1, 1 )
        all_lines = self.client.annotate( positional_args[0],
                    revision_start=start_revision,
                    revision_end=end_revision )
        self.printNotifyMessages()

        for line in all_lines:
            print '%d| r%d | %s | %s | %s' % \
                (line['number'],
                line['revision'].number,
                line['author'],
                line['date'],
                line['line'])
    cmd_ann = cmd_annotate

    def cmd_cat( self, args ):
        revision = args.getOptionalRevision( '--revision', 'head' )
        text = self.client.cat( args.getPositionalArgs( 1, 1 )[0], revision=revision )
        print text

    def cmd_checkout( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( os.path.basename( positional_args[0] ) )

        self.revision_update_complete = None
        self.client.checkout( positional_args[0], positional_args[1], recurse=recurse )
        self.printNotifyMessages()

        if self.revision_update_complete is not None:
            print 'Checked out revision',self.revision_update_complete.number
        else:
            print 'Checked out unknown revision - checkout failed?'

    cmd_co = cmd_checkout

    def cmd_cleanup( self, args ):
        positional_args = args.getPositionalArgs( 0, 1 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        self.client.cleanup( positional_args[0] )

    def cmd_checkin( self, args ):
        msg = args.getOptionalValue( '--message', '' )

        recurse = args.getBooleanOption( '--non-recursive', False )
        positional_args = args.getPositionalArgs( 0 )
        if len(positional_args) == 0:
            positional_args.append( '.' )
        if msg == '':
            msg = self.getLogMessage()
            
        rev = self.client.checkin( positional_args, msg, recurse=recurse )
        self.printNotifyMessages()

        if rev is None:
            print 'Nothing to commit'
        elif rev.number > 0:
            print 'Revision',rev.number
        else:
            print 'Commit failed'

    cmd_commit = cmd_checkin
    cmd_ci = cmd_checkin

    def cmd_copy( self, args ):
        positional_args = args.getPositionalArgs( 2, 2 )
        self.client.copy( positional_args[0], positional_args[1] )
    cmd_cp = cmd_copy

    def cmd_diff( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        revision1, revision2 = args.getOptionalRevisionPair( '--revision', 'base', 'working' )
        positional_args = args.getPositionalArgs( 0, 1 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        if os.environ.has_key('TEMP'):
            tmpdir = os.environ['TEMP']
        elif os.environ.has_key('TMPDIR'):
            tmpdir = os.environ['TMPDIR']
        elif os.environ.has_key('TMP'):
            tmpdir = os.environ['TMP']
        elif os.path.exists( '/usr/tmp' ):
            tmpdir = '/usr/tmp'
        elif os.path.exists( '/tmp' ):
            tmpdir = '/tmp'
        else:
            print 'No tmp dir!'
            return

        tmpdir = os.path.join( tmpdir, 'svn_tmp' )
        self.debug( 'cmd_diff %r, %r, %r, %r, %r' % (tmpdir, positional_args[0], recurse, revision1, revision2) )
        diff_text = self.client.diff( tmpdir, positional_args[0], recurse=recurse,
                                            revision1=revision1, revision2=revision2,
                                            diff_options=['-u'] )
        print diff_text.encode('utf-8')

    def cmd_export( self, args ):
        force = args.getBooleanOption( '--force', False )
        revision_url = args.getOptionalRevision( '--revision', 'head' )
        revision_wc = args.getOptionalRevision( '--revision', 'working' )
        native_eol = args.getOptionalValue( '--native-eol', None )
        positional_args = args.getPositionalArgs( 2, 2 )
        if self.client.is_url( positional_args[0] ):
            revision = revision_url
        else:
            revision = revision_wc

        self.client.export( positional_args[0], positional_args[1], revision=revision, force=force, native_eol=native_eol )

    def cmd_info( self, args ):
        positional_args = args.getPositionalArgs( 0, 1 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        path = positional_args[0]

        entry = self.client.info( path )

        print 'Path:',path
        if entry.name and entry.name != 'svn:this_dir':
            print 'Name:',entry.name.encode('utf-8')
        if entry.url:
            print 'Url:',entry.url.encode('utf-8')
        if entry.repos and self.pysvn_testing >= '01.03.00':
            print 'Repository:',entry.repos
        if entry.uuid:
            print 'Repository UUID:',entry.uuid
        if entry.revision.kind == pysvn.opt_revision_kind.number:
            print 'Revision:',entry.revision.number
        if entry.kind == pysvn.node_kind.file:
            print 'Node kind: file'
        elif entry.kind == pysvn.node_kind.dir:
            print 'Node kind: directory'
        elif entry.kind == pysvn.node_kind.none:
            print 'Node kind: none'
        else:
            print 'Node kind: unknown'

        if entry.schedule == pysvn.wc_schedule.normal:
            print "Schedule: normal"
        elif entry.schedule == pysvn.wc_schedule.add:
            print "Schedule: add"
        elif entry.schedule == pysvn.wc_schedule.delete:
            print "Schedule: delete"
        elif entry.schedule == pysvn.wc_schedule.replace:
            print "Schedule: replace"
        if entry.is_copied:
            if entry.copyfrom_url:
                print 'Copied From URL:', entry.copyfrom_url.encode('utf-8')
            if entry.copyfrom_rev.number:
                print 'Copied From Rev:', entry.copyfrom_rev.number
        if entry.commit_author:
            print 'Last Changed Author:', entry.commit_author.encode('utf-8')
        if entry.commit_revision.number:
            print 'Last Changed Rev:', entry.commit_revision.number
        if entry.commit_time:
            print 'Last Changed Date:', fmtDateTime( entry.commit_time )
        if entry.text_time:
            print 'Text Last Updated:', fmtDateTime( entry.text_time )
        if entry.properties_time and self.pysvn_testing == '99.99.99':
            print 'Properties Last Updated:', fmtDateTime( entry.properties_time )
        if entry.checksum:
            print 'Checksum:', entry.checksum

    def cmd_info2( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision_url = args.getOptionalRevision( '--revision', 'head' )
        revision_path = args.getOptionalRevision( '--revision', 'unspecified' )

        positional_args = args.getPositionalArgs( 0, 1 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        path = positional_args[0]

        if self.client.is_url( path ):
            revision = revision_url
        else:
            revision = revision_path

        all_entries = self.client.info2( path, revision=revision,  recurse=recurse )

        for path, info in all_entries:
            print
            print 'Path:',path.encode('utf-8')

            if info.URL:
                print 'Url:',info.URL.encode('utf-8')
            if info.rev:
                print 'Revision:',info.rev.number
            if info.repos_root_URL and self.pysvn_testing >= '01.03.00':
                print 'Repository root URL:',info.repos_root_URL
            if info.repos_UUID:
                print 'Repository UUID:',info.repos_UUID
            if info.last_changed_author:
                print 'Last changed author:',info.last_changed_author.encode('utf-8')
            if info.last_changed_date:
                print 'Last Changed Date:', fmtDateTime( info.last_changed_date )
            if info.last_changed_rev.kind == pysvn.opt_revision_kind.number:
                print 'Last changed revision:',info.last_changed_rev.number
            if info.kind == pysvn.node_kind.file:
                print 'Node kind: file'
            elif info.kind == pysvn.node_kind.dir:
                print 'Node kind: directory'
            elif info.kind == pysvn.node_kind.none:
                print 'Node kind: none'
            else:
                print 'Node kind: unknown'
            if info.lock:
                print 'Lock Owner:',info.lock.owner.encode('utf-8')
                print 'Lock Creation Date:',fmtDateTime( info.lock.creation_date )
                if info.lock.expiration_date is not None:
                    print 'Lock Expiration Date:',fmtDateTime( info.lock.expiration_date )
                print 'Lock Token:',info.lock.token
                print 'Lock Comment:'
                if info.lock.comment not in ['', None]:
                    print info.lock.comment
            if info.wc_info:
                wc_info = info.wc_info
                if wc_info.schedule == pysvn.wc_schedule.normal:
                    print "Schedule: normal"
                elif wc_info.schedule == pysvn.wc_schedule.add:
                    print "Schedule: add"
                elif wc_info.schedule == pysvn.wc_schedule.delete:
                    print "Schedule: delete"
                elif wc_info.schedule == pysvn.wc_schedule.replace:
                    print "Schedule: replace"
                if wc_info.copyfrom_url:
                    print 'Copied From URL:', wc_info.copyfrom_url.encode('utf-8')
                    print 'Copied From Rev:', wc_info.copyfrom_rev.number
                if wc_info.text_time:
                    print 'Text Last Updated:', fmtDateTime( wc_info.text_time )
                if wc_info.prop_time and self.pysvn_testing == '99.99.99':
                    print 'Properties Last Updated:', fmtDateTime( wc_info.prop_time )
                if wc_info.checksum:
                    print 'Checksum:', wc_info.checksum


    def cmd_import( self, args ):
        msg = self.getOptionalValue( '--message', '' )
        recurse = args.getBooleanOption( '--non-recursive', False )
        positional_args = args.getPositionalArgs( 2, 2 )
        self.client.import_( positional_args[0], positional_args[1], recurse=recurse )

    def cmd_lock( self, args ):
        msg = args.getOptionalValue( '--message', '' )
        force = args.getBooleanOption( '--force', True )
        positional_args = args.getPositionalArgs( 1, 1 )
        self.client.lock( positional_args[0], msg, force );

    def cmd_log( self, args ):
        start_revision, end_revision = args.getOptionalRevisionPair( '--revision', 'head', '0' )
        verbose = args.getBooleanOption( '--verbose', True )
        positional_args = args.getPositionalArgs( 1, 1 )
        all_logs = self.client.log( positional_args[0],
                    revision_start=start_revision,
                    revision_end=end_revision,
                    discover_changed_paths=verbose )

        for log in all_logs:
            print '-'*60
            print 'rev %d: %s | %s | %d lines' % \
                (log.revision.number, log.author, fmtDateTime( log.date ),
                len(log.message.split('\n')))

            if len(log.changed_paths) > 0:
                print 'Changed paths:'
                for change_info in log.changed_paths:
                    if change_info.copyfrom_path is None:
                        print '  %s %s' % (change_info.action, change_info.path)
                    else:
                        print '  %s %s (from %s:%d)' % \
                            (change_info.action, change_info.path,
                            change_info.copyfrom_path, change_info.copyfrom_revision.number)

            print log.message

        print '-'*60

    def cmd_ls( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision = args.getOptionalRevision( '--revision', 'head' )
        verbose = args.getBooleanOption( '--verbose', True )
        positional_args = args.getPositionalArgs( 0 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        for arg in positional_args:
            all_files = self.client.ls( arg, revision=revision, recurse=recurse )
            if verbose:
                for file in all_files:
                    args = {}
                    args.update( file )
                    args['name'] = args['name'].encode('utf-8')  
                    args['last_author'] = args['last_author'].encode('utf-8')  
                    args['time_str'] = fmtDateTime( file.time )
                    args['created_rev_num'] = file.created_rev.number
                    print '%(created_rev_num)7d %(last_author)-10s %(size)6d %(time_str)s %(name)s' % args
            else:
                for file in all_files:
                    print '%(name)s' % file

    def cmd_merge( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        dry_run = args.getBooleanOption( '--dry-run', False )
        notice_ancestry = args.getBooleanOption( '--notice-ancestry', False )

        # need to figure out which variaty of the merge command this is
        if args.haveOption( '--revision' ):
            # its merge -r N:M SOURCE [WCPATH]
            revision1, revision2 = args.getMandatoryRevisionPair( '--revision' )
            positional_args = args.getPositionalArgs( 1, 2 )
            if len(positional_args) == 1:
                positional_args.append( '.' )
            path1 = positional_args[0]
            path2 = positional_args[0]
            wcpath = positional_args[1]
        else:
            # its merge sourceURL1[@N] sourceURL2[@M] [WCPATH]
            positional_args = args.getPositionalArgs( 2, 3 )
            if len(positional_args) == 2:
                positional_args.append( '.' )

            path1, rev1 = self.parsePathWithRevision( positional_args[0] )
            path2, rev2 = self.parsePathWithRevision( positional_args[1] )
            wcpath = positional_args[2]

            
        self.client.merge( path1, revision1, path2, revision2, wcpath,
                recurse=recurse, dry_run=dry_run, notice_ancestry=notice_ancestry )

    def cmd_mkdir( self, args ):
        msg = args.getOptionalValue( '--message', '' )
        if msg == '':
            msg = self.getLogMessage()

        self.client.mkdir( args.getPositionalArgs( 1, 1 )[0], msg )

    def cmd_move( self, args ):
        positional_args = args.getPositionalArgs( 2, 2 )
        self.client.move( positional_args[0], positional_args[1] )
    cmd_mv = cmd_move

    def props_by_path( self, a, b ):
        return cmp( a[0], b[0] )


    def cmd_proplist( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision = args.getOptionalRevision( '--revision', 'working' )
        verbose = args.getBooleanOption( '--verbose', True )
        positional_args = args.getPositionalArgs( 0, 0 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        for arg in positional_args:

            if self.client.is_url( arg ):
                revision = args.getOptionalRevision( '--revision', 'head' )

            all_props = self.client.proplist( arg, revision=revision, recurse=recurse )
            all_props.sort( self.props_by_path )

            for path, props in all_props:
                print "Properties on '%s':" % path
                prop_names = props.keys()
                prop_names.sort()
                for name in prop_names:
                    if verbose:
                        print '  %s: %s' % (name, props[name])
                    else:
                        print '  %s' % name
            
    cmd_pl = cmd_proplist

    def cmd_propget( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision = args.getOptionalRevision( '--revision', 'working' )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( '.' )
        if self.client.is_url( positional_args[0] ):
            revision = args.getOptionalRevision( '--revision', 'head' )

        props = self.client.propget( positional_args[0], positional_args[1], revision=revision, recurse=recurse )
        prop_names = props.keys()
        prop_names.sort()
        for name in prop_names:
            print '%s: %s' % (name, props[name])

    cmd_pg = cmd_propget

    def cmd_propset( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision = args.getOptionalRevision( '--revision', 'working' )
        verbose = args.getBooleanOption( '--verbose', True )
        positional_args = args.getPositionalArgs( 2, 3 )
        if len(positional_args) == 2:
            positional_args.append( '.' )
        if self.client.is_url( positional_args[0] ):
            revision = args.getOptionalRevision( '--revision', 'head' )

        self.client.propset( positional_args[0], positional_args[1], positional_args[2], revision=revision, recurse=recurse )
    cmd_ps = cmd_propset

    def cmd_propdel( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        revision = args.getOptionalRevision( '--revision', 'working' )
        verbose = args.getBooleanOption( '--verbose', True )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( '.' )
        if self.client.is_url( positional_args[0] ):
            revision = args.getOptionalRevision( '--revision', 'head' )

        self.client.propdel( positional_args[0], positional_args[1], revision=revision, recurse=recurse )
    cmd_pd = cmd_propdel

    def cmd_revproplist( self, args ):
        revision = args.getOptionalRevision( '--revision', 'head' )
        verbose = args.getBooleanOption( '--verbose', False )
        positional_args = args.getPositionalArgs( 0, 1 )
        if len(positional_args) == 0:
            positional_args.append( '.' )

        rev, prop_dict = self.client.revproplist( positional_args[0], revision=revision )
        print 'Revision:',rev.number
        prop_keys = prop_dict.keys()
        prop_keys.sort()
        for key in prop_keys:
            print '%s: %s' % (key, prop_dict[ key ])

    cmd_rpl = cmd_revproplist

    def cmd_revpropget( self, args ):
        revision = args.getOptionalRevision( '--revision', 'head' )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( '.' )

        rev, value = self.client.revpropget( positional_args[0], positional_args[1], revision=revision )
        print 'Revision:',rev.number
        print '%s: %s' % (positional_args[0], value)

    cmd_rpg = cmd_revpropget

    def cmd_revpropset( self, args ):
        force = args.getBooleanOption( '--force', False )
        revision = args.getOptionalRevision( '--revision', 'head' )
        positional_args = args.getPositionalArgs( 2, 3 )
        if len(positional_args) == 2:
            positional_args.append( '.' )

        rev = self.client.revpropset( positional_args[0], positional_args[1], positional_args[2], revision=revision, force=force )
    cmd_rps = cmd_revpropset

    def cmd_revpropdel( self, args ):
        force = args.getBooleanOption( '--force', False )
        revision = args.getOptionalRevision( '--revision', 'head' )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( '.' )

        self.client.revpropdel( positional_args[0], positional_args[1], revision=revision, force=force )
    cmd_rpd = cmd_revpropdel

    def cmd_remove( self, args ):
        force = args.getBooleanOption( '--force', True )
        positional_args = args.getPositionalArgs( 1, 0 )
        self.client.remove( positional_args, force=force )
    cmd_rm = cmd_remove

    def cmd_resolved( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        positional_args = args.getPositionalArgs( 1, 1 )
        self.client.resolved( positional_args[0], recurse=recurse )

    def cmd_revert( self, args ):
        recurse = args.getBooleanOption( '--recursive', True )
        positional_args = args.getPositionalArgs( 1, 1 )
        self.client.revert( positional_args[0], recurse=recurse )

    def by_path( self, a, b ):
        return cmp( a.path, b.path )

    def cmd_status( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        verbose = args.getBooleanOption( '--verbose', True )
        ignore = args.getBooleanOption( '--no-ignore', False )
        update = args.getBooleanOption( '--show-updates', True )

        positional_args = args.getPositionalArgs( 0 )
        if len(positional_args) == 0:
            all_files = self.client.status( '', recurse=recurse, get_all=verbose, ignore=ignore, update=update )
            self._cmd_status_print( all_files, verbose, update, ignore )
        else:
            for arg in positional_args:
                all_files = self.client.status( arg, recurse=recurse, get_all=verbose, ignore=ignore, update=update )
                self._cmd_status_print( all_files, verbose, update, ignore )

    def _cmd_status_print( self, all_files, detailed, update, ignore ):
        all_files.sort( self.by_path )
        for file in all_files:
            if file.text_status == pysvn.wc_status_kind.ignored and ignore:
                continue

            state = '%s%s%s%s%s' % (wc_status_kind_map[ file.text_status ],
                    wc_status_kind_map[ file.prop_status ],
                    ' L'[ file.is_locked ],
                    ' +'[ file.is_copied ],
                    ' S'[ file.is_switched ])

            if( file.repos_text_status != pysvn.wc_status_kind.none
            or  file.repos_prop_status != pysvn.wc_status_kind.none ):
                odd_status = '%s%s' % (wc_status_kind_map[ file.repos_text_status ],
                    wc_status_kind_map[ file.repos_prop_status ])
            else:
                odd_status = '  '

            lock_state = ' '
            if file.entry is not None and hasattr( file.entry, 'lock_token' ):
                if file.entry.lock_token is not None:
                    lock_state = 'K'

            if hasattr( file, 'repos_lock' ) and file.repos_lock is not None:
                lock_state = 'O'

            if file.entry is not None and detailed:
                print '%s%s %s %6d %6d %-14s %s' % (state, lock_state,
                    odd_status,
                    file.entry.revision.number,
                    file.entry.commit_revision.number,
                    file.entry.commit_author.encode('utf-8'),
                    file.path.encode('utf-8'))

            elif detailed:
                print '%s%s %s %6s %6s %-14s %s' % (state, lock_state,
                    odd_status,
                    '',
                    '',
                    '',
                    file.path.encode('utf-8'))

            elif update:
                print '%s%s %s %s' % (state, lock_state,
                    odd_status,
                    file.path.encode('utf-8'))

            else:
                if( file.text_status != pysvn.wc_status_kind.normal
                or file.prop_status != pysvn.wc_status_kind.normal
                or lock_state.strip() != ''):
                    print '%s%s %s' % (state, lock_state, file.path.encode('utf-8'))

    cmd_st = cmd_status
    cmd_stat = cmd_status

    def cmd_switch( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        revision = args.getOptionalRevision( '--revision', 'head' )
        positional_args = args.getPositionalArgs( 1, 2 )
        if len(positional_args) == 1:
            positional_args.append( '.' )
        self.client.switch( positional_args[0], positional_args[1],
                recurse=recurse, revision=revision )

    def cmd_relocate( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        positional_args = args.getPositionalArgs( 2, 3 )
        if len(positional_args) == 2:
            positional_args.append( '.' )
        self.client.relocate( positional_args[0], positional_args[1],
                positional_args[2], recurse=recurse )

    def cmd_unlock( self, args ):
        force = args.getBooleanOption( '--force', False )
        positional_args = args.getPositionalArgs( 1, 1 )
        self.client.unlock( positional_args[0], force );

    def cmd_update( self, args ):
        recurse = args.getBooleanOption( '--non-recursive', False )
        positional_args = args.getPositionalArgs( 0 )
        if len(positional_args) == 0:
            positional_args.append( '.' )
        rev_list = self.client.update( positional_args[0], recurse=recurse )
        self.printNotifyMessages()
        if type(rev_list) == type([]) and len(rev_list) != 1:
            print 'rev_list = %r' % [rev.number for rev in rev_list]

        if self.revision_update_complete is not None:
            print 'Updated to revision',self.revision_update_complete.number
        else:
            print 'Updated to unknown revision - update failed?'

    cmd_up = cmd_update

    def cmd_help( self, args ):
        print 'Version: pysvn %d.%d.%d-%d' % pysvn.version,'svn %d.%d.%d-%s' % pysvn.svn_version
        valid_cmd_names = [name for name in SvnCommand.__dict__.keys() if name.find('cmd_') == 0]
        valid_cmd_names.sort()
        print 'Available subcommands:'
        index = 0
        for name in valid_cmd_names:
            print '   %-12s' % name[4:],
            if index % 4 == 3:
                print
            index += 1

# key is long option name, value is 1 if need next arg as value
long_opt_info = {
    '--pause': 0,

    '--auto-props': 0,          # enable automatic properties
    '--config-dir': 1,          # read user configuration files from directory ARG
    '--diff-cmd': 1,            # use ARG as diff command
    '--diff3-cmd': 1,           # use ARG as merge command
    '--dry-run': 0,             # try operation but make no changes
    '--editor-cmd': 1,          # use ARG as external editor
    '--encoding': 1,            # treat value as being in charset encoding ARG
    '--force': 0,               # force operation to run
    '--force-log': 0,           # force validity of log message source
    '--incremental': 0,         # give output suitable for concatenation
    '--new': 1,                 # use ARG as the newer target
    '--no-auth-cache': 0,       # do not cache authentication tokens
    '--no-auto-props': 0,       # disable automatic properties
    '--no-diff-deleted': 0,     # do not print differences for deleted files
    '--no-ignore': 0,           # disregard default and svn:ignore property ignores
    '--non-interactive': 0,     # do no interactive prompting
    '--notice-ancestry': 0,     # notice ancestry when calculating differences
    '--old': 1,                 # use ARG as the older target
    '--password': 1,            # specify a password ARG
    '--relocate': 0,            # relocate via URL-rewriting
    '--revprop': 0,             # operate on a revision property (use with -r)
    '--strict': 0,              # use strict semantics
    '--targets': 1,             # pass contents of file ARG as additional args
    '--username': 1,            # specify a username ARG
    '--version': 0,             # print client version info
    '--xml': 0,                 # output in xml
    '--file': 1,                # read data from file ARG
    '--native-eol': 1,          # native eol ARG
    '--non-recursive': 0,       # operate on single directory only
    '--recursive': 0,           # descend recursively
    '--message': 1,             # specify commit message ARG
    '--quiet': 0,               # print as little as possible
    '--revision': 1,            # revision X or X:Y range.  X or Y can be one of:
    '--show-updates': 0,        # display update information
    '--verbose': 0,             # print extra information
    '--extensions': 1,          # pass ARG as bundled options to GNU diff
    '--pysvn-testing': 1,       # modify behaviour to assist testing pysvn
    '--debug': 0,               # do debug stuff
}

# map short name to long
short_opt_info = {
    '-F': '--file',
    '-N': '--non-recursive',
    '-R': '--recursive',
    '-m': '--message',
    '-q': '--quiet',
    '-r': '--revision',
    '-u': '--show-updates',
    '-v': '--verbose',
    '-x': '--extensions',
}


#
# Usage:
#    Construct with a commnad list
#    call getCommandName()
#    call getBooleanOption() and getOptionalValue() as needed
#    finally call getPositionalArgs()
#
#
class SvnArguments:
    def __init__( self, all_args ):
        self.positional_args = []
        self.named_options = {}
        self.used_named_options = {}

        need_next_arg = 0
        name = ''

        for arg in all_args:
            if need_next_arg:
                self.named_options[ name ] = arg
                need_next_arg = 0

            elif self._isOption( arg ):
                name, need_next_arg = self._optionInfo( arg )
                if not need_next_arg:
                    self.named_options[ name ] = None

            else:
                expanded_arg = glob.glob( arg )
                if len(expanded_arg) > 0:
                    self.positional_args.extend( expanded_arg )
                else:
                    self.positional_args.append( arg )
        if need_next_arg:
            raise CommandError, 'Missing arg to option %s' % name

    def _isOption( self, arg ):
        return arg[0] == '-'
            
    def _optionInfo( self, opt ):
        # return long_name, arg_needed
        long_opt = short_opt_info.get( opt, opt )
        if long_opt_info.has_key( long_opt ):
            return long_opt, long_opt_info[ long_opt ]
        raise CommandError, 'unknown option %s' % opt

    def _checkOptionsUsed( self ):
        # check all options have been used
        for opt_name in self.named_options.keys():
            if not self.used_named_options.has_key( opt_name ):
                raise CommandError, 'unused option %s' % opt_name

    def parsePathWithRevision( self, path_rev, default_rev ):
        if '@' in path_rev:
            path = path_rev[:path_rev.find('@')]
            rev = self._parseRevisionArg( path_rev[path_rev.find('@')+1:] )
        else:
            path = path_rev
            rev = self._parseRevisionArg( default_rev )
        return path, rev

    def _parseRevisionArg( self, rev_string ):
        if rev_string.lower() == 'base':
            return pysvn.Revision( pysvn.opt_revision_kind.base )
        if rev_string.lower() == 'head':
            return pysvn.Revision( pysvn.opt_revision_kind.head )
        if rev_string.lower() == 'working':
            return pysvn.Revision( pysvn.opt_revision_kind.working )
        if rev_string.lower() == 'committed':
            return pysvn.Revision( pysvn.opt_revision_kind.committed )
        if rev_string.lower() == 'prev':
            return pysvn.Revision( pysvn.opt_revision_kind.prev )
        if rev_string.lower() == 'unspecified':
            return pysvn.Revision( pysvn.opt_revision_kind.unspecified )
        if rev_string[0] == '{' and rev_string[-1] == '}':
            try:
                date = parse_datetime.parse_time( rev_string[1:-2] )
                return pysvn.Revision( pysvn.opt_revision_kind.date, date )
            except parse_datetime.DateTimeSyntaxError, e:
                raise CommandError, e.reason()
        # either a rev number or a date
        try:
            return pysvn.Revision( pysvn.opt_revision_kind.number, int(rev_string) )
        except ValueError:
            pass
        raise CommandError, 'Cannot parse %s as a revision value' % rev_string


    def _splitRevisionString( self, rev_string ):
        # split the string at the first : that is not inside a {} pair
        if rev_string[0] == '{':
            # the : may be after the closing }
            close_paren_index = rev_string.find( '}' )
            if close_paren_index == -1:
                # error leave to others to report
                return [rev_string]

            if close_paren_index == len(rev_string ):
                # its just one revision
                return [rev_string]

            if rev_string[close_paren_index+1] == ':':
                return [rev_string[:close_paren_index+1], rev_string[close_paren_index+2:]]

            # another error case
            return [rev_string]
        else:
            return rev_string.split(':',1)

    def getCommandName( self, default_command ):
        if len(self.positional_args) > 0:
            return self.positional_args.pop( 0 )
        else:
            return default_command

    def haveOption( self, opt_name ):
        return self.named_options.has_key( opt_name )

    def getBooleanOption( self, opt_name, present_value=True ):
        if self.named_options.has_key( opt_name ):
            self.used_named_options[ opt_name ] = None
            return present_value
        else:
            return not present_value

    def getOptionalValue( self, opt_name, default ):
        if self.named_options.has_key( opt_name ):
            self.used_named_options[ opt_name ] = None
            return self.named_options[ opt_name ]
        else:
            return default

    def getOptionalRevision( self, opt_name, start_default ):
        if self.named_options.has_key( opt_name ):
            self.used_named_options[ opt_name ] = None
            rev_string = self.named_options[ opt_name ]

            return self._parseRevisionArg( rev_string )
        else:
            return self._parseRevisionArg( start_default )

    def getMandatoryRevisionPair( self, opt_name ):
        # parse a M:N or M as revision pair
        if not self.named_options.has_key( opt_name ):
            raise CommandError,'mandatory %s required' % opt_name

        self.used_named_options[ opt_name ] = None

        rev_strings = self._splitRevisionString( self.named_options[ opt_name ] )
        if len(rev_strings) == 1:
            raise CommandError,'mandatory %s requires a pair of revisions' % opt_name

        return [self._parseRevisionArg( rev_strings[0] ),
            self._parseRevisionArg( rev_strings[1] )]

    def getOptionalRevisionPair( self, opt_name, start_default, end_default=None ):
        # parse a M:N or M as revision pair
        if self.named_options.has_key( opt_name ):
            self.used_named_options[ opt_name ] = None
            rev_strings = self._splitRevisionString( self.named_options[ opt_name ] )
            if len(rev_strings) == 1:
                if end_default is None:
                    # M means M:M
                    rev_strings.append( rev_strings[0] )
                else:
                    # M means M:end_default
                    rev_strings.append( end_default )

            return [self._parseRevisionArg( rev_strings[0] ),
                self._parseRevisionArg( rev_strings[1] )]
        else:
            return (self._parseRevisionArg( start_default ),
                self._parseRevisionArg( end_default ))

    def getPositionalArgs( self, min_args, max_args=0 ):
        # check min and max then return the list
        if len(self.positional_args) < min_args:
            raise CommandError, 'too few arguments - need atlease %d' % min_args
        if max_args != 0 and len(self.positional_args) > max_args:
            raise CommandError, 'too many arguments - need no more then %d' % max_args

        # as this is the last call on the args object we check the option where all used
        self._checkOptionsUsed()

        return self.positional_args

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
