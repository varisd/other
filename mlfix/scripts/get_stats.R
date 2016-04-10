#!/usr/bin/env Rscript
library(infotheo)

#args = commandArgs(trailingOnly = TRUE)
#input = args[1]

data = read.csv(input, header=TRUE, quote="", colClasses="factor", encoding="UTF-8", sep="\t")

nodenames = names(data)[grep("new", names(data))]
nodenames = gsub("new_", "", nodenames)

for(name in nodenames) {
    if(name != "node_other") {
        print(name)
        print(table(data[,gsub("^", "new_", name)], data[,gsub("^", "old_", name)]))
    }
}

write.table(data.filtered, file=output, quote=FALSE, row.names=FALSE, col.names=TRUE, na="", sep="\t")
