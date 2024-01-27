### ASSET ALLOCATION - DATA SOURCING MODULE (functions)

library(quantmod)
library(data.table)
library(futile.logger)
library(purrr)

yahoo_sourcing <- function(asset_class_yahoo_subset, local_save = TRUE, output_dir = getwd()){
  
  yahoo_data <- asset_class_yahoo_subset %>% pull(index_id_in_ds) %>% 
    lapply(FUN = function(symbol) getSymbols(Symbols = symbol, auto.assign = FALSE))
  
  custom_output <- function(data, market, index_name, symbol){
    
    if(local_save){
      fwrite(x = data, file = paste0(output_dir, "/", market, "_", symbol, "yahoo_export_",Sys.Date(), ".csv"))
      flog.info(paste0(index_name, " data (", market,") exported successfully!"), data %>% head(), capture = T)
      return(NULL)
    }else{
      return(data)
    }
    
  }
  
  OUTPUT <- list(data = yahoo_data, 
                 market = asset_class_yahoo_subset %>% pull(market),
                 index_name = asset_class_yahoo_subset %>% pull(index_name),
                 symbol = asset_class_yahoo_subset %>% pull(index_id_in_ds)) %>% 
    pwalk(custom_output)
  
  if(!local_save){
    return(OUTPUT)
  }else{
    return(NULL)
  }
  
}

sp_sourcing <- function()