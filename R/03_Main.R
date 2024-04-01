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
data_saving_config <- fromJSON("data_saving.JSON")

sourcing_date <- Sys.Date()


# raw data sourcing -------------------------------------------------------

#dataSourcing(asset_classes_config[["Equities"]], data_saving_config = data_saving_config$raw_data_saving)

list(assetClassConfig = asset_classes_config[asset_classes_config %>% sapply(FUN = function(x) !is_empty(x))],
     data_saving_config = data_saving_config$raw_data_saving) %>% 
  pwalk(dataSourcing, .progress = TRUE)

# data loading ------------------------------------------------------------

raw_data <- dataLoading(assetClassConfig = asset_classes_config[["Equities"]],
                    data_saving_config = data_saving_config$raw_data_saving,
                    sourcingDate = sourcing_date)


# data pre processing -----------------------------------------------------

processed_data <- preProcessing(raw_data)


# export pre processed data -----------------------------------------------

output_dir <- paste0(data_saving_config$processed_data_saving, "/", sourcing_date)

if(!dir.exists(output_dir)){
  dir.create(output_dir)
}

list(x = processed_data,
     file = paste0(output_dir, "/", names(processed_data), "_", sourcing_date, ".csv")) %>% 
  pwalk(fwrite)


# export single dataframe (for each asset class) --------------------------

processed_data_rename <- processed_data %>% names() %>% 
  lapply(FUN = function(market_name) processed_data[[market_name]] %>% mutate(PRICE = as.numeric(PRICE)) %>% rename(!!market_name := !!as.symbol("PRICE")))
data <- Reduce(function(x, y) merge(x, y, by = "DATE", all = TRUE), processed_data_rename)

fwrite(data, file = "equities_2024-02-25.csv")



