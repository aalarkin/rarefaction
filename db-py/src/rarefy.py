#!/usr/bin/env/python

# rarefy.py
#
# Pull data from database and calculate coverage per ecotype per station per gene.
# Stations that have a summed read_length less than the defined THRESHOLD value are ignored.

# NOTE: This version queries each depth, each station -- so it uses less memory, but is SLOWER.
# This should only be used on very large ecotypes, if the other version uses too much memory.

# Number of gene_read records per station per ecotype required for consideration
STATION_READ_MIN = 0 # TODO: Deprecated

# Number of gene_reads randomly sampled per station per ecotype
DEPTHS = [10000, 25000, 50000, 75000, 100000]
#DEPTHS = [25000, 50000, 75000, 100000]

import multiprocessing as mp
from datetime import datetime as dt
from mysql.connector import connect
import os, pandas as pd, sys
import pytz


def populateOutputTable(con, ecotypeId, sampleDepth, stationId, stationName, geneLengths):

    # Simpler query through genes table
    df = pd.read_sql('''
        SELECT gr.gene_id, gr.station_id station_id, gr.read_length FROM gene_reads gr
        LEFT JOIN genes g ON g.gene_id = gr.gene_id
        LEFT JOIN ecotypes e ON e.id = g.ecotype_id
        WHERE 1=1
            AND gr.station_id = '%s'
            AND g.ecotype_id = '%s'
        ''' % (stationId, ecotypeId),
        con=con
    )

    outputSeries = pd.Series(index=geneLengths.index)
    outputSeries.values[:] = 0
    stationDf = df[df.station_id == stationId]
    stationReadCount = len(stationDf.index)

    del df

    # If stationReadCount < sampleDepth, zerofill the station
    if stationReadCount < sampleDepth:
        sys.stdout.write('\t!%s' % str(sampleDepth))

        return outputSeries

    # Random sampling of this station's gene_reads
    sampleDf = stationDf.sample(n = sampleDepth)

    del stationDf

    # Sums of the `read_length` column for each gene for this station
    geneReadLengthSums = sampleDf.groupby('gene_id')['read_length'].sum().reset_index(name = 'sum').set_index('gene_id')

    # The number of gene_reads for this gene in this station
    uniqueGeneCount = sampleDf['gene_id'].nunique()

    del sampleDf

    # Join sums of read lengths with gene reference lengths, so it has two columns: sum and length
    grls = geneReadLengthSums.join(geneLengths, how='right')
    grls.fillna(0, downcast='infer', inplace=True)

    # Populate the output dataframe's stationName column with the calculated coverage
    outputSeries = grls['sum'] / grls['length']
    outputSeries = outputSeries.round(4)

    del grls

    sys.stdout.write('\t %s' % str(sampleDepth))

    return outputSeries


def main():
    if len(sys.argv) not in (2, 3):
        exit('Usage: rarefy.py ECOTYPE')

    ECOTYPE = sys.argv[1]
    OUTPUT_DIR = '/app/output'

    # If second argument is given, use as suffix for file name (eg. a, b, c...)
    FILE_SUFFIX = '_' + sys.argv[2] if len(sys.argv) == 3 else ''

    if not (os.access(OUTPUT_DIR, os.W_OK) and os.path.isdir(OUTPUT_DIR)):
        exit('Problem with output directory %s. Ensure it exists and is writeable.' % OUTPUT_DIR)


    # Connect to MySQL DB
    con = connect(
        database=os.getenv('MYSQL_DB'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASS'),
    )
    cur = con.cursor()

    # Fetch ecotypes, verify input
    ecotypes = {} # name => id
    cur.execute('SELECT id, name FROM ecotypes')
    for ecotypeId, ecotypeName in cur.fetchall():
        ecotypes[ecotypeName] = ecotypeId
    if ECOTYPE not in ecotypes:
        exit('Ecotype "%s" not found in database. Ecotypes found: %s' % (ECOTYPE, ', '.join([*ecotypes])))

    ecotypeId = ecotypes[ECOTYPE]

    # Length of genes based on reference sequence
    print('Fetching Gene Lengths')
    geneLengths = pd.read_sql('SELECT gene_id, length FROM genes WHERE ecotype_id = %s' % ecotypeId, con=con).set_index('gene_id')

    # Fetch stations
    print('Fetching Stations')
    cur.execute('SELECT id, name FROM stations')
    stations = {id: name for id, name in cur.fetchall()}

    # Query through contig table
#    df = pd.read_sql('''
#        SELECT gr.gene_id, gr.station_id station_id, gr.read_length FROM gene_reads gr
#        LEFT JOIN genes g ON g.gene_id = gr.gene_id
#        LEFT JOIN contigs c ON c.id = gr.contig_id
#        LEFT JOIN ecotypes e ON e.id = c.ecotype_id
#        WHERE 1=1
#            AND e.name = '%s'
#            AND g.ecotype_id = '%s'
#        ''' % (ECOTYPE, ecotypeId),
#        con=con
#    )

    # Generate blank dataframes
    outputTables = {}
    for sampleDepth in DEPTHS:
        outputTables[sampleDepth] = pd.DataFrame(index=geneLengths.index)

    START_TIME = dt.now(pytz.timezone('US/Pacific'))

    sys.stdout.write('[%s]' % START_TIME)
    for stationId, stationName in stations.items():
        elapsed_seconds = round((dt.now(pytz.timezone('US/Pacific')) - START_TIME).total_seconds())
        sys.stdout.write('\n[T+%s s]\t%s' % (str(elapsed_seconds).rjust(8, ' '), stationName))
        for sampleDepth in DEPTHS:
            outputTables[sampleDepth][stationName] = populateOutputTable(con, ecotypeId, sampleDepth, stationId, stationName, geneLengths)

#        print(
#            outputTable[(outputTable.T != 0).all()] # This is slow
#        )
    print()
    for sampleDepth in DEPTHS:
        fileOutName = OUTPUT_DIR + '/' + ECOTYPE + '_' + str(sampleDepth) + FILE_SUFFIX + '.tsv'
        print('Writing to file: ' + fileOutName)
        fileOut = open(fileOutName, 'w')
        outputTables[sampleDepth].to_csv(fileOut, sep='\t')

    del outputTables

    cur.close()
    con.close()

if __name__ == "__main__":
    main()
