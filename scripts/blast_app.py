"""Blast."""

import os
import sys
import json
import string
import tempfile
import subprocess

from flask import Flask, request

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

app = Flask(__name__)


BLAST_CMD = 'blastn'
BLAST_DB = 'data/blastdb/constructs'
SAMPLE_QUERY = 'atggcaaagagcaatgaagaatcatcgaatctgaatgtgatgaacaaaccacctttgaagaaaacaaagacacttccttccctcaatctcagagtttctgttactcctcccaatcccaatgacaacaatggaattggaggaacttcaactactaaaactgatttctcagaacaacaatggaactacccttctttccttggcattggcagcacctccagaaaaagaaggcaaccaccccctcctccttccaaacctcctgtaaacctcattcctcctcatccccgtcccctctccgtcaacgaccacaacaaaaccacctcctcacttcttccacaaccttcctcttcctccatcaccaaacaacaacaacaacactctacctcctctcccatcttctatcttttagttatctgttgtattattcttgtaccctattcagcttatttacaatacaaacttgccaaactcaaggatatgaaacttcaactctgtggtcaaattgatttttgttcccgtaacggaaaaacatccatacaagaagaggttgatgacgatgataatgcagatagtagaacaatagctttatatattgtgcttttcacattgattttgccttttgtattgtacaaatatcttgattatcttcctcaaataattaatttcttgaggagaacagaaagtaacaaggaggatgtaccattaaagaagagagttgcttatatggtagatgtatttttctccatatatccttatgcaaagctacttgcacttctttgtgcaactctctttcttatagcatttggtggtttagcgttgtatgcggttactggtggtagcatggctgaagcactttggcattcttggacttatgtagctgacgcaggaaatcacgctgaaacagaaggaaccggccagagaatcgtgtctgtctcaattagtgcgggtggcatgcttatatttgccatgatgcttgggcttgtttcggatgctatatcagagaaggttgattcacttagaaaaggaaagagcgaagtcatcgaaagaaaccatgtactcatccttggctggagtgacaaattgggctcacttttgaagcagctagcaatagccaataagagtgttggtggtggtgttattgtggtgcttgcagaaaaggaaaaggaggaaatggaaatggatattgcaaagctcgaattcgatttcatggggacatcagtaatatgtagaagtggcagtccactaatacttgctgacctaaagaaggtttcagtttcaaaggcacgtgcaatcattgttttagctgcggacgaaaatgcagatcagagtgatgcacgtgctttgagagttgttcttagcttagctggtgtaaaggagggcttaagggggcatgttgttgtagagatgagcgacctagacaatgaacccctagtgaaacttgttggtggagaactcattgaaacagttgttgcacatgatgtgattggacgtttgatgattcagtgtgctctacagcctggccttgcacagatatgggaggacattctaggatttgagaatgctgagttttacataaaaagatggcctgaactggatgatcttcttttcaaagacatattaatttcatttcctgatgcaataccgtgtggagttaaggttgctgcagatggagggaagattgtcataaatccagatgataattatgttctgagagatggtgatgaagtccttgttatagctgaggatgatgacacttatgccccaggccctctgccagaggtacgcaagggttatttccctaggatacgtgatccccctaaatatccagagaagatactgttttgtggctggcgccgtgacattgatgatatgatcatggttttagaagcattcttggcccctggttcagaactttggatgttcaatgaagttcctgaaaaggaaagagagaggaaacttgctgctggtgaacttgatgtttttggattagagaacataaagcttgttcaccgggagggaaatgctgtcattaggcggcacctcgagagtctacctttggagacttttgattctatccttattcttgcagatgagtcagtggaggactctgttgctcattctgactcaagatccctagccactcttctgctcattcgtgatatacagtcgaggcgtctaccttaccgagatacgaagtcaacttctttaaggttatctgggttctctcataactcatggatccgcgaaatgcaacaagcttcagataaatcaattataattagtgaaattttggattctaggactagaaatctagtttctgtatccaggatcagtgattatgtattatccaatgagctggttagcatggcactagctatggtagctgaagataagcagatcaaccgtgttcttgaggaattatttgcggaggaggggaacgagatgtgtattaagccagcagagttctatttatttgaccaggaggagctctgtttctatgatataatgattaggggtcgtacaagaaaggagattgttataggctatcgcctggccaaccaagagcgtgctattatcaacccttcagaaaaatctgtgccaagaaaatggtcccttgatgatgtttttgttgttttagcctcaggtgaatga'

# Grabbed from web to allow cross domain POST and return
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def blast_search_file(filename):

	blast_command = [BLAST_CMD,
					 '-db',
					 BLAST_DB,
					 '-query',
					 filename,
					 '-outfmt',
					 '6'
					 ]

	p = subprocess.Popen(blast_command, stdout=subprocess.PIPE, 
										stderr=subprocess.PIPE)

	stdout, stderr = p.communicate()

	return stdout, stderr

def result_list_to_dict(result_list):
	"""Given a blast result as a list of values, return a dictionary."""
	info_dict = {1 : "ConstructID", 2 : "PercentID"}

	return {name: result_list[index] for index, name in info_dict.items()}

def format_blast_output(raw_output):
	"""Given raw blast output, convert to a list of lists, each sublist
	containing the output from one line."""

	output_lines = raw_output.split('\n')
	output_as_lists = [line.split() for line in output_lines if len(line)]

	return [result_list_to_dict(l) for l in output_as_lists]

def blast_search(sequence):
	"""Perform a BLAST search for the given sequence. Format the result as JSON
	and return it."""

	f = tempfile.NamedTemporaryFile(delete=False)
	f.write(sequence)
	f.close()

	stdout, stderr = blast_search_file(f.name)

	list_output = format_blast_output(stdout)

	json_output = json.dumps(list_output)

	return(json_output)

@app.route('/blast', methods=['POST'])
@crossdomain(origin='*')
def blast_http_request():
	sequence = request.form['sequence']

	return blast_search(sequence)

def complement_sequence(sequence):
    """Return the complement of a nucleotide sequence."""

    translation = string.maketrans('ATCG', 'TAGC')

    return sequence.upper().translate(translation)

def test_complement_sequence():

    assert(complement_sequence('aaaa') == 'TTTT')
    assert(complement_sequence('') == '')
    assert(complement_sequence('ATCG') == ('TAGC'))
    assert(complement_sequence('AAAA') == ('TTTT'))


def main():
	#test_sequence = 'aatttccca'

	#blast_search(SAMPLE_QUERY)

	app.run(debug=True)


if __name__ == '__main__':
	main()
