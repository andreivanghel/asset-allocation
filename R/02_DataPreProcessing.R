### ASSET ALLOCATION - DATA PRE PROCESSING MODULE (functions)

sp_preProcessing <- function(sp_xls){

  output <- sp_xls[(which(sp_xls[,1] == "Effective date") + 1):(nrow(sp_xls) - 4),] %>% 
    setNames(c("DATE", "PRICE")) %>% 
    mutate(DATE = DATE %>% as.numeric() %>% as.Date(origin = "1899-12-30"))
  
  return(output)
  
}

yahoo_preProcessing <- function(yahoo_csv){
  
  col_names <- colnames(yahoo_csv)
  open_col <- col_names[grepl(pattern = "Open", x = col_names)]
  high_col <- col_names[grepl(pattern = "High", x = col_names)]
  low_col <- col_names[grepl(pattern = "Low", x = col_names)]
  close_col <- col_names[grepl(pattern = "Close", x = col_names)]
  volume_col <- col_names[grepl(pattern = "Volume", x = col_names)]
  adjusted_col <- col_names[grepl(pattern = "Adjusted", x = col_names)]
  
  output <- yahoo_csv %>% 
    rename(DATE = index) %>% 
    rename(OPEN := sym(open_col)) %>% 
    rename(HIGH := sym(high_col)) %>% 
    rename(LOW := sym(low_col)) %>% 
    rename(CLOSE := sym(close_col)) %>% 
    rename(VOLUME := sym(volume_col)) %>% 
    rename(PRICE := sym(adjusted_col)) %>% 
    select(DATE, PRICE) # same format as sp sourcing
  
  return(output)
}

preProcessing <- function(loadedData){
  
  loadedData[["sp"]] <- loadedData[["sp"]] %>% lapply(FUN = function(x) sp_preProcessing(x))
  loadedData[["yahoo"]] <- loadedData[["yahoo"]] %>% lapply(FUN = function(x) yahoo_preProcessing(x))
  
  output <- c(loadedData[["sp"]], loadedData[["yahoo"]])
  return(output)
  
}

#test_processed <- preProcessing(TEST)
