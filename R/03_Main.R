### ASSET ALLOCATION - MAIN DATA GATHERING

setwd("~/Documents/GitHub/asset-allocation")


# libraries ---------------------------------------------------------------

library(purrr)


# custom functions --------------------------------------------------------

source("./R/00_DataSourcing.R")
source("./R/01_DataLoading.R")
source("./R/02_DataPreProcessing.R")


# configuration -----------------------------------------------------------

asset_classes_config <- fromJSON("markets_mapping.JSON")
asset_classes_config <- asset_classes_config[asset_classes_config %>% sapply(FUN = function(x) !is_empty(x))]

fx_config <- fromJSON("fx_mapping.JSON")

data_saving_config <- fromJSON("data_saving.JSON")

sourcing_date <- Sys.Date()


# raw data sourcing -------------------------------------------------------

sapply(X = asset_classes_config, 
       FUN = function(x) dataSourcing(assetClassConfig = x, data_saving_config = data_saving_config$raw_data_saving,
                                      sp_username = "andreivanghel@gmail.com",
                                      sp_password = ))

fx_config$fx %>% yahoo_sourcing(data_saving_config = data_saving_config$raw_data_saving, local_save = TRUE)


# data loading ------------------------------------------------------------

raw_data <- lapply(X = asset_classes_config,
                   FUN = function(x) dataLoading(assetClassConfig = x,
                                                 data_saving_config = data_saving_config$raw_data_saving,
                                                 sourcingDate = sourcing_date))

raw_data_fx <- dataLoading(assetClassConfig = fx_config$fx,
                           data_saving_config = data_saving_config$raw_data_saving,
                           sourcingDate = sourcing_date)

# data pre processing -----------------------------------------------------

processed_data_assets <- lapply(X = raw_data, 
                         FUN = function(x) preProcessing(x))
processed_data_fx <- raw_data_fx %>% preProcessing() %>% fxProcessing()
processed_data <- c(processed_data_assets, FX = list(processed_data_fx))
# export pre processed data -----------------------------------------------

export_processed_asset_class <- function(asset_class, processed_data, output_dir){
  
  if(!dir.exists(paste0(output_dir, "/", asset_class))){
    dir.create(paste0(output_dir, "/", asset_class))
  }
  
  list(x = processed_data,
       file = paste0(output_dir, "/", asset_class, "/", names(processed_data), "_", sourcing_date, ".csv")) %>% 
    pwalk(fwrite)
}

output_dir <- paste0(data_saving_config$processed_data_saving, "/", sourcing_date)

if(!dir.exists(output_dir)){
  dir.create(output_dir)
}

list(asset_class = names(processed_data),
     processed_data = processed_data,
     output_dir = output_dir) %>% 
  pwalk(export_processed_asset_class)


# export single dataframe (for each asset class) --------------------------

export_asset_class_time_series <- function(asset_class, processed_data, output_dir){
  
  processed_data_rename <- processed_data %>% names() %>% 
    lapply(FUN = function(market_name) processed_data[[market_name]] %>% mutate(PRICE = as.numeric(PRICE)) %>% rename(!!market_name := !!as.symbol("PRICE")))
  data <- Reduce(function(x, y) merge(x, y, by = "DATE", all = TRUE), processed_data_rename)
  fwrite(data, file = paste0(output_dir, "/", asset_class, "_", sourcing_date, ".csv"))
  
}

list(asset_class = names(processed_data),
     processed_data = processed_data,
     output_dir = output_dir) %>% 
  pwalk(export_asset_class_time_series)



##### TO BE IMPROVED

tmp = list()
for(i in 1:length(processed_data_assets)){
  tmp = c(tmp, processed_data_assets[[i]])
}
processed_data_rename <- tmp %>% names() %>% 
  lapply(FUN = function(market_name) tmp[[market_name]] %>% mutate(PRICE = as.numeric(PRICE)) %>% rename(!!market_name := !!as.symbol("PRICE")))
data <- Reduce(function(x, y) merge(x, y, by = "DATE", all = TRUE), processed_data_rename)
fwrite(data, file = paste0(output_dir, "/", "all_markets", "_", sourcing_date, ".csv"))


