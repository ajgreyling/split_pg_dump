import sys
import re
import os
import argparse

parser = argparse.ArgumentParser(description='Split output from pg_dump into seperate files. See https://github.com/kruckenb/split_postgres_dump/blob/master/split-pg-dump.pl')
parser.add_argument('sourcefile', help='SQL input file. Typically from pg_dump')
args = parser.parse_args()

type_prefix = {
    'MATERIALIZED VIEW' : '_mv_',
    'SEQUENCE' : '_sq_',
    'INDEX' : '_ix_',
    'TABLE' : '_tb_',
    'TYPE' : '_ty_',
    'VIEW' : '_vw_',
    'FUNCTION' : '_fn_'
}

print "input file:", args.sourcefile
inputfile = ''
inputfile=args.sourcefile
# delete contents of 00000_pre_execute.sql. If it does not exist, create it
#open('00000_pre_execute.sql', 'w').close()

with open(inputfile) as fo:
        skip = True
        newfile = True
        cntr = 1
        filename = ''
        object_type_set = set()
        for line in fo.readlines():
            match_result = re.search('-- Name: (?P<object_name>\w+\(?\)?); Type: (?P<object_type>\w+ ?\w+);', line)
            if not (match_result is None):
                newfile = True
                object_name = match_result.group('object_name')
                object_type = match_result.group('object_type')
                if object_name == 'FUNCTION':
                    print object_name
                skip = (object_type == 'SCHEMA' or object_type == 'TABLE' or '__idx_he_' in object_name or '__he_' in object_name or object_name in '__change_')
                if not skip :
                    object_type_set.add(object_type)

                    if (newfile):
                        filename = '{0:05d}'.format(cntr) + type_prefix[object_type] + object_name + '.sql'
                        print filename
                        with open (filename,'w') as opf:
                            if object_type == 'VIEW' or object_type == 'MATERIALIZED VIEW':
                                opf.write('\nDO $$ BEGIN\n')
                                opf.write('PERFORM __he_delete_table_or_view__(\'' + object_name + '\');\n')
                                opf.write('END $$;\n\n')    
                            opf.write(line)
                            opf.close
                            cntr+=1
                        newfile = False
                    else:
                        opf.write(line)
            else:
                if skip == False:
                    with open (filename,'a') as opf:
                        opf.write(line)       
                        opf.close
fo.close()

#def write_pre_excute(object_name)
#    with open ('00000_pre_execute.sql','a') as opf:
#        opf.write('\nDO $$ BEGIN\n')
#        opf.write('PERFORM __he_delete_table_or_view__(\'' + object_name + '\');\n')
#        opf.write('END $$;\n\n')   