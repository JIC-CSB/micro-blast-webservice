makeblastdb -in constructs.fasta -dbtype nucl
makeblastdb -in data/fasta/all_constructs.fasta -dbtype nucl -out data/blastdb/constructs

blastn -db data/blastdb/constructs -query query -outfmt 6

