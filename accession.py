#! /usr/bin/env python
'''
Runs (Spectrum) accessioning procedures on packages
that have been through the Object Entry process
Written by Kieran O'Leary
MIT License
'''

import sys
import os
import argparse
import ififuncs
import manifest

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Accessions objects into the Irish Film Institute collection'
        'Completes the transformation of a SIP into an AIP.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        'source', help='Input directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.')
    parser.add_argument(
        '-number',
        help='Enter the Accession number for the representation.The parent Object Entry number will be replaced with this name.'
    )
    parser.add_argument(
        '-force',
        help='Renames OE with accession number without confirmation.', action='store_true'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args
def main(args_):
    '''
    Launches the various functions that will accession a package
    '''
    args = parse_args(args_)
    source = args.source
    uuid_directory = ififuncs.check_for_sip([source])
    if uuid_directory is not None:
        oe_path = os.path.dirname(uuid_directory)
        oe_number = os.path.basename(oe_path)
        if args.user:
            user = args.user
        else:
            user = ififuncs.get_user()
        if args.number:
            if args.number[:3] != 'aaa':
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
                accession_number = ififuncs.get_accession_number()
            elif len(args.number[3:]) != 4:
                accession_number = ififuncs.get_accession_number()
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
            elif not args.number[3:].isdigit():
                accession_number = ififuncs.get_accession_number()
                print 'First three characters must be \'aaa\' and last four characters must be four digits'
            else:
                accession_number = args.number
        else:
            accession_number = ififuncs.get_accession_number()
        accession_path = os.path.join(
            os.path.dirname(oe_path), accession_number
        )
        uuid = os.path.basename(uuid_directory)
        new_uuid_path = os.path.join(accession_path, uuid)
        logs_dir = os.path.join(new_uuid_path, 'logs')
        sipcreator_log = os.path.join(logs_dir, uuid) + '_sip_log.log'
        if args.force:
            proceed = 'Y'
        else:
            proceed = ififuncs.ask_yes_no(
                'Do you want to rename %s with %s' % (oe_number, accession_number)
            )
        if proceed == 'Y':
            os.rename(oe_path, accession_path)
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = accession.py started'
        )
        ififuncs.generate_log(
            sipcreator_log,
            'eventDetail=accession.py %s' % ififuncs.get_script_version('accession.py')
        )
        ififuncs.generate_log(
            sipcreator_log,
            'Command line arguments: %s' % args
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = agentName=%s' % user
        )
        ififuncs.generate_log(
            sipcreator_log,
            'EVENT = eventType=Identifier assignment,'
            ' eventIdentifierType=accession number, value=%s'
            % accession_number
        )
        sip_manifest = os.path.join(
            accession_path, uuid
            ) + '_manifest.md5'
        sha512_log = manifest.main([new_uuid_path, '-sha512', '-s'])
        ififuncs.merge_logs_append(sha512_log, sipcreator_log, sip_manifest)
        os.remove(sha512_log)
    else:
        print 'not a valid package. The input should include a package that has been through Object Entry'
if __name__ == '__main__':
    main(sys.argv[1:])