#!/usr/bin/env Rscript
data = read.csv("all_edits.tsv.gz", sep="\t")

columns = rep(FALSE, ncol(data))
for(i in seq(ncol(data))) {
	columns[i] = (nrow(table(data[,i])) > 1)
}
data.filtered = data[,columns==TRUE]

write.table(data.filtered, file="all_edits_filtered.tsv", quote=FALSE, row.names=FALSE, col.names=TRUE, na="", sep="\t")
