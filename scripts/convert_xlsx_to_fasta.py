
import sys
import string

import xlrd

FASTA_TEMPLATE = """> {} {}
{}
"""

def format_as_fasta(construct_id, sequence):
	description = "Construct with ID {}".format(construct_id)
	return FASTA_TEMPLATE.format(construct_id, description, sequence)

def sanitise_sequence(sequence):
	return str(sequence.upper())

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
	filename = sys.argv[1]

	workbook = xlrd.open_workbook(filename)

	row_offset = 3
	for row in range(0, 103):
		construct_id = workbook.sheet_by_index(0).cell(row_offset + row, 2).value
		sequence = workbook.sheet_by_index(0).cell(row_offset + row, 3).value
		sanitised_sequence = sanitise_sequence(sequence)
		print format_as_fasta(construct_id, sanitised_sequence),
		#print format_as_fasta(construct_id + '-com', complement_sequence(sanitised_sequence)[::-1]),

	# with open('data/fasta/all_constructs.fasta', 'w') as f:
	# 	row_offset = 3
	# 	for row in range(0, 2):
	# 		construct_id = workbook.sheet_by_index(0).cell(row_offset + row, 2).value
	# 		sequence = workbook.sheet_by_index(0).cell(row_offset + row, 3).value
	# 		#f.write(format_as_fasta(construct_id, sequence))
 #        	print format_as_fasta(construct_id, sequence)

if __name__ == '__main__':
	main()	
