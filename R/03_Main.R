### ASSET ALLOCATION - MAIN DATA GATHERING

setwd("~/Documents/GitHub/asset-allocation")


# custom functions --------------------------------------------------------

source("./R/00_DataSourcing.R")
source("./R/01_DataLoading.R")
source("./R/02_DataPreProcessing.R")


# configuration -----------------------------------------------------------

asset_classes_config <- fromJSON("markets_mapping.JSON")
data_saving_config <- fromJSON("data_saving.JSON")

sourcing_date <- Sys.Date()


# raw data sourcing -------------------------------------------------------

dataSourcing(asset_classes_config[["Equities"]], data_saving_config = data_saving_config$raw_data_saving)


# data loading ------------------------------------------------------------

raw_data <- dataLoading(assetClassConfig = asset_classes_config[["Equities"]],
                    data_saving_config = data_saving_config$raw_data_saving,
                    sourcingDate = sourcing_date)


# data pre processing -----------------------------------------------------

processed_data <- preProcessing(raw_data)


# export pre processed data -----------------------------------------------

list(x = processed_data,
     file = paste0(data_saving_config$processed_data_saving, "/", names(processed_data), "_", sourcing_date, ".csv")) %>% 
  pwalk(fwrite)



