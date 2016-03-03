#!/usr/bin/env Rscript
args = commandArgs(trailingOnly = TRUE)
input = args[1]
output = args[2]

data = read.csv(input, sep="\t")

columns = rep(FALSE, ncol(data))
for(i in seq(ncol(data))) {
	columns[i] = (nrow(table(data[,i])) > 1)
}
data.filtered = data[,columns==TRUE]

write.table(data.filtered, file=output, quote=FALSE, row.names=FALSE, col.names=TRUE, na="", sep="\t")
