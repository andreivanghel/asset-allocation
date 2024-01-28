### ASSET ALLOCATION - DATA PRE PROCESSING MODULE (functions)

sp_preProcessing <- function(sp_xls){

  output <- sp_xls[(which(sp_xls[,1] == "Effective date") + 1):(nrow(sp_xls) - 4),] %>% 
    setNames(c("DATE", "PRICE")) %>% 
    mutate(DATE = DATE %>% as.numeric() %>% as.Date(origin = "1899-12-30"))
  
  return(output)
  
}

