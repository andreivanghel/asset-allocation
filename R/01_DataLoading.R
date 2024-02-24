### ASSET ALLOCATION - DATA LOADING MODULE

setwd("~/Documents/GitHub/asset-allocation")

# libraries ---------------------------------------------------------------

library(jsonlite)
library(readxl)


### TO DO 
# -> config list -> check for already saved files -> lapply to single dfs for downlaod 
# -> check for duplicates in output file?? -> shouldn't be a problem given all have the same date


# loading script ----------------------------------------------------------


dataLoading <- function(assetClassConfig, data_saving_config, sourcingDate){
  
  # separate configuration dataset into sub-datasets (by source)
  data_source_list <- split(assetClassConfig, assetClassConfig %>% pull(data_source))
  
  sources <- names(data_source_list)
  output <- list()
  
  # data loading
  for(source in sources){
    
    indexes_from_source <- data_source_list[[source]]
    output_dir <- data_saving_config %>% filter(data_source == source) %>% pull(output_dir)
    source_directory <- paste0(output_dir, "/", sourcingDate)
    
    # data to be loaded
    file_names <- list(market = indexes_from_source %>% pull(market),
                       index_id = indexes_from_source %>% pull(index_id_in_ds),
                       data_source = indexes_from_source %>% pull(data_source)) %>% 
      pmap(outputDataNaming) %>% unlist()
    file_names <- gsub("\\^", "\\\\^", file_names)
    
    # files in source_directory
    dir_files <- list.files(source_directory, full.names = TRUE)
    
    # keep only paths requested from 'indexes_from_source'
    cond <- sapply(X = dir_files,
                   FUN = function(y) grep(x = y, pattern = paste0(file_names, collapse = "|")) %>% any()) %>% as.logical()
    print(cond)
    dir_files <- dir_files[cond]
    
    
    # loading data based on source
    output[[source]] <- switch(source,
                               "sp" = list(path = dir_files) %>% pmap(read_excel, col_names = FALSE),
                               "yahoo" = list(file = dir_files) %>% pmap(read_csv)) %>% 
      setNames(sub(paste0(".*", source_directory, "/(.*)_", source, ".*"), "\\1", dir_files))
    
  }
  
  return(output)
}





